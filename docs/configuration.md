
The software is written to just work out of the box. By that, it pumps out metrics!

You can squeeze more juice out of the box with custom configuration explained below.

- [Custom Configuration](#custom-configuration)
  * [Custom Sensor Mappings](#custom-sensor-mappings)
  * [Timezone](#timezone)
  * [Barometer Choice](#barometer-choice)
  * [Custom Telemtry Message](#custom-telemtry-message)
  * [Callsign](#callsign)
  * [Listen Port](#listen-port)
  * [Listen Address](#listen-address)

### Custom Configuration

A custom configuration can be created at `/etc/bridge.ini` to alter the default behavior of this software.

A full sample config is below, with each setting explained in detail within each of the following sections.

```
[General]
timezone = US/Eastern
telemetry_message = N5IPT WX/digi/igate running Ecowitt Weather GW1100B_V2.0.2
listen_addr = 0.0.0.0
listen_port = 5000
callsign = N0CALL
barometer = absolute

[Sensor Mappings]
temp_sensor = temp2f
humidity_sensor = humidity2
```

*NOTE 1: All section names, for example `[General]` should only be listed once with associated settings underneath. If you have duplicate section names, things may not work as expected. Confusion may result.*

#### Custom Sensor Mappings

The software automatically uses the outdoor **temp/humidity** sensor that comes with Ecowitt Products. If this sensor is not suitable, you can buy additional WH31/WH32 sensors and configure this software to use them. You can use the sensor overview page at `http://<IP ADDRESS OF THIS SOFTWARE>:5000/sensor/overview` to discover the name of the probe and set them in the configuration file like this:

```
[Sensor Mappings]
temp_sensor = temp3f
humidity_sensor = humidity3
```

You will notice the name of the sensor corresponds with the ID typically visible on the bottom right of the temp/humidity probe's LCD screen.

For example (sensor ID's you might be interested in for your APRS WX report):

* `tempinf` or `humidityin` - the ecowitt gateway's probe "on that dangling wire"
* `tempf` or `humidity` - the outdoor probe that comes with many station units
* `temp1f` or `humidity1` - WH32 probe ID 1
* `temp2f` or `humidity2` - WH32 probe ID 2
* `temp3f` or `humidity3` - WH32 probe ID 3
* `temp4f` or `humidity4` - WH32 probe ID 4
* `temp5f` or `humidity5` - WH32 probe ID 5
* `temp6f` or `humidity6` - WH32 probe ID 6

Use the sensor overview page to identify the probe if you're having difficulty, and correlate with temp/humidify on the LCD screen for a reference value.

#### Timezone

The software actually operates in UTC for most things, but if you want to see your timezone in dashboards, etc you can set it here:

```
[General]
tmezone = US/Hawaii
```

You can find a list of available timezones in `docs/timezones.txt`

#### Barometer Choice

Ecowitt GW has two barometer metrics, relative and absolute. The default is `absolute`.

To override this, define this setting:
```
[General]
barometer = relative
```

**NOTE: `relative` and `absolute` are the only valid inputs here**

#### Custom Telemtry Message

The software doesn't send any beacon text by default; only WX telemtry. Customized beacon text is configured as follows:

```
[General]
telemetry_message = custom beacon message that directly follows WX telemtry in the APRS packet
```

#### Callsign

This setting is **NOT neccessary** if your APRS software is already configured with a valid callsign. However, some APRS stations pefer to use a abstract tactical callsign/SSID, which is USA FCC Part 97 compliant if the station transmits their callsign in the APRS message packets every 10min. In this case, it is still best radio amateur practice to beacon a callsign with as many packets as possible (so everyone can convienently identify your station.)

```
[General]
callsign = N0CALL
```

#### Listen Port

This software listens on TCP port `5000` by default. If you have a requirement to change the port, it can be customized with

```
[General]
listen_port = 8080
```

#### Listen Address

The default is to listen on all Linux/UNIX interfaces (`0.0.0.0`)

If you want to only listen on a specific network interface, you can alter this below:
```
[General]
listen_addr = 0.0.0.0
```
