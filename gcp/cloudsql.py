from pulumi_gcp.sql import Database, DatabaseInstance, DatabaseInstanceSettingsArgs, User
from pulumi import Config, export, Output

config = Config("gcp")
region = config.get("region")
project = config.get("project")


def create_sql_database(name, engine, engine_version, username="username", password="password",
                        instance_class="db-f1-micro", environment={}, opts=None):
    database_version = engine.upper() + "_" + engine_version.replace(".", "_")
    cloud_sql_instance = DatabaseInstance(
        name,
        name=name,
        database_version=database_version,
        deletion_protection=False,
        settings=DatabaseInstanceSettingsArgs(tier=instance_class)
    )

    database = Database(
        name,
        name=name,
        instance=cloud_sql_instance.name
    )

    users = User(
        username,
        name=username,
        instance=cloud_sql_instance.name,
        password=password
    )

    export(f"sqldb-{name}-public-ip", cloud_sql_instance.public_ip_address)
    export(f"sqldb-{name}-private-ip", cloud_sql_instance.private_ip_address)
    if engine_version == "postgres":
        export(f"sqldb-{name}", Output.concat("postgres://", username, ":", password, "@/", name, "?host=/cloudsql/",
                                              cloud_sql_instance.connection_name))
    elif engine_version == "mysql":
        export(f"sqldb-{name}", Output.concat("mysql://", username, ":", password, "@/", name, "?host=/cloudsql/",
                                              cloud_sql_instance.connection_name))

    environment["DATABASE_NAME"] = name
    environment["INSTANCE_CONNECTION_NAME"] = cloud_sql_instance.connection_name
    return cloud_sql_instance, environment
