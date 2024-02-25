'''
Python mapper function

Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
'''


import json
import resource

# constants
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
        contents = response['Body'].read().decode("utf-8")  # Test
        #print(f"type: {type(contents)}")
        #print(f"contents: {contents}")

        for line in contents.split('\n')[:-1]:
            line_count += 1
            # try:
            #     data = line.split(',')
            #     srcIp = data[0][:8]
            #     if srcIp not in output:
            #         output[srcIp] = 0
            #     output[srcIp] += float(data[3])
            # except Exception as e:
            #     print(e)
                # err += '%s' % e

    time_in_secs = (time() - start_time)
    # timeTaken = time_in_secs * 1000000000 # in 10^9
    # s3DownloadTime = 0
    # totalProcessingTime = 0
    pret = [len(src_keys), line_count, time_in_secs, err]
    mapper_fname = "%s/%s%s" % (job_id, TASK_MAPPER_PREFIX, mapper_id)
    metadata = {
        "linecount": '%s' % line_count,
        "processingtime": '%s' % time_in_secs,
        "memoryUsage": '%s' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    }

    print("metadata", metadata)
    write_to_s3(job_bucket, mapper_fname, bytes(str(line_count), "ascii"), metadata)
    return pret
