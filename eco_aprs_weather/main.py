"""
N5IPT (c) 2022 All Rights Reserved.
License: Re-Distribution of this code is forbidden beyond sharing this link. Including, sharing, selling, packaging or dispensing this code for profit in any manner is strictly forbidden.
-
This is a python webserver is used to recieve weather data over HTTP from my
   ECOWITT GW1102 Home Weather Station (i know for a fact should be compatible with GW1004 gateway and maybe similar gateways)
and transmit the data over HTTP to my Direwolf APRS station
this is in very early stages of development but I plan to throw better documentation together soon!
keep an eye on this igate for announcements when you can build your own!
thanks to N5AMD to donating the hardware (Radio, Rasberry Pi 1 (rev 2011.12) for this project, without this the code would never have been written
"""
from flask import Flask, render_template, request, make_response, url_for, send_from_directory, abort, jsonify
import json
import dateutil.parser
import hashlib
import os
import time
import datetime
import configparser
import calendar

app = Flask(__name__)
config = configparser.ConfigParser()
config.read('/etc/bridge.ini')
class Configuration(object):
   def __init__(self):
      self.status = config.get('General', 'telemetry_message', fallback='')
      self.sensor_temp = config.get('Sensor Mappings', 'temp_sensor', fallback='tempinf')
      self.sensor_humidity = config.get('Sensor Mappings', 'humidity_sensor', fallback='humidityin')
      self.max_days_telemetry_stored = config.get('Misc', 'max_days_telemetry_stored', fallback=200)
   def __new__(cls):
      if not hasattr(cls, 'instance'):
         cls.instance = super(Configuration, cls).__new__(cls)
      return cls.instance

class TelemetrySingleton(object):
   """
   this singleton stores a snapshot of the latest telemetry packet in memory
   """
   def __init__(self):
      self.weather = {
         "dailyrainin": None,
         "monthlyrainin": None,
         "yearlyrainin": None,
         "eventrainin": None,
         "weeklyrainin": None
        }
   def __new__(cls):
      if not hasattr(cls, 'instance'):
         cls.instance = super(TelemetrySingleton, cls).__new__(cls)
      return cls.instance

class WeatherSingleton(object):
   """
   this singleton stores working memory of station telemetry over period of time
   """
   def __init__(self):
      self.hourlyrainfall = {}
      self.metrics = {}
   def __new__(cls):
      if not hasattr(cls, 'instance'):
         cls.instance = super(WeatherSingleton, cls).__new__(cls)
      return cls.instance

singleton = TelemetrySingleton()
wx = WeatherSingleton()
configuration = Configuration()
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

def generate_telemetry(winddir,windspeedmph,windgustmph,hourlyrainin,dailyrainin,temp_outdoor,humidity_outdoor,baromabsin):
    dt = datetime.datetime.utcnow()
    fields = []
    fields.append("%03d" % int(winddir)) # wind dir
    fields.append("/%03d" % int(float(windspeedmph))) # wind speed
    fields.append("g%03d" % int(float(windgustmph))) # gust
    #fields.append("t%03d" % int(float(singleton.weather[probes['temp_outdoor']])))
    fields.append("t%03d" % int(float(temp_outdoor)))
    fields.append("r%03d" % int(float(hourlyrainin) * 100)) # hour rain
    fields.append("p%03d" % int(calculate_24hour_rainfall() * 100)) # rain 24
    fields.append("P%03d" % int(float(dailyrainin)* 100)) # day rain
    if int(humidity_outdoor) < 0 or 100 <= int(humidity_outdoor):
        humidity_outdoor = 0
    #fields.append("h%03d" % int(singleton.weather[probes['humidity_outdoor']]))
    fields.append("h%03d" % (int(humidity_outdoor) + int(2)))
    #fields.append("b%05d" % int(float(float(singleton.weather['baromabsin']) * 33.864 * float(10)))) # barometer
    fields.append("b%05d" % int(float(float(baromabsin) * 33.864 * float(10) + float(29)))) # barometer
    date = dt.strftime("%b %d %Y %H:%M\n")
    wxnow = date + ''.join(fields) + f'{configuration.status}\n'
    return wxnow

