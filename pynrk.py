__author__ = 'user'

import urllib2
import threading
from xml.etree import ElementTree
from weathermodel import WeatherModel
from forecastmodel import ForeceastModel
import dateutil.parser
import time


class YR(threading.Thread):

    global yr_base_url
    global yr_end_url
    global yr_geoname
    global yr_date

    def __init__(self, geoname, date, weatherInfoQue):
        super(YR, self).__init__()
        self.yr_base_url = "http://www.yr.no/place/"
        self.yr_end_url  = "/forecast.xml"
        self.yr_geoname = geoname
        self.yr_date = date
        self.weatherInfoQue = weatherInfoQue

    # Returns an array of weather maps
    def get_weather(self, url, date):
        p = urllib2.urlopen(url).read()
        return self.parse_xml(p, date)


    def parse_xml(self, data, date):
        tree = ElementTree.fromstring(data)
        forecast_elem = tree.find("forecast")
        tabular_elem = forecast_elem.find("tabular")
        weathermodel = WeatherModel()
        weathermodel.sun_rise = tree.find("sun").attrib["rise"]
        weathermodel.sun_set = tree.find("sun").attrib["set"]

        for forecast in tabular_elem:
            startDate = dateutil.parser.parse(forecast.attrib["from"]).date()
            fixedDate = dateutil.parser.parse(date).date()
            if startDate == fixedDate:
                forecastModel = ForeceastModel()
                forecastModel.start_time = dateutil.parser.parse(forecast.attrib["from"]).time()
                forecastModel.end_time = dateutil.parser.parse(forecast.attrib["to"]).time()
                forecastModel.period_time = forecast.attrib["period"]
                forecastModel.weather_symbol = forecast.find("symbol").attrib
                forecastModel.precipitation = forecast.find("precipitation").attrib
                forecastModel.temperature = forecast.find("temperature").attrib
                forecastModel.pressure = forecast.find("pressure").attrib
                forecastModel.wind_direction = forecast.find("windDirection").attrib
                forecastModel.wind_speed = forecast.find("windSpeed").attrib
                weathermodel.forecastmodel.append(forecastModel)
        return weathermodel

    def run(self):
        while True:
            weather = self.get_weather(self.yr_base_url+self.yr_geoname+self.yr_end_url, self.yr_date)
            self.weatherInfoQue.queue.clear()
            self.weatherInfoQue.put(weather)
            time.sleep(360)
