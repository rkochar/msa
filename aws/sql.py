from pulumi_aws.rds import Instance, Proxy, ProxyArgs, ProxyAuthArgs
from pulumi import export


def create_sql_database(name, engine, engine_version, storage, username, password, instance_class="db.t3.micro",
                        opts=None):
    sqldb = Instance(name,
                     name=name,
                     engine=engine,
                     engine_version=engine_version,
                     allocated_storage=storage,
                     instance_class=instance_class,
                     username=username,
                     password=password,
                     skip_final_snapshot=True,
                     publicly_accessible=False,
                     opts=opts
                     )
    export(f"sqldb-{name}-endpoint", sqldb.endpoint)
    export(f"sqldb-{name}-address", sqldb.address)
    return sqldb


def create_rds_proxy(name, engine, username, password):
    rds_proxy = Proxy(f"sqldb-{name}-proxy",
                      debug_logging=False,
                      engine_family=engine.upper(),
                      idle_client_timeout=300,
                      require_tls=False,
                      auths=[ProxyAuthArgs(
                          username=username,
                          client_password_auth_type="MYSQL_NATIVE_PASSWORD"  # TODO: Clean up
                      )]
                      )
    export(f"sqldb-{name}-proxy-endpoint", rds_proxy.foo)
    return rds_proxy
