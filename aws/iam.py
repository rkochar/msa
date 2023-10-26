from json import loads

from pulumi_aws import iam


def read_file(file):
    return loads(open(file).read())


def create_iam_role(name, file, opts=None):
    apigw_lambda_policy = read_file(file)
    apigw_lambda_role = iam.Role(name,
                                 assume_role_policy=apigw_lambda_policy,
                                 opts=opts
                                 )
    return apigw_lambda_role


def create_iam_policy(name, file, opts=None):
    policy = iam.Policy(name, policy=read_file(file), opts=opts)
    return policy


def create_role_policy_attachment(name, policyname, policyfile, rolename, rolefile, opts=None):
    role = create_iam_role(rolename, rolefile, opts=opts)
    policy = create_iam_policy(policyname, policyfile, opts=opts)
    role_policy_attachment = iam.RolePolicyAttachment(name,
                                                      role=role.name,
                                                      policy_arn=policy.arn,
                                                      opts=opts
                                                      )
    return role
