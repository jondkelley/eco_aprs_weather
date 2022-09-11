"""
N5IPT; Jonathan Kelley (c) 2022 All Rights Reserved.
"""
from eco_aprs_weather import (AprsTelemetrySingleton, WxTelemetrySingleton, WeatherSingleton, ConfigurationSingleton)
from eco_aprs_weather.weathertelemfun import (update_wx_metric_into_memory, update_hourlyrainfall_into_memory)
from flask import Flask, render_template, request, make_response, url_for, send_from_directory, abort, jsonify

import argparse
import json
import dateutil.parser
import hashlib
import os
import time
import datetime, pytz
import calendar
import subprocess, shlex


#CBEACON delay=0:45 every=5:00 SENDTO=IG infocmd="echo ':WESTWD   :PARM.Cpu,Temp,FreeM,RxP,TxP'"
#CBEACON delay=0:45 every=5:00 SENDTO=IG infocmd="echo ':WESTWD   :UNIT.Load,DegC,Mb,Pkt,Pkt'"
#CBEACON delay=0:45 every=5:00 SENDTO=IG infocmd="echo ':WESTWD   :EQNS.0,1,0,0,1,0,0,1,0,0,1,0,0,1,0'"
#CBEACON delay=0:45 every=5:00 SENDTO=IG infocmd="echo T#1,1.13,54.5,52996,216,44,00000000"
# Bit Sense / Project Title
#:MYCALL   :BITS.XXXXXXXX,Project Title
# X indicates the active polarity of the corresponding b value in the telemetry packets. Thus, when b = X, the value is considered true.
# The project title may be displayed above any telemetry plot. The project title is limited to 183 bytes, with a recommended presentation length of 23 characters.
# this would filter the character length ot 23 characers (data[:19] + '...') if len(data) > 19 else data

# Telemetry Parameter Name Data
#:MYCALL   :PARM.A1,A2,A3,A4,A5,B1,B2,B3,B4,B5,B6,B7,B8
#Parameter name labels begin with "PARM." followed by 13 fields to name the five analog and eight binary fields. There is no length restriction on individual field lengths except that the total message contents (PARM., fields, and commas) may not exceed 197.

#Telemetry Unit/Label Data
#:MYCALL   :UNIT.A1,A2,A3,A4,A5,B1,B2,B3,B4,B5,B6,B7,B8
#Unit/label data begins with "UNIT." followed by 13 fields to name the units for the five analog and eight binary fields. There is no length restriction on individual field lengths except that the total message contents (UNIT., fields, and commas) may not exceed 197.

app = Flask(__name__)
telemetry = AprsTelemetrySingleton()
singleton = WxTelemetrySingleton()
wx = WeatherSingleton()
configuration = ConfigurationSingleton()

@app.errorhandler(500)
def fail(error):
    return 'ECOWITT internal server error, abort, abort!!!!!'


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

@app.route('/get/telemetry/bit/<field>', methods=['GET'])
def telemtry_bit_get(field):
    """
    gets a telemtry bit field boolean value
    useful if you want to exend some external tooling into APRS telemetry
    """
    status = {
      'value': telemetry.bool[int(field)]
    }
    return status

@app.route('/set/telemetry/bit/<field>/<value>', methods=['GET'])
def telemtry_bit_set(field, value):
    """
    sets a telemtry bit field boolean value
    useful if you want to exend some external tooling into APRS telemetry
    """
    if int(value) == telemetry.bool[int(field)]:
      drift = 'NOCHANGE'
    else:
      drift = 'CHANGED'
    if int(value)  > 1:
      raise Exception('value cannot be greater than 1')
    telemetry.bool[int(field)] = int(value)
    status = {
      'bit_status': drift,
      'value': int(value)
    }
    return status

@app.route('/telemetry/parm', methods=['GET'])
def telemtry_parm():
    return ':WESTWD   :PARM.Cpu,Temp,FreeM,RxP,TxP'

@app.route('/telemetry/unit', methods=['GET'])
def telemtry_unit():
    if configuration.call == '':
      call = 'N0CALL'
    else:
      call =configuration.call
    call = call.ljust(9)
    return f':{call}:UNIT.Load,DegC,Mb,Pkt,Pkt'

@app.route('/telemetry/eqns', methods=['GET'])
def telemtry_eqns():
    if configuration.call == '':
      call = 'N0CALL'
    else:
      call =configuration.call
    call = call.ljust(9)
    return f':{call}:EQNS.0,1,0,0,1,0,0,1,0,0,1,0,0,1,0'

