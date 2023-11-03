from pulumi_aws import rds
from pulumi import export

def create_sql_database(name, engine, engine_version, storage, username, password, instance_class="db.t3.micro", opts=None):
    sqldb = rds.Instance(name,
                         name=name,
                         engine=engine,
                         engine_version=engine_version,
                         allocated_storage=storage,
                         instance_class=instance_class,
                         username=username,
                         password=password,
                         skip_final_snapshot=True,
                         opts=opts
                         )
    export(f"sqldb-{name}-endpoint", sqldb.endpoint)
    return sqldb
