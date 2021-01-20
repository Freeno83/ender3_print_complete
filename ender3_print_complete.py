"""
This script is used to detect when a 3D print is complete on an ender 3 V2 printer
When it sees the text M31 accross the serial connection it will take a photo
The photo is then sent over email giving notification that the print is done
A laptop camera should be pointed at the printer and the laptop connected to the printer via USB
"""

#Library imports
import os
import cv2
import serial
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


#User defined variables
"""
Make sure the "CH341ser.exe" driver is installed
typically you can see which port in device manager or in Arduino IDE
"""
com_port = "COM27"

"""Must setup 2FA in gmail and use the app password, not your normal password"""
address = "email@gmail.com"
password = "app_password"


def detect_M31(com_port, baudrate=115200):
    """Connect to Ender3 V2 serial port and wait for the print to end"""

    ender3 = serial.Serial(port=com_port, baudrate=baudrate)
    buffer_size = 0

    while True:
        while buffer_size < 1:
            buffer_size = ender3.in_waiting

        text = str(ender3.read_until())

        if "M31" in text:
            print(f"M31 found in: {text}")
            break

        ender3.reset_input_buffer()


def capture_image():
    """Take a photo of the printing bed with laptop web camera"""

    img_name = "3D_Print_Complete.png"

    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    cv2.imwrite(img_name, frame)
    cam.release()

    return img_name


def send_email(img_name, address, password):
    """Takes an image path and sends it as an email"""

    try:
        with open(img_name, "rb") as f:
            img_data = f.read()
            
        msg = MIMEMultipart()
        msg["subject"] = "3D Printing Complete"
        msg["to"] = address
        msg["from"] = address

        image = MIMEImage(img_data, name=os.path.basename(img_name))
        msg.attach(image)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(address, password)
        server.send_message(msg)
        server.quit()

        print("Email with photo attachment sent successfully!")

    except:
        print("Error sending e-mail, please check code")


#Main sequence
detect_M31(com_port)
send_email(img_name=capture_image(),
           address=address,
           password=password)
