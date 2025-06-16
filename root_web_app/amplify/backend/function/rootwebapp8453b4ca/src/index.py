import json

def handler(event, context):    
    dashboard_data = {
        'title': "Root Web App Dashboard"
    }
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
            "Content-Type": "application/json"
        },
        'body': json.dumps(dashboard_data)
    }
    