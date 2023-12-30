from pulumi import ResourceOptions

from utils.monad import Monad


def zookeeper():
    m = Monad()

    iam_role_writer = m.create_iam("a-lambda-iam-role", "lambda-basic-role",
                                   "iam-attachment-dynamodb", "lambda-iam-policy-dynamodb", "lambda-writer-policy")
    lambda_writer = m.create_lambda("zookeeper/writer", 'writer', "writer.handler", template="http",
                                    role=iam_role_writer)

    # routes = [
    #     ("/foo", "GET", lambda_foo, "foobar-foo", "lambda for foo"),
    #     ("/bar", "GET", lambda_bar, "foobar-bar", "lambda for bar")
    # ]
    # m.create_apigw('foobar', routes, opts=ResourceOptions(depends_on=[lambda_foo, lambda_bar],
    #                                                       replace_on_changes=["*"], delete_before_replace=True))
