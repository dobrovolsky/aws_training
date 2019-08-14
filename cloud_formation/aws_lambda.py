from troposphere import (
    GetAtt,
    Ref,
    iam,
    awslambda,
    Parameter,
)

from db import (
    db,
    db_name,
    db_password,
    db_user,
    dynamo_db,
)
from sns import sns_topic

source_code_bucket = Parameter(
    "SourceCodeBucket",
    Description="Bucket with source code",
    Type="String",
)

zip_file_path = Parameter(
    "ZipFilePath",
    Description="Bucket with source code",
    Type="String",
)

lambda_name = Parameter(
    "LambdaName",
    Description="Bucket with source code",
    Type="String",
)

# ============================================================================
# Lambda Function
# ============================================================================
lambda_processing = awslambda.Function(
    'LambdaProcessing',
    Handler='lambda_function.lambda_handler',
    Role=GetAtt("LambdaExecutionRole", "Arn"),
    Runtime='python3.7',
    FunctionName=Ref(lambda_name),
    Code=awslambda.Code(
        S3Bucket=Ref(source_code_bucket),
        S3Key=Ref(zip_file_path)
    ),
    Environment=awslambda.Environment(
        Variables={
            'DB_HOST': GetAtt(db, 'Endpoint.Address'),
            'DB_NAME': Ref(db_name),
            'DB_PASSWORD': Ref(db_password),
            'DB_PORT': GetAtt(db, 'Endpoint.Port'),
            'DB_USERNAME': Ref(db_user),
            'DYNAMODB_TABLE': Ref(dynamo_db),
            'SNS_TOPIC': Ref(sns_topic),
        }
    )
)

# ============================================================================
# Lambda Permission
# ============================================================================
s3_lambda_permission = awslambda.Permission(
    'S3LambdaPermission',
    Action='lambda:invokeFunction',
    Principal='s3.amazonaws.com',
    FunctionName=Ref(lambda_processing),
)

lambda_execution_role = iam.Role(
    "LambdaExecutionRole",
    Path="/",
    Policies=[iam.Policy(
        PolicyName="S3Policy",
        PolicyDocument={
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': [
                        's3:GetObject',
                        's3:PutObject',
                        'S3:DeleteObject'],
                    'Resource': 'arn:aws:s3:::*',
                    'Effect': 'Allow'
                },
                {
                    'Effect': 'Allow',
                    'Action': [
                        'sns:Publish'
                    ],
                    'Resource': 'arn:aws:sns:*:*:*'
                },
                {
                    'Effect': 'Allow',
                    'Action': [
                        'dynamodb:DeleteItem',
                        'dynamodb:GetItem',
                        'dynamodb:PutItem',
                        'dynamodb:Scan',
                        'dynamodb:UpdateItem'
                    ],
                    'Resource': 'arn:aws:dynamodb:eu-central-1:954489397717:table/*'
                }
            ]
        })],
    AssumeRolePolicyDocument={
        "Version": "2012-10-17",
        "Statement": [{
            "Action": ["sts:AssumeRole"],
            "Effect": "Allow",
            "Principal": {
                "Service": ["lambda.amazonaws.com"]
            }
        }]
    },
)