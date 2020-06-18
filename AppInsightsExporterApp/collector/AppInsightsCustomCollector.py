import logging
import re

from appinsightswrapper.AppInsightsWrapper import AppInsightsWrapper
from collector.AppInsightsCollector import AppInsightsCollector
from data.metric import AppInsightsMetric

class AppInsightsCustomCollector(AppInsightsCollector):
    def __init__(self, application_id, api_key, servicelevelindicators=None, customdimensions=None):
        AppInsightsCollector.__init__(self, application_id, api_key)
        self.servicelevelindicators = servicelevelindicators
        self.customdimensions = customdimensions

    def collect(self):
        if (self.servicelevelindicators):
            mname = self.servicelevelindicators['name']
            mquery = self.servicelevelindicators['query']
            schema = self.servicelevelindicators['schema']
            gauge_metrics = self.client.count(schema, mquery, customdimensions=self.customdimensions)
            if gauge_metrics:
                for gauge in gauge_metrics:
                    yield self.create_gauge_metric(mname, mquery, gauge)
        else:
            self.logger.error("No servicelevelindicator were provided.")
