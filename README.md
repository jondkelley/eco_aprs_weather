# eco_aprs_weather

The Eco_APRS_Weather software exists to allow Ecowitt Weather Stations to work with APRS software for amateur radio. This software integrates directly with your weather station after changing some settings, and can integrate directly with software like Direwolf using the `wxnow.txt` amateur radio weather telemetry format.

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

1. Click the Elipsis (...) symbol in the top right (of the screen showing your WX station live metrics)
2. In dropdown, select "Others"
3. In the "Edit Gateway" screen click "DIY Upload Servers" button
4. In the "DIY Upload Servers" screen click "Customized" (Globe Icon)
   * In the "Server / Host Name" field enter the IP address of the computer running this software
   * In the "Port" field make sure it is "5000"
   * In the "Upload Interval" field select the fastest interval
   * Click save.
5. Hit < (top right) to return to previous screens
6. WX configuration Done!


#### To confirm weather station telemtry is being recieved by the bridge

Visit `http://<IP ADDRESS OF THIS SOFTWARE>:5000/sensor/overview` and verify you have station data coming in.

You may have to wait 5-10 minutes and refresh this page periodically, sometimes it takes a while for Ecowitt device settings to take effect.

If you do not see station data, possible solutions involve:

* Check the Ecowitt WX Station configuration settings
* Ensure the path field says exactly "data/report"
* Ensure the computer running this software does not have any sort of Firewall enabled
* Verifying your network configuration and trying again
