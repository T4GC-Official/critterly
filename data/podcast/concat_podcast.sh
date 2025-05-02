#!/bin/bash

# Create a 0.5 second silence file
ffmpeg -f lavfi -t 0.5 -i anullsrc=r=44100:cl=stereo silence.mp3

# Initialize the input list
input_files=""

# Loop through the files and create the concatenation list
for i in {1..11}
do
    input_files+="host$i.mp3|silence.mp3|guest$i.mp3|silence.mp3|"
done

# Add the final host12.mp3 (no guest file after this)
input_files+="host12.mp3"

# Concatenate the files using FFmpeg
ffmpeg -i "concat:$input_files" -acodec copy final_podcast.mp3

# Clean up silence file 
rm silence.mp3 
