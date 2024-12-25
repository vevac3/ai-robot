import time

import vlc

import RPi.GPIO as GPIO

import google.generativeai as genai

import cv2

import numpy as np

import face_recognition

import pyttsx3

from gtts import gTTS

import os

import speech_recognition as sr

import subprocess

import youtube_dl

import spotipy

from spotipy.oauth2 import SpotifyClientCredentials



# Initialize GPIO

# GPIO setup

GPIO.setmode(GPIO.BCM)



IN1 = 17  # Motor A Input 1

IN2 = 27  # Motor A Input 2

IN3 = 22  # Motor B Input 1

IN4 = 23  # Motor B Input 2

ENA = 24  # Motor A Enable

ENB = 25  # Motor B Enable

# Set up GPIO pins for Line Following Sensors

left_sensor_pin = 7

right_sensor_pin = 8



#Ir pin

IR_PIN = 4



# Define GPIO pins for ultrasonic sensors

TRIG_FRONT = 5

ECHO_FRONT = 6

TRIG_LEFT = 13

ECHO_LEFT = 19

TRIG_RIGHT = 26

ECHO_RIGHT = 21

TRIG_BACK1 = 2

ECHO_BACK1 = 3

TRIG_BACK2 = 18

ECHO_BACK2 = 12



# Setup GPIO pins

GPIO.setup(TRIG_FRONT, GPIO.OUT)

GPIO.setup(ECHO_FRONT, GPIO.IN)

GPIO.setup(TRIG_LEFT, GPIO.OUT)

GPIO.setup(ECHO_LEFT, GPIO.IN)

GPIO.setup(TRIG_RIGHT, GPIO.OUT)

GPIO.setup(ECHO_RIGHT, GPIO.IN)

GPIO.setup(TRIG_BACK1, GPIO.OUT)

GPIO.setup(ECHO_BACK1, GPIO.IN)

GPIO.setup(TRIG_BACK2, GPIO.OUT)

GPIO.setup(ECHO_BACK2, GPIO.IN)

GPIO.setup(left_sensor_pin, GPIO.IN)

GPIO.setup(right_sensor_pin, GPIO.IN)

GPIO.setup(IN1, GPIO.OUT)

GPIO.setup(IN2, GPIO.OUT)

GPIO.setup(IN3, GPIO.OUT)

GPIO.setup(IN4, GPIO.OUT)

GPIO.setup(ENA, GPIO.OUT)

GPIO.setup(ENB, GPIO.OUT)



# Set up GPIO pins for servo motors

servo_11 = 16

servo_22 = 10

servo_33 = 9

servo_44 = 11

servo_55  = 20

servo_66 = 1

GPIO.setup(servo_11, GPIO.OUT)

GPIO.setup(servo_22, GPIO.OUT)

GPIO.setup(servo_33, GPIO.OUT)

GPIO.setup(servo_44, GPIO.OUT)

GPIO.setup(servo_55, GPIO.OUT)

GPIO.setup(servo_66, GPIO.OUT)













# Initialize PWM on each servo pin at 50Hz

servo_1 = GPIO.PWM(servo_11, 50)

servo_2 = GPIO.PWM(servo_22, 50)

servo_3 = GPIO.PWM(servo_33, 50)

servo_4 = GPIO.PWM(servo_44, 50)

servo_5 = GPIO.PWM(servo_55, 50)

servo_6 = GPIO.PWM(servo_66, 50)



servo_1.start(0)

servo_2.start(0)

servo_3.start(0)

servo_4.start(0)

servo_5.start(0)

servo_6.start(0)





# Function to move servo to a specific angle

def move_servo(pwm, angle):

    duty_cycle = (angle / 18) + 2

    pwm.ChangeDutyCycle(duty_cycle)

    time.sleep(0.5)

    pwm.ChangeDutyCycle(0)



# Motor Control Functions (For L298N)

