from pulumi import ResourceOptions

from utils.monad import Monad


def apigw_foobar():
    m = Monad()

    apigw_lambda_iam_role = m.create_iam("a-lambda-iam-role", "lambda-role")

    lambda_foo = m.create_lambda('foobar-foo', "foobar.foo", template="http", role=apigw_lambda_iam_role)
    lambda_bar = m.create_lambda('foobar-bar', "foobar.bar", template="http", role=apigw_lambda_iam_role)

    routes = [
        ("/foo", "GET", lambda_foo, "foobar-foo", "lambda for foo"),
        ("/bar", "GET", lambda_bar, "foobar-bar", "lambda for bar")
    ]
    m.create_apigw('foobar', routes, opts=ResourceOptions(depends_on=[lambda_foo, lambda_bar],
                                                         replace_on_changes=["*"], delete_before_replace=True))

