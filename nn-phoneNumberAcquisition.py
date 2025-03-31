import boto3
import json
from boto3.dynamodb.conditions import Attr

# DynamoDB クライアントとテーブルの取得
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("phoneInfoDemo")

def lambda_handler(event, context):
    try:
        # phoneConfirmation が True のアイテムのみ取得
        response = table.scan(
            FilterExpression=Attr('phoneConfirmation').eq(True)
        )
        items = response.get('Items', [])
        print("取得したアイテム数:", len(items))
        
        # callTimestamp で昇順（古い順）にソート
        sorted_items = sorted(items, key=lambda x: x.get('callTimestamp', ''))
        
        if sorted_items:
            # 最も古いアイテムを取得し、その phoneNumber を返す
            oldest_item = sorted_items[0]
            print(oldest_item)
            return {
                "phoneNumber": oldest_item.get('phoneNumber', '')
            }
        else:
            return {
                "statusCode": 404,
                "body": json.dumps({"message": "No items with phoneConfirmation True found"})
            }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
