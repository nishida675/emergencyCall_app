import boto3
from datetime import datetime, timezone, timedelta
from boto3.dynamodb.conditions import Key

# DynamoDB リソースとテーブルの取得
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("phoneInfoDemo")

def lambda_handler(event, context):
    try:
        print("受け取った event:", event)
        
        # 電話番号を取得（例: Amazon Connect のイベント）
        phoneNumber = event["Details"]["ContactData"]["CustomerEndpoint"]["Address"]

        # JST (日本標準時) で現在日時を取得
        JST = timezone(timedelta(hours=9), 'JST')
        current_date = datetime.now(JST)
        callTimestamp = current_date.isoformat()  # ISO形式のタイムスタンプ

        # 同じ電話番号で phoneConfirmation が True のレコードが存在するかチェック
        response = table.query(
            KeyConditionExpression=Key('phoneNumber').eq(phoneNumber)
        )
        items = response.get('Items', [])
        
        # 存在するレコードを走査し、phoneConfirmation が True なら新規挿入しない
        for item in items:
            if item.get('phoneConfirmation') is True:
                print("既に phoneConfirmation が True のレコードが存在するため、新規挿入は行いません。")
                return {"statusCode": 200, "body": "Record already exists with confirmation True."}
        
        # 条件を満たすレコードが存在しなければ、新規レコードを挿入
        table.put_item(
            Item={
                'phoneNumber': phoneNumber,      # パーティションキー
                'callTimestamp': callTimestamp,  # ソートキーとして通話ごとのタイムスタンプ
                'phoneConfirmation': True
            }
        )
        
        return {"statusCode": 200, "body": "Record inserted successfully."}
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"statusCode": 500, "body": f"Error: {str(e)}"}
