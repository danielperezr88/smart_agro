Arduino + Blynk + Flask smart-agro (RPi + Arduino)
==================================================
Functional Prototype code for Smart-Agro applications.

Main features are the following:

- Real-time sensor/actuator handling via mobile app (Blynk).
- Image/data preprocessing over python with a Raspberry Pi (with the help of scientific and image processing software, such as scikit-learn and OpenCV).
- Self-hosted Flask webapp inside the Raspberry Pi, suitable for system-specific configurations.
- Capacity for autonomously running and training Machine Learning models, to control the environment variables.

SCOPE:  **[*Proof of Concept*]**

STATUS: **[*Production Ready*]**

This project is composed of 2 parts:

- **python_blynk**: Handles Serial Connection with Arduino board and Over-Internet API with Blynk servers, in addition to Raspberry Pi camera, which image preprocesses with OpenCV. Everything is executed asynchronously, making use of AsyncIO python library, in order to avoid processes blocking each other. You just have to run ``app.py`` to start.
- **arduino**: Serves as an interface between sensors/actuators and the serial port. Except for the sensor drivers, data processing is minimal.

Additionally, this project contains the submodule ``flask_video_streaming``, which features a project for camera and streaming tests. This project is not necessary for the deployment setup, but in case you wanted to clone it too with the rest of the contents, remember using the *--recursive* option.

Notes:
------
Given its multi-device nature, this project lacks a containerized deployment method. To put it to work you'll have to wire everything up correctly, program a suitable Arduino board with the Arduino code provided, and prepare a Raspberry Pi with python 3 and all of the required python modules.
About the requirements, although they haven't been extensively tested, here we'll provide a tentative list:

- click==6.7
- Flask==0.12.2
- itsdangerous==0.24
- Jinja2==2.9.6
- MarkupSafe==1.0
- picamera==1.13
- Werkzeug==0.12.2
- numpy==1.13.1
- opencv-python==3.2.0.8

In case you needed any assistance with the setting up, feel free to contact dperez@human-forecast.com or alopez@human-forecast.com.
