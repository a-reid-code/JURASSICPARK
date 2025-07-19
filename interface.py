"""
Runs the GUI for JURASSIC PARK
"""

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2

from attendance_class import AttendanceTracker

# create attendance object

with open("names.txt", encoding="utf-8") as f:
    text = f.read()
members = text.splitlines()
attendance = AttendanceTracker(members)

print("Welcome to JURASSIC PARK")
print("which stands for")
print("Joint User Record for Attendance Scanning - Storing Information on Crew - Providing Accurate Robotics Knowledge")


# opening screen

root = tk.Tk()
root.geometry("200x150")
root.title("setup")
# lock aspect ratio - no need to resize
root.resizable(width=False, height=False)

display_text = tk.Label(root, text="Choose your meeting type:")
meeting_type = tk.StringVar(value="None")

def outreach_command():
    """
    Sets meeting type to outreach
    """
    meeting_type.set("outreach")
    attendance.set_type(meeting_type.get())
    root.destroy()

def meeting_command():
    """
    Sets meeting type to regular meeting
    """
    meeting_type.set("meeting")
    attendance.set_type(meeting_type.get())
    root.destroy()

outreach_button = tk.Button(root, text="OUTREACH", command=outreach_command)
meeting_button = tk.Button(text="MEETING", command=meeting_command)

display_text.pack(pady=10)
outreach_button.pack(pady=10)
meeting_button.pack(pady=10)

root.mainloop()


# main GUI

# Set desired video display size and start GUI
VIDEO_WIDTH = 400
VIDEO_HEIGHT = 300

root = tk.Tk()
root.geometry(f"{VIDEO_WIDTH+400}x{VIDEO_HEIGHT+100}")
root.configure(background="#FFEE8C")
root.title("JURASSIC PARK")
# lock aspect ratio - no need to resize
root.resizable(width=False, height=False)

# establish JURASSIC PARK layout

cap = cv2.VideoCapture(0)
detector = cv2.QRCodeDetector()

# frame for video with fixed size

video_frame = tk.Frame(root, width=VIDEO_WIDTH, height=VIDEO_HEIGHT, bg="black")
video_frame.pack(side=tk.LEFT, padx=10, pady=10)
video_frame.pack_propagate(False)

# label inside video_frame to show video

video_label = tk.Label(video_frame)
video_label.pack()

# right side frame for info

info_frame = tk.Frame(root, width=400, height=VIDEO_HEIGHT, background="blue")
info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
info_frame.pack_propagate(False)

# information frames

top_row = tk.Frame(info_frame, height=75, background="grey")
top_row.pack(side=tk.TOP, fill=tk.X)

button_row = tk.Frame(info_frame, height=75, background="#FFEE8C")
button_row.pack(fill=tk.X)
button_row.pack_propagate(False)

bottom_row = tk.Frame(info_frame,width=400, background="#FFEE8C")
bottom_row.pack(fill=tk.BOTH, expand=True)

bottom_left = tk.Frame(bottom_row, width=200, background="#FFEE8C")
bottom_left.pack(side=tk.LEFT, fill=tk.X)


# header/end meeting things

header_frame = tk.Frame(top_row, width=300, height=75, background="#FFEE8C")
header_frame.pack(side=tk.LEFT)
header_frame.pack_propagate(False)

close_frame = tk.Frame(top_row, width=100, height=75, background="#FFEE8C")
close_frame.pack(side=tk.LEFT)
close_frame.pack_propagate(False)

result_label = tk.Label(header_frame, text="Waiting for QR code...", font=("Arial", 16))
result_label.pack(pady=20)

# storage for most recent QR code scan

current_name = tk.StringVar(value="None")

# close window button

def close_window():
    """
    Prompts pop-up for closing the JURASSIC PARK window.
    Closes window if user accepts pop-up.
    """

    val = messagebox.askokcancel(message="Make sure all team members in attendance have signed out before closing JURASSIC PARK.")

    if val:
        root.destroy()

close_button = tk.Button(close_frame, text="X", command=close_window)
close_button.config(highlightbackground="red")
close_button.pack(pady=20)


# sign in and out buttons

def sign_in_clicked():
    """
    Signs in a team member after they scan their QR code
    """

    attendance.sign_in(current_name.get())
    in_button.pack_forget()
    out_button.pack_forget()

    present_list.delete(0, tk.END)
    for name in attendance.humans_in_meeting():
        present_list.insert(tk.END, name)
    result_label.config(text="Waiting for QR code...")

def sign_out_clicked():
    """
    Signs out a team member after they scan their QR code
    """

    attendance.sign_out(current_name.get())
    in_button.pack_forget()
    out_button.pack_forget()

    present_list.delete(0, tk.END)
    for name in attendance.humans_in_meeting():
        present_list.insert(tk.END, name)
    result_label.config(text="Waiting for QR code...")

in_button = tk.Button(button_row, text="Sign In", command=sign_in_clicked)
in_button.configure(highlightbackground="green")

out_button = tk.Button(button_row, text="Sign Out", command=sign_out_clicked)
out_button.configure(highlightbackground="red")


# people who are present - scrollable list

present_header = tk.Label(bottom_left, text="Currently In Meeting:")
present_header.pack(pady=2)

present_list = tk.Listbox(bottom_left)
present_list.configure(highlightbackground="blue", highlightthickness=2)
present_list.pack(fill=tk.X)


# aesthetic team logo option

img_width, img_height = 175, 175

img_frame = tk.Frame(bottom_row, width=img_width, height=img_height, background="white")
img_frame.pack(side=tk.RIGHT)
img_frame.pack_propagate(False)


# TODO - replace with your team logo
img = Image.open("logo.png")
resized_img = img.resize((img_width,img_height))
tk_img = ImageTk.PhotoImage(resized_img)
image_label = tk.Label(img_frame, image=tk_img)
image_label.image = tk_img
image_label.pack(fill=tk.BOTH, expand=True)


# QR scanning loop

def update():
    """
    Handles QR code reading/updating
    """

    ret, frame = cap.read()
    if ret:
        # Resize the frame to fit the video_label size exactly
        frame = cv2.resize(frame, (VIDEO_WIDTH, VIDEO_HEIGHT))

        # Detect QR code
        data, bbox, _ = detector.detectAndDecode(frame)
        if data:
            if attendance.valid_scan(data, bbox):
                current_name.set(data)

                # show sign in info
                result_label.config(text=f"QR Code: {data}")
                in_button.pack(padx=(100, 10), pady=5, side=tk.LEFT, anchor="n")
                out_button.pack(padx=10, pady=5, side=tk.LEFT, anchor="n")

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(frame))

        # Update the label with the image
        video_label.imgtk = img
        video_label.config(image=img)

    root.after(10, update)


# runs app
update()
root.mainloop()


# once app is closed - get rid of openCV processes
cap.release()
cv2.destroyAllWindows()


# end of meeting behavior
attendance.sign_all_out()
attendance.push_meeting_data()
