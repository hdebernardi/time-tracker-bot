# core modules
import abc
import subprocess
import re

# extra modules
from absl import app, logging
logging.set_verbosity(logging.DEBUG)


class Window:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_active(self):
        """
        Returns the details about the window.
        """
        raise NotImplementedError


class WindowLinux(Window):
    def __init__(self):
        pass

    @staticmethod
    def _get_active_id(stdout):
        return re.search(r"^_NET_ACTIVE_WINDOW.* ([\w]+)$", stdout)

    @staticmethod
    def _get_active_raw_name(stdout):
        return re.match(r"WM_NAME\(\w+\) = (?P<name>.+)$", stdout)

    def get_active(self):
        """
        Get the name of the current active window.

        Code found there :
        https://stackoverflow.com/questions/10266281/obtain-active-window-using-python

        Returns
        -------
        string: The name of the current active window.
        """

        # root.communicate() gives bytes so we need to apply .decode()
        # to convert bytes to str in python3

        root = subprocess.Popen(
            ['xprop', '-root', '_NET_ACTIVE_WINDOW'], stdout=subprocess.PIPE)
        stdout, _ = root.communicate()

        window_id = self._get_active_id(stdout.decode())
        logging.debug(f"window id found : {window_id}")
        if window_id is None:
            return None

        window_id = window_id.group(1)
        window = subprocess.Popen(
            ['xprop', '-id', window_id, 'WM_NAME'], stdout=subprocess.PIPE)
        stdout, _ = window.communicate()

        window_name = self._get_active_raw_name(stdout.decode())
        logging.debug(f"window name found : {window_name}")
        if window_name is None:
            return None

        window_raw = window_name.group("name").strip('"')
        logging.debug(f"window raw found : {window_raw}")

        window_list = window_raw.split(" - ")
        logging.debug(f"window list found : {window_list}")
        if window_list is None:
            return None

        window_name = window_list[-1]
        logging.debug(f"window name found : {window_name}")

        if 'Chromium' in window_name:
            window_list.pop()
            window_list = window_list[::-1]
            return 'Chromium/' + "/".join(window_list)

        return window_name


def main(argv):
    del argv
    window_handler = WindowLinux()
    print(window_handler.get_active())


if __name__ == "__main__":
    app.run(main)
