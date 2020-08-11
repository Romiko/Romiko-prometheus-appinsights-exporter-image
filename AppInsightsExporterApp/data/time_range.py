import datetime


class AppInsightsTimeRange():
    """
    Time ranger helpers for filtering appinisght queries
    """

    def __init__(self, hours, minutes, seconds):
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds

    @staticmethod
    def get_time_filter(date, time_range):
        """[summary]

        Args:
            dt ([type]): datetime.datetime object. Used for unit testing override
            time_range ([type]): [description]

        Returns:
            [type]: [description]
        """
        now = date.utcnow()
        false_now = now - datetime.timedelta(minutes=5)
        date = datetime.timedelta(
            hours=time_range.hours, minutes=time_range.minutes,
            seconds=time_range.seconds)
        before = false_now - date
        now_str = false_now.strftime("%Y-%m-%dT%H:%M:%SZ")
        before_str = before.strftime("%Y-%m-%dT%H:%M:%SZ")
        return "where timestamp > datetime({0}) | where timestamp < datetime({1})".format(before_str, now_str)
