import json
from helpers.helpers import compute_batch_size, calculate_costs, batch_creator
from time import time, sleep


def lambda_handler(headers, query_parameters):
    job_id, L_PREFIX = "bl-release", "BL"
    mapper_lambda_name, reducer_lambda_name, rc_lambda_name = L_PREFIX + "-mapper-" + job_id, L_PREFIX + "-reducer-" + job_id, L_PREFIX + "-rc-" + job_id

    # 1. Get all keys to be processed  
    # init 
    config = json.loads(open('helpers/driverconfig.json', 'r').read())
    bucket = config["bucket"]
    job_bucket = config["jobBucket"]
    lambda_memory = config["lambdaMemory"]
    concurrent_lambdas = config["concurrentLambdas"]


    all_keys = []
    for obj in filter_objects_s3(bucket, prefix=config["prefix"]):
        all_keys.append(obj)

    print(f"Total keys to process: {len(all_keys)}")
    print(f"s3 objects: {get_all_objects_s3(bucket)}")

    bsize = compute_batch_size(all_keys, lambda_memory, concurrent_lambdas)
    batches = batch_creator(all_keys, bsize)
    n_mappers = len(batches)

    write_job_config(job_id, job_bucket, n_mappers, reducer_lambda_name, config["reducer"]["handler"])

    j_key = job_id + "/jobdata"
    data = json.dumps({
        "totalS3Files": len(all_keys),
        "startTime": time()
    })
    write_to_s3(job_bucket, j_key, data, {})  # TODO: Cloud agnostic

    Ids = [i + 1 for i in range(n_mappers)]
    mappers_executed = 0
    while mappers_executed < n_mappers:
        nm = min(concurrent_lambdas, n_mappers)
        output = publish_message(str({"body": {"batches": batches, "mapperId": Ids[mappers_executed: mappers_executed + nm][0], "jobBucket": job_bucket, "bucket": bucket, "jobId": job_id}}), publish=True)
        mappers_executed += nm

    return str(output)


def write_job_config(job_id, job_bucket, n_mappers, r_func, r_handler):
    fname = "./helpers/jobinfo.json"
    with open(fname, 'r') as f:
        data = json.dumps({
            "jobId": job_id,
            "jobBucket": job_bucket,
            "mapCount": n_mappers,
            "reducerFunction": r_func,
            "reducerHandler": r_handler
        }, indent=4)
        f.close()
        write_to_s3(job_bucket, "jobinfo.json", data)
