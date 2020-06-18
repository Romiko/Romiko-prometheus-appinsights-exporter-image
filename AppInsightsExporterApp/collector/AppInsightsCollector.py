import logging
import re

from appinsightswrapper.AppInsightsWrapper import AppInsightsWrapper
from data.metric import AppInsightsMetric
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, HistogramMetricFamily, Counter

class AppInsightsCollector(object):
    def __init__(self, application_id, api_key, customdimensions=[]):
        self.application_id = application_id
        self.api_key = api_key
        self.client = AppInsightsWrapper(application_id, api_key)
        self.logger = logging.getLogger()
        self.customdimensions = customdimensions
        self.metricDict = {}

    def create_gauge_metric(self, metric_name, description, gauge_results):
        mname = 'appinsights_exporter_{0}'.format(metric_name)
        gauge = GaugeMetricFamily(mname, description, labels=gauge_results.labelnames.split(","))
        gauge.add_metric(gauge_results.labelvalues, gauge_results.value)
        self.logger.debug("Gauge {0} with value {1} labels {2} created".format(mname, gauge_results.value, gauge_results.labelvalues))
        return gauge

    def collect(self):
        yield self.create_gauge_metric('this_must_be_overridden', 'override_me', 0)
