import datetime
import json
import logging
import re
import requests

from data.metric import AppInsightsMetric 
from data.time_range import AppInsightsTimeRange 

class AppInsightsWrapper(object):

    def __init__(self, application_id, api_key):
        self.application_id = application_id
        self.api_key = api_key
        self.url_base = 'https://api.applicationinsights.io/v1/apps/{0}/query?query='.format(application_id)
        self.headers = {'Content-Type': 'application/json', 'X-Api-Key': '{0}'.format(api_key)}
        self.logger = logging.getLogger()
        self.exporter_interval = AppInsightsTimeRange(0, 1, 0)

    def _construct_query(self, schema, query, time_range=None,customdimensions=None):
        if not time_range:
            time_range = self.exporter_interval
        self.logger.info("Constructing Query: {0} Schema: {1} Hours/Minutes/Seconds: {2}".format(query, schema, time_range))
        now = datetime.datetime.utcnow()
        false_now = now - datetime.timedelta(minutes=5)
        d = datetime.timedelta(hours=time_range.hours, minutes=time_range.minutes, seconds=time_range.seconds)
        before = false_now - d
        now_str = false_now.strftime("%Y-%m-%dT%H:%M:%SZ")
        before_str = before.strftime("%Y-%m-%dT%H:%M:%SZ")
        time_string = "where timestamp > datetime({0}) | where timestamp < datetime({1}) | order by timestamp desc".format(before_str, now_str)
        query_string = '{0} | {1} | {2}'.format(schema, time_string, query)
        summarize='| summarize count()'
        dimensions=[]
        if(customdimensions):
            summarize = summarize + " by "
            for cd in customdimensions:
                dimensions.append('tostring(customDimensions["{0}"])'.format(cd))
        query_string += summarize + ",".join(dimensions)
        return query_string 

    def _construct_count_query(self, schema, query, time_range=None, customdimensions=None):
        return self._construct_query(schema, "{0}".format(query), time_range, customdimensions)

    def _query_api(self, query):
        query_url = self.url_base + query

        retry_count = 0
        while retry_count <= 3:
            try:
                # set timeout to 20 seconds on connect and 120 seconds on read
                response = requests.get(query_url, headers=self.headers, timeout=(20, 120))
                response_content = response.content.decode('utf-8')
                break
            except requests.exceptions.Timeout:
                retry_count += 1
            except requests.exceptions.RequestException as e:
                self.logger.error("Ambiguous exception occurred during request. Exception: {0}".format(e))
                return False

        if response.status_code != 200:
            self.logger.warning("Got response code {0} for query: {1}.".format(response.status_code, query)) 
            return False
        elif not response_content:
            self.logger.warning('No content for query {0}.'.format(query))
            return False
        else:
            self.logger.debug("Query Success. {0}".format(query)) 
            json_response = json.loads(response_content)
            self.logger.info('response: {0}'.format(json_response))
            return json_response

    def count(self, schema, query_string, time_range=None, customdimensions=None):
        summarize_column = ",".join(customdimensions)
        query_string = self._construct_count_query(schema, query_string, time_range=time_range,customdimensions=customdimensions)
        self.logger.info("Count with query: {0}".format(query_string))
        result = self._query_api(query_string)
        if not result:
            return False
        try:
                metrics = []
                for row in result['tables'][0]['rows']:
                    metric = AppInsightsMetric(summarize_column, row[-1], row[:-1])
                    self.logger.info("Metric: Value {0} Labels {1}".format(metric.value, metric.labelvalues))
                    metrics.append(metric)
        except Exception as e:
            self.logger.warning("Exception in count. Error: {0}".format(str(e)))
            return None
        self.logger.debug("count with query: {0}".format(query_string))
        return metrics


