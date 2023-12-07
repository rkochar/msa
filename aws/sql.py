from pulumi import export
from pulumi_aws.rds import Instance

from aws.secretsmanager import create_secret


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
    :param environment:
    :param aws_config:
    :param opts: of Pulumi
    :return: database object
    """
    subnet_group = aws_config.get("subnet_group")
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

    environment["SQLDB_HOST"] = rds.address
    environment["SQLDB_PORT"] = rds.port
    environment["SQLDB_DBNAME"] = name

    return rds, environment
