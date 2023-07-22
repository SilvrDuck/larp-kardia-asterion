import network


# Replace the following with your WIFI Credentials
SSID = "Raccoon City"
SSI_PASSWORD = "crime city"

sta_if = network.WLAN(network.STA_IF)

def connect():
    if not sta_if.isconnected():
        sta_if.active(True)
        sta_if.connect(SSID, SSI_PASSWORD)
        while not sta_if.isconnected():
            pass
    print('Connected! Network config:', sta_if.ifconfig())

connect()