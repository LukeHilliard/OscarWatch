#!/bin/bash
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
export AWS_DEFAULT_REGION=

cd ~/amazon-kinesis-video-streams-producer-sdk-cpp/build
gst-launch-1.0 libcamerasrc ! video/x-raw, width=1920, height=1080, framerate=30/1, format=NV12 ! videoconvert ! x264enc tune=zerolatency bitrate=1024 key-int-max=30 ! kvssink stream-name=OscarWatch_CAM01 aws-region=eu-west-1
