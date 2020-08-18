import logging
import datetime
import hashlib

from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily
from appinsightswrapper.AppInsightsWrapper import AppInsightsWrapper


class AppInsightsCollector():
    """[summary]
    Create and collect metrics
    """

    CounterValues = {}

    def __init__(self, application_id, api_key, customdimensions=[], scrape_interval_seconds=60):
        """[summary]

        Args:
            application_id ([type]): Appinsights appid
            api_key ([type]): Appinisghts key
            customdimensions (list, optional): Grouping metrics into labels. Defaults to []
        """
        self.application_id = application_id
        self.api_key = api_key
        self.client = AppInsightsWrapper(
            application_id, api_key, datetime.datetime, scrape_interval_seconds)
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

    def create_counter_metric(self, metric_name, description, counter_results, collectiontimestamp):
        """
        Ensure prometheus scrapes every SCRAPE_INTERVAL_SECONDS
        This will ensure the counter increments correctly on aggregated data.

        Args:
            metric_name ([type]): Prometheus metric name
            description ([type]): Prometheus metric description
            counter_results ([type]): Gauage values

        Returns:
            [type]: [description]
        """
        value = 0
        key = metric_name + (hashlib.md5(bytes(counter_results.labelnames.join(counter_results.labelvalues), 'utf-8'))).hexdigest()
        mname = 'appinsights_exporter_{0}'.format(metric_name)
        counter = CounterMetricFamily(
            mname, description, labels=counter_results.labelnames.split(","))

        if key in self.CounterValues:
            value = self.CounterValues[key]['value']
            lastcollecteddate = self.CounterValues[key]['timestamp']
            if (collectiontimestamp-lastcollecteddate).total_seconds() >= 60:
                value = counter_results.value + self.CounterValues[key]['value']
                self.CounterValues.update({key :{'timestamp': collectiontimestamp, 'value': value}})
        else:
            value = counter_results.value
            self.CounterValues.update({key : {'timestamp': collectiontimestamp, 'value': counter_results.value}})

        counter.add_metric(counter_results.labelvalues, value)

        self.logger.debug('Gauge %s with value %s labels %s created',
                          mname, counter_results.value, counter_results.labelvalues)
        return counter


    def collect(self):
        """[summary]

        Yields:
            [type]: Override this method to create a metric
        """
        yield self.create_gauge_metric('this_must_be_overridden', 'override_me', 0)
