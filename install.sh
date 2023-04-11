#/bin/sh
apt update
apt install python3-pip -y
systemctl restart networkd-dispatcher.service unattended-upgrades.service
mkdir /app && cd /app
git clone https://github.com/yohanesyuen/coinhunt.git
cd /app/coinhunt
pip install -e .
# celery -A coinhunt.tasks worker --loglevel=info
cp ./install/coinhunt.service /etc/systemd/system/coinhunt.service
systemctl daemon-reload
systemctl enable coinhunt.service
systemctl start coinhunt.service
