
# Example HTTP Format for Amateur Radio weather telemetry

A webserver http request should reply in plain text with two lines of data, with a return char seperating them

      Feb 01 2009 12:34
      272/010g006t069r010p030P020h61b10150
      

# Format of the file

The first line is the time the file was created in local PC time. Please note that the day of the month, the hour and the minute must be padded to two digits with zeros if needed.

The second line is the wx report, in the format used in APRS "complete weather reports". The format is:

* 272 - wind direction - 272 degrees
* 010 - wind speed - 10 mph
* g006 - wind gust - 6 mph
* t069 - temperature - 69 degrees F
* r010 - rain in last hour in hundredths of an inch - 0.1 inches
* p030 - rain in last 24 hours in hundredths of an inch - 0.3 inches (Cumulus does not supply this value)
* P020 - rain since midnight in hundredths of an inch - 0.2 inches
* h61 - humidity 61% (00 = 100%)
* b10150 - barometric pressure in tenths of a millibar - 1015.0 millibars

