from pulumi_aws.secretsmanager import Secret, SecretVersion


def create_secret(name, secret_string, opts=None):
    """
    Create secret in AWS Secrets Manager.

    :param name: of secret
    :param secret_string: secret value
    :param opts: of Pulumi
    :return: secret object
    """
    secret = Secret(name,
                    opts=opts
                    )
    SecretVersion(name,
                  secret_id=secret.id,
                  secret_string=secret_string,
                  opts=opts
                  )
    return secret
