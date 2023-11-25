from aws.vpc import create_vpc


def setup_aws():
    return create_vpc("for-database")
