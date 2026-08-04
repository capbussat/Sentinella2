#!/usr/bin/env python3

#!/usr/bin/env python3
from pathlib import Path
from dataclasses import dataclass

HOSTS = "/etc/sentinella/hosts"

@dataclass
class Host:
    ip: str
    label: str

    def __str__(self) -> str:
        return f"{self.label} ({self.ip})"


def load_hosts_from_file(filename: str = HOSTS) -> list[Host]:
    file_path = Path(filename)

    if not file_path.exists():
        raise FileNotFoundError(f"Hosts file not found: {file_path}")

    hosts: dict[str, Host] = {}  # clau=ip, garanteix unicitat

    with open(file_path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            parts = line.split()

            if len(parts) == 0:
                continue

            ip = parts[0]
            label = parts[1] if len(parts) > 1 else ip  # fallback a la IP

            if ip in hosts:
                print(f"[WARN] IP duplicada a la línia {lineno}: {ip} — ignorada")
                continue

            hosts[ip] = Host(ip=ip, label=label)

    return list(hosts.values())