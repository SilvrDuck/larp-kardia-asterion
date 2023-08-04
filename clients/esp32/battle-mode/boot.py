import network
import time

# Replace the following with your WIFI Credentials
SSID = "saintsorny"
SSI_PASSWORD = "saintsorny"

wlan = network.WLAN(network.STA_IF)

def disconnect():
    print("Disconnecting from network if connected...")
    try:
        wlan.disconnect()
    except OSError:
        pass
    finally:    
        wlan.active(False)

def connect():
    print('Connecting to network...')
    if not wlan.isconnected():
        while True:
            try:
                # Some persistence issues with the ESP32 require us to
                # deactivate and reactivate the interface before connecting.
                wlan.active(True)

                time.sleep(.1)

                wlan.connect(SSID, SSI_PASSWORD)

                time.sleep(.1)

                while not wlan.isconnected():
                    time.sleep(.1)
                break
            except OSError:
                print("Connection failed.")
                time.sleep(1)
    print('Connected! Network config:', wlan.ifconfig())

if __name__ == "__main__":
    # More stable if we create a fresh connection every time.
    #disconnect()
    connect()
