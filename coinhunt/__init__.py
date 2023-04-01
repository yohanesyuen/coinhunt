import dotenv
import os

ROOT_PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(ROOT_PACKAGE_DIR)

dotenv.load_dotenv(f'{ROOT_DIR}/.env')

REDIS_PASS = os.environ.get('REDIS_PASS')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_HOST = os.environ.get('REDIS_HOST')

REDIS_URL = f'redis://:{REDIS_PASS}@{REDIS_HOST}:{REDIS_PORT}/0'

print(ROOT_DIR)