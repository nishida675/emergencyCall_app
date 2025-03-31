import boto3
from boto3.dynamodb.conditions import Key

# DynamoDB クライアントの作成
dynamodb = boto3.resource('dynamodb')

# テーブル名を指定
table = dynamodb.Table("phoneInfoDemo")

def lambda_handler(event, context):
    print(event)
    try:
        phone_number = event.get('Details', {}).get('Parameters', {}).get('phoneNumber')
        if not phone_number:
            return {
                "statusCode": 400,
                "body": "phoneNumber is missing in the parameters"
            }
        
        response = table.query(
            KeyConditionExpression=Key('phoneNumber').eq(phone_number)
        )
        items = response.get('Items', [])
        
        if not items:
            return {
                "statusCode": 404,
                "body": "No matching item found"
            }

        # `phoneConfirmation=True` のデータを取得
        true_items = [item for item in items if item.get('phoneConfirmation') is True]

        # `True` のデータがない場合は 404 を返す
        if not true_items:
            return {
                "statusCode": 404,
                "body": "No matching item found with phoneConfirmation=True"
            }

        # 一番古い `True` のデータを取得
        target_item = sorted(true_items, key=lambda x: x['callTimestamp'])[0]

        # `phoneConfirmation` を `False` に更新
        table.update_item(
            Key={
                "phoneNumber": target_item["phoneNumber"],
                "callTimestamp": target_item["callTimestamp"]
            },
            UpdateExpression="SET phoneConfirmation = :falseVal",
            ExpressionAttributeValues={":falseVal": False}
        )

        return {
            "statusCode": 200,
            "body": f"Updated phoneNumber {phone_number} with callTimestamp {target_item['callTimestamp']} to false"
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }
