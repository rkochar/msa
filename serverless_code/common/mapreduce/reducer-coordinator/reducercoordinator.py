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
        f = f.get("Name") if isinstance(f, dict) else f.key
        if "reducerstate." in f:
            idx = int(f.split('.')[1])
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
        contents = json.loads(get_from_s3(bucket=job_bucket, key=key))
        print(f"Reducer state contents: {contents}")
        # get reducer outputs
        for f in files:
            fname = f.get("Name") if isinstance(f, dict) is not None else f.key
            print(f"fname: {fname}")
            parts = fname.split('/')
            if len(parts) < 3:
                continue
            rFname = 'reducer/' + str(r_index)
            if rFname in fname:
                reducers.append(f)
            # reducers.append(f)

        print(f"reducers: {reducers}")
        if int(contents["reducerCount"]) == len(reducers):
            return (r_index, reducers)
        else:
            print("Reducer step not done yet. empty reducers")
            return (r_index, [])


# def write_reducer_state(n_reducers, n_s3, bucket, fname):
#     ts = time.time()
#     data = json.dumps({
#         "reducerCount": '%s' % n_reducers,
#         "totalS3Files": '%s' % n_s3,
#         "start_time": '%s' % ts
#     })
#     write_to_s3(bucket, fname, data)


def lambda_handler(s3_event):
    print("Received event: " + str(s3_event))
    start_time = time.time()

    # Job Bucket. We just got a notification from this bucket
    bucket = s3_event.get('bucket')
    if isinstance(bucket, dict):
        bucket = bucket['name']
    config = json.loads(get_from_s3(bucket, "jobinfo.json"))

    job_id, map_count, job_bucket, result_bucket = config["jobId"], config["mapCount"], config["jobBucket"], config["resultBucket"]
    files = filter_objects_s3(bucket=bucket, prefix=job_id)
    print(f'Files in the bucket: {files}')

    # if check_job_done(files):
    #     print(f"Execution time: {time.time() - start_time}")
    #     print("Job done!!! Check the result file")
    #     # TODO:  Delete reducer and coordinator lambdas
    #     return ""
    if False:
        print("TODO: see above commented block of code")
        return
    else:
        ### Stateless Coordinator logic
        mapper_keys = get_mapper_files(files)
        print(f"mapper_keys: {mapper_keys}")
        print(f"Mappers done so far: {len(mapper_keys)} and map_count: {map_count}")

        if map_count == len(mapper_keys):

            # All the mappers have finished, time to schedule the reducers
            stepInfo = get_reducer_state_info(files, job_id, bucket)
            print("stepInfo", stepInfo)
            step_number, reducer_keys = stepInfo[0], stepInfo[1]

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
            n_s3 = n_reducers * len(r_batch_params[0])
            step_id, outputs = step_number + 1, []

            for i in range(len(r_batch_params)):
                batch = None
                if isinstance(r_batch_params[0][0], dict):
                    batch = [b['Name'] for b in r_batch_params[i]]
                else:
                    batch = [b.key for b in r_batch_params[i]]

                payload = json.dumps({
                    "bucket": bucket,
                    "keys": batch,
                    "jobBucket": bucket,
                    "resultBucket": result_bucket,
                    "jobId": job_id,
                    "nReducers": n_reducers,
                    "stepId": step_id,
                    "reducerId": i
                })
                outputs.append(publish_message(str({"body": payload}), publish=True))

            # Now write the reducer state
            fname = "%s/reducerstate.%s" % (job_id, step_id)
            # write_reducer_state(n_reducers, n_s3, bucket, fname)
        else:
            print("Still waiting for all the mappers to finish")

    print(f"Execution time: {time.time() - start_time}")
    return ""
