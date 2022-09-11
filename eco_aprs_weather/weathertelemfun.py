"""
N5IPT; Jonathan Kelley (c) 2022 All Rights Reserved.
"""

from eco_aprs_weather import (AprsTelemetrySingleton, WxTelemetrySingleton, WeatherSingleton, ConfigurationSingleton)
import datetime

telemetry = AprsTelemetrySingleton()
singleton = WxTelemetrySingleton()
wx = WeatherSingleton()
configuration = ConfigurationSingleton()

def update_wx_metric_into_memory(post_dict):
   """ constantly updates a table in memory with last metric totals at top of the hour """
   # unused? utcminute = ":".join(post_dict['dateutc'].split('+')[1].split(':')[:-1])
   utcday = post_dict['dateutc'].split('+')[0]
   RUN_EVERY_MINUTE = False
   if datetime.datetime.utcnow().minute in {5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 0} or RUN_EVERY_MINUTE:
      #datetime.datetime.strptime(post_dict['dateutc'], '%Y-%m-%d+%H:%M:%S').
      post_dict = post_dict.copy()
      del post_dict['PASSKEY']
      del post_dict['stationtype']
      del post_dict['model']
      del post_dict['freq']
      todelete = []
      for key in post_dict:
         if 'batt' in key:
            todelete.append(key)
      for key in todelete:
            del post_dict[key]
      todelete = []
      for key in post_dict:
         if 'rain' in key:
            todelete.append(key)
      for key in todelete:
            del post_dict[key]

      if utcday in wx.metrics:
         wx.metrics[utcday][datetime.datetime.utcnow().strftime("%H:%M")] = post_dict
      else:
         wx.metrics[utcday] = {}
         wx.metrics[utcday][datetime.datetime.utcnow().strftime("%H:%M")] = post_dict

def update_hourlyrainfall_into_memory(post_dict):
   """ constantly updates a table in memory with latest hourly rainfall totals """
   utchour = post_dict['dateutc'].split('+')[1].split(':')[:-2][0]
   utcday = post_dict['dateutc'].split('+')[0]
   print(wx.hourlyrainfall)
   if utcday in wx.hourlyrainfall:
      try:
          wx.hourlyrainfall[utcday][utchour] = post_dict['hourlyrainin']
      except:
          wx.hourlyrainfall[utcday][utchour] = 0
   else:
      try:
          wx.hourlyrainfall[utcday] = {}
          wx.hourlyrainfall[utcday][utchour] = post_dict['hourlyrainin']
      except:
          wx.hourlyrainfall[utcday][utchour] = 0
