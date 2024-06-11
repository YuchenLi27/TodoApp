import json

import boto3
from botocore.exceptions import ClientError

from config import DB_SECRET_NAME, AWS_REGION_NAME

def get_secret():
    session = boto3.session.Session()
    client = session.client(service_name = 'secretsmanager',
                            region_name= AWS_REGION_NAME,
    )

    try:
        
