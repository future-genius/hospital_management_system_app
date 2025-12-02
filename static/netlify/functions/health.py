def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/plain'},
        'body': 'OK - functions detected (static/netlify/functions)'
    }
