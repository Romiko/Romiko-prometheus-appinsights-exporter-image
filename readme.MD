<!-- Because this file contains custom formatting for the heading, we need to
    disable some of the markdownlint rules -->
<!-- markdownlint-disable -->
<p align=center><img src="./docs/media/logos/promitor.png" alt="Promitor Logo" height="150"></p>

<h1 align="center">Bringing Azure ApplicationInsight metrics to Prometheus.</h1>

<p align="center">
    <a href="./LICENSE" rel="nofollow"><img src="https://img.shields.io/github/license/mashape/apistatus.svg?style=flat-square" alt="License"></a>

# Deployment
Here is an overview of how you can deploy Promitor on your infrastructure, we support both Linux

## Docker

```
docker run -d -p 8999:8080  --name prom-appinsights-exporter \
                            --env AZURE_APP_INSIGHTS_KEY=<azure-appinsights-key>  \
                            --env AZURE_APP_INSIGHTS_APP_ID=<azure-appinsights-appid>   \
                            --env LOG_LEVEL=<info|critical|debug|warning>   \
                            --volume /home/dev/queries.yaml:/config/queries.yaml \
                            romiko/appinsights-prometheus-exporter:1.0.0
```

## Kubernetes

TBA
