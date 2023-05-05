#/bin/bash
apt update
apt install python3 -y
apt install python3-pip -y
apt install python-is-python3 -y
systemctl restart networkd-dispatcher.service unattended-upgrades.service
if [ ! -d "/app" ]; then
    mkdir /app
fi
if [ ! -d "/app/coinhunt" ]; then
    git clone https://github.com/yohanesyuen/coinhunt.git /app/coinhunt
    cd /app/coinhunt
    pwd
    git submodule update --init --recursive
    pip install -e /app/coinhunt
else
    cd /app/coinhunt
    git pull
fi
if [ -f "/app/coinhunt/.env" ]; then
    cp /app/coinhunt/install/coinhunt.service /etc/systemd/system/coinhunt.service
    cp /app/coinhunt/install/coinhunt.config /etc/coinhunt.conf
    systemctl daemon-reload
    systemctl enable coinhunt.service
    systemctl start coinhunt.service
fi