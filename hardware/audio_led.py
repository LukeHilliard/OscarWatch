from gpiozero import LED

import time
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub, SubscribeListener
from dotenv import load_dotenv
import os
import json

print("Starting audio-led script...")


indicator_led = LED(18)

load_dotenv(override=True)
sensors_list = ["led"]
data = {}

class Listener(SubscribeListener):
    def status(self, pubnub, status):
        print(f'Audio LED Status: {status.category.name}')


config = PNConfiguration()
config.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE_KEY")
config.publish_key = os.getenv("PUBNUB_PUBLISH_KEY")
config.user_id = "ow-pi-audio-led"

pubnub = PubNub(config)
pubnub.add_listener(Listener())

app_channel = "ow-pi-channel"
subscription = pubnub.channel(app_channel).subscription()
subscription.on_message= lambda message: handle_message(message)
subscription.subscribe()
publish_result = pubnub.publish().channel(app_channel).message("Hello from CAM01(audio-led)! If your seeing this then the buzzer has connected to PubNub.").sync()

def handle_message(message):
    print(message.message)
    msg = json.loads(json.dumps(message.message))
    if "message" in msg:
        if "recording" in msg["message"]:
            result = msg["message"]["recording"]
            print(f"From PubNub: {result}")
            if result == "True":
                indicator_led.on()
            if result == "False":
                indicator_led.off()
                
                print("Finished buzzing")
