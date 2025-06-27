import json

def handler(event, context):    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
            "Content-Type": "application/json"
        },
        'body': json.dumps("""<iframe
                width="960"
                height="720"
                src="https://us-east-1.quicksight.aws.amazon.com/sn/embed/share/accounts/141924116863/dashboards/c14ef6e0-7264-4a64-99c5-60c2329d6857?directory_alias=qk-tfm-unir">
            </iframe>""")
    }