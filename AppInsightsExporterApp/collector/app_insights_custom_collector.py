from datetime import datetime
from collector.app_insights_collector import AppInsightsCollector

class AppInsightsCustomCollector(AppInsightsCollector):
    """[summary]

    Args:
        AppInsightsCollector ([type]): Create SLI metrics
    """

    def __init__(self, application_id, api_key, servicelevelindicators=None, customdimensions=None, sample_rate_seconds=60):
        """[summary]

        Args:
            application_id ([type]): Appinisghts appid
            api_key ([type]): AppInsights key
            servicelevelindicators ([type], optional): SLI query config. Defaults to None.
            customdimensions ([type], optional): Labels from custom dimensions in appinsights. Defaults to None.
        """
        AppInsightsCollector.__init__(self, application_id, api_key, sample_rate_seconds)
        self.servicelevelindicators = servicelevelindicators
        self.customdimensions = customdimensions
        self.sample_rate_seconds = sample_rate_seconds

    def collect(self):
        """[summary]

        Yields:
            [type]: Create a gauge metric
        """
        if self.servicelevelindicators:
            collectiontimestamp = datetime.now()
            sample_rate_seconds = self.sample_rate_seconds
            mname = self.servicelevelindicators['name']
            mquery = self.servicelevelindicators['query']
            schema = self.servicelevelindicators['schema']
            metrictype = self.servicelevelindicators['metrictype']
            metrics = self.client.count(
                schema, mquery, customdimensions=self.customdimensions)
            if metrics:
                for metric in metrics:
                    if metrictype == 'counter':
                        yield self.create_counter_metric(mname, mquery, metric, collectiontimestamp, sample_rate_seconds)
                    elif metrictype == 'gauge':
                        yield self.create_gauge_metric(mname, mquery, metric)
                    else:
                        raise ValueError('metrictype not supported %s' % metrictype)
        else:
            self.logger.error("No servicelevelindicator were provided.")
