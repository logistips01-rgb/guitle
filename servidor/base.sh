#!/usr/bin/env bash
# Paso "base" del servidor propio de guitle.com (IONOS, Ubuntu): seguridad básica y programas. Se puede repetir.
# Lo lanza .github/workflows/servidor.yml (primera línea de .github/servidor.txt: "base").
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

echo "== Actualizaciones y programas"
apt-get update -qq
apt-get -y -qq upgrade
apt-get -y -qq install ufw unattended-upgrades fail2ban caddy rclone rsync python3 curl jq >/dev/null
dpkg-reconfigure -f noninteractive unattended-upgrades >/dev/null 2>&1 || true

echo "== Memoria de intercambio (1 GB: el servidor tiene 2 GB)"
if [ ! -f /swapfile ]; then
  fallocate -l 1G /swapfile && chmod 600 /swapfile && mkswap /swapfile >/dev/null && swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

echo "== Entrada solo con llave (la llave ya funciona: GitHub ha entrado con ella)"
mkdir -p /etc/ssh/sshd_config.d
cat > /etc/ssh/sshd_config.d/10-guitle.conf <<'EOF'
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin prohibit-password
EOF
systemctl reload ssh || systemctl reload sshd || true

echo "== Cortafuegos del sistema: solo SSH y web"
ufw --force reset >/dev/null
ufw default deny incoming >/dev/null
ufw default allow outgoing >/dev/null
ufw allow 22/tcp >/dev/null
ufw allow 80/tcp >/dev/null
ufw allow 443/tcp >/dev/null
ufw --force enable >/dev/null
ufw status | head -12

echo "== fail2ban (bloquea a quien prueba contraseñas por SSH)"
systemctl enable --now fail2ban >/dev/null 2>&1 || true

echo "== Versiones"
caddy version | head -1; rclone version | head -1; python3 --version
free -m | head -2; df -h / | tail -1
echo "base: listo"
