from os import getenv
import json
from urllib3 import request
from time import time


def calculate_costs(total_s3_size, job_keys, total_s3_get_ops, reducer_lambda_time, total_lambda_secs, lambda_memory,
                    total_lines):
    # S3 Storage cost - Account for mappers only; This cost is neglibile anyways since S3 costs 3 cents/GB/month
    s3_storage_hour_cost = 1 * 0.0000521574022522109 * (total_s3_size / 1024.0 / 1024.0 / 1024.0)  # cost per GB/hr
    s3_put_cost = len(job_keys) * 0.005 / 1000

    # S3 GET # $0.004/10000 
    total_s3_get_ops += len(job_keys)
    s3_get_cost = total_s3_get_ops * 0.004 / 10000

    # Total Lambda costs
    total_lambda_secs += reducer_lambda_time
    lambda_cost = total_lambda_secs * 0.00001667 * lambda_memory / 1024.0
    s3_cost = (s3_get_cost + s3_put_cost + s3_storage_hour_cost)

    # Print costs
    print("Reducer L", reducer_lambda_time * 0.00001667 * lambda_memory / 1024.0)
    print("Lambda Cost", lambda_cost)
    print("S3 Storage Cost", s3_storage_hour_cost)
    print("S3 Request Cost", s3_get_cost + s3_put_cost)
    print("S3 Cost", s3_cost)
    print("Total Cost: ", lambda_cost + s3_cost)
    print("Total Lines:", total_lines)

    return {"Reducer L": reducer_lambda_time * 0.00001667 * lambda_memory / 1024.0,
            "Lambda Cost": lambda_cost,
            "S3 Storage Cost": s3_storage_hour_cost,
            "S3 Request Cost": s3_get_cost + s3_put_cost,
            "S3 Cost": s3_cost,
            "Total Cost": lambda_cost + s3_cost,
            "Total Lines": total_lines
            }


def write_job_config(job_id, job_bucket, n_mappers, r_func, r_handler):
    fname = "jobinfo.json";
    with open(fname, 'w') as f:
        data = json.dumps({
            "jobId": job_id,
            "jobBucket": job_bucket,
            "mapCount": n_mappers,
            "reducerFunction": r_func,
            "reducerHandler": r_handler
        }, indent=4)
        f.write(data)


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
    '''
    '''
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


def invoke_lambda(batch, m_id, batches, bucket, job_bucket, job_id, mapper_outputs=[]):
    APIGW_URL = getenv("APIGW_URL")
    batch = [k.key for k in batches[m_id - 1]]
    response = request("POST",
                       APIGW_URL,
                       headers={
                           "bucket": bucket,
                           "keys": batch,
                           "jobBucket": job_bucket,
                           "jobId": job_id,
                           "mapperId": m_id
                       })

    print(f"Response: {response}")
    out = eval(response['Payload'].read())
    mapper_outputs.append(out)
    print("mapper output", out)

    return mapper_outputs


def get_mapper_files(files):
    ret = []
    for mf in files:
        if "task/mapper" in mf["Key"]:
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
