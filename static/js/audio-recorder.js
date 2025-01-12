// referenced from: https://developer.mozilla.org/en-US/play

const startButton = document.getElementById('start');
const stopButton = document.getElementById('stop');
const playback = document.getElementById('playback');

let mediaRecorder;
let audioChunks = [];

startButton.addEventListener('click', async () => {
    startButton.disabled = true;
    stopButton.disabled = false;

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            playback.src = URL.createObjectURL(audioBlob);
            uploadRecording(audioBlob);
            audioChunks = [];
        };

        mediaRecorder.start();
    } catch (err) {
        console.error("Error accessing media devices:", err);
    }
});

stopButton.addEventListener("click", () => {
    startButton.disabled = false;
    stopButton.disabled = true;
    mediaRecorder.stop();
});

function uploadRecording(blob) {
    const formData = new FormData();
    formData.append("audio", blob, "recording.webm");

    fetch('/upload', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => console.log("Upload successful:" +  data))
    .catch(error => console.error("Upload error:" +  error))
}