class AppInsightsMetric(object):
    
    def __init__(self, labelnames, value, labelvalues):
        self.labelnames = labelnames
        self.value = value
        self.labelvalues = labelvalues
