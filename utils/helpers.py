from pulumi import ResourceOptions


def merge_opts(opts1: ResourceOptions, opts2: ResourceOptions):
    if opts1 is None and opts2 is None:
        return None
    elif opts1 is None:
        return opts2
    elif opts2 is None:
        return opts1
    return ResourceOptions.merge(opts1, opts2)