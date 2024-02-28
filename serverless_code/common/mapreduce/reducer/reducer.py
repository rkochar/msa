import resource

TASK_MAPPER_PREFIX, TASK_REDUCER_PREFIX = "task/mapper/", "task/reducer/"


def lambda_handler(message):
    headers = literal_eval(message)
    print(f"received message: {headers}")
    start_time = time()

    job_bucket, bucket, result_bucket, job_id, reducer_keys, n_reducers = headers.get('jobBucket'), headers.get('bucket'), headers["resultBucket"], headers.get('jobId'), headers.get('keys'), headers.get('nReducers')
    results, line_count = {}, 0

    for key in reducer_keys:
        contents = get_from_s3(bucket=job_bucket, key=key)
        print(f"contents: {contents}")

        line_count += int(contents)

    time_in_secs = (time() - start_time)
    pret = [len(reducer_keys), line_count, time_in_secs]
    print(f"linecount: {line_count}, processing_time: {time_in_secs}, memory_usage: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}")
    write_to_s3(result_bucket, "%s/result" % job_id, bytes(str(line_count), "ascii"))
    return pret
