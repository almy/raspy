import os
import pygame
import time
import pywapi
from pitft import PiTFT
from pynrk import YR

# Weather Icons used with the following permissions:
#
# VClouds Weather Icons
# Created and copyrighted by VClouds - http://vclouds.deviantart.com/
#
# The icons are free to use for Non-Commercial use, but If you use want to use it with your art
# please credit me and put a link leading back to the icons DA page - http://vclouds.deviantart.com/gallery/#/d2ynulp
#
# *** Not to be used for commercial use without permission!
# if you want to buy the icons for commercial use please send me a note - http://vclouds.deviantart.com/ ***
print os.getcwd()
installPath = "images/"

# location for Lincoln, UK on weather.com
weatherDotComLocationCode = 'HKXX0049'
# convert mph = kpd / kphToMph
kphToMph = 1.60934400061

# font colours
colourWhite = (255, 255, 255)
colourBlack = (0, 0, 0)


# update interval
updateRate = 60  # seconds

# Create an instance of the PyScope class
mytft = PiTFT()

pygame.mouse.set_visible(False)

# set up the fonts
# choose the font
fontpath = pygame.font.match_font('dejavusansmono')
# set up 2 sizes
font = pygame.font.Font(fontpath, 20)
fontSm = pygame.font.Font(fontpath, 18)


def main():
            while True:
                # retrieve data from weather.com
                weather_com_result = pywapi.get_weather_from_weather_com(weatherDotComLocationCode)
                weather = YR("Sweden/Stockholm/Stockholm/", "2015-12-01")

                # extract current data for today
                today = weather_com_result['forecasts'][0]['day_of_week'][0:3] + " " \
                    + weather_com_result['forecasts'][0]['date'][4:] + " " \
                    + weather_com_result['forecasts'][0]['date'][:3]
                windSpeed = int(weather_com_result['current_conditions']['wind']['speed']) / kphToMph
                currWind = "{:.0f}mph ".format(windSpeed) + weather_com_result['current_conditions']['wind']['text']
                currTemp = weather_com_result['current_conditions']['temperature'] + u'\N{DEGREE SIGN}' + "C"
                currPress = weather_com_result['current_conditions']['barometer']['reading'][:-3] + "mb"
                uv = "UV {}".format(weather_com_result['current_conditions']['uv']['text'])
                humid = "Hum {}%".format(weather_com_result['current_conditions']['humidity'])
                city = weather_com_result['location']['name']

                # extract forecast data
                forecastDays = {}
                forecaseHighs = {}
                forecaseLows = {}
                forecastPrecips = {}
                forecastWinds = {}

                start = 0
                try:
                    test = float(weather_com_result['forecasts'][0]['day']['wind']['speed'])
                except ValueError:
                    start = 1

                for i in range(start, 5):

                    if not(weather_com_result['forecasts'][i]):
                        break
                    forecastDays[i] = weather_com_result['forecasts'][i]['day_of_week'][0:3]
                    forecaseHighs[i] = weather_com_result['forecasts'][i]['high'] + u'\N{DEGREE SIGN}' + "C"
                    forecaseLows[i] = weather_com_result['forecasts'][i]['low'] + u'\N{DEGREE SIGN}' + "C"
                    forecastPrecips[i] = weather_com_result['forecasts'][i]['day']['chance_precip'] + "%"
                    forecastWinds[i] = "{:.0f}".format(int(weather_com_result['forecasts'][i]['day']['wind']['speed'])  / kphToMph) + \
                        weather_com_result['forecasts'][i]['day']['wind']['text']

                # blank the screen
                mytft.screen.fill(colourBlack)

                # Render the weather logo at 0,0
                icon = installPath + (weather_com_result['current_conditions']['icon']) + ".png"
                logo = pygame.image.load(icon).convert()
                mytft.screen.blit(logo, (0, 0))

                # set the anchor for the current weather data text
                textAnchorX = 140
                textanchory = 5
                textYoffset = 20

                # add current weather data text artifacts to the screen
                text_surface = font.render(city, True, colourWhite)
                mytft.screen.blit(text_surface, (textAnchorX, textanchory))
                textanchory+=textYoffset
                text_surface = font.render(today, True, colourWhite)
                mytft.screen.blit(text_surface, (textAnchorX, textanchory))
                textanchory+=textYoffset
                text_surface = font.render(currTemp, True, colourWhite)
                mytft.screen.blit(text_surface, (textAnchorX, textanchory))
                textanchory+=textYoffset
                text_surface = font.render(currWind, True, colourWhite)
                mytft.screen.blit(text_surface, (textAnchorX, textanchory))
                textanchory+=textYoffset
                # text_surface = font.render(currPress, True, colourWhite)
                # mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                # textAnchorY+=textYoffset
                text_surface = font.render(uv, True, colourWhite)
                mytft.screen.blit(text_surface, (textAnchorX, textanchory))
                textanchory+=textYoffset
                text_surface = font.render(humid, True, colourWhite)
                mytft.screen.blit(text_surface, (textAnchorX, textanchory))

                # set X axis text anchor for the forecast text
                textAnchorX = 0
                textXoffset = 65

                # add each days forecast text
                for data in weather.weather.forecastmodel:
                    textanchory = 130
                    text_surface = fontSm.render(data.start_time, True, colourWhite)
                    mytft.screen.blit(text_surface, (textAnchorX, textanchory))
                    textanchory+=textYoffset
                # refresh the screen with all the changes
                pygame.display.update()

                # Wait
                time.sleep(updateRate)

if __name__ == '__main__':
    main()