def move_forward():

    print("Moving forward")

    GPIO.output(IN1, GPIO.HIGH)

    GPIO.output(IN2, GPIO.LOW)

    GPIO.output(IN3, GPIO.HIGH)

    GPIO.output(IN4, GPIO.LOW)



def move_backward():

    print("Moving backward")

    GPIO.output(IN1, GPIO.LOW)

    GPIO.output(IN2, GPIO.HIGH)

    GPIO.output(IN3, GPIO.LOW)

    GPIO.output(IN4, GPIO.HIGH)



def turn_left():

    print("Turning left")

    GPIO.output(IN1, GPIO.LOW)

    GPIO.output(IN2, GPIO.HIGH)

    GPIO.output(IN3, GPIO.HIGH)

    GPIO.output(IN4, GPIO.LOW)



def turn_right():

    print("Turning right")

    GPIO.output(IN1, GPIO.HIGH)

    GPIO.output(IN2, GPIO.LOW)

    GPIO.output(IN3, GPIO.LOW)

    GPIO.output(IN4, GPIO.HIGH)



def stop():

    print("Stopping")

    GPIO.output(IN1, GPIO.LOW)

    GPIO.output(IN2, GPIO.LOW)

    GPIO.output(IN3, GPIO.LOW)

    GPIO.output(IN4, GPIO.LOW)



# Line Following Functionality

def follow_line():

    print("Following the line...")

    while True:

        left_sensor = GPIO.input(left_sensor_pin)

        right_sensor = GPIO.input(right_sensor_pin)



        if left_sensor == 1 and right_sensor == 0:

            print("Turning left")

            turn_left()

            # Add your code to turn left

        elif left_sensor == 0 and right_sensor == 1:

            print("Turning right")

            turn_right()

            # Add your code to turn right

        elif left_sensor == 0 and right_sensor == 0:

            print("Moving forward")

            move_forward()

            # Add your code to move forward

        else:

            print("Line lost, stopping")

            # Add your code to stop

            stop()





# Define function for obstacle detection

def measure_distance(TRIG_PIN, ECHO_PIN):

    GPIO.output(TRIG_PIN, GPIO.LOW)

    time.sleep(0.5)

    GPIO.output(TRIG_PIN, GPIO.HIGH)

    time.sleep(0.00001)

    GPIO.output(TRIG_PIN, GPIO.LOW)

    pulse_start = time.time()

    pulse_end = time.time()

    while GPIO.input(ECHO_PIN) == 0:

        pulse_start = time.time()

    while GPIO.input(ECHO_PIN) == 1:

        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start

    distance = pulse_duration * 17150

    distance = round(distance, 2)

    return distance



def avoid_obstacles():

    front_distance = measure_distance(TRIG_FRONT, ECHO_FRONT)

    left_distance = measure_distance(TRIG_LEFT, ECHO_LEFT)

    right_distance = measure_distance(TRIG_RIGHT, ECHO_RIGHT)

    back1_distance = measure_distance(TRIG_BACK1, ECHO_BACK1)

    back2_distance = measure_distance(TRIG_BACK2, ECHO_BACK2)

    

    if front_distance < 20:

        print("Obstacle detected in front!")

        move_backward()

    elif left_distance < 20:

        print("Obstacle detected on the left!")

        turn_right()

        # Add code to turn right

    elif right_distance < 20:

        print("Obstacle detected on the right!")

        turn_left()

        # Add code to turn left

    elif back1_distance < 20 or back2_distance < 20:

        print("Obstacle detected in the back!")

        move_forward()

        # Add code to stop or move forward



# Initialize the Gemini API with your API key

genai.configure(api_key="AIzaSyAxfHqHTxBH5oCMTNvDb26fwV6hUisuhuc")



def chat_with_gemini(prompt):

    # Generate a response using the Gemini API

    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(

        f"{prompt}\n\n reply with plain text only", # Adjust token limits as needed

    )

    return response.text  # Extract the content of the response



def text_to_speech(text):

    tts = gTTS(text=text, lang='en')

    tts.save("response.mp3")

    p = vlc.MediaPlayer("./response.mp3")

    p.play()

    return p