@app.route('/wxnow.txt', methods=['GET'])
def wxnow():
    """
    generate wxnow.txt dynamically based on latest WX data

    example direwolf config below:
        PBEACON sendto=IG delay=0:10 every=5 lat=1.000000 long=-1.000000 SYMBOL="weather station" COMMENTCMD="curl -s http://192.168.1.250:5000/wxnow.txt | tail -1"
    to igate your WX data every 5 minutes
    """
    probes = {
        'temp_outdoor': 'temp2f',
        'humidity_outdoor': 'humidity2'
    }
    try:
      return generate_telemetry(winddir=singleton.weather['winddir'],windspeedmph=singleton.weather['windspeedmph'],windgustmph=singleton.weather['windgustmph'],hourlyrainin=singleton.weather['hourlyrainin'],dailyrainin=singleton.weather['dailyrainin'],temp_outdoor=singleton.weather[probes['temp_outdoor']],humidity_outdoor=singleton.weather[probes['humidity_outdoor']],baromabsin=singleton.weather['baromabsin'])
    except KeyError:
      date = datetime.datetime.utcnow().strftime("%b %d %Y %H:%M\n")
      # TODO add a ECOWITT GATEWAY OFFLINE message if no recent telemetry is uploaded in 1 hour
      wxnow = date + 'note: ecowitt weather bridge is running but no data from ecowitt gateway\n'
      return wxnow

@app.route('/data/metrics.json', methods=['GET'])
@app.route('/data/metric.json', methods=['GET'])
def query_metrics():
   """
   returns metrics record in memory
   """
   out = {
      "metrics": wx.metrics
   }
   return json.dumps(out, indent=3)

@app.route('/data/rain.json', methods=['GET'])
def query_rainfall():
   """
   returns rainfall record in memory
   """
   out = {
      "rainfall": {
         "hourly_telemetry": wx.hourlyrainfall,
         "summary": {
            "daily_inches": singleton.weather['dailyrainin'],
            "weekly_inches": singleton.weather['weeklyrainin'],
            "monthly_inches": singleton.weather['monthlyrainin'],
            "yearly_inches": singleton.weather['yearlyrainin'],
            "event": singleton.weather['eventrainin']
         }
      }
   }
   return json.dumps(out, indent=3)

@app.route('/retention_management/rain', methods=['GET'])
def purge_old_rainfall():
   """
   purges rainfall record in memory to keep stack under control
   returns the number of records purged
   """
   now = datetime.datetime.utcnow()
   keys_to_remove = []
   number_keys_to_remove = 0
   for day in wx.hourlyrainfall:
      loop_dt = datetime.datetime.strptime(day, '%Y-%m-%d')
      elapsed = now - loop_dt
      duration_in_d = elapsed.days
      if duration_in_d > args.get("max_days", default=int(configuration.max_days_telemetry_stored), type=int): # that is about 30,000 metrics (7*24*180)
         keys_to_remove.append(day)
         number_keys_to_remove += 1

   for key in keys_to_remove:
      del wx.hourlyrainfall[key]
   return json.dumps({'number_days_purged': number_keys_to_remove, "days_purged": keys_to_remove})

@app.route('/retention_management/metrics', methods=['GET'])
def purge_old_metics():
   """
   purges rainfall record in memory to keep stack under control
   returns the number of records purged
   """
   now = datetime.datetime.utcnow()
   keys_to_remove = []
   number_keys_to_remove = 0
   for day in wx.metrics:
      loop_dt = datetime.datetime.strptime(day, '%Y-%m-%d')
      elapsed = now - loop_dt
      duration_in_d = elapsed.days
      if duration_in_d > args.get("max_days", default=int(configuration.max_days_telemetry_stored), type=int):
         keys_to_remove.append(day)
         number_keys_to_remove += 1

   for key in keys_to_remove:
      del wx.metrics[key]
   return json.dumps({'number_days_purged': number_keys_to_remove, "days_purged": keys_to_remove})