def poll_aprs_telemetry():
    pass

@app.route('/telemetry/sequence', methods=['GET'])
def telemtry_seq():
    # resume sequence numbering where we left off
    if telemetry.sequence > 255:
      telemetry.sequence = 0
    seq = str(f'{telemetry.sequence:03d}')
    telemetry.sequence += 1
    # do stuff
    telem = f'{telemetry.analog[0]},{telemetry.analog[1]},{telemetry.analog[2]},{telemetry.analog[3]},{telemetry.analog[4]}'
    bits = f'{telemetry.bool[0]}{telemetry.bool[1]}{telemetry.bool[2]}{telemetry.bool[3]}{telemetry.bool[4]}{telemetry.bool[5]}{telemetry.bool[6]}{telemetry.bool[7]}'
    message = f'T#{seq},{telem},{bits}'
    return message

@app.route('/wxnow.txt', methods=['GET'])
def wxnow():
    """
    generate wxnow.txt dynamically based on latest WX data

    example direwolf config below:
        PBEACON sendto=IG delay=0:10 every=5 lat=1.000000 long=-1.000000 SYMBOL="weather station" COMMENTCMD="curl -s http://192.168.1.250:5000/wxnow.txt | tail -1"
    to igate your WX data every 5 minutes
    """
    probes = {
        'temp_outdoor': configuration.sensor_temp,
        'humidity_outdoor': configuration.sensor_humidity
    }
    try:
        winddir = singleton.weather['winddir']
    except KeyError:
        winddir = 350
    try:
        windspeedmph = singleton.weather['windspeedmph']
    except KeyError:
        windspeedmph = 0
    try:
        windgustmph = singleton.weather['windgustmph']
    except KeyError:
        windgustmph = 0
    try:
        hourlyrainin = singleton.weather['hourlyrainin']
    except KeyError:
        hourlyrainin = 0
    try:
        dailyrainin = singleton.weather['dailyrainin']
    except KeyError:
        dailyrainin = 0
    try:
        dailyrainin = singleton.weather['dailyrainin']
    except KeyError:
        dailyrainin = 0
    try:
        tempoutside = singleton.weather[probes['temp_outdoor']]
    except KeyError:
        tempoutside = 999
    try:
        tempoutside = singleton.weather[probes['temp_outdoor']]
    except KeyError:
        tempoutside = 999
    try:
        humidityoutside = singleton.weather[probes['humidity_outdoor']]
    except KeyError:
        humidityoutside = 999
    try:
        baroabs = singleton.weather[probes['baromabsin']]
    except KeyError:
        baroabs = 0
    try:
        barorel = singleton.weather[probes['baromrelin']]
    except KeyError:
        barorel = 0
    error = None
    if singleton.weather.get('dateutc'):
        now = datetime.datetime.utcnow()
        loop_dt = datetime.datetime.strptime(singleton.weather.get('dateutc'), '%Y-%m-%d+%H:%M:%S')
        elapsed = now - loop_dt
        duration_in_s = elapsed.total_seconds()
        t = int(duration_in_s)
        print(f'last report={t} seconds ago')
        if duration_in_s >= configuration.stale_threshold:
            #date = datetime.datetime.utcnow().strftime("%b %d %Y %H:%M\n")
            dateutc = singleton.weather.get('dateutc')
            error = f'[WX.Tmp.OffAir:ERROR:NODATA in since {dateutc} ({t}sec)] {configuration.status}'
            winddir = 0
            windspeedmph = 0
            windgustmph = 0
            hourlyrainin = 0
            dailyrainin = 0
            tempoutside = 999
            humidityoutside = 0
            baroabs = 0
            barorel = 0
    else:
        #date = datetime.datetime.utcnow().strftime("%b %d %Y %H:%M\n")
        error = f'[WX.Tmp.OffAir:WARN:Waiting for ECOWITT GW data stream] {configuration.status}'
        winddir = 0
        windspeedmph = 0
        windgustmph = 0
        hourlyrainin = 0
        dailyrainin = 0
        tempoutside = 999
        humidityoutside = 0
        baroabs = 0
        barorel = 0
        #return wxnow
    return generate_telemetry(error=error,winddir=winddir,windspeedmph=windspeedmph,windgustmph=windgustmph,hourlyrainin=hourlyrainin,dailyrainin=dailyrainin,temp_outdoor=tempoutside,humidity_outdoor=humidityoutside,baromabsin=baroabs,baromrelin=barorel)


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

