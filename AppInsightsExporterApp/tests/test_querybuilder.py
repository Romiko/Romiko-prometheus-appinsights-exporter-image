import datetime
import unittest
from unittest import mock
from appinsightswrapper.AppInsightsWrapper import AppInsightsWrapper
from collector.app_insights_collector import AppInsightsCollector
from data.metric import PromMetric

class TestQueries(unittest.TestCase):

    def test_basic_query(self):
        testdt = datetime.datetime(2020, 1, 1, 12, 30, 30, 123456)
        with mock.patch('datetime.datetime') as dt_mock:
            dt_mock.utcnow.return_value = testdt
            client = AppInsightsWrapper("appid", "appkey", dt_mock, 60)
            actual = client.build_summary_count_query("requests", '')
            expected = "requests | where timestamp > datetime(2020-01-01T12:24:30Z) | where timestamp < datetime(2020-01-01T12:25:30Z) | summarize sum(itemCount)"
            self.assertEqual(actual, expected)

    def test_query_filter(self):
        testdt = datetime.datetime(2020, 1, 1, 12, 30, 30, 123456)
        with mock.patch('datetime.datetime') as dt_mock:
            dt_mock.utcnow.return_value = testdt
            client = AppInsightsWrapper("appid", "appkey", dt_mock, 60)
            actual = client.build_summary_count_query(
                "requests", 'where resultCode startswith "5"')
            expected = 'requests | where timestamp > datetime(2020-01-01T12:24:30Z) | where timestamp < datetime(2020-01-01T12:25:30Z) | where resultCode startswith "5" | summarize sum(itemCount)'
            self.assertEqual(actual, expected)

    def test_query_customdimension(self):
        testdt = datetime.datetime(2020, 1, 1, 12, 30, 30, 123456)
        with mock.patch('datetime.datetime') as dt_mock:
            dt_mock.utcnow.return_value = testdt
            client = AppInsightsWrapper("appid", "appkey", dt_mock, 60)
            actual = client.build_summary_count_query(
                "requests", 'where resultCode startswith "5"', customdimensions=["Environment"])
            expected = 'requests | where timestamp > datetime(2020-01-01T12:24:30Z) | where timestamp < datetime(2020-01-01T12:25:30Z) | where resultCode startswith "5" | summarize sum(itemCount) by tostring(customDimensions["Environment"])'
            self.assertEqual(actual, expected)

    def test_labelname_dots_replaced(self):
        metric = PromMetric("my.label1, my.label2", 0, "foo, bar")
        actual = metric.labelnames
        expected = "my_label1, my_label2"
        self.assertEqual(actual, expected)

    def test_no_customdimensions(self):
        wrapper = AppInsightsWrapper('appid', 'key', datetime.datetime(2020, 1, 1, 12, 30, 30, 123456), 60)
        wrapper.query_api = self.fake_api
        actual = wrapper.count('trader_browserTimings_homepage', 'where name == "Home-Page"')
        self.assertTrue(len(actual) > 0)

    def test_counter(self):
        scrapeinterval = 60
        testdt = datetime.datetime(2020, 1, 1, 12, 30, 30, 123456)
        customdimensions = ['Environment', 'Deployment']
        collector = AppInsightsCollector("appid", "appkey", customdimensions, 60)
        counterresults = PromMetric("my.label1, my.label2", 100, "foo, bar")
        result = collector.create_counter_metric("abc", "my metric", counterresults, testdt, scrapeinterval)
        self.assertEqual(collector.CounterValues['abc3115a23f2321a965fcbbadf2cb5936ad']['value'], result.samples[0].value)
        self.assertEqual(100, result.samples[0].value)

    def test_counter_not_increment_before_60_sec(self):
        scrapeinterval = 60
        testdt = datetime.datetime(2020, 1, 1, 12, 30, 30, 123456)
        customdimensions = ['Environment', 'Deployment']
        collector = AppInsightsCollector("appid", "appkey", customdimensions, scrapeinterval)
        collector.CounterValues = {}
        counterresults = PromMetric("my.label1, my.label2", 100, "foo, bar")
        collector.create_counter_metric("abc", "my metric", counterresults, testdt, scrapeinterval)
        result = collector.create_counter_metric("abc", "my metric", counterresults, testdt + datetime.timedelta(seconds=40), scrapeinterval)
        self.assertEqual(collector.CounterValues['abc3115a23f2321a965fcbbadf2cb5936ad']['value'], result.samples[0].value)
        self.assertEqual(100, result.samples[0].value)

    def test_counter_does_increment_after_60_sec(self):
        scrapeinterval = 60
        testdt = datetime.datetime(2020, 1, 1, 12, 30, 30, 123456)
        customdimensions = ['Environment', 'Deployment']
        collector = AppInsightsCollector("appid", "appkey", customdimensions, scrapeinterval)
        collector.CounterValues = {}
        counterresults = PromMetric("my.label1, my.label2", 100, "foo, bar")
        result = collector.create_counter_metric("abc", "my metric", counterresults, testdt, scrapeinterval)
        result = collector.create_counter_metric("abc", "my metric", counterresults, testdt + datetime.timedelta(seconds=120), scrapeinterval)
        self.assertEqual(collector.CounterValues['abc3115a23f2321a965fcbbadf2cb5936ad']['value'], result.samples[0].value)
        self.assertEqual(200, result.samples[0].value)

    def fake_api(self, query):
        print(self, query)
        result = {
            "tables": [{
                'columns' : [{'name': 'path', 'type': 'string'}, {'name': 'duration', 'type': 'long'}],
                'rows' : [["homepage", 70], ["slowpage", 7000]]
                }]
            }
        return result

if __name__ == '__main__':
    unittest.main()
