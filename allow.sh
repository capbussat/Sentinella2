#!/bin/bash
# --- Comprovació: cal executar com a root ---
if [ "$EUID" -ne 0 ]; then
  die "Executa aquest script com a root: sudo bash $0"
fi

ufw  --force reset
ufw default allow outgoing
# veyon
ufw allow 11100/tcp
ufw allow 11200/tcp
ufw allow 11300/tcp
ufw allow 11400/tcp
#services
ufw allow to any port 22 proto tcp
ufw allow to any port 53
# final
ufw --force enable
ufw status verbose
}

