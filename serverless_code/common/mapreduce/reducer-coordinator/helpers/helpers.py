from os import getenv
import json
from urllib3 import request


def compute_batch_size(keys, lambda_memory, concurrent_lambdas):
    max_mem_for_data = 0.6 * lambda_memory * 1000 * 1000;
    size = 0.0
    for key in keys:
        if isinstance(key, dict):
            size += key['Size']
        else:
            size += key.size
    print(f"Size: {size}, nKeys: {len(keys)}")
    avg_object_size = size / max(1, len(keys))
    print("Dataset size: %s, nKeys: %s, avg: %s" % (size, len(keys), avg_object_size))
    if avg_object_size < max_mem_for_data and len(keys) < concurrent_lambdas:
        b_size = 1
    else:
        b_size = int(round(max_mem_for_data / max(1, avg_object_size)))
    return b_size


def batch_creator(all_keys, batch_size):
    # TODO: Create optimal batch sizes based on key size & number of keys

    batches = []
    batch = []
    for i in range(len(all_keys)):
        batch.append(all_keys[i]);
        if (len(batch) >= batch_size):
            batches.append(batch)
            batch = []

    if len(batch):
        batches.append(batch)
    return batches


def get_mapper_files(files):
    ret = []
    for mf in files:
        if isinstance(mf, dict):
            if "task/mapper" in mf.get("Name"):
                ret.append(mf)
        elif "task/mapper" in mf.key:
            ret.append(mf)

    return ret


def get_reducer_batch_size(keys):
    # TODO: Paramertize memory size
    batch_size = compute_batch_size(keys, 1536, 1000)
    return max(batch_size, 2)  # At least 2 in a batch - Condition for termination


def check_job_done(files):
    # TODO: USE re
    for f in files:
        if "result" in f["Key"]:
            return True
    return False
