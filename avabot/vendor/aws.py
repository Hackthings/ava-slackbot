# -*- coding: utf-8 -*-
import boto3
from slackbot.bot import settings

__all__ = ['s3', 's3_client']

config = settings.config


s3 = boto3.resource(
    's3',
    aws_access_key_id=config.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=config.get('AWS_SECRET_ACCESS_KEY')
)
s3_client = boto3.client(
    's3',
    aws_access_key_id=config.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=config.get('AWS_SECRET_ACCESS_KEY')
)
