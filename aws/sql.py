from pulumi_aws.rds import Instance, Proxy, ProxyArgs, ProxyAuthArgs
from pulumi import export
from aws.secretsmanager import create_secret
from json import dumps


def create_sql_database(name, engine, engine_version, storage, username, password, instance_class="db.t3.micro",
                        environment={}, aws_config=None, opts=None):
    """
    Create SQL database.

    :param name: of database
    :param engine: mysql or postgres
    :param engine_version:
    :param storage: in GB
    :param username: of database
    :param password: of database
    :param instance_class: EC2 instance type
    :param aws_config:
    :param opts: of Pulumi
    :return: database object
    """
    vpc, subnet, subnet_group = aws_config
    rds = Instance(name,
                   engine=engine,
                   engine_version=engine_version,
                   allocated_storage=storage,
                   instance_class=instance_class,
                   username=username,
                   password=password,
                   db_name=name,
                   skip_final_snapshot=True,
                   publicly_accessible=False,
                   db_subnet_group_name=subnet_group.name,
                   opts=opts
                   )
    export(f"rds-{name}-endpoint", rds.endpoint)
    export(f"rds-{name}-address", rds.address)

    # secret_string = create_rds_secret(rds, username, password, engine)
    # secret = create_secret(f"sqldb-{name}", secret_string=secret_string, opts=opts)
    # create_proxy(name, username, engine, secret, opts=opts)
    return rds, environment


def create_rds_secret(rds, username, password, engine):
    secret = {
        "username": username,
        "password": password,
        "engine": engine,
        # "host": rds.endpoint,
        # "port": rds.port
    }
    # secret["dbname"] = rds.db_name

    return dumps(secret)


def create_proxy(name, username, engine, secret, opts=None):
    proxy = Proxy(f"{name}-proxy",
                  engine_family=engine.upper(),
                  auths=[ProxyAuthArgs(
                      auth_scheme="SECRETS",
                      iam_auth="DISABLED",
                      secret_arn=secret.arn,
                      username=username
                  )],
                  opts=opts
                  )
    export(f"rds-{name}-proxy-endpoint", proxy.endpoint)
    return proxy
