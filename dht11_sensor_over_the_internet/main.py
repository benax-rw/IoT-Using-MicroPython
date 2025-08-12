# main.py  — ESP8266 + DHT11 → MQTT (retained + timestamp)
import time, network, machine, ubinascii
import ujson as json
from machine import Pin
import dht
from umqtt.simple import MQTTClient

# ---------- CONFIG ----------
WIFI_SSID = "Benax-POP8A"
WIFI_PASS = "dusH@8910!"

MQTT_HOST = "broker.benax.rw"
MQTT_PORT = 1883          # TCP (browser uses WSS separately)
TOPIC_DATA = b"sensors/dht"  # your dashboard subscribes here
CLIENT_ID  = b"esp8266_" + ubinascii.hexlify(machine.unique_id())
TOPIC_STATUS = b"iot/status/" + CLIENT_ID  # optional status topic

PUBLISH_EVERY_SEC = 5     # DHT11 is fine at ~1 Hz; we use 5s
# ---------------------------

# --- Wi‑Fi connect ---
def wifi_connect():
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    if not sta.isconnected():
        print("Wi-Fi: connecting to", WIFI_SSID)
        sta.connect(WIFI_SSID, WIFI_PASS)
        t0 = time.ticks_ms()
        while not sta.isconnected():
            if time.ticks_diff(time.ticks_ms(), t0) > 15000:
                raise RuntimeError("Wi-Fi connect timeout")
            time.sleep(0.3)
    print("Wi-Fi OK:", sta.ifconfig())

# --- Optional NTP (for real timestamps) ---
def try_ntp():
    try:
        import ntptime
        for _ in range(3):
            try:
                ntptime.settime()  # sets RTC (UTC)
                print("NTP synced")
                return
            except:
                time.sleep(1)
        print("NTP failed (continuing with local ticks)")
    except:
        print("ntptime not available")

# --- MQTT connect (with LWT) ---
def mqtt_connect():
    c = MQTTClient(client_id=CLIENT_ID, server=MQTT_HOST, port=MQTT_PORT, keepalive=30)
    # Last Will: mark device offline if it disconnects unexpectedly
    c.set_last_will(TOPIC_STATUS, b"offline", retain=True, qos=0)
    c.connect()
    # Mark online on successful connect
    c.publish(TOPIC_STATUS, b"online", retain=True)
    print("MQTT connected as", CLIENT_ID)
    return c

def main():
    wifi_connect()
    try_ntp()

    # DHT11 on D1 (GPIO5)
    sensor = dht.DHT11(Pin(5))
    time.sleep(2)  # sensor settle

    client = None
    while True:
        try:
            if client is None:
                client = mqtt_connect()

            # Read sensor (DHT11 ~1 Hz max)
            sensor.measure()
            temp = sensor.temperature()  # °C (int)
            hum  = sensor.humidity()     # %  (int)

            # Timestamp (Unix seconds). If NTP worked: real UTC.
            # If not, some boards still return seconds since 2000/boot.
            ts = int(time.time())

            payload = {"temperature": temp, "humidity": hum, "ts": ts}
            msg = json.dumps(payload)

            # Retained so dashboards get an immediate last reading on connect
            client.publish(TOPIC_DATA, msg, retain=True)
            print("PUB", TOPIC_DATA, msg)

            time.sleep(PUBLISH_EVERY_SEC)

        except OSError as e:
            # DHT read error or transient WiFi glitch
            print("Error:", e)
            time.sleep(2)
        except Exception as e:
            # MQTT error: try a quick reconnect
            print("MQTT exception:", e)
            try:
                if client:
                    client.disconnect()
            except:
                pass
            client = None
            time.sleep(3)

# --- run ---
if __name__ == "__main__":
    main()