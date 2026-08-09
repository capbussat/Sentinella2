# sentinella.py
"""
Client WebSocket de supervisio (versio amb Threads).
Espera missatge del controlador i envia confirmacio.
"""
import argparse
import asyncio
import json
from os import path
import queue
import re
import subprocess
import sys
import threading
import time
import websockets
from websockets.exceptions import ConnectionClosed

IFACE = "enp2s0"        # interficie de xarxa a consultar
STATUS_READ_INTERVAL = 5  # segons entre lectures de la cua
BINARIES="/usr/local/bin"
SETTINGS="/etc/sentinella"
DATA="/tmp"

msg_queue = queue.Queue()

def execute_command(command, *args):
    binari = path.join(BINARIES, command)
    try:
        sortida = subprocess.run(
            [binari, *args],
            capture_output=True, text=True, check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        sys.exit(f"No s'ha pogut executar: {e}")
    return sortida

def check():
    print ("Aplica check!")
    sortida = execute_command("ping", "-c", "4", "www.google.com")
    return sortida

def browser_policy():
    print ("Aplica broswer_policy!")
    sortida = execute_command("add-browser-policies.sh")
    return sortida

def restrict_internet():
    print ("Aplica restrict_internet!")

def allow():
    print ("Aplica allow!")
    sortida = execute_command("remove-browser-policies.sh")

# definit després de les funcions
call_actions = {
    "check": check,
    "browser_policy": browser_policy,
    "allow": allow,
    "restrict_internet": restrict_internet
}

# ----------------------------------------------------
def detect_own_ip(iface: str = IFACE) -> str:
    """Obté la IPv4 de la interfície indicada mitjançant 'ip addr'."""
    try:
        sortida = subprocess.run(
            ["ip", "-4", "-oneline", "addr", "show", "dev", iface],
            capture_output=True, text=True, check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        sys.exit(f"No s'ha pogut consultar la interficie {iface}: {e}")
    match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", sortida)
    if not match:
        sys.exit(f"La interficie {iface} no té IPv4 assignada")
    return match.group(1)

# ---------- Thread 1: servidor websockets ----------

async def handler(websocket):
    async for message in websocket:
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            data = json.dumps({"status": "invalid"})

        await websocket.send(message)  # eco

        if isinstance(data, dict) and "status" in data:
            msg_queue.put(data)
        else:
            print(f"[warn] missatge amb format inesperat: {data!r}")

# coroutines
async def ws_main(host, port):
    async with websockets.serve(handler, host, port):
        await asyncio.Future()  # bloqueja per sempre

def start_server(host="0.0.0.0", port=8765):
# Necessari per començar coroutines
    asyncio.run(ws_main(host, port))

# ---------- Thread 2: process loop  ----------

def process_loop():
    """Thread que, cada STATUS_READ_INTERVAL segons, treu un element de la cua i n'imprimeix el status."""
    while True:
        time.sleep(STATUS_READ_INTERVAL)
        try:
            data = msg_queue.get(block=True, timeout=STATUS_READ_INTERVAL)
            log_time = time.strftime("%Y-%m-%d %H:%M:%S")
            status = data['status']
            print(f"[status] {log_time} status={status}")
            # Crida a la funció apropiada
            if status in call_actions:
                result = call_actions[status]()
                print(result)
        except queue.Empty:
            # print("Queue is empty")
            pass

# ---------- Main ------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sentinella amb websockets")
    parser.add_argument("--iface", default=IFACE, help="Interficie de xarxa (per defecte enp2s0)")
    args = parser.parse_args()
    my_ip = detect_own_ip(args.iface)

    try:
        t_status = threading.Thread(target=process_loop, args=(), daemon=True)
        t_server = threading.Thread(target=start_server,  args=(), daemon=True)
        t_status.start()
        t_server.start()
        t_server.join()

    except KeyboardInterrupt:
        print("\nClient aturat (CTRL+C)")
