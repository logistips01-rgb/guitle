#!/usr/bin/env bash
# Servidor de casa de guitle (fase 1): deja el portátil haciendo cada día las lecturas que bloquean a GitHub (CDGO).
# Uso, en el portátil con Ubuntu recién instalado:
#   curl -fsSL https://raw.githubusercontent.com/logistips01-rgb/guitle/claude/friendly-fermat-yycain/servidor/instalar.sh | bash
# Hace: instala lo necesario, crea una clave solo para subir datos a GitHub (te la enseña para añadirla al repo),
# descarga el proyecto, programa el barrido diario (11:23) y evita que el portátil se duerma con la tapa cerrada.
set -euo pipefail
REPO=logistips01-rgb/guitle
BRANCH=claude/friendly-fermat-yycain
DIR="$HOME/guitle"

echo "== 1/5 Paquetes"
sudo apt-get update -qq
sudo apt-get install -y -qq git python3 python3-venv python3-pip curl >/dev/null

echo "== 2/5 Que no se duerma con la tapa cerrada ni por inactividad"
sudo sed -i 's/^#\?HandleLidSwitch=.*/HandleLidSwitch=ignore/; s/^#\?HandleLidSwitchExternalPower=.*/HandleLidSwitchExternalPower=ignore/' /etc/systemd/logind.conf
grep -q '^HandleLidSwitch=ignore' /etc/systemd/logind.conf || echo 'HandleLidSwitch=ignore' | sudo tee -a /etc/systemd/logind.conf >/dev/null
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target >/dev/null 2>&1 || true
sudo systemctl restart systemd-logind || true

echo "== 3/5 Clave para subir datos a GitHub (solo este repositorio)"
mkdir -p "$HOME/.ssh" && chmod 700 "$HOME/.ssh"
if [ ! -f "$HOME/.ssh/guitle_deploy" ]; then
  ssh-keygen -t ed25519 -N "" -C "servidor-casa-guitle" -f "$HOME/.ssh/guitle_deploy" >/dev/null
fi
cat > "$HOME/.ssh/config" <<CFG
Host github.com
  IdentityFile ~/.ssh/guitle_deploy
  IdentitiesOnly yes
CFG
ssh-keyscan -q github.com >> "$HOME/.ssh/known_hosts" 2>/dev/null || true

echo "== 4/5 Proyecto"
if [ ! -d "$DIR/.git" ]; then
  git clone -q --depth 1 --branch "$BRANCH" "https://github.com/$REPO.git" "$DIR"
fi
cd "$DIR"
git remote set-url origin "git@github.com:$REPO.git"
git config user.name "servidor-casa-guitle"
git config user.email "servidor@guitle.com"
python3 -m venv "$HOME/guitle-venv"
"$HOME/guitle-venv/bin/pip" install -q -r requirements.txt

echo "== 5/5 Barrido diario (11:23, hora del portátil)"
chmod +x "$DIR/servidor/barrido.sh"
( crontab -l 2>/dev/null | grep -v 'servidor/barrido.sh' ; echo "23 11 * * * $DIR/servidor/barrido.sh >> $HOME/barrido.log 2>&1" ) | crontab -
sudo timedatectl set-timezone Europe/Madrid || true

echo
echo "=============================================================================="
echo "FALTA UN PASO: copia esta línea (la clave pública) y añádela en GitHub:"
echo "  github.com/$REPO/settings/keys → Add deploy key → título 'servidor casa',"
echo "  pega la clave y MARCA 'Allow write access' → Add key"
echo
cat "$HOME/.ssh/guitle_deploy.pub"
echo
echo "Después, para probarlo ya:  $DIR/servidor/barrido.sh"
echo "=============================================================================="
