from pulumi import AssetArchive, FileArchive
from pulumi_aws_apigateway import RouteArgs

from aws.lambdafunction import create_lambda
from aws.apigw import create_apigw
from aws.iam import create_iam_role

apigw_lambda_iam_role = create_iam_role("apigw-lambda-iam-role", file="policy/aws/lambda-apigw.json")

apigw_lambda_foo = create_lambda('lambda-apigw-foo', "apigw-lambda", "foo", role=apigw_lambda_iam_role)
apigw_lambda_bar = create_lambda('lambda-apigw-bar', "apigw-lambda", "bar", role=apigw_lambda_iam_role)

routes = [
    ("/", "GET", apigw_lambda_foo),
    ("/bar", "GET", apigw_lambda_bar)
]
create_apigw('apigw', routes)

