import dotenv
import os

ROOT_PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(ROOT_PACKAGE_DIR)
ENV_FILE = f'{ROOT_DIR}/.env'

dotenv.load_dotenv(ENV_FILE)

REDIS_PASS = os.environ.get('REDIS_PASS')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_HOST = os.environ.get('REDIS_HOST')

REDIS_URL = f'redis://:{REDIS_PASS}@{REDIS_HOST}:{REDIS_PORT}/0'

LINODE_TOKEN = os.environ.get('LINODE_TOKEN')
LINODE_ROOT_PASSWORD = os.environ.get('LINODE_ROOT_PASSWORD')
