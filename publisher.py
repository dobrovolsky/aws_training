import argparse
import os
import shutil
import tempfile
import zipfile

from subprocess import call

import boto3

ENVS = ('dev', 'qa')
ACTIONS = ('generate', 'upload', 'deploy')


parser = argparse.ArgumentParser(description='Publishing.')

parser.add_argument(
    'env',
    type=str,
    nargs=1,
    choices=ENVS,
    help='Env that should be processed.',
)
parser.add_argument(
    'action',
    type=str,
    nargs=1,
    choices=ACTIONS,
    help='Witch action should be performed.'
)

args = parser.parse_args()

env = args.env[0]
action = args.action[0]

filename = f'{env}_lambda'
zip_filename = filename + '.zip'

FunctionName = 'LambdaProcessingDEV'
bucket = 'cf-templates-f5lkgopzuq9c-eu-central-1'


def generate_zip():
    print('Creating zip file...')
    with tempfile.TemporaryDirectory() as tmpdirname:
        src = './src'

        src_files = os.listdir(src)
        for file_name in src_files:
            full_file_name = os.path.join(src, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, tmpdirname)

        call(["pip", "install", "-r", "requirements.txt", "-t", tmpdirname])

        shutil.make_archive(filename, 'zip', tmpdirname)
        zip_file = zipfile.ZipFile(zip_filename, 'a')
        for f in os.listdir(tmpdirname):
            zip_file.write(os.path.join(tmpdirname, f))
        zip_file.close()


def upload_file():
    print('Uploading file...')
    s3_client = boto3.client('s3')
    s3_client.upload_file(zip_filename, bucket, zip_filename)


def deploy():
    print('Updating lambda function...')
    lambda_client = boto3.client('lambda')
    lambda_client.update_function_code(
        FunctionName=FunctionName,
        S3Bucket=bucket,
        S3Key=zip_filename,
        Publish=True,
    )


generate_zip()
if action == 'upload':
    upload_file()

elif action == 'deploy':
    upload_file()
    deploy()


