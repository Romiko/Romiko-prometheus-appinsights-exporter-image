import logging
import os
import sys
import time
import yaml
import pyfiglet
import json_log_formatter
import requests

from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY
from collector.app_insights_custom_collector import AppInsightsCustomCollector

CONFIG_FILE_QUERY_PATH = "/config/queries.yaml"
PORT = 8080
SCRAPE_INTERVAL_SECONDS = 60

def configure_logging(log_conf_level):
    """[summary]

    Args:
        log_conf_level ([type]): Set the logging level

    Returns:
        [type]: [description]
    """
    if log_conf_level == 'critical':
        level = logging.CRITICAL
    elif log_conf_level == 'error':
        level = logging.ERROR
    elif log_conf_level == 'warning':
        level = logging.WARNING
    elif log_conf_level == 'debug':
        level = logging.DEBUG
    else:
        level = logging.INFO

    formatter = json_log_formatter.JSONFormatter()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(level)

    log = logging.getLogger()
    log.setLevel(level)
    log.addHandler(handler)
    return log


def get_custom_dimensions(conf):
    customdimensions = []
    if 'customdimensions' in conf:
        customdimensions = conf['customdimensions']
    return customdimensions


if __name__ == "__main__":
    ascii_banner = pyfiglet.figlet_format("Appinsights Prometheus Exporter")
    print(ascii_banner)

    try:
        key = os.environ['AZURE_APP_INSIGHTS_KEY']
        appid = os.environ['AZURE_APP_INSIGHTS_APP_ID']
        log_level = os.environ['LOG_LEVEL']
        if "QUERY_FILE" in os.environ:
            CONFIG_FILE = os.environ['QUERY_FILE']
        else:
            CONFIG_FILE = CONFIG_FILE_QUERY_PATH
    except KeyError as exception:
        MSG = """Please set the environment variables:
        AZURE_APP_INSIGHTS_KEY - The Azure Application Insights Key
        AZURE_APP_INSIGHTS_APP_ID - The Azure Application Insights App Id
        LOG_LEVEL - Log Level critical|warning|error|debug|info
        QUERY_FILE - The full path to the queries config file"""
        print(MSG)
        print("ERROR: Missing Environment Variable %s", exception)
        sys.exit(1)

    logger = configure_logging(log_level)
    conf_path = CONFIG_FILE

    with open(conf_path, 'r') as yamlfile:
        configuration = yaml.safe_load(yamlfile)

    try:
        COLLECTOR = 'customCollectors'
        if COLLECTOR in configuration:
            customConf = configuration[COLLECTOR]
            if 'servicelevelindicators' in customConf:
                for sli in customConf['servicelevelindicators']:
                    cd = get_custom_dimensions(sli)
                    REGISTRY.register(AppInsightsCustomCollector(
                        appid, key, servicelevelindicators=sli,
                        customdimensions=cd, scrape_interval_seconds=SCRAPE_INTERVAL_SECONDS))

    except Exception as exception:
        logger.error('Error creating collector: %s', str(exception))
        sys.exit(2)

    start_http_server(PORT)

    while True:
        time.sleep(SCRAPE_INTERVAL_SECONDS)
        # Call itself every 60 seconds. This is to ensure counter metric types are updated
        r = requests.get('http://localhost:%s' % PORT)
