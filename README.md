# eco_aprs_weather

The Eco_APRS_Weather bridge software exists to allow Ecowitt Weather Stations to work with APRS software for amateur radio. This software integrates directly with your weather station after changing some settings, and can integrate directly with software like Direwolf using the `wxnow.txt` amateur radio weather telemetry format.

### Supported Weather Station devices

This software is designed for Ecowitt Weather stations of the following models:

* GW1004
* GW1100
* GW1102 

Other models may be supported as long as the device can output HTTP in "Ecowitt" station format. See the *Ecowitt Setup* section for details.

### Software Requirements

A computer with Python 3.2 or greater.

This software can be hosted on a Raspberry Pi alongside the Direwolf install. It is rather lightweight.

* Memory: 2 GB minimum RAM suggested
* CPU: Whatever works!


### Install Directions

This software can be installed by PIP

```
todo
````

### Ecowitt WX Station Configuration

Once you have the service started for `Eco_APRS_Weather` you need to determine the IP address of your PC.
The IP address will be used to point your weather station reports to it.

Within your Ecowitt phone app:

1. Click the elipsis (`...`) symbol in the top right (of the screen showing your WX station live metrics)
2. In dropdown, select "Others"
3. In the "Edit Gateway" screen click "DIY Upload Servers" button
4. In the "DIY Upload Servers" screen click "Customized" (Globe Icon)
   * In the `"Server / Host Name"` field enter the IP address of the computer running this software
   * In the `"Port"` field make sure it is `"5000"`
   * In the `"Upload Interval"` field select the fastest interval
   * Click save.
5. Hit `<` (top right) to return to previous screens
6. WX station should start sending metrics to the bridge in the next few minutes!

### Software Configuration

This software configuration file is located at `/etc/bridge.ini` and can be used to customize the WX bridge behavior.

A sample config is below, with each setting explained in detail within the following sections.

```
[General]
status_message=N5IPT WX/digi/igate running Ecowitt Weather GW1100B_V2.0.2

[Sensor Mappings]
temp_sensor=temp2f
humidity_sensor=humidity2
```

#### Custom Sensor Mappings

The software automatically uses the outdoor **temp/humidity** sensor that comes with Ecowitt Products. If this sensor is not suitable, you can buy additional WH31/WH32 sensors and configure this software to use them. You can use the sensor overview page at `http://<IP ADDRESS OF THIS SOFTWARE>:5000/sensor/overview` to discover the name of the probe and set them in the configuration file like this:

```
[Sensor Mappings]
temp_sensor=temp3f
humidity_sensor=humidity3
```

You will notice the name of the sensor corresponds with the ID typically screen on the bottom right of the probe LCD screen.

For example:

* `tempinf` or `humidityin` - the ecowitt gateway's probes
* `tempf` or `humidity` - the outdoor probe that comes with many station units
* `temp1f` or `humidity1` - WH32 probe ID 1
* `temp2f` or `humidity2` - WH32 probe ID 2
* `temp3f` or `humidity3` - WH32 probe ID 3
* `temp4f` or `humidity4` - WH32 probe ID 4
* `temp5f` or `humidity5` - WH32 probe ID 5
* `temp6f` or `humidity6` - WH32 probe ID 6

#### Custom Beacon Message

The software doesn't send any beacon text by default; only WX telemtry. Customized beacon text is configured as follows:

```
[General]
status_message=custom beacon message that directly follows WX telemtry in the APRS packet
```

#### To confirm weather station telemtry is being recieved by the bridge

Visit `http://<IP ADDRESS OF THIS SOFTWARE>:5000/sensor/overview` and verify you have station data coming in.

You may have to wait 5-10 minutes and refresh this page periodically, sometimes it takes a while for Ecowitt device settings to take effect.

If you do not see station data, possible solutions involve:

* Check the Ecowitt WX Station configuration settings
* Ensure the path field says exactly "data/report"
* Ensure the computer running this software does not have any sort of Firewall enabled
* Verifying your network configuration and trying again
