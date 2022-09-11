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

      self.telemetry_project_title = config.get('Telemetry', 'project_title', fallback='Custom Telemetry')
      self.telemetry_1_label = config.get('Telemetry 1', 'label', fallback='LightningNum')
      self.telemetry_1_unit = config.get('Telemetry 1', 'unit', fallback='Ions')
      self.telemetry_1_eqns = config.get('Telemetry 1', 'eqns', fallback='0,1,0')
      self.telemetry_1_source = config.get('Telemetry 1', 'source', fallback='lightning_num')

      self.telemetry_2_label = config.get('Telemetry 2', 'label', fallback='TempIndoor')
      self.telemetry_2_unit = config.get('Telemetry 2', 'unit', fallback='TempF')
      self.telemetry_2_eqns = config.get('Telemetry 2', 'eqns', fallback='0,1,0')
      self.telemetry_2_source = config.get('Telemetry 2', 'source', fallback='temp2f')

      self.telemetry_3_label = config.get('Telemetry 3', 'label', fallback='')
      self.telemetry_3_unit = config.get('Telemetry 3', 'unit', fallback='')
      self.telemetry_3_eqns = config.get('Telemetry 3', 'eqns', fallback='0,1,0')
      self.telemetry_3_source = config.get('Telemetry 3', 'source', fallback='')

      self.telemetry_4_label = config.get('Telemetry 4', 'label', fallback='')
      self.telemetry_4_unit = config.get('Telemetry 4', 'unit', fallback='')
      self.telemetry_4_eqns = config.get('Telemetry 4', 'eqns', fallback='0,1,0')
      self.telemetry_4_source = config.get('Telemetry 4', 'source', fallback='')

      self.telemetry_5_label = config.get('Telemetry 5', 'label', fallback='')
      self.telemetry_5_unit = config.get('Telemetry 5', 'unit', fallback='')
      self.telemetry_5_eqns = config.get('Telemetry 5', 'eqns', fallback='0,1,0')
      self.telemetry_5_source = config.get('Telemetry 5', 'source', fallback='')

      self.telemetry_bit_0_default = config.get('Telemetry Bitwise', 'bit0_default_value', fallback='')
      self.telemetry_bit_0_label = config.get('Telemetry Bitwise', 'bit0_label', fallback='')
      self.telemetry_bit_1_default = config.get('Telemetry Bitwise', 'bit1_default_value', fallback='')
      self.telemetry_bit_1_label = config.get('Telemetry Bitwise', 'bit1_label', fallback='')
      self.telemetry_bit_2_default = config.get('Telemetry Bitwise', 'bit2_default_value', fallback='')
      self.telemetry_bit_2_label = config.get('Telemetry Bitwise', 'bit2_label', fallback='')
      self.telemetry_bit_3_default = config.get('Telemetry Bitwise', 'bit3_default_value', fallback='')
      self.telemetry_bit_3_label = config.get('Telemetry Bitwise', 'bit3_label', fallback='')
      self.telemetry_bit_4_default = config.get('Telemetry Bitwise', 'bit4_default_value', fallback='')
      self.telemetry_bit_4_label = config.get('Telemetry Bitwise', 'bit4_label', fallback='')
      self.telemetry_bit_5_default = config.get('Telemetry Bitwise', 'bit5_default_value', fallback='')
      self.telemetry_bit_5_label = config.get('Telemetry Bitwise', 'bit5_label', fallback='')
      self.telemetry_bit_6_default = config.get('Telemetry Bitwise', 'bit6_default_value', fallback='')
      self.telemetry_bit_6_label = config.get('Telemetry Bitwise', 'bit6_label', fallback='')
      self.telemetry_bit_7_default = config.get('Telemetry Bitwise', 'bit7_default_value', fallback='')
      self.telemetry_bit_7_label = config.get('Telemetry Bitwise', 'bit7_label', fallback='')
   def __new__(cls):
      if not hasattr(cls, 'instance'):
         cls.instance = super(ConfigurationSingleton, cls).__new__(cls)
      return cls.instance


class AprsTelemetrySingleton(object):
   def __init__(self):
      # used for iterative telemetry sequence order numbering
      self.sequence = 0
      self.analog = {
        0: '0',
        1: '0',
        2: '0',
        3: '0',
        4: '0'
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
