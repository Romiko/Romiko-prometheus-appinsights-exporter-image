class PromMetric():
    """Metric Poco for prometheus
    """

    def __init__(self, labelnames, value, labelvalues):
        self.labelnames = labelnames
        self.value = value
        self.labelvalues = labelvalues
        self.clean_label_names()


    def clean_label_names(self):
        self.labelnames = self.labelnames.replace(".", "_")
