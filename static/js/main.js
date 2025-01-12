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
    console.log(message)
    if(message.data)
    {
        document.getElementById("temperature_c").innerHTML = message.data.temperature_c
        document.getElementById("humidity").innerHTML = message.data.humidity
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


function handleScreenshotClicked() {
    const video = document.getElementById("video-player")
    const canvas = document.createElement("canvas")

    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    const ctx = canvas.getContext("2d")
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

    const base64Image = canvas.toDataURL("image/png")
    console.log(base64Image)
    uploadScreenshot(base64Image)
}

async function uploadScreenshot(base64Image) {
    console.log("Uploading image...");
    const userId = document.getElementById("user_id").value;
    console.log(`userID: ${userId}`)

    const response = await fetch(`https://api.oscarwatch.online/api/screenshot/${userId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ images: [base64Image] }),
        mode: "cors",
    });

    if (response.ok) {
        console.log("Screenshot appended successfully");
    } else {
        const errorData = await response.json();
        console.error("Failed to append screenshot:", errorData.detail);
    }
}
