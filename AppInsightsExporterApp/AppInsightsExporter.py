import argparse
import logging
import json
import os
import requests
import sys
import time
import yaml
import pyfiglet

from logging.handlers import RotatingFileHandler
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY

from collector.AppInsightsCollector import AppInsightsCollector
from collector.AppInsightsCustomCollector import AppInsightsCustomCollector

CONFIG_FILE_QUERY_PATH="/config/queries.yaml"

def configure_logging(log_conf_level):
    if log_conf_level == 'critical':
        log_level = logging.CRITICAL
    elif log_conf_level == 'error':
        log_level = logging.ERROR
    elif log_conf_level == 'warning':
        log_level = logging.WARNING
    elif log_conf_level == 'debug':
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    my_formatter = logging.Formatter('[AppInsightsMetricsExporter] %(asctime)s %(levelname)-7.7s %(message)s')
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(my_formatter)
    handler.setLevel(log_level)

    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(handler)

    return True

def getCollectorCustomDimensions(configuration):
    customdimensions = []
    if 'customdimensions' in configuration:
        customdimensions = configuration['customdimensions']
    return customdimensions

if __name__ == "__main__":
    ascii_banner = pyfiglet.figlet_format("Appinsights Prometheus Exporter")
    print(ascii_banner)
    print(pyfiglet.figlet_format("http://romikoderbynew.com", font = "digital" ) )
    
    try:  
        key = os.environ['AZURE_APP_INSIGHTS_KEY']
        appid = os.environ['AZURE_APP_INSIGHTS_APP_ID']
        log_level = os.environ['LOG_LEVEL']
        if "QUERY_FILE" in os.environ:
            configuration_file = os.environ['QUERY_FILE']
        else:
            configuration_file = CONFIG_FILE_QUERY_PATH
    except KeyError as e: 
        msg = """Please set the environment variables:
        AZURE_APP_INSIGHTS_KEY - The Azure Application Insights Key 
        AZURE_APP_INSIGHTS_APP_ID - The Azure Application Insights App Id
        LOG_LEVEL - Log Level critical|warning|error|debug|info
        QUERY_FILE - The full path to the configuration file containing the queries"""
        print(msg)
        print("ERROR: Missing Key {0}".format(e))
        
        sys.exit(1)

    configure_logging(log_level)
    logger = logging.getLogger()
    conf_path = configuration_file

    with open(conf_path, 'r') as yamlfile:
        configuration = yaml.safe_load(yamlfile)

    try:
        collector = 'customCollectors'
        if (collector in configuration):
                customConf = configuration[collector]
                if 'servicelevelindicators' in customConf:
                    for sli in customConf['servicelevelindicators']:
                        cd = getCollectorCustomDimensions(sli)
                        REGISTRY.register(AppInsightsCustomCollector(appid, key, servicelevelindicators=sli, customdimensions=cd))
        
    except Exception as e:
        logger.error('Error creating collector: {0}'.format(str(e)))
        sys.exit(2)

    start_http_server(8080)
    
    while True:
        time.sleep(60)
