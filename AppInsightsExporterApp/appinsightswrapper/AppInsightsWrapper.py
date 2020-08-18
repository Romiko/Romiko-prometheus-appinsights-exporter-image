import json
import logging
import requests
from data.metric import PromMetric
from data.time_range import AppInsightsTimeRange

API_URL = "https://api.applicationinsights.io/v1/apps/{0}/query?query="


class AppInsightsWrapper():

    def __init__(self, application_id, api_key, date, scrape_interval_seconds):
        self.application_id = application_id
        self.api_key = api_key
        self.url_base = API_URL.format(application_id)
        self.headers = {'Content-Type': 'application/json',
                        'X-Api-Key': '{0}'.format(api_key)}
        self.logger = logging.getLogger()
        self.exporter_interval = AppInsightsTimeRange(0, 0, scrape_interval_seconds)
        self.date = date

    def build_summary_count_query(self, schema, query, time_range=None, customdimensions=None):
        if not time_range:
            time_range = self.exporter_interval
        self.logger.info(
            'Constructing Query: %s Schema: %s Hours/Minutes/Seconds: %s',
            query, schema, time_range)
        time_string = AppInsightsTimeRange.get_time_filter(
            self.date, time_range)
        query_string = '{0} | {1}'.format(schema, time_string)
        if query:
            query_string = '{0} | {1}'.format(query_string, query)
        summarize = 'summarize sum(itemCount)'
        dimensions = []
        if customdimensions:
            summarize = '{0} {1}'.format(summarize, "by")
            for cud in customdimensions:
                dimensions.append(
                    'tostring(customDimensions["{0}"])'.format(cud))
        query_string = '{0} | {1} {2}'.format(
            query_string, summarize, ",".join(dimensions)).strip()
        return query_string

    def query_api(self, query):
        query_url = self.url_base + query

        retry_count = 0
        while retry_count <= 3:
            try:
                # set timeout to 20 seconds on connect and 120 seconds on read
                response = requests.get(
                    query_url, headers=self.headers, timeout=(20, 120))
                response_content = response.content.decode('utf-8')
                break
            except requests.exceptions.Timeout:
                retry_count += 1
            except requests.exceptions.RequestException as exception:
                self.logger.error(
                    'Ambiguous exception occurred during request. Exception: %s', exception)
                return False

        if response.status_code != 200:
            self.logger.warning(
                'Got response code %s for query: %s.',
                response.status_code, query)
            return False

        if not response_content:
            self.logger.warning('No content for query %s.', query)
            return False

        self.logger.debug('Query Success. %s', query)
        json_response = json.loads(response_content)
        self.logger.info('response: %s', json_response)
        return json_response

    def count(self, schema, query_string, time_range=None, customdimensions=None):
        if customdimensions:
            summarize_column = ",".join(customdimensions)
        else:
            summarize_column = ""
        query_string = self.build_summary_count_query(
            schema, query_string, time_range, customdimensions)
        self.logger.info('Count with query: %s', query_string)
        result = self.query_api(query_string)
        if not result:
            return False
        try:
            metrics = []
            if len(result['tables'][0]['rows']) == 0:
                metric = PromMetric('', 0, '')
                metrics.append(metric)
                return metrics
            for row in result['tables'][0]['rows']:
                metric = PromMetric(summarize_column, row[-1], row[:-1])
                self.logger.info(
                    'Metric: Value %s Labels %s', metric.value, metric.labelvalues)
                metrics.append(metric)
        except Exception as exception:
            self.logger.warning(
                'Exception in count. Error: %s', str(exception))
            return None
        self.logger.debug('count with query: %s', query_string)
        return metrics
