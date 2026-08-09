# controller.py
import json
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
# import tkinter as tk
from concurrent.futures import ThreadPoolExecutor, as_completed
from settings import settings
from hosts import  load_hosts_from_file
import websockets
from websockets.sync.client import connect

MAX_THREADS = 4

def send(host,command):
    uri = f"ws://{host}:8765"
    message = json.dumps({"status": command})
    try:
        with connect(uri) as websocket:
            websocket.send(message)
            print(f">>> {host} {message}")
            answer = websocket.recv()
            print(f"<<< {host} {answer}")
    # el servidor no s'executa, bloquejat pel tallafocs o el  port no és correcte
    except OSError as e:
            print(f"No hi ha ruta al host {host}")
    except ConnectionRefusedError:
            print("No hi ha connexió a{host}.")

class SentinellaApp(ttk.Window):

    def __init__(self):
        super().__init__(themename="superhero")
        self.buttons_config = []
        self.buttons_config = settings.buttons

        self.title("Sentinella GUI")
        self.geometry("800x400")
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        ttk.Separator(self.main_frame, orient=HORIZONTAL).pack(fill=X, pady=8)
        self.create_dynamic_buttons()

    def create_dynamic_buttons(self):

        if not self.buttons_config:
            return

        for btn in self.buttons_config:
            title = btn.get("title", "Button")
            command = btn.get("command", "")
            style= btn.get("style","PRIMARY")
            button = ttk.Button(
                self.main_frame,
                text=title,
                bootstyle=style,
            )
            button.config(
                command=lambda b=button, c=command, t=title:
                    self.run_dynamic_command(b, t, c)
            )
            button.pack(side=LEFT, padx=5)

    def run_dynamic_command(self, button, title, command):
         with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
             self.hosts = load_hosts_from_file()
             for host in self.hosts:
                 executor.submit(send(host.ip,command))

    def hosts(self):
       pass

if __name__ == "__main__":
    try:
        app = SentinellaApp()
        app.mainloop()
    except KeyboardInterrupt:
        print ("Acabat amb CTRL+C")
