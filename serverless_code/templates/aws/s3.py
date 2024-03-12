import boto3
import re
from os import getenv
from ast import literal_eval
from time import time
from uuid import uuid4
import resource


def template(event, context):
    name = ""
    <start-time>
    <start-span>
    print("starting")
    parent_span = message.get('span') or {}

    if span is not None:
        span["span_depth"] = (parent_span.get('span_depth') or 0) + 1
        span["parent_span_id"] = parent_span.get('span_id')
        span["parent_name"] = parent_span.get('name')

    body = ""

    <end-time>

    if span is not None:
        <end-span>
        print(f"span: {span}")
