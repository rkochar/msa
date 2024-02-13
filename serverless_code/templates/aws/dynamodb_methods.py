#from boto3 import resource
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import json

def insert_data(item):
    table_name = getenv("DYNAMODB_TABLE_NAME")
    dynamodb = boto3.resource('dynamodb')

    try:
        print(f"Inserting {item} into table: {table_name}")
        response = dynamodb.put_item(
            TableName=table_name,
            Item=item,
            ReturnConsumedCapacity='TOTAL',
            ReturnValues='ALL_NEW'
        )

        print("Data inserted successfully")
        return {
            'statusCode': 200,
            'body': json.dumps('Data inserted successfully')
        }
    except BotoCoreError as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'An error occurred while inserting data: {e}')
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'An error occurred while inserting data: {e}')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'An error occurred while inserting data: {e}')
        }
