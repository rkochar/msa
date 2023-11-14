from pulumi import ResourceOptions

from utils.monad import Monad


def apigw_foobar():
    d = Monad()

    apigw_lambda_iam_role = d.create_iam_role("a-lambda-iam-role", "lambda-role")

    lambda_foo = d.create_lambda('foobar-foo', "foobar.foo", role=apigw_lambda_iam_role)
    lambda_bar = d.create_lambda('foobar-bar', "foobar.bar", role=apigw_lambda_iam_role)

    routes = [
        ("/foo", "GET", lambda_foo, "foobar-foo", "lambda for foo"),
        ("/bar", "GET", lambda_bar, "foobar-bar", "lambda for bar")
    ]
    d.create_apigw('foobar', routes, opts=ResourceOptions(depends_on=[lambda_foo, lambda_bar],
                                                         replace_on_changes=["*"], delete_before_replace=True))
