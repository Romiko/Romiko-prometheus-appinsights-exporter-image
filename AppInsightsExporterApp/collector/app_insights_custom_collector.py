from collector.app_insights_collector import AppInsightsCollector


class AppInsightsCustomCollector(AppInsightsCollector):
    """[summary]

    Args:
        AppInsightsCollector ([type]): Create SLI metrics
    """

    def __init__(self, application_id, api_key, servicelevelindicators=None, customdimensions=None):
        """[summary]

        Args:
            application_id ([type]): Appinisghts appid
            api_key ([type]): AppInsights key
            servicelevelindicators ([type], optional): SLI query config. Defaults to None.
            customdimensions ([type], optional): Labels from custom dimensions in appinsights. Defaults to None.
        """
        AppInsightsCollector.__init__(self, application_id, api_key)
        self.servicelevelindicators = servicelevelindicators
        self.customdimensions = customdimensions

    def collect(self):
        """[summary]

        Yields:
            [type]: Create a gauge metric
        """
        if self.servicelevelindicators:
            mname = self.servicelevelindicators['name']
            mquery = self.servicelevelindicators['query']
            schema = self.servicelevelindicators['schema']
            gauge_metrics = self.client.count(
                schema, mquery, customdimensions=self.customdimensions)
            if gauge_metrics:
                for gauge in gauge_metrics:
                    yield self.create_gauge_metric(mname, mquery, gauge)
        else:
            self.logger.error("No servicelevelindicator were provided.")
