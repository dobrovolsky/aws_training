from troposphere import (
    Template,
    GetAtt,
)

from troposphere import (
    s3,
    rds,
    awslambda,
)
from troposphere.iam import (
    Role,
    Policy,
)

t = Template()

# db = t.add_resource(
#     rds.DBInstance(
#         'Postgres',
#         DBInstanceClass='db.t2.micro',
#         Engine='postgres',
#         MasterUsername='postgres',
#         MasterUserPassword='postgres',
#         AllocatedStorage="5",
#         DBName="Postgres",
#     ))

lambda_func = t.add_resource(awslambda.Function(
    'LambdaProcessing',
    Handler='lambda_function.lambda_handler',
    Role=GetAtt("LambdaExecutionRole", "Arn"),
    Runtime='python3.7',
    Code=awslambda.Code(
        ZipFile='print("hello world!!!!!!!!")'
        # S3Bucket='code-4ed9328a-1818-4984-8534-c1a214428dc4',
        # S3Key='code.zip'
    ),
))

t.add_resource(
    s3.Bucket(
        'UploadedResources',
        BucketName='uploaded-file-processing-ee5a4c2a-b5a7-4b80-ac22-5763e7a93552',
        VersioningConfiguration=s3.VersioningConfiguration(
            Status='Enabled',
        ),
        DependsOn=['LambdaProcessing',],
        NotificationConfiguration=s3.NotificationConfiguration(
            LambdaConfigurations=[
                s3.LambdaConfigurations(
                    Event='s3:ObjectCreated:*',
                    Function=GetAtt(lambda_func, 'Arn')
                )
            ]
        )
    )
)

# t.add_resource(
#     s3.Bucket(
#         'CodeStorage',
#         BucketName='code-4ed9328a-1818-4984-8534-c1a214428dc4',
#     )
# )

LambdaExecutionRole = t.add_resource(Role(
    "LambdaExecutionRole",
    Path="/",
    Policies=[Policy(
        PolicyName="S3Policy",
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [{
                "Action": ["s3:GetObject", 's3:PutObject', 'S3:DeleteObject'],
                "Resource": "arn:aws:s3:::*",
                "Effect": "Allow"
            }]
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
))

with open('cf.yaml', 'w+') as f:
    print(t.to_yaml(), file=f)
