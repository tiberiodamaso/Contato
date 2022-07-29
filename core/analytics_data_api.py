import os, json
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange
from google.analytics.data_v1beta.types import Dimension
from google.analytics.data_v1beta.types import Metric
from google.analytics.data_v1beta.types import MetricType
from google.analytics.data_v1beta.types import RunReportRequest
from google.analytics.data_v1beta.types import Filter
from google.analytics.data_v1beta.types import FilterExpression
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/tiberio/Desktop/Projects/Contato/client_secrets.json'


def run_report(property_id, pagina):
    """Runs a simple report on a Google Analytics 4 property."""
    #  developer: Uncomment this variable and replace with your
    #  Google Analytics 4 property ID before running the sample.
    property_id = "323214127"

    # Using a default constructor instructs the client to use the credentials
    # specified in GOOGLE_APPLICATION_CREDENTIALS environment variable.
    client = BetaAnalyticsDataClient()

    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[
            Dimension(name="pagePath"),
            Dimension(name="pageTitle"),
            ],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="newUsers"),
            Metric(name="averageSessionDuration"),
            Metric(name="bounceRate"),
            ],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="yesterday")],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="pagePath",
                string_filter=Filter.StringFilter(value=pagina),
            )
        ),
    )
    response = client.run_report(request)
    return response.rows[0].metric_values

    def print_run_report_response(response):
        """Prints results of a runReport call."""
        print(f"{response.row_count} rows received")
        for dimensionHeader in response.dimension_headers:
            print(f"Dimension header name: {dimensionHeader.name}")
        for metricHeader in response.metric_headers:
            metric_type = MetricType(metricHeader.type_).name
            print(f"Metric header name: {metricHeader.name} ({metric_type})")

    print_run_report_response(response)

    print("Report result:")
    for row in response.rows:
        print(row)
        print(row.dimension_values[0].value, row.metric_values[0].value)

if __name__ == "__main__":
    run_report()