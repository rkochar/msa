import helpers.model as model
import boto3
from os import getenv
from faaskeeper.node import Node
from faaskeeper.version import EpochCounter, SystemCounter, Version


def init(event, context):
    s3_data_bucket, service, region = getenv("S3_DATA_BUCKET"), getenv("DEPLOYMENT_NAME"), getenv("DEPLOYMENT_REGION")
    assert s3_data_bucket is not None and service is not None and region is not None

    dynamodb = boto3.client("dynamodb", region_name=region)
    # clean state table
    dynamodb.put_item(
        TableName=f"{service}-state",
        Item={"path": {"S": "fxid"}, "cFxidSys": {"L": [{"N": "0"}]}},
    )

    # initialize root
    dynamodb.put_item(
        TableName=f"{service}-state",
        Item={
            "path": {"S": "/"},
            "cFxidSys": {"L": [{"N": "0"}]},
            "mFxidSys": {"L": [{"N": "0"}]},
            "children": {"L": []},
        },
    )
    dynamodb.put_item(
        TableName=f"{service}-data",
        Item={
            "path": {"S": "/"},
            "cFxidSys": {"L": [{"N": "0"}]},
            "mFxidSys": {"L": [{"N": "0"}]},
            "mFxidEpoch": {"SS": [""]},
            "children": {"L": []},
        },
    )

    # Initialize root node for S3
    s3 = model.UserS3Storage(bucket_name=s3_data_bucket)
    node = Node("/")
    node.created = Version(SystemCounter.from_raw_data([0]), None)
    node.modified = Version(
        SystemCounter.from_raw_data([0]), EpochCounter.from_raw_data(set())
    )
    node.children = []
    node.data = b""
    s3.write(node)
