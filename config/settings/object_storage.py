from config.env import env
from storages.backends.s3boto3 import S3Boto3Storage

DEFAULT_FILE_STORAGE = 'yandex_s3_storage.ClientDocsStorage'
YANDEX_CLIENT_DOCS_BUCKET_NAME = env('YANDEX_CLIENT_DOCS_BUCKET_NAME')
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_S3_ENDPOINT_URL = 'https://storage.yandexcloud.net'
AWS_S3_REGION_NAME = 'ru-central1'


class ClientDocsStorage(S3Boto3Storage):
    bucket_name = YANDEX_CLIENT_DOCS_BUCKET_NAME
    file_overwrite = False
