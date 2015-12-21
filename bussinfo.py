import requests
import time
import datetime
import threading
import yaml
from bussmodel import NextBusInfo

class NextBusChecker(threading.Thread):
    def __init__(self, busInfoQueue):
        super(NextBusChecker, self).__init__()
        self.last_data_updated_at = None
        self.last_data_minutes_to_next_bus = None
        self.minutes_to_next_bus = None
        self.bus_is_coming = False
        self.error_with_data = False
        self.busInfoQueue = busInfoQueue

    def get_config_entries(self):
        return yaml.safe_load(open("config.yaml"))

    def get_data_from_api(self):

        config_data = self.get_config_entries()

        api_url = config_data["SL"]["URL"]

        api_result = "No data"
        try:
            api_request = requests.get(api_url, timeout=10)
        except:
            pass
        else:
            try:
                api_result = api_request.json()
            except:
                pass

        return api_result

    def get_bus_data(self):
        api_result = self.get_data_from_api()

        try:
            self.busInfoQueue.empty()
            for data in api_result["ResponseData"]["Buses"]:
                busInfo = NextBusInfo()
                busInfo.bus_number = data["LineNumber"]
                busInfo.bus_destination = data["Destination"]
                busInfo.bus_arrival_display = data["DisplayTime"]
                busInfo.bus_arrival_time = data["ExpectedDateTime"]
                self.busInfoQueue.put(busInfo)

        except (KeyError, TypeError):
            return "No data"
        except IndexError:
            return "No bus"

    def get_minutes_to_next_bus(self):
        """
        Gets minutes to next bus
        """
        api_result = self.get_data_from_api()

        try:
            expected_time = api_result["ResponseData"]["Buses"][0]["ExpectedDateTime"]
            latest_update = api_result["ResponseData"]["LatestUpdate"]
            data_age = api_result["ResponseData"]["DataAge"]
        except (KeyError, TypeError):
            return "No data"
        except IndexError:
            return "No bus"

        expected_time = datetime.datetime.strptime(expected_time, "%Y-%m-%dT%H:%M:%S")
        latest_update = datetime.datetime.strptime(latest_update, "%Y-%m-%dT%H:%M:%S")
        sl_time = latest_update + datetime.timedelta(seconds=data_age)
        if expected_time > sl_time:
            minutes = (expected_time - sl_time).seconds / 60
        else:
            minutes = 0
        return minutes

    def print_next_bus(self):
        if self.last_data_updated_at is None:
            print "Getting data"
            return
        if self.bus_is_coming:
            print "Next bus leaves in: %s minutes (%s, data from: %s)" % (
                self.minutes_to_next_bus, self.get_now(), self.last_data_updated_at)
        else:
            print "No bus in data (%s, data from: %s)" % (self.get_now(), self.last_data_updated_at)

    def get_now(self):
        return datetime.datetime.now()

    def recalculate_minutes_to_next_bus(self):
        # Check data
        if self.last_data_updated_at is None:
            self.minutes_to_next_bus = None
            return
        if self.last_data_minutes_to_next_bus is None:
            self.minutes_to_next_bus = None
            return

        # When no data recorded, don't recalculate
        if self.last_data_updated_at is None:
            return
        minutes_since_update = (self.get_now() - self.last_data_updated_at).seconds / 60
        if self.last_data_minutes_to_next_bus - minutes_since_update > 0:
            self.minutes_to_next_bus = self.last_data_minutes_to_next_bus - minutes_since_update
        else:
            self.minutes_to_next_bus = 0

    def tick(self):
        now = self.get_now()

        self.recalculate_minutes_to_next_bus()

        busInfo = NextBusInfo()
        busInfo.last_data_updated_at = self.last_data_updated_at
        busInfo.minutes_to_next_bus = self.minutes_to_next_bus
        busInfo.bus_is_coming = self.bus_is_coming
        busInfo.error_with_data = self.error_with_data

        self.get_bus_data()
        self.busInfoQueue.put(busInfo)

        self.print_next_bus()

        # Check if data should be updated
        if self.last_data_updated_at is not None:
            if (now - self.last_data_updated_at).seconds < 30:
                return

        if self.minutes_to_next_bus > 10:
            return

        if not self.bus_is_coming and self.last_data_updated_at is not None:
            if (now - self.last_data_updated_at).seconds < 1800:
                return

        # Update and handle data
        data = self.get_minutes_to_next_bus()

        if data == "No data":
            self.error_with_data = True
        elif data == "No bus":
            self.last_data_updated_at = now
            self.last_data_minutes_to_next_bus = None
            self.bus_is_coming = False
            self.error_with_data = False
        else:
            self.last_data_updated_at = now
            self.last_data_minutes_to_next_bus = data
            self.bus_is_coming = True
            self.error_with_data = False

    def run(self):
        while True:
            # tick every second
            self.tick()
            time.sleep(1)
