import os
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI', default='sqlite:///db.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', default='YOUR_SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Сервис коротких ссылок
    BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000/")

    # Яндекс.Диск
    DISK_API_HOST = "https://cloud-api.yandex.net/"
    DISK_API_VERSION = "v1"
    DISK_TOKEN = os.getenv("DISK_TOKEN", "")
    REQUEST_UPLOAD_URL = f"{DISK_API_HOST}{DISK_API_VERSION}/disk/resources/upload"
    DOWNLOAD_LINK_URL = f"{DISK_API_HOST}{DISK_API_VERSION}/disk/resources/download"

    DEBUG = True
