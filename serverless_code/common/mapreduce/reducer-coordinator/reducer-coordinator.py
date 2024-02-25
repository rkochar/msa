'''
REDUCER Coordinator

Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
'''

import json
import time
from helpers.helpers import batch_creator, get_reducer_batch_size, get_mapper_files, check_job_done

MAPPERS_DONE, REDUCER_STEP = 0, 1


def get_reducer_state_info(files, job_id, job_bucket):
    reducers, reducer_step, r_index= [], False, 0

    # Check for the Reducer state
    # Determine the latest reducer step#
    for f in files:
        # parts = f['Key'].split('/');
        if "reducerstate." in f['Key']:
            idx = int(f['Key'].split('.')[1])
            if idx > r_index:
                r_index = idx
            reducer_step = True

    # Find with reducer state is complete 
    if reducer_step == False:
        # return mapper files
        return [MAPPERS_DONE, get_mapper_files(files)]
    else:
        # Check if the current step is done
        key = "%s/reducerstate.%s" % (job_id, r_index)
        response = get_from_s3(bucket=job_bucket, key=key)
        contents = json.loads(response['Body'].read())

        # get reducer outputs
        for f in files:
            fname = f['Key']
            parts = fname.split('/')
            if len(parts) < 3:
                continue
            rFname = 'reducer/' + str(r_index)
            if rFname in fname:
                reducers.append(f)

        if int(contents["reducerCount"]) == len(reducers):
            return (r_index, reducers)
        else:
            return (r_index, [])


def write_reducer_state(n_reducers, n_s3, bucket, fname):
    ts = time.time()
    # Write some stats to S3
    # data = json.dumps({
    #     "reducerCount": '%s' % n_reducers,
    #     "totalS3Files": '%s' % n_s3,
    #     "start_time": '%s' % ts
    # })
    # write_to_s3(bucket, fname, data, {})


def lambda_handler(s3_event):
    print("Received event: " + str(s3_event))
    start_time = time.time()

    # Job Bucket. We just got a notification from this bucket
    bucket = s3_event['bucket']['name']
    config = json.loads(get_from_s3(bucket, "jobinfo.json")["Body"].read())

    job_id, map_count = config["jobId"], config["mapCount"]
    files = list_objects_from_s3(bucket=bucket, prefix=job_id)

    if check_job_done(files):
        print(f"Execution time: {time.time() - start_time}")
        print("Job done!!! Check the result file")
        # TODO:  Delete reducer and coordinator lambdas
        return ""
    else:
        ### Stateless Coordinator logic
        mapper_keys = get_mapper_files(files)
        print("Mappers Done so far ", len(mapper_keys))

        if map_count == len(mapper_keys):

            # All the mappers have finished, time to schedule the reducers
            stepInfo = get_reducer_state_info(files, job_id, bucket)

            print("stepInfo", stepInfo)

            step_number = stepInfo[0];
            reducer_keys = stepInfo[1];

            if len(reducer_keys) == 0:
                print("Still waiting to finish Reducer step ", step_number)
                return

            # Compute this based on metadata of files
            r_batch_size = get_reducer_batch_size(reducer_keys)

            print("Starting the the reducer step", step_number)
            print("Batch Size", r_batch_size)

            # Create Batch params for the Lambda function
            r_batch_params = batch_creator(reducer_keys, r_batch_size)

            # Build the lambda parameters
            n_reducers = len(r_batch_params)
            #n_s3 = n_reducers * len(r_batch_params[0])
            step_id, outputs = step_number + 1, []

            for i in range(len(r_batch_params)):
                batch = [b['Key'] for b in r_batch_params[i]]
                payload = json.dumps({
                    "bucket": bucket,
                    "keys": batch,
                    "jobBucket": bucket,
                    "jobId": job_id,
                    "nReducers": n_reducers,
                    "stepId": step_id,
                    "reducerId": i
                })
                outputs.append(publish_message(str({"body": payload}), publish=True))

            # Now write the reducer state
            # fname = "%s/reducerstate.%s" % (job_id, step_id)
            # write_reducer_state(n_reducers, n_s3, bucket, fname)
        else:
            print("Still waiting for all the mappers to finish")

    print(f"Execution time: {time.time() - start_time}")
    return str(outputs)
