"""
N5IPT; Jonathan Kelley (c) 2022 All Rights Reserved.

Store singleton objects here
"""

import configparser


config = configparser.ConfigParser()
config.read('/etc/bridge.ini')
class ConfigurationSingleton(object):
   def __init__(self):
      self.status = config.get('General', 'telemetry_message', fallback='')
      if not config.get('General', 'disable_telemetry_message_footer', fallback=False) and self.status != '': 
        self.status = self.status + ' {ECOWITT}'
      self.timezone = config.get('General', 'timezone', fallback='UTC')
      self.call = config.get('General', 'callsign', fallback='')
      self.listen_port = int(config.get('General', 'listen_port', fallback=5000))
      self.listen_addr = config.get('General', 'listen_port', fallback='0.0.0.0')
      self.stale_threshold = int(config.get('General', 'stale_data_shutdown_threshold_seconds', fallback=60))
      self.sensor_temp = config.get('Sensor Mappings', 'temp_sensor', fallback='tempf')
      self.sensor_humidity = config.get('Sensor Mappings', 'humidity_sensor', fallback='humidity')
      self.barometer = config.get('Sensor Mappings', 'barometer', fallback='absolute')
      self.max_days_telemetry_stored = config.get('Misc', 'max_days_telemetry_stored', fallback=200)
   def __new__(cls):
      if not hasattr(cls, 'instance'):
         cls.instance = super(ConfigurationSingleton, cls).__new__(cls)
      return cls.instance


class AprsTelemetrySingleton(object):
   def __init__(self):
      # used for iterative telemetry sequence order numbering
      self.sequence = 0
      self.analog = {
        0: 0,
        1: 0,
        2: 0,
        3: 0,
        4: 0
      }
      self.bool = {
        0: 0,
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0,
        7: 0,
        8: 0
      }
   def __new__(cls):
      if not hasattr(cls, 'instance'):
         cls.instance = super(AprsTelemetrySingleton, cls).__new__(cls)
      return cls.instance

class WxTelemetrySingleton(object):
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
         cls.instance = super(WxTelemetrySingleton, cls).__new__(cls)
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
