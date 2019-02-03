import boto3
from django.conf import settings
from django.core.files import File
from tempfile import NamedTemporaryFile
from django.core.files.storage import Storage


class S3Storage(Storage):

    def __init__(self):
        self.client = boto3.client('s3')
        self.bucket = settings.AWS_STORAGE_BUCKET_NAME
        self.prefix = 'photos/'

    def exists(self, name):
        key = self._format_key(name)
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except:
            return False

    def listdir(self, path):
        path = self._format_key(path)
        results = self.client.list_objects(
            Bucket=self.bucket,
            Prefix=path,
            Delimiter='/'
        )

        dirs = []
        if results.get('CommonPrefixes') is not None:
            for item in results.get('CommonPrefixes'):
                dirs.append(item['Prefix'][7:])  # Remove photos/ prefix

        files = []
        for item in results.get('Contents'):
            if item['Key'][-1] != '/':  # Do not process directories
                files.append(item['Key'][7:])

        return (dirs, files)

    def listfiles(self, path):
        path = self._format_key(path)
        results = self.client.list_objects(
            Bucket=self.bucket,
            Prefix=path,
            Delimiter='/'
        )

        files = []
        for item in results.get('Contents'):
            if item['Key'][-1] != '/':  # Do not process directories
                files.append({
                    'name': item['Key'][7:],
                    'size': item['Size'],
                    'modified': item['LastModified'],
                })
        return files

    def open(self, name):
        tmpfile = NamedTemporaryFile(delete=False)
        path = self._format_key(name)
        self.client.download_file(self.bucket, path, tmpfile.name)
        return tmpfile

    def _format_key(self, key):
        if key == '/':
            key = ''

        return self.prefix + key
