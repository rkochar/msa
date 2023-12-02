from pulumi_aws.ec2 import Vpc, SecurityGroup, SecurityGroupIngressArgs, SecurityGroupEgressArgs, SecurityGroupRule, \
    Subnet, VpcEndpoint
from pulumi_aws.rds import SubnetGroup

from pulumi import Config

config = Config("aws")
region = config.require("region")


def create_vpc(name):
    vpc = Vpc(f"vpc-{name}",
              cidr_block="10.0.0.0/16",
              enable_dns_support=True,
              enable_dns_hostnames=True
              )
    # security_group = SecurityGroup(f"security-group-{name}",
    #                                description="Connect with SQS",
    #                                vpc_id=vpc.id,
    #                                ingress=[SecurityGroupIngressArgs(
    #                                    description="TLS from VPC",
    #                                    from_port=0,
    #                                    to_port=65535,
    #                                    protocol="tcp",
    #                                    cidr_blocks=[vpc.cidr_block]
    #                                )],
    #                                egress=[SecurityGroupEgressArgs(
    #                                    from_port=443,
    #                                    to_port=443,
    #                                    protocol="tcp",
    #                                    cidr_blocks=[vpc.cidr_block]
    #                                )]
    #                                )

    security_group_ingress_rule = SecurityGroupRule(f"ingress-{name}",
                                                    type="ingress",
                                                    from_port=0,
                                                    to_port=65535,
                                                    protocol="tcp",
                                                    cidr_blocks=[vpc.cidr_block],
                                                    security_group_id=vpc.default_security_group_id
                                                    )
    security_group_egress_rule = SecurityGroupRule(f"egress-{name}",
                                                   type="egress",
                                                   from_port=0,
                                                   to_port=65535,
                                                   protocol="tcp",
                                                   cidr_blocks=[vpc.cidr_block],
                                                   security_group_id=vpc.default_security_group_id
                                                   )

    subnet = Subnet(f"subnet-{name}",
                    vpc_id=vpc.id,
                    availability_zone=f"{region}a",
                    cidr_block="10.0.1.0/24"
                    )
    subnet_extra = Subnet(f"subnet-extra-{name}",
                          vpc_id=vpc.id,
                          availability_zone=f"{region}b",
                          cidr_block="10.0.2.0/24"
                          )
    subnet_group = SubnetGroup(f"subnet-group-{name}",
                               subnet_ids=[subnet.id, subnet_extra.id]
                               )

    vpc_endpoint = VpcEndpoint(f"vpc-endpoint-{name}",
                               vpc_id=vpc.id,
                               service_name=f"com.amazonaws.{region}.sqs",
                               vpc_endpoint_type="Interface",
                               security_group_ids=[vpc.default_security_group_id],
                               private_dns_enabled=True)
    return vpc, subnet, subnet_group, vpc_endpoint
