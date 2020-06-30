import logging
import datetime

from prometheus_client.core import GaugeMetricFamily
from appinsightswrapper.AppInsightsWrapper import AppInsightsWrapper


class AppInsightsCollector():
    """[summary]
    Create and collect gauage metrics
    """

    def __init__(self, application_id, api_key, customdimensions=[]):
        """[summary]

        Args:
            application_id ([type]): Appinsights appid
            api_key ([type]): Appinisghts key
            customdimensions (list, optional): Grouping metrics into labels. Defaults to []
        """
        self.application_id = application_id
        self.api_key = api_key
        self.client = AppInsightsWrapper(
            application_id, api_key, datetime.datetime)
        self.logger = logging.getLogger()
        self.customdimensions = customdimensions

    def create_gauge_metric(self, metric_name, description, gauge_results):
        """[summary]

        Args:
            metric_name ([type]): Prometheus metric name
            description ([type]): Prometheus metric description
            gauge_results ([type]): Gauage values

        Returns:
            [type]: [description]
        """
        mname = 'appinsights_exporter_{0}'.format(metric_name)
        gauge = GaugeMetricFamily(
            mname, description, labels=gauge_results.labelnames.split(","))
        gauge.add_metric(gauge_results.labelvalues, gauge_results.value)
        self.logger.debug('Gauge %s with value %s labels %s created',
                          mname, gauge_results.value, gauge_results.labelvalues)
        return gauge

    def collect(self):
        """[summary]

        Yields:
            [type]: Override this method to create a gauage
        """
        yield self.create_gauge_metric('this_must_be_overridden', 'override_me', 0)
