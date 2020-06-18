
# Deployment
Here is an overview of how you can deploy Promitor on your infrastructure, we support both Linux

## Docker

'''
docker run -d -p 8999:8080  --name promitor-appinisghts-exporter \
                            --env AZURE_APP_INSIGHTS_KEY=<azure-appinsights-key> \
                            --env AZURE_APP_INSIGHTS_APP_ID=<azure-appinsights-appid> \
                            --env LOG_LEVEL=<info|critical|debug|warning> \
                            --volume /home/dev/queries.yaml:/config/queries.yaml\
                            romiko/appinsights-prometheus-exporter:1.0.0
'''

## Kubernetes

TBA
