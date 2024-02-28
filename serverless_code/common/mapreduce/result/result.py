def lambda_handler(headers, query_parameter):
    result_bucket, job_id = getenv('resultBucket'), getenv('jobId')
    return str(get_from_s3(bucket=result_bucket, key="%s/result" % job_id))
