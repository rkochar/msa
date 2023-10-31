from utils.distribute import Distribute


def apigw_foobar():
    d = Distribute()
    apigw_lambda_iam_role = d.create_iam_role("apigw-lambda-iam-role", d.iam_role_json("lambda-role"))

    lambda_apigw_foo = d.create_lambda('lambda-apigw-foo', "apigw-lambda.foo", role=apigw_lambda_iam_role)
    lambda_apigw_bar = d.create_lambda('lambda-apigw-bar', "apigw-lambda.bar", role=apigw_lambda_iam_role)

    routes = [
        ("/foo", "GET", lambda_apigw_foo, "lambda-apigw-foo", "lambda for foo"),
        ("/bar", "GET", lambda_apigw_bar, "lambda-apigw-bar", "lambda for bar")
    ]
    d.create_apigw('apigw', routes)
