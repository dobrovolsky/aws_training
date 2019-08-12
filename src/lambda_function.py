import datetime
import os
from urllib.parse import unquote_plus

import boto3
from boto3.dynamodb.types import TypeSerializer

from db import DBPostgres

s3 = boto3.client('s3')
dynamodb = boto3.client('dynamodb')
sns = boto3.client('sns')


class Handler:
    def __init__(self, event, context, sns_topic, dynamodb_table):
        self.event = event
        self.context = context
        self.sns_topic = sns_topic
        self.dynamodb_table = dynamodb_table

    def handle(self, event, context, db):
        self.log_start_to_dynamodb(event, context)

        file = self.fetch_file_data(event)
        if file['ContentType'] == 'text/csv':
            file_body = file['Body'].read()

            prepared_data = self.prepare_data(file_body)

            if prepared_data:
                db.save(prepared_data)

        self.send_to_sns_topic()
        self.log_finish_to_dynamodb(event, context)

    @staticmethod
    def fetch_file_data(event):
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
        try:
            response = s3.get_object(Bucket=bucket, Key=key)
            return response
        except Exception as e:
            print(e)
            raise

    @staticmethod
    def prepare_data(body):
        prepared_data = []
        for s in body.decode().split('\n'):
            parsed = s.split(',')
            if len(parsed) == 4:
                date, item, amount, category = parsed
                date = int(datetime.datetime.strptime(date, '%d.%m.%Y').timestamp())
                prepared_data.append((date, item, amount, category))
        return prepared_data

    def log_start_to_dynamodb(self, event, context):
        data = {
            'start_time': int(datetime.datetime.now().timestamp()),
            'lambda_status': 'started',
            'request_id': str(context.aws_request_id)
        }

        dynamodb.put_item(
            TableName=self.dynamodb_table,
            Item={k: TypeSerializer().serialize(v) for k, v in data.items()},
        )

    def log_finish_to_dynamodb(self, event, context):
        dynamodb.update_item(
            TableName=self.dynamodb_table,
            Key={
                'request_id': TypeSerializer().serialize(str(context.aws_request_id)),
            },
            UpdateExpression='set lambda_status = :s, finish_time = :t',
            ExpressionAttributeValues={
                ':s': TypeSerializer().serialize('done'),
                ':t': TypeSerializer().serialize(int(datetime.datetime.now().timestamp())),
            }
        )

    def send_to_sns_topic(self):
        sns.publish(
            TopicArn=self.sns_topic,
            Message=f'Processed request {self.context.aws_request_id}',
        )


def lambda_handler(event, context):
    amazon = Handler(
        event=event,
        context=context,
        sns_topic=os.environ['SNS_TOPIC'],
        dynamodb_table=os.environ['DYNAMODB_TABLE'],
    )
    db = DBPostgres(
        host=os.environ['DB_HOST'],
        port=int(os.environ['DB_PORT']),
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD'],
    )

    amazon.handle(event, context, db)


