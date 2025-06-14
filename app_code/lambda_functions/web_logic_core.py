import json

def lambda_handler(event, context):
    """
    A simple AWS Lambda function placeholder.
    """
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "https://web.d347kktgec41m0.amplifyapp.com",
            "Access-Control-Allow-Headers": "Content-Type,authorization",
            "Access-Control-Allow-Methods": "GET"
        },
        'body': json.dumps({ 
            'dashboard': "placeholder"
        })
    }