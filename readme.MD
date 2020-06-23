<!-- Because this file contains custom formatting for the heading, we need to
    disable some of the markdownlint rules -->
<!-- markdownlint-disable -->
<p align=center><img src="./docs/media/logos/rangerrom.png" alt="RangerRom Logo" height="150"></p>

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

There is a helm chart in my repo that you can use to deploy this to kubernetes.
git@github.com:Romiko/helm-charts.git

```
helm repo add  romiko https://romiko.github.io/helm-charts
helm install romiko/prometheus-appinsights-exporter
```

## Prometheus AppInsights Exporter
This chart will allow you to export metrics from Azure AppInsights into Prometheus.

* Download the chart.
* Update the values.yaml file
* Setup your queries in the files/queries.yaml


<p align=center><img src="./docs/media/Kubernetes Deployment.png" alt="ArgoCD K8 Deployment View for Prometheus Exporter" height="150"></p>
