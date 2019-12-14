# core modules
import os
import time
import json
import datetime
import sys

# extra modules
from absl import app, flags, logging

# own modules
from activity import Activity, ActivityList, TimeEntry
from window_handler import Window, WindowLinux

# app flags
FLAGS = flags.FLAGS
flags.DEFINE_string('activities_filepath', 'activities.json',
                    'Path of the file to read and save activities.')


class TimeTrackerBot:
    """
    A bot to track user activities.

    Parameters
    ----------
    filepath: string
        Path of the file where to save activities
    window_handler: Window
        The window handler for that tracker, only Linux available yet
    """
    def __init__(self, filepath, window_handler):
        self.window_handler = window_handler
        self.filepath = filepath
        self.activities = self.read_activities_from_json()

        self.last_activity_name = window_handler.get_active()
        self.last_activity_time = datetime.datetime.now()
        
        self.last_time_since_saving = time.time()

    def write_activities_to_json(self, activities):
        """
        Write activities to a JSON file.

        Parameters
        ----------
        activities: array-like
            The activities to write
        """
        with open(self.filepath, 'w+') as f:
            json.dump(activities, f, indent=4, sort_keys=True)

    def read_activities_from_json(self):
        """
        Read activities from a JSON file.

        Returns
        -------
        array-like: The activities as an array of ``Activity``
        """
        try:
            with open(self.filepath, 'r') as f:
                logging.debug("Reading activities from %s.", self.filepath)
                data = json.load(f)

        except (IOError, json.JSONDecodeError):
            logging.debug("%s is either empty or does not exist.", self.filepath)
            data = []

        return ActivityList(data).activities

    def serialize_activities(self):
        """
        Serialize all the activities.

        Returns
        -------
        dict: The activities serialized as JSON object
        """
        return [activity.serialize() for activity in self.activities]

    def _is_new_activity(self, activity_name):
        """
        Check if the current window is different from the last saved.

        Parameters
        ----------
        activity_name: string
            The name of the activity to check

        Returns
        -------
        bool: True if the current window is new, False otherwise
        """
        return activity_name != self.last_activity_name

    def _add_activity(self, activity_name, time_entry):
        """
        Add the activity with its time entry to the activity list.

        If activity was already present in the list, only update the duration
        and add the time entry. If activity was not present, add it.

        Parameters
        ----------
        activity_name: string
            The name of the activity to add
        time_entry: TimeEntry
            The time entry of the activity to add

        Returns
        -------
        bool: True
        """
        for activity in self.activities:
            if activity_name == activity.name:
                activity.duration += time_entry.delta
                activity.entries.append(time_entry)
                return True

        activity = Activity(name=activity_name,
                            duration=time_entry.delta,
                            entries=[time_entry])

        self.activities.append(activity)
        return True

    def run(self, save_frequency=30):
        """
        Main infinite loop.

        Get the current active window and add it when it changes. As long as a
        window stays active, just sleeps for 2 seconds.

        Save activities every ``save_frequency`` seconds.

        TODO : use signals instead of active loops.
        """
        try:
            while True:
                current_activity_name = self.window_handler.get_active()

                if not self._is_new_activity(current_activity_name):
                    time.sleep(2)
                    continue

                # get the current time of the activity and add activity to the list
                current_activity_time = datetime.datetime.now()
                current_time_entry = TimeEntry(self.last_activity_time, current_activity_time)
                self._add_activity(current_activity_name, current_time_entry)

                # restart time counter and active window name
                self.last_activity_time = datetime.datetime.now()
                self.last_activity_name = current_activity_name

                # save activities every 30 seconds
                t = time.time()
                if t - self.last_time_since_saving > save_frequency:
                    self.last_time_since_saving = t
                    self.write_activities_to_json(self.serialize_activities())
                    logging.info("Saved %s activities.", len(self.activities))

        # save activities on exception
        except (KeyboardInterrupt, Exception):
            self.write_activities_to_json(self.serialize_activities())
            logging.info("Saved %s activities.", len(self.activities))


def main(argv):
    del argv

    logging.get_absl_handler().use_absl_log_file(
        program_name='time-tracker-bot',
        log_dir='./logs/'
    )
    logging.set_verbosity(logging.INFO)

    logging.info("Starting time-tracker-bot.")
    logging.info("sys.platform=%s", sys.platform)
    logging.info("python.version=%s.", sys.version)

    window_handler = WindowLinux()
    bot = TimeTrackerBot(filepath=FLAGS.activities_filepath, window_handler=window_handler)
    bot.run()

    logging.info("Closing time-tracker-bot.")


if __name__ == '__main__':
    app.run(main)  # , argv=('--log-dir=./logs', ))