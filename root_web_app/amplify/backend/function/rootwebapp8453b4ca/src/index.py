import json
import boto3
import jwt
import time
import os

def getMetabaseDashboard():
    sm = boto3.client('secretsmanager')
    response = sm.get_secret_value(
        SecretId='METABASE_SECRET_KEY'
    )

    METABASE_SITE_URL = "http://ec2-54-166-177-96.compute-1.amazonaws.com:3000/"
    METABASE_SECRET_KEY = response['SecretString']
    payload = {
    "resource": {"dashboard": 2},
    "params": {
        
    },
    "exp": round(time.time()) + (60 * 10) # 10 minute expiration
    }
    token = jwt.encode(payload, METABASE_SECRET_KEY, algorithm="HS256")

    iframeUrl = METABASE_SITE_URL + "/embed/dashboard/" + token + "#bordered=true&titled=true"
    return iframeUrl


def handler(event, context):    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
            "Content-Type": "application/json"
        },
        'body': json.dumps(getMetabaseDashboard())
    }