def recognize_speech():

    recognizer = sr.Recognizer()



    with sr.Microphone(device_index=1) as source:

        print("Listening...")

        audio = recognizer.listen(source)

        try:

            command = recognizer.recognize_google(audio)

            print(f"Recognized: {command}")

            return command.lower()

        except sr.UnknownValueError:

            print("Sorry, I did not get that")

            return ""

        

def Introduction():

    text_to_speech("Hi, my name is Jarvis. I am made by Swarnava. I am an multifunctional robot ")



# Functions for Arm Movements

def wave_arm():

    servo_1.ChangeDutyCycle(7)

    time.sleep(1)

    servo_1.ChangeDutyCycle(5)

    time.sleep(1)

    servo_1.ChangeDutyCycle(7)

    time.sleep(1)

    servo_1.ChangeDutyCycle(0)



def point_arm():

    servo_2.ChangeDutyCycle(6)

    time.sleep(1)

    servo_2.ChangeDutyCycle(0)



def pick_up_object():

    servo_1.ChangeDutyCycle(3)

    time.sleep(1)

    servo_2.ChangeDutyCycle(10)

    time.sleep(1)

    servo_1.ChangeDutyCycle(7)

    time.sleep(1)

    servo_2.ChangeDutyCycle(5)

    time.sleep(1)



def expressive_gesture():

    for _ in range(2):

        servo_1.ChangeDutyCycle(6)

        time.sleep(0.5)

        servo_1.ChangeDutyCycle(4)

        time.sleep(0.5)



def dance_move():

    for _ in range(5):

        servo_1.ChangeDutyCycle(8)

        servo_2.ChangeDutyCycle(4)

        time.sleep(0.5)

        servo_1.ChangeDutyCycle(4)

        servo_2.ChangeDutyCycle(8)

        time.sleep(0.5)



def guide_direction():

    servo_2.ChangeDutyCycle(7)

    time.sleep(1)

    servo_2.ChangeDutyCycle(5)

    time.sleep(1)

    servo_2.ChangeDutyCycle(3)

    time.sleep(1)

    servo_2.ChangeDutyCycle(5)



def simon_says_action():

    servo_1.ChangeDutyCycle(8)

    time.sleep(1)

    servo_1.ChangeDutyCycle(0)



def follow_the_leader_action():

    servo_2.ChangeDutyCycle(6)

    time.sleep(1)

    servo_2.ChangeDutyCycle(0)



# Camera and Object Recognition

def recognize_object():

    video_capture = cv2.VideoCapture(0)

    known_objects = {"bottle": "A container to hold liquids", "phone": "A device used for communication"}

    

    while True:

        ret, frame = video_capture.read()

        rgb_frame = frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_frame)

        object_name = None  # Implement object detection logic here



        if object_name in known_objects:

            description = known_objects[object_name]

            text_to_speech(f"This is a {object_name}. {description}")

            break



    video_capture.release()



# Hide and Seek Game

def capture_and_lock_face():

    video_capture = cv2.VideoCapture(0)

    known_face_encodings = []

    known_face_names = []



    print("Locking onto your face...")

    text_to_speech("Locking onto your face...")

    pan_angle = 90  # Initial camera position (center)

    tilt_angle = 90



    move_servo(servo_5, pan_angle)  # Pan servo control

    move_servo(servo_6, tilt_angle)    # Tilt servo control



    while True:

        ret, frame = video_capture.read()

        if not ret:

            print("Failed to capture frame. Retrying...")

            text_to_speech("Failed to capture frame. Retrying....")

            continue



        rgb_frame = frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_frame)



        if face_locations:

            face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]

            known_face_encodings.append(face_encoding)

            known_face_names.append("Seeker")

            print("Face locked in! Now go hide.")

            text_to_speech("Face locked in! Now go hide.")

            break



    video_capture.release()



