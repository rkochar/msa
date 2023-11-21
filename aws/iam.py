from json import loads

from pulumi_aws import iam


def read_file(file):
    """
    Read a file.

    :param file: path to file
    :return: Deserialized python object of file
    """
    return loads(open(file).read())


def create_iam_role(name, file, opts=None):
    """
    Creates IAM role from a json file.

    :param name: of role
    :param file: path to file that stores the role in json
    :param opts: of Pulumi
    :return: IAM role object
    """
    apigw_lambda_policy = read_file(file)
    apigw_lambda_role = iam.Role(name,
                                 assume_role_policy=apigw_lambda_policy,
                                 opts=opts
                                 )
    return apigw_lambda_role


def create_iam_policy(name, file, opts=None):
    """
    Create IAM policy from json file.

    :param name: of policy
    :param file: path to file that stores the policy in json
    :param opts: of Pulumi
    :return: IAM policy object
    """
    policy = iam.Policy(name, policy=read_file(file), opts=opts)
    return policy


def create_role_policy_attachment(name, policyname, policyfile, rolename, rolefile, opts=None):
    """
    Create IAM Role Policy Attachment.

    :param name: of Role Policy Attachment
    :param policyname: name of policy
    :param policyfile: path to file that stores the policy in json
    :param rolename: name of role
    :param rolefile: path to file that stores the role in json
    :param opts: of Pulumi
    :return: Role Policy Attachment file
    """
    role = create_iam_role(rolename, rolefile, opts=opts)
    policy = create_iam_policy(policyname, policyfile, opts=opts)
    role_policy_attachment = iam.RolePolicyAttachment(name,
                                                      role=role.name,
                                                      policy_arn=policy.arn,
                                                      opts=opts
                                                      )
    return role
