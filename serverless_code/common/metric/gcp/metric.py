from google.cloud import monitoring_v3
import datetime
from google.cloud.logging import Client


def metric(headers, query_parameters):
    client = monitoring_v3.MetricServiceClient()
    project_id = "master-thesis-faas-monad"
    project_name = f"projects/{project_id}"

    # Define the metric type for Cloud Function execution times
    metric_type = "cloudfunctions.googleapis.com/function/execution_times"

    # Create a time interval for which you want to get the metrics
    interval = monitoring_v3.TimeInterval()
    now = datetime.datetime.now()
    interval.end_time = now.strftime('%Y-%m-%dT%H:%M:%SZ')
    interval.start_time = now - datetime.timedelta(minutes=5)

    # # # Define the aggregation settings
    # aggregation = monitoring_v3.Aggregation()
    # # aggregation.alignment_period = Duration(seconds=300)  # 5 minutes
    # aggregation.per_series_aligner = monitoring_v3.Aggregation.Aligner.ALIGN_MEAN

    # Call the list_time_series method with the project name, metric type, time interval, and aggregation settings
    results = client.list_metric_descriptors(
        request={
            "name": project_name,
            "filter": f'metric.type = "{metric_type}"',
            # "interval": interval,
            # "aggregation": aggregation,
        }
    )

    return results


# def test(function_name):
#     project_id = "master-thesis-faas-monad"
#     project_name = f"projects/{project_id}"
#     client = monitoring_v3.MetricServiceClient()
#
#     # # List metrics available
#     # filter_ = 'metric.type = starts_with("cloudfunctions.googleapis.com")'
#     # metrics = client.list_metric_descriptors({
#     #     "name" : project_name,
#     #     "filter": filter_
#     # })
#     #
#     # for metric in metrics:
#     #     print(metric)
#
#     # Get the executions across time
#     interval = monitoring_v3.types.TimeInterval()
#     now = datetime.datetime.now()
#     interval.end_time = now.strftime('%Y-%m-%dT%H:%M:%SZ')
#     interval.start_time = now - datetime.timedelta(minutes=5)
#
#     filter_ = f'metric.type = "cloudfunctions.googleapis.com/function/execution_times" AND resource.label.function_name = "{function_name}"'
#     result = client.list_time_series(
#         {
#             "name": project_name,
#             "filter": filter_,
#             "interval": interval,
#             # "view": monitoring_v3.enums.ListTimeSeriesRequest.TimeSeriesView.FULL
#         }
#     )
#
#     for series in result:
#         print(series)


def test(name):
    client = Client()
    logger = client.logger(name=name)  # read logs from GCP
    client.list_entries(max_results=5)


if __name__ == "__main__":
    # print(metric(None, None))
    test("metric")