def find_person():

    video_capture = cv2.VideoCapture(0)

    print("Starting to search for you...")

    text_to_speech("Starting to search for you...")



    pan_angle = 90  # Initial camera position

    tilt_angle = 90

    move_servo(servo_5, pan_angle)  # Pan servo control

    move_servo(servo_6, tilt_angle)    # Tilt servo control



    while True:

        ret, frame = video_capture.read()

        if not ret:

            print("Failed to capture frame. Retrying...")

            text_to_speech("Failed to capture frame. Retrying...")

            continue



        rgb_frame = frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_frame)

        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)



        for face_encoding in face_encodings:

            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

            if True in matches:

                print("Found you!")

                text_to_speech("I found you!")

                video_capture.release()

                return



        # Example logic to adjust camera for searching

        pan_angle += 10  # Increment pan angle

        if pan_angle > 180:

            pan_angle = 0  # Reset pan angle

            tilt_angle += 10  # Increment tilt angle



        if tilt_angle > 180:

            tilt_angle = 90  # Reset tilt angle after a full sweep



        move_servo(servo_5, pan_angle)  # Adjust pan servo

        move_servo(servo_6, tilt_angle)    # Adjust tilt servo



    video_capture.release()



# Self-Charging Dock Search

def get_distance():

    GPIO.output(TRIG_FRONT, GPIO.HIGH)

    time.sleep(0.00001)

    GPIO.output(TRIG_FRONT, GPIO.LOW)



    start_time = time.time()

    stop_time = time.time()



    while GPIO.input(ECHO_FRONT) == 0:

        start_time = time.time()



    while GPIO.input(ECHO_FRONT) == 1:

        stop_time = time.time()



    elapsed_time = stop_time - start_time

    distance = (elapsed_time * 34300) / 2  # Speed of sound in cm/s

    return distance



def move_to_charging_dock():

    print("Searching for the charging dock...")

    while True:

        # Check IR signal

        if GPIO.input(IR_PIN) == 1:

            print("IR signal detected! Approaching the dock.")

            while True:

                # Measure distance to dock

                distance = get_distance()

                print(f"Distance to dock: {distance:.2f} cm")



                if distance > 30:  # Move closer if dock is far

                    move_forward()

                elif 10 < distance <= 30:  # Align if within range

                    stop()

                    print("Aligning with the dock...")

                    time.sleep(1)  # Simulate alignment

                    move_forward()

                else:  # Docking complete

                    stop()

                    print("Docked successfully!")

                    return



        else:

            # Roam and search for the signal

            print("Roaming...")

            avoid_obstacle()



def align_to_item():

    front_distance = measure_distance(TRIG_FRONT, ECHO_FRONT)

    if front_distance > 30:  # If too far from the object, move forward

        print("Object detected, moving forward to align")

        move_forward()

    elif front_distance < 20:  # If too close to the object, move backward

        print("Object too close, moving backward to align")

        move_backward()

    else:

        print("Aligned to object")

        stop()  # If at a proper distance, stop



# YouTube Video Playback

def play_youtube_video(url):

    ydl_opts = {

        'format': 'best',

        'outtmpl': 'video.mp4',

        'quiet': True

    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:

        ydl.download([url])

    subprocess.call(['omxplayer', 'video.mp4'])

def show_emotions():

    emotions = {

        "happy": "happy_eyes.jpg",

        "sad": "sad_eyes.jpg",

        "surprised": "surprised_eyes.jpg",

        "angry": "angry_eyes.jpg"

    }



    while True:

        for emotion, image_file in emotions.items():

            # Load and display the image

            img = cv2.imread(image_file)

            if img is None:

                print(f"Error: Image {image_file} not found.")

                continue

            cv2.imshow("Robot Emotion", img)



            # Display each emotion for 2 seconds

            key = cv2.waitKey(2000)



            # If 'q' is pressed, exit loop

            if key == ord('q'):

                cv2.destroyAllWindows()

                return





# Spotify Playback

def play_spotify_song(song_name):

    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id='c0bc9132d3354b34a6a3fae16526249d',

                                                               client_secret='8b981b83829940679c3b1dee709574b6'))

    results = sp.search(q=song_name, limit=1)

    if results['tracks']['items']:

        track_url = results['tracks']['items'][0]['external_urls']['spotify']

        subprocess.call(['xdg-open', track_url])

    else:

        text_to_speech("Song not found")