@app.route('/data/report/', methods=['GET'])
@app.route('/data/report', methods=['GET'])
def weather_query():
    """ read the last raw weather report out of memory """
    return singleton.weather

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

@app.route('/data/report/', methods=['POST'])
@app.route('/data/report', methods=['POST'])
def weather_report():
    """ write WX report into memory from GW1004, GW1100B and similar devices """
    # example of what device sends: curl -d "PASSKEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX&stationtype=GW1000B_V1.5.5&dateutc=2020-01-05+02:25:46&tempinf=73.9&humidityin=42&baromrelin=2humidity1=37&temp2f=46.58&humidity2=49&soilmoisture1=93&soilmoisture2=52&batt1=0&batt2=0&soilbatt1=1.8&soilbatt2=1.7&freq=915M&model=GW1000_Pro" localhost:5001/data/report
    if request.get_data().decode("utf-8") == '':
        print('/data/report recieved a zero payload input')
        return "Must send a POST payload", 400
    post_dict = dict()
    try:
        post_string = request.get_data().decode("utf-8").split('&')
    except Exception as e:
        print(f'Recieved a malformed POST ({e}) when splitting & into a key')
        return 'Malformed POST data', 400
    for kv in post_string:
        try:
            key = kv.split('=')[0]
        except IndexError as e:
            print(f'/data/report recieved a malformed POST ({e}) when splitting = into a key')
            return 'Malformed POST data', 400
        try:
            val = kv.split('=')[1]
        except IndexError as e:
            print(f'/data/report recieved a malformed POST ({e}) when splitting = into a value')
            return 'Malformed POST data', 400
        post_dict[key] = val
    singleton.weather = post_dict
    update_wx_metric_into_memory(post_dict)
    update_hourlyrainfall_into_memory(post_dict)
    print(wx.hourlyrainfall)
    return 'OK; Telemetry Accepted'

@app.route('/', methods=['GET'])
def about():
    """ read the last raw weather report out of memory """
    out = {
      "author": {
         "callsign": "N5IPT",
         "name": "Jonathan Kelley",
         "email": "jonk@omg.lol"
      },
      "copyright": {
         "author": "Jonathan Kelley",
         "year": "2022",
         "comment": "All Rights Reserved"
      },
      "about": {
         "tagline": "you know, for getting weather stations on to APRS"
      }
    }
    return out

@app.route('/graph/metric/<metric>', methods=['GET'])
def metrics(metric):
    output = list()
    xdata = []
    ydata = []
    for day, v in wx.metrics.items():
        for hour, item in v.items():
            dtstr = f'{day}+{hour}'
            dt = datetime.datetime.strptime(dtstr, '%Y-%m-%d+%H:%M')
            epoch = calendar.timegm(dt.timetuple())
            try:
                #output.append([epoch, float(item[metric])])
                xdata.append(epoch)
                ydata.append(float(item[metric]))
            except ValueError:
                #output.append([epoch, float(item[metric])])
                xdata.append(epoch)
                ydata.append(float(item[metric]))

    from nvd3 import cumulativeLineChart
    chart = cumulativeLineChart(name='cumulativeLineChart', x_is_date=True)
    #xdata = [1365026400000, 1365026500000, 1365026600000]
    #ydata = [6, 5, 1]
    #y2data = [36, 55, 11]

    extra_serie = {"tooltip": {"y_start": "There are ", "y_end": " calls"}}
    chart.add_serie(name="Serie 1", y=ydata, x=xdata, extra=extra_serie)

    #extra_serie = {"tooltip": {"y_start": "", "y_end": " mins"}}
    #chart.add_serie(name="Serie 2", y=y2data, x=xdata, extra=extra_serie)
    chart.buildhtml()
    return chart
    #return jsonify(output)

pairs_list = []
@app.route('/sensor/overview')
def index():
    return render_template('sensor_overview.html', weather=singleton.weather, title="Sensor Overview")

def main():
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=5000)