"""
N5IPT; Jonathan Kelley (c) 2022 All Rights Reserved.

file for helper functions that support generation of wxnow.tx or
accept telemetry from the ECOWITT device
"""

from eco_aprs_weather import (AprsTelemetrySingleton, WxTelemetrySingleton, WeatherSingleton, ConfigurationSingleton)
import datetime

telemetry = AprsTelemetrySingleton()
singleton = WxTelemetrySingleton()
wx = WeatherSingleton()
configuration = ConfigurationSingleton()


def calculate_24hour_rainfall():
   """
   calculates rainfall within the past 24 hours since ecowitt devices only transmit the "last day" metric
   """
   total_rainfall = 0
   now = datetime.datetime.utcnow()
   for day, v in wx.hourlyrainfall.items(): 
      for hour, rainfall in v.items():
         time = f'{day}+{hour}:00:00'
         loop_dt = datetime.datetime.strptime(time, '%Y-%m-%d+%H:%M:%S')
         elapsed = now - loop_dt
         seconds_in_a_day = 24 * 60 * 60
         duration_in_s = elapsed.total_seconds()
         if duration_in_s <= seconds_in_a_day:
            total_rainfall = total_rainfall + float(rainfall)
   return total_rainfall


def generate_telemetry(error,winddir,windspeedmph,windgustmph,hourlyrainin,dailyrainin,temp_outdoor,humidity_outdoor,baromabsin,baromrelin):
    callsign = f'{configuration.call} '
    if configuration.barometer == 'absolute':
        barometer = baromabsin
    elif configuration.barometer == 'relative':
        barometer = baromrelin
    else:
        raise("Configuration error section General, key barometer Error! value must be only `absolute` or `relative`")
        exit()
    dt = datetime.datetime.utcnow()
    fields = []
    fields.append("%03d" % int(winddir)) # wind dir
    fields.append("/%03d" % int(float(windspeedmph))) # wind speed
    fields.append("g%03d" % int(float(windgustmph))) # gust
    fields.append("t%03d" % int(float(temp_outdoor)))
    fields.append("r%03d" % int(float(hourlyrainin) * 100)) # hour rain
    fields.append("p%03d" % int(calculate_24hour_rainfall() * 100)) # rain 24
    fields.append("P%03d" % int(float(dailyrainin)* 100)) # day rain
    if int(humidity_outdoor) < 0 or 100 <= int(humidity_outdoor):
        humidity_outdoor = 0
    fields.append("h%03d" % (int(humidity_outdoor)))
    #fields.append("b%05d" % int(float(float(singleton.weather['baromabsin']) * 33.864 * float(10)))) # barometer
    fields.append("b%05d" % int(float(float(barometer) * 33.864 * float(10)))) # barometer
    date = dt.strftime("%b %d %Y %H:%M\n")
    if error:
      message = error
    else:
      message = configuration.status
    wxnow = date + ''.join(fields) + f'{callsign}{message}\n'
    return wxnow


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
