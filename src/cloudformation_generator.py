from troposphere import Template

from cf import aws_lambda
from cf import bucket
from cf import db
from cf import sns

t = Template()


t.add_resource(aws_lambda.lambda_processing)
t.add_resource(aws_lambda.s3_lambda_permission)
t.add_resource(aws_lambda.lambda_execution_role)

t.add_resource(bucket.bucket)

t.add_resource(db.db)
t.add_resource(db.dynamo_db)

t.add_resource(sns.sns_topic)
t.add_resource(sns.subscription)

with open('cf.yaml', 'w+') as f:
    print(t.to_yaml(), file=f)
