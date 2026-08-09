#!/bin/bash
# --- Comprovació: cal executar com a root ---
if [ "$EUID" -ne 0 ]; then
  die "Executa aquest script com a root: sudo bash $0"
fi

# comprovació de ip
ALLOW_FILE=/etc/sentinella/allow

ips=()
# Comprova IPs
is_ipv4() {
    [[ "$1" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]]
}

while IFS= read -r domini; do
    # Salta línies buides i comentaris
    [[ -z "$domini" || "$domini" == \#* ]] && continue

    while IFS= read -r ip; do
        is_ipv4 "$ip" && ips+=("$ip")
    done < <(dig +short "$domini")
done < "$ALLOW_FILE"

# bucle ufw allow
ufw_allow_list(){
for ip in "${ips[@]}"; do
    ufw allow out to "$ip" port 443 proto tcp
    ufw allow out to "$ip" port 80 proto tcp
done
}

    ufw default deny outgoing
    ufw_allow_list
    ufw allow proto icmp
    ufw allow 11100/tcp
    ufw allow 11200/tcp
    ufw allow 11300/tcp
    ufw allow 11400/tcp
    ufw allow out proto udp to any port 53
    ufw allow out proto tcp to any port 53
    ufw enable
    ufw status verbose
    touch "${CHECK_ON}"
    echo "$(log_date) Enabled UFW rules" >> "${LOG}"
    echo "$(log_date) Set ${CHECK_ON}" >> "${LOG}"
}
