from pulumi_aws.dynamodb import Table


def create_dynamodb(name, attributes, hash_key, range_key, billing_mode, read_capacity, write_capacity):
    """
    Create DynamoDB database.

    Parameters
    ----------
    name
    attributes
    hash_key
    range_key
    billing_mode
    read_capacity
    write_capacity

    Returns
    -------

    """
    return Table(name,
                 attributes=attributes,
                 hash_key=hash_key,
                 range_key=range_key,
                 billing_mode=billing_mode,
                 read_capacity=read_capacity,
                 write_capacity=write_capacity
                 )