@app.route('/data/report/', methods=['POST'])
@app.route('/data/report', methods=['POST'])
def weather_report():
    """ write WX report into memory from GW1004, GW1100B and similar devices """
    # example of what device sends: curl -d "PASSKEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX&stationtype=GW1000B_V1.5.5&dateutc=2020-01-05+02:25:46&tempinf=73.9&humidityin=42&baromrelin=2humidity1=37&temp2f=46.58&humidity2=49&soilmoisture1=93&soilmoisture2=52&batt1=0&batt2=0&soilbatt1=1.8&soilbatt2=1.7&freq=915M&model=GW1000_Pro" localhost:5001/data/report
    # example2 curl -d "PASSKEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX&stationtype=GW1000B_V1.5.5&dateutc=2020-01-05+02:25:46&tempinf=73.9&humidityin=42&baromrelin=2humidity1=37&temp2f=46.58&humidity2=49&soilmoisture1=93&soilmoisture2=52&batt1=0&batt2=0&soilbatt1=1.8&soilbatt2=1.7&freq=915M&model=GW1000_Pro&hourlyrainin=33&winddir=3&windspeedmph=3&windgustmph=3&dailyrainin=3&baromabsin=3" 192.168.1.250:5000/data/report -XPOST
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

@app.route('/version', methods=['GET'])
def version():
    return __version__


@app.route('/set/telemetry_message', methods=['GET'])
def set_telem_message():
    """will dynamically update the telemetry message broadcasted with wx beacon packet telemetry """
    args = request.args
    new_message = args.get("message", default=None, type=str)
    temporary = args.get("temporary", default=None, type=str)
    if not new_message:
      return 'error: must define `message` parameter in HTTP get request'
    configuration.status = new_message

    config['General']['telemetry_message'] = new_message
    if not temporary:
      # UNLESS temporary is defined in request, flush the config to disk too!
      with open('/etc/bridge.ini', 'w') as configfile:    # save
          config.write(configfile)
    return 'update OK'

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
    tz = pytz.timezone(configuration.timezone)
    now = datetime.datetime.now()
    localnow = now.astimezone(tz).strftime("%Y-%m-%d+%H:%M:%S")
    return render_template('sensor_overview.html', localnow=localnow, timezone=tz, weather=singleton.weather, title="Sensor Overview")

def main():
    home = os.path.expanduser("~")
    app.debug = False
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', dest='version', action='store_true', help=f'Display the app version ({__version__})')
    parser.add_argument('--kill', dest='kill', action='store_true', help=f'Kill running instances of this application')
    parser.add_argument('--screen', dest='screen', action='store_true', help=f'Fork application into screen session backround service')
    parser.add_argument('--initialsetup', dest='initialsetup', action='store_true', help=f'Run this once after installing')
    args = parser.parse_args()
    if args.version:
      print(f'version={__version__}')
      exit()
    if args.kill:
      subprocess.call(['pkill', '-9','eco_aprs_weath'])
      exit()
    if args.screen:
      print(" ☕   It takes about 30 seconds to start...")
      if not os.path.exists(f'{home}/eco-aprs-weather-start.sh'):
        cmd = f'curl -s "https://raw.githubusercontent.com/jondkelley/eco_aprs_weather/master/scripts/eco-aprs-weather-start.sh" -o "{home}/eco-aprs-weather-start.sh"'
        subprocess.call(shlex.split(cmd))
        cmd = f'chmod 755 {home}/eco-aprs-weather-start.sh'
        subprocess.call(shlex.split(cmd))
        cmd = f'bash {home}/eco-aprs-weather-start.sh'
        subprocess.call(shlex.split(cmd))
      else:
        cmd = f'bash {home}/eco-aprs-weather-start.sh'
        subprocess.call(shlex.split(cmd))
      print("\n   🌉   Ecowitt Bridge now ACTIVE")
      print("   screen -x   will attach to the Bridge webserver to view live logs")
      print("   you can type CTRL-D to detatch from the Bridge logs session at any time, or just close this terminal")
      print("   it is now safe to close your terminal. :)")
      exit()

      
    app.run(host=configuration.listen_addr, port=configuration.listen_port)

if __name__ == "__main__":
    main()