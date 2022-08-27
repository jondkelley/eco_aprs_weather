
## Troubleshooting Tips

### Reviewing raw APRS messages from your system

I find FINDU to be helful, check this out:

* https://www.findu.com/cgi-bin/raw.cgi?call=WESTWD

### What does beacon text "wx OFF AIR-No data from ECOWITT gw for over 60s"

This means your station hasn't received data from your ECOWITT gateway in some time.

Telemetry automatically shuts off, as there is no data to report.

Stale data is still will still be available / displayed in local web dashboards.

You can visit `http:/IP ADDRESS:5000/sensor/overview` to get a sense for when last reported data was sent.