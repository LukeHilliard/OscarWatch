from gpiozero import Buzzer, LED

import time
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub, SubscribeListener
from dotenv import load_dotenv
import os
import json

bz = Buzzer(3)
indicator_led = LED(4)
flashing_led = LED(14)


load_dotenv(override=True)
sensors_list = ["buzzer"]
data = {}

class Listener(SubscribeListener):
    def status(self, pubnub, status):
        print(f'Status: \n{status.category.name}')
    
config = PNConfiguration()
config.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE_KEY")
config.publish_key = os.getenv("PUBNUB_PUBLISH_KEY")
config.user_id = "OscarWatch-CAM01"


pubnub = PubNub(config)
pubnub.add_listener(Listener())

app_channel = "ow-pi-channel"

subscription = pubnub.channel(app_channel).subscription()
subscription.on_message= lambda message: handle_message(message)
subscription.subscribe()
publish_result = pubnub.publish().channel(app_channel).message("Hello from CAM01! If your seeing this then the buzzer has connected to PubNub.").sync()


def handle_message(message):
    print(message.message)
    msg = json.loads(json.dumps(message.message))
    if 'message' in msg:
        result = msg['message']['buzzer-on']
        print(f"From PubNub: {result}")
        if result == 'True':
            print("Buzzing 3 times & and flashing LED")
            indicator_led.on()
            # TODO when the buzzer is activated i want an led to blink indicating its on as there is no audio
            for i in range(3):
                print(i + 1)
                bz.on()
                flashing_led.on()
                time.sleep(0.5)
                bz.off()
                flashing_led.off()
                time.sleep(1)
            indicator_led.off()
            print("Finished buzzing")



def main():
    print("Done")