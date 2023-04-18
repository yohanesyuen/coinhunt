#/bin/bash
systemctl restart networkd-dispatcher.service unattended-upgrades.service
mkdir /app
git clone https://github.com/yohanesyuen/coinhunt.git /app/coinhunt
cd /app/coinhunt
pip install -e /app/coinhunt
# celery -A coinhunt.tasks worker --loglevel=info
cp ./install/coinhunt.service /etc/systemd/system/coinhunt.service
systemctl daemon-reload
systemctl enable coinhunt.service
systemctl start coinhunt.service
