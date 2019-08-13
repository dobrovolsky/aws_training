from troposphere import Template

from cloud_formation import aws_lambda
from cloud_formation import bucket
from cloud_formation import db
from cloud_formation import sns

t = Template()

t.add_resource(aws_lambda.lambda_processing)
t.add_resource(aws_lambda.s3_lambda_permission)
t.add_resource(aws_lambda.lambda_execution_role)
t.add_parameter(aws_lambda.source_code_bucket)
t.add_parameter(aws_lambda.zip_file_path)
t.add_parameter(aws_lambda.lambda_name)

t.add_resource(bucket.bucket)

t.add_resource(db.db)
t.add_parameter(db.db_user)
t.add_parameter(db.db_password)
t.add_parameter(db.db_name)
t.add_resource(db.dynamo_db)

t.add_resource(sns.sns_topic)
t.add_resource(sns.subscription)

with open('templates/lambda-func.json', 'w+') as f:
    print(t.to_json(), file=f)