# Main loop to wait for wake word

def blah():

    while True:

        command = recognize_speech()

        if command and "jarvis" in command.lower():

            text_to_speech("Yes?")

            command = recognize_speech()



            if "wave" in command:

                wave_arm()

            elif "introduce" in command:

                Introduction()

            elif "point" in command:

                point_arm()

            elif "pick" in command:

                pick_up_object()

            elif "expressive gesture" in command:

                expressive_gesture()

            elif "dance" in command:

                dance_move()

            elif "guide" in command:

                guide_direction()

            elif "simon says" in command:

                simon_says_action()

            elif "follow the leader" in command:

                follow_the_leader_action()

            elif "recognize object" in command:

                recognize_object()

            elif "hide" in command:

                capture_and_lock_face()

                time.sleep(10)  # Simulate counting to 10

                find_person()

            elif "charging dock" in command:

                move_to_charging_dock()

            elif "youtube" in command:

                video_url = "https://www.youtube.com/watch?v=6dMjCa0nqK0"  # Set your YouTube video URL

                play_youtube_video(video_url)

            elif "spotify" in command:

                song_name = "Cupid"  # Set your Spotify song name

                play_spotify_song(song_name)

            else:

                response = chat_with_gemini(command)

                text_to_speech(response)

# Servo Motor Control for Sorting

def sort_items(item_color):

    print(f"Sorting {item_color} items...")



    # Align the robot to the item's position

    align_to_item()



    # Use left arm to pick up item

    move_servo(left_arm_vertical_pwm, 90)  # Move arm down to pick

    move_servo(left_arm_grab_pwm, 45)  # Close grab to pick item



    # Move arm to place item

    move_servo(left_arm_vertical_pwm, 0)  # Move arm up with item

    move_servo(left_arm_grab_pwm, 0)  # Release item



    print(f"Placed {item_color} item in correct spot.")



# Full AI Control via ChatGPT

def execute_chatgpt_command(command):

    print(f"Executing command: {command}")

    # Parse the command and execute corresponding functions

    if "line follow" in command:

        follow_line()

    elif "sort" in command:

        item_color = command.split(" ")[-1]

        sort_items(item_color)

    elif "introduce" in command:

            Introduction()

    elif "wave" in command:

        wave_arm()

    elif "point" in command:

        point_arm()

    elif "pick up" in command:

        pick_up_object()

    elif "expressive gesture" in command:

        expressive_gesture()

    elif "dance" in command:

        dance_move()

    elif "guide" in command:

        guide_direction()

    elif "simon says" in command:

        simon_says_action()

    elif "follow the leader" in command:

        follow_the_leader_action()

    elif "recognize object" in command:

        recognize_object()

    elif "hide and seek" in command:

        capture_and_lock_face()

        time.sleep(10)  # Simulate counting to 10

        find_person()

    elif "go back to your charging dock" in command:

        move_to_charging_dock()

    elif "play youtube video" in command:

        video_url = "YOUR_YOUTUBE_VIDEO_URL"  # Set your YouTube video URL

        play_youtube_video(video_url)

    elif "play spotify song" in command:

        song_name = "YOUR_SONG_NAME"  # Set your Spotify song name

        play_spotify_song(song_name)

    else:

        response = chat_with_gemini(command)

        text_to_speech(response)

    # Add more functionalities

def main():

    while True:

        print("Say 'exit' to end the program.")

        user_input = recognize_speech()

        if user_input and user_input.lower() == "exit":

            break

            # Send the transcribed speech to the Gemini chat function

        response = chat_with_gemini(user_input)

            # Convert Gemini's response to speech

        p = text_to_speech(response)



# Run the main loop

if __name__ == "__main__":

    blah()



# Clean up GPIO

GPIO.cleanup()


