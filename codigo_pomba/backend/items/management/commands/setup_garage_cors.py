import boto3
from botocore.client import Config
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Configura CORS en el bucket de Garage para permitir subidas presignadas desde el navegador'

    def handle(self, *args, **kwargs):
        cliente = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            config=Config(
                signature_version='s3v4',
                s3={'addressing_style': 'path'},
            ),
        )

        cliente.put_bucket_cors(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            CORSConfiguration={
                'CORSRules': [
                    {
                        'AllowedHeaders': ['*'],
                        'AllowedMethods': ['GET', 'PUT', 'HEAD'],
                        'AllowedOrigins': ['http://localhost', 'http://127.0.0.1'],
                        'ExposeHeaders': ['ETag'],
                        'MaxAgeSeconds': 3600,
                    }
                ]
            },
        )

        self.stdout.write(self.style.SUCCESS(
            f'CORS configurado correctamente en el bucket "{settings.AWS_STORAGE_BUCKET_NAME}"'
        ))
