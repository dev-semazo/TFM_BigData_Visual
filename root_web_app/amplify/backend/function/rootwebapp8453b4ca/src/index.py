import json
import boto3

def getQuickSightDashboardUrl():
    #Create QuickSight client
    #quickSight = boto3.client('quicksight', region_name="us-east-1")
    #response = quickSight.generate_embed_url_for_anonymous_user(
    #AwsAccountId = "141924116863",
    #Namespace = 'default',
    #ExperienceConfiguration = {'Dashboard':{'InitialDashboardId': "c14ef6e0-7264-4a64-99c5-60c2329d6857"}},
    #AuthorizedResourceArns = ["arn:aws:quicksight:us-east-1:141924116863:dashboard/c14ef6e0-7264-4a64-99c5-60c2329d6857"],
    #SessionLifetimeInMinutes = 60,
    #)
    #return response["EmbedUrl"]
    return """
    <iframe
        width="960"
        height="720"
        src="https://us-east-1.quicksight.aws.amazon.com/sn/embed/share/accounts/141924116863/dashboards/c14ef6e0-7264-4a64-99c5-60c2329d6857?directory_alias=qk-tfm-unir">
    </iframe>"""



def handler(event, context):    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
            "Content-Type": "application/json"
        },
        'body': json.dumps(getQuickSightDashboardUrl())
    }