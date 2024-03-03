import json
from helpers.helpers import compute_batch_size, batch_creator
import time


def lambda_handler(headers, query_parameters):
    job_id, L_PREFIX = "bl-release", "BL"
    mapper_lambda_name, reducer_lambda_name, rc_lambda_name = L_PREFIX + "-mapper-" + job_id, L_PREFIX + "-reducer-" + job_id, L_PREFIX + "-rc-" + job_id
    config = json.loads(open('helpers/driverconfig.json', 'r').read())
    bucket, job_bucket, result_bucket, lambda_memory, concurrent_lambdas = config["bucket"], config["jobBucket"], config["resultBucket"], config["lambdaMemory"], config["concurrentLambdas"]

    all_keys = []
    for obj in filter_objects_s3(bucket, prefix=config["prefix"]):
        print(f"obj: {obj}")
        all_keys.append(obj)

    print(f"Total keys to process: {len(all_keys)}")
    print(f"s3 objects: {get_all_objects_s3(bucket)}")

    bsize = compute_batch_size(all_keys, lambda_memory, concurrent_lambdas)
    batches = batch_creator(all_keys, bsize)
    n_mappers, mappers_executed = len(batches), 0
    print(f"batches: {batches}, n_mappers: {n_mappers}")

    write_job_config(job_id, job_bucket, result_bucket, n_mappers, reducer_lambda_name, config["reducer"]["handler"])

    j_key = job_id + "/jobdata"
    data = json.dumps({
        "totalS3Files": len(all_keys),
        "startTime": time.time()
    })
    write_to_s3(job_bucket, j_key, data)

    Ids = [i + 1 for i in range(n_mappers)]
    while mappers_executed < n_mappers:
        nm = min(concurrent_lambdas, n_mappers)
        output = publish_message(str({"body": {"batches": batches, "mapperId": Ids[mappers_executed: mappers_executed + nm][0], "jobBucket": job_bucket, "bucket": bucket, "resultBucket": result_bucket, "jobId": job_id}}), publish=True)
        mappers_executed += nm

    return str(output)


def write_job_config(job_id, job_bucket, result_bucket, n_mappers, r_func, r_handler):
    fname = "./helpers/jobinfo.json"
    with open(fname, 'r') as f:
        data = json.dumps({
            "jobId": job_id,
            "jobBucket": job_bucket,
            "resultBucket": result_bucket,
            "mapCount": n_mappers,
            "reducerFunction": r_func,
            "reducerHandler": r_handler
        }, indent=4)
        f.close()
        write_to_s3(job_bucket, "jobinfo.json", data)
