import resource

TASK_MAPPER_PREFIX = "task/mapper/"


def flatten(xss):
    return [x for xs in xss for x in xs]


def lambda_handler(headers):
    print(f"start message: {headers}")
    start_time = time()

    job_bucket, src_bucket = headers.get('jobBucket'), headers.get('bucket')
    job_id, mapper_id = headers.get('jobId'), headers.get('mapperId')
    src_keys = [x["key"] for x in flatten(headers.get('batches'))]
    output, line_count, err = {}, 0, ''

    # Download and process all keys
    for key in src_keys:
        response = get_from_s3(bucket=src_bucket, key=key)
        contents = response['Body'].read().decode("utf-8")

        for _ in contents.split('\n')[:-1]:
            line_count += 1

    time_in_secs = (time() - start_time)
    pret = [len(src_keys), line_count, time_in_secs, err]
    mapper_fname = "%s/%s%s" % (job_id, TASK_MAPPER_PREFIX, mapper_id)
    print(f"line_count: {line_count}, processing_time (seconds): {time_in_secs}, memoryUsage: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}")
    write_to_s3(job_bucket, mapper_fname, bytes(str(line_count), "ascii"))
    return pret
