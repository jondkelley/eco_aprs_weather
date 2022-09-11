from os import environ
from eco_aprs_weather.singleton import (AprsTelemetrySingleton, WxTelemetrySingleton, WeatherSingleton, ConfigurationSingleton)

__version__ = environ.get('APP_VERSION', '1.0.1')

telemetry = AprsTelemetrySingleton()
singleton = WxTelemetrySingleton()
wx = WeatherSingleton()
configuration = ConfigurationSingleton()
