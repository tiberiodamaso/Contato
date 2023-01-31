import os
import json
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange
from google.analytics.data_v1beta.types import Dimension
from google.analytics.data_v1beta.types import Metric
from google.analytics.data_v1beta.types import MetricType
from google.analytics.data_v1beta.types import RunReportRequest
from google.analytics.data_v1beta.types import Filter
from google.analytics.data_v1beta.types import FilterExpression
from django.conf import settings
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(
    settings.BASE_DIR, 'client_secrets.json')
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/tiberio/Desktop/Projects/Contato/client_secrets.json'


def run_report_city(property_id, pagina):
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
            # Dimension(name="sessionDefaultChannelGrouping"),
            # Dimension(name="sessionSource"),
            Dimension(name="city"),
            # Dimension(name="deviceCategory"),
            # Dimension(name="screenResolution"),
            # Dimension(name="pagePath"),
            # Dimension(name="pageTitle"),
        ],
        metrics=[
            Metric(name="totalUsers"),
            Metric(name="activeUsers"),
            Metric(name="newUsers"),
            Metric(name="userEngagementDuration"),
            Metric(name="sessions"),
            Metric(name="averageSessionDuration"),
            # Metric(name="engagedSessions"),
            Metric(name="screenPageViews"),
            # Metric(name="screenPageViewsPerSession"),
            Metric(name="bounceRate"),
        ],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="yesterday")],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="pagePath",
                string_filter=Filter.StringFilter(value=pagina),
            )
        ),
        metric_aggregations=[
            "TOTAL"
        ]
    )
    response = client.run_report(request)
    return response


def run_report_session_origin(property_id, pagina):
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
            Dimension(name="sessionDefaultChannelGrouping"),
            # Dimension(name="sessionSource"),
            # Dimension(name="city"),
            # Dimension(name="deviceCategory"),
            # Dimension(name="screenResolution"),
            # Dimension(name="pagePath"),
            # Dimension(name="pageTitle"),
        ],
        metrics=[
            Metric(name="totalUsers")
        ],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="yesterday")],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="pagePath",
                string_filter=Filter.StringFilter(value=pagina),
            )
        ),
        metric_aggregations=[
            "TOTAL"
        ]
    )
    response = client.run_report(request)
    return response

    def print_run_report_response(response):
        """Prints results of a runReport call."""
        print(f"{response.row_count} rows received")
        for dimensionHeader in response.dimension_headers:
            print(f"Dimension header name: {dimensionHeader.name}")
        for metricHeader in response.metric_headers:
            metric_type = MetricType(metricHeader.type_).name
            print(f"Metric header name: {metricHeader.name} ({metric_type})")

    print_run_report_response(response_city)


def run_report_page_path(property_id, pagina):
    property_id = "323214127"
    client = BetaAnalyticsDataClient()

    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[
            Dimension(name="pagePath"),
        ],
        metrics=[
            Metric(name="screenPageViews")
        ],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="yesterday")],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="pagePath",
                in_list_filter=Filter.InListFilter(
                    values=pagina
                ),
            )
        ),
        metric_aggregations=[
            "TOTAL"
        ]
    )
    response = client.run_report(request)
    return response

def run_report_source_traffic(property_id, pagina):
    property_id = "323214127"
    client = BetaAnalyticsDataClient()

    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[
            Dimension(name="pagePath"),
            Dimension(name="sessionDefaultChannelGroup")
        ],
        metrics=[
            Metric(name="screenPageViews")
        ],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="yesterday")],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="pagePath",
                # caseSensitive="false",
                in_list_filter=Filter.InListFilter(
                    values=pagina
                ),
            )
        ),
        metric_aggregations=[
            "TOTAL"
        ]
    )
    response = client.run_report(request)
    return response


if __name__ == "__main__":
    run_report()
