Documentation about the API / WEB requests you can make to this server, with some examples.

### WebAPI Spec

# GET - /set/telemetry_message?message=sample text

Sets the beacon telemetry message sent with WX packet.

This will permanently update the status message going forward.

To bypass the permanance you and make it temporary (until you restart eco_aprs_weather) you can append `&temporary=true` to the request.