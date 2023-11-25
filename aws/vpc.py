from pulumi_aws.ec2 import Vpc, Subnet
from pulumi_aws.rds import SubnetGroup

from pulumi import Config

config = Config("aws")
region = config.require("region")


def create_vpc(name):
    vpc = Vpc(f"vpc-{name}", cidr_block="10.0.0.0/16")
    # subnets = []
    # for zone in ["a", "b", "c"]:
    #     subnets.append(Subnet(f"subnet-{name}-{zone}",
    #                           vpc_id=vpc.id,
    #                           availability_zone=f"eu-west-1{zone}",
    #                           cidr_block="10.0.1.0/24"
    #                           )
    #                    )
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
                               subnet_ids=[subnet.id, subnet_extra.id]  # [subnet.id for subnet in subnets],
                               )
    return vpc, subnet, subnet_group
