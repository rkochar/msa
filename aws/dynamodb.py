from pulumi_aws.dynamodb import Table, TableAttributeArgs, TableGlobalSecondaryIndexArgs, TableLocalSecondaryIndexArgs


def create_dynamodb(name, attributes, hash_key, range_key, billing_mode, stream_enabled, stream_view_type, read_capacity, write_capacity, environment, opts=None):
    """
    Create DynamoDB database.

    Parameters
    ----------
    name
    attributes
    hash_key
    range_key
    billing_mode
    stream_enabled
    stream_view_type
    read_capacity
    write_capacity
    environment

    Returns DynamoDB Table
    -------

    """
    environment["DYNAMODB_TABLE_NAME"] = name
    table = Table(name,
                 name=name,
                 attributes= [ TableAttributeArgs(name=x[0], type=x[1]) for x in attributes ],
                 hash_key=hash_key,
                 range_key=range_key,
                 billing_mode=billing_mode,
                 stream_enabled=stream_enabled,
                 stream_view_type=stream_view_type,
                 read_capacity=read_capacity,
                 write_capacity=write_capacity
                 )
    return table, environment
