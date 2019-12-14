# extra modules
from dateutil import parser


class ActivityList:
    """
    Represents a list of ``Activity``.

    Parameters
    ----------
    data: array-like
        The raw data provided by a JSON file
    """
    def __init__(self, data):
        self.activities = self.get_activities_from_json(data)

    def get_activities_from_json(self, data):
        return list(map(
            lambda activity: Activity(
                name=activity['name'],
                duration=activity['duration'],
                entries=self.get_entries_from_json(activity['entries'])
            ), data))

    @staticmethod
    def get_entries_from_json(entries):
        return list(map(
            lambda entry: TimeEntry(
                start_time=parser.parse(entry['start_time']),
                end_time=parser.parse(entry['end_time'])
            ), entries))

    def __repr__(self):
        return f"Activities : {len(self.activities)}."


class Activity:
    """
    Represents an activity.

    Parameters
    ----------
    name: basestring
        The name of the activity
    duration: int
        The total duration of the activity
    entries: array-like
        All the time entries of the activity
    """
    def __init__(self, name, duration, entries):
        self.name = name
        self.duration = duration
        self.entries = entries

    def serialize(self):
        """
        Serialize an activity using ``TimeEntry`` serialization.

        Returns
        -------
        dict: An activity serialized as JSON object
        """
        return {
            'name': self.name,
            'duration': self.duration,
            'entries': [entry.serialize() for entry in self.entries]
        }

    def __repr__(self):
        return f"Activity : {self.name}, {self.duration} seconds, {len(self.entries)} entries."


class TimeEntry:
    """
    Represents a TimeEntry.

    Parameters
    ----------
    start_time: datetime.datetime
        The starting time of the entry
    end_time: datetime.datetime
        The ending time of the entry
    """
    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
        self.delta = (end_time - start_time).total_seconds()

    def serialize(self):
        """
        Serialize a time entry.

        Returns
        -------
        dict: A time entry serialized as JSON object
        """
        return {
            'start_time': self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            'end_time': self.end_time.strftime("%Y-%m-%d %H:%M:%S"),
            'delta': self.delta
        }

    def __repr__(self):
        return f"TimeEntry : {self.start_time} to {self.end_time}, {self.delta} seconds."
