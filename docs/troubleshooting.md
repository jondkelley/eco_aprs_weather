
## Troubleshooting Tips

### Reviewing raw APRS messages from your system

I find FINDU to be helful, check this out:

* https://www.findu.com/cgi-bin/raw.cgi?call=WESTWD

### What does beacon text "wx OFF AIR-No data from ECOWITT gw for over 60s" mean?

This means your station hasn't received data from your ECOWITT gateway in some time.

Telemetry automatically shuts off if there is no updates in 60 seconds.

Stale data will still be shown in this apps local (LAN) web dashboards, but not repoted to APRS network for accuracy.

You can visit `http:/IP ADDRESS:5000/sensor/overview` to get a sense for when last reported data was sent.

#### Troubleshooting:

* You might want to make sure ECOWITT gw is powered on and working normally.
* Make sure ECOWITT gateway is configured for 15 or 30 second updates.

#### Workarounds:

You can configure this setting in `/etc/bridge.conf`

For example, to make this message appear after 5 minutes of stale data:

```
[General]
stale_data_shutdown_threshold_seconds=300
```

### What does beacon text "wx OFF AIR-software bridge ready but no WX report from ECOWITT gw received yet" mean?

This can happen if you recently started the `eco_aprs_weather` service when your APRS system requested `wxnow.txt`

When this application starts up, it doesn't have anything to report until the regular checkin from your ECOWITT gateway.

#### Troubleshooting:

If this message persists beyond the ECOWITT configured *Upload Interval* further troubleshooting is required with the ECOWITT gateway device.

