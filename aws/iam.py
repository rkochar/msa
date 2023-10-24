from json import loads

from pulumi import AssetArchive, FileArchive
from pulumi_aws import iam

def create_iam_role(name, file):
    apigw_lambda_policy = loads(open('policy/aws/lambda-apigw.json').read())
    apigw_lambda_role = iam.Role('lambda-apigw-role',
                                 assume_role_policy=apigw_lambda_policy
                                 )
    return apigw_lambda_role

