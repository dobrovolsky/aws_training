#!/bin/bash

set -e

BUILD_DIR=/tmp/lambda_build
SRC_DIR=./src

ZIP_FILE=lambda.zip

echo "Copy source..."
mkdir -p $BUILD_DIR
cp -a $SRC_DIR/* $BUILD_DIR/
pip install -r requirements.txt -t $BUILD_DIR

echo "Create the zip..."
cd $BUILD_DIR
zip -9 -r ../$ZIP_FILE ./
cd ..

echo "Clean update function..."
aws s3 cp lambda.zip s3://cf-templates-f5lkgopzuq9c-eu-central-1/

aws lambda update-function-code \
--s3-bucket cf-templates-f5lkgopzuq9c-eu-central-1 \
--s3-key lambda.zip \
--publish \
--function-name LambdaProcessing

echo "Clean up.."
rm -r $BUILD_DIR


