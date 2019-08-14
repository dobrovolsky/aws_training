from troposphere import (
    GetAtt,
    s3,
)

from aws_lambda import lambda_processing

bucket = s3.Bucket(
    'UploadedResources',
    BucketName='uploaded-file-processing-ee5a4c2a-b5a7-4b80-ac22-5763e7a93552',
    VersioningConfiguration=s3.VersioningConfiguration(
        Status='Enabled',
    ),
    DependsOn=['LambdaProcessing', ],
    NotificationConfiguration=s3.NotificationConfiguration(
        LambdaConfigurations=[
            s3.LambdaConfigurations(
                Event='s3:ObjectCreated:*',
                Function=GetAtt(lambda_processing, 'Arn')
            )
        ]
    )
)
