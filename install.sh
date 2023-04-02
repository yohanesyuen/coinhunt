#/bin/sh
apt update
apt install python3-pip -y
systemctl restart networkd-dispatcher.service unattended-upgrades.service
mkdir /app && cd /app
pip install -r requirements.txt
pip install -e .
celery -A coinhunt.tasks worker --loglevel=info