import datetime
import unittest
from unittest import mock
from appinsightswrapper.AppInsightsWrapper import AppInsightsWrapper
from data.metric import PromMetric

class TestQueries(unittest.TestCase):

    def test_basic_query(self):
        testdt = datetime.datetime(2020, 1, 1, 12, 30, 30, 123456)
        with mock.patch('datetime.datetime') as dt_mock:
            dt_mock.utcnow.return_value = testdt
            client = AppInsightsWrapper("appid", "appkey", dt_mock)
            actual = client.build_summary_count_query("requests", '')
            expected = "requests | where timestamp > datetime(2020-01-01T12:24:30Z) | where timestamp < datetime(2020-01-01T12:25:30Z) | summarize sum(itemCount)"
            self.assertEqual(actual, expected)

    def test_query_filter(self):
        testdt = datetime.datetime(2020, 1, 1, 12, 30, 30, 123456)
        with mock.patch('datetime.datetime') as dt_mock:
            dt_mock.utcnow.return_value = testdt
            client = AppInsightsWrapper("appid", "appkey", dt_mock)
            actual = client.build_summary_count_query(
                "requests", 'where resultCode startswith "5"')
            expected = 'requests | where timestamp > datetime(2020-01-01T12:24:30Z) | where timestamp < datetime(2020-01-01T12:25:30Z) | where resultCode startswith "5" | summarize sum(itemCount)'
            self.assertEqual(actual, expected)

    def test_query_customdimension(self):
        testdt = datetime.datetime(2020, 1, 1, 12, 30, 30, 123456)
        with mock.patch('datetime.datetime') as dt_mock:
            dt_mock.utcnow.return_value = testdt
            client = AppInsightsWrapper("appid", "appkey", dt_mock)
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
        wrapper = AppInsightsWrapper('appid', 'key', datetime.datetime(2020, 1, 1, 12, 30, 30, 123456))
        wrapper.query_api = self.fake_api
        actual = wrapper.count('trader_browserTimings_homepage', 'where name == "Home-Page"')
        self.assertTrue(len(actual) > 0)

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
