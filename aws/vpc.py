from pulumi_aws.ec2 import Vpc, SecurityGroup, SecurityGroupIngressArgs, SecurityGroupEgressArgs, SecurityGroupRule, \
    Subnet, VpcEndpoint
from pulumi_aws.rds import SubnetGroup

from pulumi import Config

config = Config("aws")
region = config.require("region")


def create_vpc_and_subnet(name):
    vpc = Vpc(f"vpc-{name}",
              cidr_block="10.0.0.0/16",
              enable_dns_support=True,
              enable_dns_hostnames=True
              )

    subnet_a = Subnet(f"subnet-a-{name}",
                      vpc_id=vpc.id,
                      availability_zone=f"{region}a",
                      cidr_block="10.0.1.0/24"
                      )

    subnet_b = Subnet(f"subnet-b-{name}",
                      vpc_id=vpc.id,
                      availability_zone=f"{region}b",
                      cidr_block="10.0.2.0/24"
                      )

    subnet_group = SubnetGroup(f"subnet-group-{name}",
                               subnet_ids=[subnet_a.id, subnet_b.id]
                               )

    return vpc, subnet_a, subnet_b, subnet_group


def create_vpc_endpoint(name, service, aws_config):
    vpc, subnet_a, subnet_b = aws_config.get("vpc"), aws_config.get("subnet_a"), aws_config.get("subnet_b")
    vpc_endpoint = VpcEndpoint(f"vpc-endpoint-{name}",
                               vpc_id=vpc.id,
                               security_group_ids=[vpc.default_security_group_id],
                               subnet_ids=[subnet_a.id, subnet_b.id],
                               private_dns_enabled=True,
                               service_name=f"com.amazonaws.{region}.{service}",
                               vpc_endpoint_type="Interface"
                               )
