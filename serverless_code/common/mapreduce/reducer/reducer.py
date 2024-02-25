"""
Python reducer function

Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
import resource

# constants
TASK_MAPPER_PREFIX, TASK_REDUCER_PREFIX = "task/mapper/", "task/reducer/"


def lambda_handler(message):
    headers = literal_eval(message)
    start_time = time()

    job_bucket, bucket, job_id = headers.get('jobBucket'), headers.get('bucket'), headers.get('jobId')
    reducer_keys, n_reducers = headers.get('keys'), headers.get('nReducers')
    r_id, step_id = headers.get('reducerId'), headers.get('stepId')

    print(f"job_bucket: {job_bucket}, bucket: {bucket}, job_id: {job_id}")
    print(f"reducer_keys: {reducer_keys}, n_reducers: {n_reducers}")
    print(f"r_id: {r_id}, step_id: {step_id}")
    results, line_count = {}, 0

    # Download and process all keys
    for key in reducer_keys:
        response = get_from_s3(bucket=job_bucket, key=key)
        contents = response['Body'].read()
        print(f"contents: {contents}")

        line_count += int(contents)

        # try:
        #     for srcIp, val in json.loads(contents).iteritems():
        #         line_count += 1
        #         if srcIp not in results:
        #             results[srcIp] = 0
        #         results[srcIp] += float(val)
        # except Exception as e:
        #     print(e)

    time_in_secs = (time() - start_time)
    # timeTaken = time_in_secs * 1000000000 # in 10^9
    # s3DownloadTime = 0
    # totalProcessingTime = 0
    pret = [len(reducer_keys), line_count, time_in_secs]
    print("Reducer output", pret)

    # if n_reducers == 1:
    #     # Last reducer file, final result
    #     fname = "%s/result" % job_id
    # else:
    #     fname = "%s/%s%s/%s" % (job_id, TASK_REDUCER_PREFIX, step_id, r_id)
    fname = "%s/result" % job_id

    metadata = {
        "linecount": '%s' % line_count,
        "processingtime": '%s' % time_in_secs,
        "memoryUsage": '%s' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    }

    write_to_s3(job_bucket, fname, bytes(str(line_count), "ascii"), metadata)
    return pret
