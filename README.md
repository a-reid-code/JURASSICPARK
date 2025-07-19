# JURASSIC PARK

## A User-Friendly Attendance Tracking Solution for *FIRST* Robotics Competition Teams

JURASSIC PARK (Joint User Record for Attendance Scanning - Storing Information on Crew - Providing Accurate Robotics Knowledge) is a QR-based system for logging attendance on *FIRST* Robotics Competition teams.

It is designed to be straightforward and user-friendly, with minimal setup, a streamlined interface, and easily accessible data reporting.

## Installation

### JURASSIC PARK System Requirements

* Computer with camera (iPad currently not supported)
* Google account

### Preparation

* Download Python
    * Tested with 3.13, >3.7 should be fine
* Use your terminal to download the following libraries:
    * NumPy, MatPlotLib, Pandas, CV2 (OpenCV), Google-Auth, Tkinter, Pillow, QRCode, PyGSheets
    * Copy-paste the line below to install them all at once

```
pip install numpy matplotlib pandas cv2 google-auth tkinter pillow qrcode
```

### JURASSIC PARK Setup

* Download and unzip the release file
* Replace the contents of *names.txt* with your team roster
    * One name per line

### JURASSIC PARK Google Integration

* Make a Google Sheet with 3 blank worksheets
* Follow steps 1-3 [here](https://www.geeksforgeeks.org/python/how-to-automate-google-sheets-with-python/) to create your credentials and link to your spreadsheet
* Replace the contents of *creds.json* with your downloaded Google service account credentials json
* Replace the service_file parameter in *AttendanceClass.py* with the file path to *creds.json*
* Replace the spreadsheet name in *AttendanceClass.py* with what you are using

### Prior to Use

* Run *MOSQUITO.py* (Module for Organizing Scannable QR Units to Initialize Tracking Operations) to generate a unique QR code for each name in *names.txt*
* (Optional) Add a square image file to the folder and update its name in *interface.py* to personalize the application

## Using JURASSIC PARK

* Run *interface.py* when you'd like to use the attendance tool
* Select your meeting type
* When a QR code is detected, the label text will change to display the name
    * It will only detect names that are in *names.txt*
    * You can safely ignore any "ECI is not supported properly" warnings
* Select sign in/out as desired
* To shut down JURASSIC PARK, use the X button in the upper right.
    * Data will auto-update on the Google Sheet if you have WiFi
    * If not, it will create 3 csv files with the meeting information (can copy-paste into your Google Sheet later)


## Help

### Tips and Tricks

* You can modify *AttendanceClass.py* to adjust how time is awarded for team members who forget to sign in/out
    * Currently - students who forget to sign in get at most 1 hour, and students who sign in, forget to sign out, and sign in again get at most 5 minutes for their initial session
* Make sure all present students have signed out before shutting down JURASSIC PARK in order for them to receive proper time credit
* Getting the "rainbow spinning mouse" (or Windows equivalent) while starting or shutting down JURASSIC PARK is normal application behavior. It goes away within a few seconds.

### More Resources for Google Sheets Integration

* [PyGSheets Directions](https://pygsheets.readthedocs.io/en/stable/authorization.html)
* [Blog Post with Directions](https://erikrood.com/Posts/py_gsheets.html$0)

### General Troubleshooting

* Make sure all dependencies are installed correctly
* It is *strongly* recommended to use VSCode (or anything but the default Python IDE) when working with JURASSIC PARK
