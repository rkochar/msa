from pulumi_gcp.sql import Database, DatabaseInstance, DatabaseInstanceSettingsArgs, User
from pulumi import Config, export, Output, ResourceOptions

config = Config("gcp")
region = config.get("region")
project = config.get("project")


def create_sql_database(name, engine, engine_version, username="username", password="password", instance_class="db-f1-micro", environment={}, opts=None):
    """
    Create SQL DatabaseInstance, Database and User.

    Parameters
    ----------
    name: of DatabaseInstance
    engine: of Database
    engine_version: of engine in Database
    username: user for database
    password: user for database
    instance_class: Virtual Machine on which the database is hosted
    environment: put connection information in here. Is passed to serverless function.
    opts: of Pulumi

    Returns DatabaseInstance and the environment (to pass into serverless function)
    -------

    """
    database_version = engine.upper() + "_" + engine_version.replace(".", "_")
    cloud_sql_instance = DatabaseInstance(
        name,
        name=name,
        database_version=database_version,
        deletion_protection=False,
        settings=DatabaseInstanceSettingsArgs(tier=instance_class),
        opts=opts
    )

    database = Database(
        name,
        name=name,
        instance=cloud_sql_instance.name,
        opts=ResourceOptions(depends_on=[cloud_sql_instance])
    )

    users = User(
        username,
        name=username,
        instance=cloud_sql_instance.name,
        password=password,
        opts=ResourceOptions(depends_on=[database])
    )

    export(f"sqldb-{name}-public-ip", cloud_sql_instance.public_ip_address)
    export(f"sqldb-{name}-private-ip", cloud_sql_instance.private_ip_address)

    # Set endpoint according to engine
    if engine_version == "postgres":
        export(f"sqldb-{name}", Output.concat("postgres://", username, ":", password, "@/", name, "?host=/cloudsql/",
                                              cloud_sql_instance.connection_name))
    elif engine_version == "mysql":
        export(f"sqldb-{name}", Output.concat("mysql://", username, ":", password, "@/", name, "?host=/cloudsql/",
                                              cloud_sql_instance.connection_name))

    # Put connection information into environment variable
    environment["DATABASE_NAME"] = name
    environment["INSTANCE_CONNECTION_NAME"] = cloud_sql_instance.connection_name
    return cloud_sql_instance, environment
