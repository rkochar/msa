from pulumi_aws import rds


def create_sql_database(name, engine, engine_version, storage, instance_class, username, password, opts=None):
    return rds.Instance(name,
                        engine=engine,
                        engine_version=engine_version,
                        allocated_storage=storage,
                        instance_class=instance_class,
                        username=username,
                        password=password,
                        opts=opts
                        )
