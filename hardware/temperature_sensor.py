# followed from: https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/python-setup?utm_source=chatgpt.com

import time
import board
import adafruit_dht

import time
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub, SubscribeListener
from dotenv import load_dotenv
import os
import json

# Initial the dht device, with data pin connected to:
dhtDevice = adafruit_dht.DHT22(board.D21)

# you can pass DHT22 use_pulseio=False if you wouldn't like to use pulseio.
# This may be necessary on a Linux single board computer like the Raspberry Pi,
# but it will not work in CircuitPython.
# dhtDevice = adafruit_dht.DHT22(board.D18, use_pulseio=False)

print("Starting temperature script...")

load_dotenv(override=True)
sensors_list = ["temperature"]
data = {}

class Listener(SubscribeListener):
    def status(self, pubnub, status):
        print(f'Temperature Status: {status.category.name}')
    
config = PNConfiguration()
config.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE_KEY")
config.publish_key = os.getenv("PUBNUB_PUBLISH_KEY")
config.user_id = "ow-pi-temperature"

pubnub = PubNub(config)
pubnub.add_listener(Listener())

app_channel = "ow-pi-channel"
subscription = pubnub.channel(app_channel).subscription()
subscription.subscribe()
publish_result = pubnub.publish().channel(app_channel).message("Hello from CAM01(temperature)! If your seeing this then the buzzer has connected to PubNub.").sync()



while True:
    try:
        # Print the values to the serial port
        temperature_c = dhtDevice.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dhtDevice.humidity

        data = {
            "data": {
                "temperature_c": temperature_c,
                "temperature_f": temperature_f,
                "humidity": humidity,
            }
        }
        print(data)
        pubnub.publish().channel(app_channel).message(data).sync()
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        time.sleep(4)
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error

    time.sleep(4)
