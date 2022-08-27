# eco_aprs_weather

The Eco_APRS_Weather bridge software exists to allow Ecowitt Weather Stations to work with APRS software for amateur radio. This software integrates directly with your Ecowitt brand weather station after changing the app settings. You basically run this software in your network, it sits and collects various metrics from you WX Station. Periodically your APRS software can collect data from this software in `wxnow.txt` format. The `wxnow.txt` format is used by popular APRS software to send radio weather telemetry packets.

Are you interested?

### Supported Weather Station devices

This software should work with Ecowitt Weather station gateways models like:

* GW1004
* GW1100
* GW1102 

Other models may be supported as long as the device settings can output customized HTTP in "Ecowitt" station format. See the *Ecowitt App Configuration* section for configuration details in the Ecowitt phone app!

### Software Requirements

* Python 3.2 or greater.
* Memory: 1 GB minimum RAM suggested

This software works great on a Raspberry Pi along with the Direwolf Sofwarre TNC.

### Install Directions

#### Using Python / Pip

This software can be installed by Python Pip.

Make sure you have python and pip installed by running:

```
python3 --version
pip3 --version
```

If you're missing these, you'll need to install python, and python-pip.
If these commands worked, install eco_aprs_weather with:
```
sudo pip3 install eco_aprs_weather
````

### Starting the `eco_aprs_weather` service

```
todo
````

### Ecowitt App Configuration

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

### Advanced Software Configuration

A custom configuration can be created at `/etc/bridge.ini` to alter the default behavior of this software.

A full sample config is below, with each setting explained in detail within each of the following sections.

```
[General]
telemetry_message=N5IPT WX/digi/igate running Ecowitt Weather GW1100B_V2.0.2
listen_port=5000

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

#### Custom Telemtry Message

The software doesn't send any beacon text by default; only WX telemtry. Customized beacon text is configured as follows:

```
[General]
telemetry_message=custom beacon message that directly follows WX telemtry in the APRS packet
```

#### Listen Port

This software listens on TCP port `5000` by default. If you have a requirement to change the port, it can be customized with

```
[General]
listen_port=8080
```

### To confirm weather station telemtry is being recieved by the bridge

Visit `http://<IP ADDRESS OF THIS SOFTWARE>:5000/sensor/overview` and verify you have station data coming in.

You may have to wait 5-10 minutes and refresh this page periodically, sometimes it takes a while for Ecowitt device settings to take effect.

If you do not see station data, possible solutions involve:

* Check the Ecowitt WX Station configuration settings
* Ensure the path field says exactly "data/report", other values don't work.
* Ensure the computer running this software does not have any sort of Firewall enabled
* Verifying your network configuration and trying again


### Configuring your APRS software to send WX [Weather] Beacons!

This is the tricky part. This bridge supports any APRS software that accepts `wxnow.txt` weather format in Cumulus weather format.

My only experience is with [Direwolf](https://github.com/wb2osz/direwolf), the modern software replacement for the old 1980's style TNC.

#### Configuring Direwolf

First thing, get your Direwolf tested and working with normal `PBEACON` config statements to verify things are up and running. That's beyond the scope of this README.

Once Direwolf is confirmed working, you can comment out your old `PBEACON` with a `#` chaacter, and try a *weather telemtry beacon* like this:

```
PBEACON sendto=IG delay=0:30 every=13 lat=1.303690 long=-1.628359 SYMBOL="weather station" COMMENTCMD="curl -s http://127.0.0.1:5000/wxnow.txt | tail -1"
```

*[Note0: Be sure to change the `lat` `long` fields to match your physical coordinates!]*

*[Note1: Change 127.0.0.1 to match the IP address of your eco_aprs_weather bridge IP!]*

*[Note2: If your running this software on the same Raspberry Pi with Direwolf, you can leave 127.0.0.1 alone.]*

This will send your weather reports straight the internet's APRS-IS backend service. It's what most people do. You can add an additional `PBEACON` line and change `sendto=IG` to `sendto=0` to send to the first radio channel in direwolf.

This would look like:
```
PBEACON sendto=IG delay=0:30 every=13 lat=1.303690 long=-1.628359 SYMBOL="weather station" COMMENTCMD="curl -s http://127.0.0.1:5000/wxnow.txt | tail -1"
PBEACON sendto=0 delay=0:30 every=13 lat=1.303690 long=-1.628359 SYMBOL="weather station" COMMENTCMD="curl -s http://127.0.0.1:5000/wxnow.txt | tail -1"
```

Having both the above `PBEACON` statements causes transmission on both `radio port 0` and `IG` (igate), sending over local RF as well as APRS-IS. Local RF packets can be received by APRS/WX-aware radios like Kenwood's or maybe some Yaesu's.


#### Other APRS Software

I don't know what other APRS software accepts `wxnow.txt` and can report telemetry. That's where you come in! I need help, I don't know *everything* APRS.

Contact me thru QRZ (N5IPT) and write up some instructions and I can post them here. You will recieve credit by default unless you ask not to be mentioned in this README.

If you know how to use Github and can make a [Pull Request](https://github.com/jondkelley/eco_aprs_weather/pulls), even better!

