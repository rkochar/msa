from pulumi import ResourceOptions

from utils.monad import Monad


def apigw_foobar():
    d = Monad()

    apigw_lambda_iam_role = d.create_iam_role("a-lambda-iam-role", "lambda-role")

    lambda_apigw_foo = d.create_lambda('lambda-apigw-foo', "apigw-lambda.foo", role=apigw_lambda_iam_role)
    lambda_apigw_bar = d.create_lambda('lambda-apigw-bar', "apigw-lambda.bar", role=apigw_lambda_iam_role)

    routes = [
        ("/foo", "GET", lambda_apigw_foo, "lambda-apigw-foo", "lambda for foo"),
        ("/bar", "GET", lambda_apigw_bar, "lambda-apigw-bar", "lambda for bar")
    ]
    d.create_apigw('foobar', routes, opts=ResourceOptions(depends_on=[lambda_apigw_foo, lambda_apigw_bar],
                                                          replace_on_changes=["*"], delete_before_replace=True))
