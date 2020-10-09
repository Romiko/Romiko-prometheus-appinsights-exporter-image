import hashlib

class Common():
    @staticmethod
    def create_key_metric_per_label(metric_name, labels):
        return metric_name + (hashlib.md5(bytes(labels, 'utf-8'))).hexdigest()
