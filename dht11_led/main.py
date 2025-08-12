# main.py — ESP8266 + DHT11 + LED control over MQTT
import time, network, machine, ubinascii
import ujson as json
from machine import Pin
import dht
from umqtt.simple import MQTTClient

# ----- CONFIG -----
WIFI_SSID = "Benax-POP8A"
WIFI_PASS = "dusH@8910!"

MQTT_HOST = "broker.benax.rw"
MQTT_PORT = 1883  # TCP for device
TOPIC_DATA   = b"sensors/dht"
TOPIC_LED_CMD   = b"control/led"
TOPIC_LED_STATE = b"control/led/status"

CLIENT_ID  = b"esp8266_" + ubinascii.hexlify(machine.unique_id())
TOPIC_STATUS = b"iot/status/" + CLIENT_ID

PUBLISH_EVERY_SEC = 5  # DHT11 ~1Hz max -> 5s is safe
# -------------------

# Pins: D1 = GPIO5 (DHT11), D2 = GPIO4 (LED)
sensor = dht.DHT11(Pin(5))
led = Pin(4, Pin.OUT)   # D2
led.value(0)            # start OFF (0 = off with external LED to GND)

def wifi_connect():
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    if not sta.isconnected():
        sta.connect(WIFI_SSID, WIFI_PASS)
        t0 = time.ticks_ms()
        while not sta.isconnected():
            if time.ticks_diff(time.ticks_ms(), t0) > 15000:
                raise RuntimeError("Wi-Fi connect timeout")
            time.sleep(0.3)
    print("Wi-Fi OK:", sta.ifconfig())

def mqtt_connect():
    c = MQTTClient(client_id=CLIENT_ID, server=MQTT_HOST, port=MQTT_PORT, keepalive=30)
    # LWT: will publish 'offline' on unexpected disconnect
    c.set_last_will(TOPIC_STATUS, b"offline", retain=True)
    c.connect()
    c.publish(TOPIC_STATUS, b"online", retain=True)
    print("MQTT connected as", CLIENT_ID)
    return c

def publish_led_state(client):
    state = b"ON" if led.value() else b"OFF"
    client.publish(TOPIC_LED_STATE, state, retain=True)
    print("LED", state)

def on_mqtt_msg(topic, msg):
    try:
        t = topic.decode()
        m = msg.decode().strip().upper()
        if t == TOPIC_LED_CMD.decode():
            if m in ("ON", "1", "TRUE"):
                led.value(1)
            elif m in ("OFF", "0", "FALSE"):
                led.value(0)
            publish_led_state(client)
    except Exception as e:
        print("Callback error:", e)

wifi_connect()

client = mqtt_connect()
client.set_callback(on_mqtt_msg)
client.subscribe(TOPIC_LED_CMD)
publish_led_state(client)  # advertise initial LED status

# Optional NTP (best-effort) for real timestamps
def try_ntp():
    try:
        import ntptime
        for _ in range(3):
            try:
                ntptime.settime()
                print("NTP synced")
                return
            except:
                time.sleep(1)
        print("NTP failed; continuing")
    except:
        print("ntptime unavailable")

try_ntp()

last_pub = time.ticks_ms()

while True:
    try:
        # Pump incoming LED commands frequently
        client.check_msg()

        # Periodic sensor publish
        if time.ticks_diff(time.ticks_ms(), last_pub) >= PUBLISH_EVERY_SEC * 1000:
            last_pub = time.ticks_ms()
            try:
                sensor.measure()
                temp = sensor.temperature()
                hum  = sensor.humidity()
                ts   = int(time.time())
                payload = {"temperature": temp, "humidity": hum, "ts": ts}
                client.publish(TOPIC_DATA, json.dumps(payload), retain=True)
                print("PUB", TOPIC_DATA, payload)
            except OSError as e:
                # DHT timing/wiring glitch
                print("DHT error:", e)
                time.sleep(2)

        time.sleep_ms(50)

    except Exception as e:
        print("Loop exception:", e)
        try:
            client.disconnect()
        except:
            pass
        time.sleep(3)
        client = mqtt_connect()
        client.set_callback(on_mqtt_msg)
        client.subscribe(TOPIC_LED_CMD)
        publish_led_state(client)