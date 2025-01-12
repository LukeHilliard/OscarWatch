let aliveSecond = 0;
let heartBeatRate = 5000;
let pubnub;
let appChannel = "ow-pi-channel"
function time() {
    let d = new Date();
    let currentSecond = d.getTime();
    if (currentSecond - aliveSecond > heartBeatRate + 1000) {
        //document.getElementById("connection_id").innerHTML = "DEAD";
    }
    else {
        //document.getElementById("connection_id").innerHTML = "ALIVE";
    }
    setTimeout('time()', 1000);
}

function keepAlive() {
    fetch('/keep_alive')
        .then(response => {
            if (response.ok) {
                let date = new Date();
                aliveSecond = date.getTime();
                return response.json();
            }
            throw new Error("Server offline");
        })
        .catch(error => console.log(error));
    setTimeout('keepAlive()', heartBeatRate);
}

const setupPubnub = async ()  => {
    console.log("Connecting to PubNub...")
    try {
        console.log("Fetching keys...")
        const response = await fetch("/get_pubnub_keys")
        const keys = await response.json() 

        // TODO figure out why the /get_pubnub_keys works locally but not on aws
        pubnub = new PubNub({
            publishKey: "pub-c-426e46d6-1500-4861-b24b-8a40e4fa9564",
            subscribeKey: "sub-c-5fea9fd9-f8ca-4292-8498-def461ba9272",
            userId: 'OscarWatch-user',
        });
        const channel = pubnub.channel(appChannel)
        const subscription = channel.subscription()
    
        pubnub.addListener({
            status: (s) =>{
                console.log("Connection Status: ", s.category)
            },
        })
    
        subscription.onMessage = (messageEvent) => {
            handleMessage(messageEvent.message)
        }
        subscription.subscribe()

    } catch(e) {
        console.error("Error while getting PubNub keys: " + e)
    }
}


// sends a messages to pubnub to trigger the buzzer
function handleBuzzerClicked() {
    publishMessage({"buzzer-on":"True"})
    console.log("published message to PubNub (buzzer)")
}

// both functions send a message to pubnub to turn the green LED on and off as audio is being recorded
function handleAudioRecordingStarted() {
    publishMessage({"recording":"True"})
    console.log("Published message to pubnub (led)")
}
function handleAudioRecordingStopped() {
    publishMessage({"recording":"False"})
    console.log("Published message to pubnub (led)")
}




function handleMessage(message)
{
    if(message == '"buzzer-on":"True"')
    {
        // update css to show buzzer being triggered
    }
}

const publishMessage = async(message) => {
    const publishPayload = {
        channel: appChannel,
        message: {
            message:message
        },
    }
    await pubnub.publish(publishPayload)
}

