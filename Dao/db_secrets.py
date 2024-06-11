import json

import boto3
from botocore.exceptions import ClientError

from config import DB_SECRET_NAME, AWS_REGION_NAME

def get_secret():
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name= AWS_REGION_NAME,
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=DB_SECRET_NAME
        )
    except ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']
    secret_dict = json.loads(secret)
    return secret_dict["username"], secret_dict["password"]

