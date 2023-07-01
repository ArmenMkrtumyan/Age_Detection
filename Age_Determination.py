#!/usr/bin/env python
# coding: utf-8

# # Imports

# In[1]:


#get_ipython().run_line_magic('matplotlib', 'tk')

from customtkinter import *
from PIL import ImageTk, Image
import serial
import time
import pandas as pd
import numpy as np
import sys
import glob
import serial
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from tkinter import filedialog
import os
from datetime import datetime
from matplotlib.widgets import Slider, CheckButtons, Button
from tkinter import messagebox
import configparser
import adafruit_fingerprint

#Images
background  = './icons_backgrounds/main_background.jpeg'
startt      = './icons_backgrounds/start_recording.png'
touch_id    = './icons_backgrounds/touch_id.png'
folder      = './icons_backgrounds/folder.png'
plott       = './icons_backgrounds/plot.png'
information = './icons_backgrounds/info.png'

# # Serial Ports

# In[2]:


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        messagebox.showerror('Serial Port Error', 'Error: Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

print(serial_ports())


# # Get Scanned Picture

# In[3]:


def show_button(grid_frame, start_button, path_opt, fingerprint_path):
    global fingerprint_button
    fingerprint_path = path_opt
    fingerprint_button=CTkButton(grid_frame, text = 'Fingerprint',
                                 font=('calibre',12, 'bold'),
                                 command = lambda: get_picture(fingerprint_path),
                                 width = 110, height = 25, fg_color = "navy",
                                 hover_color = "cornflowerblue",
                                 image = CTkImage(light_image= Image.open(touch_id),
                                                  size=(25, 25)), compound='right')
    start_button.grid_forget()
    fingerprint_button.grid(row=1,column=5)
    #For MacOs
    fingerprint_button.bind("<Enter>", lambda event: show_tooltip(event, "Scan the finger"))
    fingerprint_button.bind("<Leave>", lambda event: hide_tooltip(event, tooltip))
def hide_button():
    fingerprint_button.grid_forget()
    start_button.grid(row=1,column=5)
def get_picture(path):
    # SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
    # SPDX-License-Identifier: MIT

    # import board
    # uart = busio.UART(board.TX, board.RX, baudrate=57600)
    # ports=[];
    # for port in list(serial.tools.list_ports.comports()):
    #     ports.append(port.device)
    #     time.sleep(0.5)
    #     ser = serial.Serial(port=port.device, baudrate=115200, timeout=.1)
    #     print('port: {}, ser: {}'.format(port.device, ser))

    # If using with a computer such as Linux/RaspberryPi, Mac, Windows with USB/serial converter:

    uart = serial.Serial('/dev/tty.usbserial-210', baudrate=57600, timeout=1)


    #uart = serial.Serial("COM30", baudrate=57600, timeout=1)

    # If using with Linux/Raspberry Pi and hardware UART:
    # uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)

    # If using with Linux/Raspberry Pi 3 with pi3-disable-bt
    # uart = serial.Serial("/dev/ttyAMA0", baudrate=57600, timeout=1)

    finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

    ##################################################


    def get_fingerprint():
        """Get a finger print image, template it, and see if it matches!"""
        print("Waiting for image...")
        while finger.get_image() != adafruit_fingerprint.OK:
            pass
        print("Templating...")
        if finger.image_2_tz(1) != adafruit_fingerprint.OK:
            return False
        print("Searching...")
        if finger.finger_search() != adafruit_fingerprint.OK:
            return False
        return True


    # pylint: disable=too-many-branches
    def get_fingerprint_detail():
        """Get a finger print image, template it, and see if it matches!
        This time, print out each error instead of just returning on failure"""
        print("Getting image...", end="")
        i = finger.get_image()
        if i == adafruit_fingerprint.OK:

            print("Image taken")
        else:
            if i == adafruit_fingerprint.NOFINGER:
                print("No finger detected")
            elif i == adafruit_fingerprint.IMAGEFAIL:
                print("Imaging error")
            else:
                print("Other error")
            return False

        print("Templating...", end="")
        i = finger.image_2_tz(1)
        if i == adafruit_fingerprint.OK:
            print("Templated")
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                print("Image too messy")
            elif i == adafruit_fingerprint.FEATUREFAIL:
                print("Could not identify features")
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                print("Image invalid")
            else:
                print("Other error")
            return False

        print("Searching...", end="")
        i = finger.finger_fast_search()
        # pylint: disable=no-else-return
        # This block needs to be refactored when it can be tested.
        if i == adafruit_fingerprint.OK:
            print("Found fingerprint!")
            return True
        else:
            if i == adafruit_fingerprint.NOTFOUND:
                print("No match found")
            else:
                print("Other error")
            return False


    # pylint: disable=too-many-statements
    def enroll_finger(location):
        """Take a 2 finger images and template it, then store in 'location'"""
        for fingerimg in range(1, 3):
            if fingerimg == 1:
                print("Place finger on sensor...", end="")
            else:
                print("Place same finger again...", end="")

            while True:
                i = finger.get_image()
                if i == adafruit_fingerprint.OK:
                    print("Image taken")
                    break
                if i == adafruit_fingerprint.NOFINGER:
                    print(".", end="")
                elif i == adafruit_fingerprint.IMAGEFAIL:
                    print("Imaging error")
                    return False
                else:
                    print("Other error")
                    return False

            print("Templating...", end="")
            i = finger.image_2_tz(fingerimg)
            if i == adafruit_fingerprint.OK:
                print("Templated")
            else:
                if i == adafruit_fingerprint.IMAGEMESS:
                    print("Image too messy")
                elif i == adafruit_fingerprint.FEATUREFAIL:
                    print("Could not identify features")
                elif i == adafruit_fingerprint.INVALIDIMAGE:
                    print("Image invalid")
                else:
                    print("Other error")
                return False

            if fingerimg == 1:
                print("Remove finger")
                time.sleep(1)
                while i != adafruit_fingerprint.NOFINGER:
                    i = finger.get_image()

        print("Creating model...", end="")
        i = finger.create_model()
        if i == adafruit_fingerprint.OK:
            print("Created")
        else:
            if i == adafruit_fingerprint.ENROLLMISMATCH:
                print("Prints did not match")
            else:
                print("Other error")
            return False

        print("Storing model #%d..." % location, end="")
        i = finger.store_model(location)
        if i == adafruit_fingerprint.OK:
            print("Stored")
        else:
            if i == adafruit_fingerprint.BADLOCATION:
                print("Bad storage location")
            elif i == adafruit_fingerprint.FLASHERR:
                print("Flash storage error")
            else:
                print("Other error")
            return False

        return True


    def save_fingerprint_image(filename):
        """Scan fingerprint then save image to filename."""
        while finger.get_image():
            pass

        # let PIL take care of the image headers and file structure
        from PIL import Image  # pylint: disable=import-outside-toplevel

        img = Image.new("L", (256, 288), "white")
        pixeldata = img.load()
        mask = 0b00001111
        result = finger.get_fpdata(sensorbuffer="image")

        # this block "unpacks" the data received from the fingerprint
        #   module then copies the image data to the image placeholder "img"
        #   pixel by pixel.  please refer to section 4.2.1 of the manual for
        #   more details.  thanks to Bastian Raschke and Danylo Esterman.
        # pylint: disable=invalid-name
        x = 0
        # pylint: disable=invalid-name
        y = 0
        # pylint: disable=consider-using-enumerate
        for i in range(len(result)):
            pixeldata[x, y] = (int(result[i]) >> 4) * 17
            x += 1
            pixeldata[x, y] = (int(result[i]) & mask) * 17
            if x == 255:
                x = 0
                y += 1
            else:
                x += 1

        if not img.save(filename):
            return True
        return False


    ##################################################


    def get_num(max_number):
        """Use input() to get a valid number from 0 to the maximum size
        of the library. Retry till success!"""
        i = -1
        while (i > max_number - 1) or (i < 0):
            try:
                i = int(input("Enter ID # from 0-{}: ".format(max_number - 1)))
            except ValueError:
                pass
        return i


    # while True:
    #     print("----------------")
    #     if finger.read_templates() != adafruit_fingerprint.OK:
    #         raise RuntimeError("Failed to read templates")
    #     print("Fingerprint templates: ", finger.templates)
    #     if finger.count_templates() != adafruit_fingerprint.OK:
    #         raise RuntimeError("Failed to read templates")
    #     print("Number of templates found: ", finger.template_count)
    #     if finger.read_sysparam() != adafruit_fingerprint.OK:
    #         raise RuntimeError("Failed to get system parameters")
    #     print("Size of template library: ", finger.library_size)
    #     print("e) enroll print")
    #     print("f) find print")
    #     print("d) delete print")
    #     print("s) save fingerprint image")
    #     print("r) reset library")
    #     print("q) quit")
    #     print("----------------")
    #     c = input("> ")

    #     if c == "e":
    #         enroll_finger(get_num(finger.library_size))
    #     if c == "f":
    #         if get_fingerprint():
    #             print("Detected #", finger.finger_id,
    #                   "with confidence", finger.confidence)
    #         else:
    #             print("Finger not found")
    #     if c == "d":
    #         if finger.delete_model(get_num(finger.library_size)) == adafruit_fingerprint.OK:
    #             print("Deleted!")
    #         else:
    #             print("Failed to delete")
    #     if c == "s":
    #         if save_fingerprint_image("fingerprint.png"):
    #             print("Fingerprint image saved")
    #         else:
    #             print("Failed to save fingerprint image")
    #     if c == "r":
    #         if finger.empty_library() == adafruit_fingerprint.OK:
    #             print("Library empty!")
    #         else:
    #             print("Failed to empty library")
    #     if c == "q":
    #         print("Exiting fingerprint example program")
    #         raise SystemExit
    save_fingerprint_image(path[:-7] + "FPT.png")

    img = CTkImage(light_image=Image.open(path[:-7] + "FPT.png"),
                                  size=(350, 350))
    label = CTkLabel(root, image = img, text = "")
    label.image = img
    label.grid(padx= 80, pady= 170)

    hide_button()


# # Graph the data

# In[4]:


def graph(path_imu, path_opt):
    global save_button, check_buttons_1, check_buttons_2, check_buttons_3, check_buttons_4

    if(path_imu[-31] != '0'):
        graph_name = "Age " + path_imu[-31:-29]+", " + path_imu[-21:-8]
    else:
        graph_name = "Age " + path_imu[-30]+", " + path_imu[-21:-8]
    graph_name_path = path_imu[-31:-29] + "_" + path_imu[-21:-8]
    graph_path = '/'.join(path_imu.split('/')[:-3]) + '/Plots/' + graph_name_path + '.png'

    def save(event):
        button_axis.set_visible(False)
        fig.savefig(graph_path)
        plt.close(fig)

    def set_visibility(lines, axis):
        visible_lines = [i for i in lines if i.get_visible()]
        if(visible_lines):
            visible_range_y = [[max(i.get_data()[1]), min(i.get_data()[1])] for i in visible_lines]
            minimum = min(min(i) for i in visible_range_y)
            maximum = max(max(i) for i in visible_range_y)
            axis.set_ylim(minimum-0.01, maximum+0.01)

    IMU = pd.read_csv(path_imu, index_col="time_millisec")
    OPT = pd.read_csv(path_opt, index_col="num")

    fig = plt.figure(figsize=(14, 14)) #Creating the figure

    ax_1 = fig.add_subplot(4, 1, 1) #Adding axes
    ax_2 = fig.add_subplot(4, 1, 2) #Adding axes
    ax_3 = fig.add_subplot(4, 1, 3) #Adding axes
    ax_4 = fig.add_subplot(4, 1, 4) #Adding axes

    plt.subplots_adjust(hspace=0.6, right=0.8)

    x_1 = IMU.index / 100 * 2

    max_1_1 = max(abs(IMU['acc_x']))
    y_1_1 = IMU['acc_x'] / max_1_1
    max_1_2 = max(abs(IMU['acc_y']))
    y_1_2 = IMU['acc_y'] / max_1_2
    max_1_3 = max(abs(IMU['acc_z']))
    y_1_3 = IMU['acc_z'] / max_1_3

    max_2_1 = max(abs(IMU['gyro_x']))
    y_2_1 = IMU['gyro_x'] / max_2_1
    max_2_2 = max(abs(IMU['gyro_y']))
    y_2_2 = IMU['gyro_y'] / max_2_2
    max_2_3 = max(abs(IMU['gyro_z']))
    y_2_3 = IMU['gyro_z'] / max_2_3

    max_3_1 = max(abs(IMU['mag_x']))
    y_3_1 = IMU['mag_x'] / max_3_1
    max_3_2 = max(abs(IMU['mag_y']))
    y_3_2 = IMU['mag_y'] / max_3_2
    max_3_3 = max(abs(IMU['mag_z']))
    y_3_3 = IMU['mag_z'] / max_3_3

    x_2 = OPT.index / 100

    max_4_1 = max(abs(OPT['ppg_sig1']))
    y_4_1 = OPT['ppg_sig1'] / max_4_1
    max_4_2 = max(abs(OPT['ppg_sig2']))
    y_4_2 = OPT['ppg_sig2'] / max_4_2
    max_4_3= max(abs(OPT['ppg_sig3']))
    y_4_3 = OPT['ppg_sig3'] / max_4_3

    fontdict = {
        'fontsize': 10,
        'fontweight': 1,
        'color': "blue",
        'verticalalignment': 'baseline',
        'horizontalalignment': 'center'
        }

    #Ax 1 --------------------------------------------------------

    ax_1.autoscale_view()

    line_1_1, = ax_1.plot(x_1, y_1_1, color = "Red", label = 'acc_x',
                      ls = "-", scalex = True, alpha = 0.8,
                       visible = True, zorder = 2.5)
    line_1_2, = ax_1.plot(x_1, y_1_2, color = "Green", label = 'acc_y',
                      ls = "-", scalex = True, alpha = 0.8,
                       visible = True, zorder = 2.5)
    line_1_3, = ax_1.plot(x_1, y_1_3, color = "Blue", label = 'acc_z',
                      ls = "-", scalex = True, alpha = 0.8,
                       visible = True, zorder = 2.5)

    #Ax 2 --------------------------------------------------------

    ax_2.autoscale_view()

    line_2_1, = ax_2.plot(x_1, y_2_1, color = "Red", label = "gyro_x",
                      ls = "-", scalex = True, alpha = 0.8,
                       visible = True, zorder = 2.5)
    line_2_2, = ax_2.plot(x_1, y_2_2, color = "Green", label = "gyro_y",
                      ls = "-", scalex = True, alpha = 0.8,
                       visible = True, zorder = 2.5)
    line_2_3, = ax_2.plot(x_1, y_2_3, color = "Blue", label = "gyro_z",
                      ls = "-", scalex = True, alpha = 0.8,
                       visible = True, zorder = 2.5)

    #Ax 3 --------------------------------------------------------

    ax_3.autoscale_view()

    line_3_1, = ax_3.plot(x_1, y_3_1, color = "Red", label = "mag_x",
                      ls = "-", scalex = True, alpha = 0.8,
                       visible = True, zorder = 2.5)
    line_3_2, = ax_3.plot(x_1, y_3_2, color = "Green", label = "mag_y",
                      ls = "-", scalex = True, alpha = 0.8,
                       visible = True, zorder = 2.5)
    line_3_3, = ax_3.plot(x_1, y_3_3, color = "Blue", label = "mag_z",
                      ls = "-", scalex = True, alpha = 0.8,
                       visible = True, zorder = 2.5)

    #Ax 4 --------------------------------------------------------

    ax_4.autoscale_view()

    line_4_1, = ax_4.plot(x_2, y_4_1, color = "Red", label = "ppg_sig1",
                      ls = "-", scalex = True, alpha = 0.8,
                       visible = True, zorder = 2.5)
    line_4_2, = ax_4.plot(x_2, y_4_2, color = "Green", label = "ppg_sig2",
                      ls = "-", scalex = True, alpha = 0.8,
                       visible = True, zorder = 2.5)
    line_4_3, = ax_4.plot(x_2, y_4_3, color = "Blue", label = "ppg_sig3",
                      ls = "-", scalex = True, alpha = 0.8,
                       visible = True, zorder = 2.5)

    #Axis Configurations -----------------------------------------

    ax_title = ax_1.set_title(graph_name, y = 1.2, fontdict = {'fontsize' : 12})

    ax_1_y_label = ax_1.set_ylabel("Accelerometer",
                                fontdict = fontdict)
    ax_2_y_label = ax_2.set_ylabel("Gyroscope",
                                fontdict = fontdict)
    ax_3_y_label = ax_3.set_ylabel("Magnetometer",
                                fontdict = fontdict)
    ax_4_y_label = ax_4.set_ylabel("PPG",
                                fontdict = fontdict)
    x_4_label = ax_4.set_xlabel("Time (seconds)")

    #Label Configurations ----------------------------------------

    acc_lines   = [line_1_1, line_1_2, line_1_3]
    gyro_lines  = [line_2_1, line_2_2, line_2_3]
    mag_lines   = [line_3_1, line_3_2, line_3_3]
    ppg_lines   = [line_4_1, line_4_2, line_4_3]

    acc_labels  = [line_1_1.get_label(), line_1_2.get_label(), line_1_3.get_label()]
    gyro_labels = [line_2_1.get_label(), line_2_2.get_label(), line_2_3.get_label()]
    mag_labels  = [line_3_1.get_label(), line_3_2.get_label(), line_3_3.get_label()]
    ppg_labels  = [line_4_1.get_label(), line_4_2.get_label(), line_4_3.get_label()]

    check_ax_1 = plt.axes([0.83, 0.80, 0.07, 0.07])
    check_ax_2 = plt.axes([0.83, 0.59, 0.07, 0.07])
    check_ax_3 = plt.axes([0.83, 0.38, 0.07, 0.07])
    check_ax_4 = plt.axes([0.83, 0.17, 0.07, 0.07])


    initial_state = [True, True, True]

    check_buttons_1 = CheckButtons(check_ax_1, acc_labels, initial_state)
    check_buttons_2 = CheckButtons(check_ax_2, gyro_labels, initial_state)
    check_buttons_3 = CheckButtons(check_ax_3, mag_labels, initial_state)
    check_buttons_4 = CheckButtons(check_ax_4, ppg_labels, initial_state)

    check_buttons_rects_1 = check_buttons_1.rectangles
    check_buttons_rects_2 = check_buttons_2.rectangles
    check_buttons_rects_3 = check_buttons_3.rectangles
    check_buttons_rects_4 = check_buttons_4.rectangles

    check_buttons_labels_1 = check_buttons_1.labels
    check_buttons_labels_2 = check_buttons_2.labels
    check_buttons_labels_3 = check_buttons_3.labels
    check_buttons_labels_4 = check_buttons_4.labels

    label_colors = ['red', 'green', 'blue']
    for label, color in zip(check_buttons_labels_1, label_colors):
        label.set_color(color)
    for label, color in zip(check_buttons_labels_2, label_colors):
        label.set_color(color)
    for label, color in zip(check_buttons_labels_3, label_colors):
        label.set_color(color)
    for label, color in zip(check_buttons_labels_4, label_colors):
        label.set_color(color)

    def func_1(label):
        index = acc_labels.index(label)
        acc_lines[index].set_visible(not acc_lines[index].get_visible())
        set_visibility(acc_lines, ax_1)
        plt.draw()
    def func_2(label):
        index = gyro_labels.index(label)
        gyro_lines[index].set_visible(not gyro_lines[index].get_visible())
        set_visibility(gyro_lines, ax_2)
        plt.draw()
    def func_3(label):
        index = mag_labels.index(label)
        mag_lines[index].set_visible(not mag_lines[index].get_visible())
        set_visibility(mag_lines, ax_3)
        plt.draw()
    def func_4(label):
        index = ppg_labels.index(label)
        ppg_lines[index].set_visible(not ppg_lines[index].get_visible())
        set_visibility(ppg_lines, ax_4)
        plt.draw()

    check_buttons_1.on_clicked(func_1)
    check_buttons_2.on_clicked(func_2)
    check_buttons_3.on_clicked(func_3)
    check_buttons_4.on_clicked(func_4)

    button_axis = plt.axes([0.89, 0.03, 0.05, 0.05])
    save_button = Button(button_axis, 'Save', color='gray', hovercolor='green')
    save_button.on_clicked(save)
    root.update()
    plt.show()


# In[5]:


# def set_visibility(lines, axis):
#     #OR
#     #axis.relim()
#     visible_lines = [i for i in lines if i.get_visible()]
#     if(visible_lines):
#         visible_range_y = [[max(i.get_data()[1]), min(i.get_data()[1])] for i in visible_lines]
#         minimum = min(min(i) for i in visible_range_y)
#         maximum = max(max(i) for i in visible_range_y)
#         axis.set_ylim(minimum-1, maximum+1)
#def graph(root, path_opt, path_imu, graph_name, graph_path):

def select_graph(database_path):
    if not os.path.exists(database_path):
        messagebox.showerror('Path Error', 'Error: Given Path not found\n')
    else:
        file_names = filedialog.askdirectory(initialdir=database_path)
        all_files = os.listdir(file_names)
        all_files = [file for file in all_files if file[-7:]=='IMU.csv']
        #print(all_files)
        selected_file = 0
        def get_selected_filename(var, window):
            nonlocal selected_file
            selected_file = var.get()
            print(selected_file)
            window.destroy()
            final_path = file_names + '/' + selected_file
            path_IMU = final_path
            path_OPT = final_path[:-7] + 'OPT.csv'
            graph(path_IMU, path_OPT)


        def create_selection_window(filenames):
            selection_window = CTkToplevel()
            selection_window.title("Select a File")
            #selection_window.geometry("+%d+%d" %(520,0))
            selection_window.geometry("+%d+%d" %(520,0))

            var = StringVar()

            for filename in filenames:
                radiobutton = CTkRadioButton(selection_window, text=filename, variable=var, value=filename)
                radiobutton.pack(anchor='w')

            select_button = CTkButton(selection_window, text="Select", fg_color = "navy", hover_color = "cornflowerblue",
                                      command= lambda: get_selected_filename(var, selection_window))
            select_button.pack()

            selection_window.mainloop()

        # Example usage
        filenames = sorted(all_files)
        create_selection_window(filenames)


# # Helper Functions

# In[6]:


def browsefunc(database_path):
    filename = filedialog.askdirectory()
    database_path.set(filename+'/')
def preambula_check(ser):
    preambula_status = 0
    preambula_count = 0
    while not preambula_status:
        byte = int.from_bytes(ser.read(1), byteorder='big')
        # print("b: ", byte)
        match preambula_count:
            case 0:
                preambula_count = 1 if byte == 0xAA else 0
            case 1:
                preambula_count = 2 if byte == 0x55 else 0
            case 2:
                preambula_count = 3 if byte == 0xAA else 0
            case 3:
                preambula_status = 1 if byte == 0x55 else 0
    return preambula_status
def send_command(ser, com_code, config_code):
    ser.write(bytes([com_code, config_code]))
def get_sensor_info(ser):
    fs=0; num_of_channels=0; num_of_bytes=0;
    # preamb = int.from_bytes(ser.read(4), byteorder='big')
    # print('preamb:', preamb)
    # if preamb==2857740885:
    if preambula_check(ser):
        fs=int.from_bytes(ser.read(2), byteorder='little')
        num_of_channels=int.from_bytes(ser.read(1), byteorder='big')
        num_of_bytes=int.from_bytes(ser.read(1), byteorder='big')
    return fs, num_of_channels, num_of_bytes


# # Data

# In[7]:


def dump_data_esp(df_data_opt, df_data_imu, path_opt, path_imu, grid_frame, start_button, fingerprint_path):
    indct = 0
    if df_data_opt.shape[0] > 0:
        print('ppg data sizes: ', df_data_opt.shape)
        indct += 1
        print(path_opt)
        df_data_opt.to_csv(path_opt, index=False)
        print('ESP: opt data saved')

    if df_data_imu.shape[0] > 0:
        print('IMU data sizes: ', df_data_imu.shape)
        indct += 1
        df_data_imu.to_csv(path_imu, index=False)
        print('ESP: IMU data saved')
    show_button(grid_frame, start_button, path_opt, fingerprint_path)
    return indct
def receive_data(ser, duration):
    com_code = 7

    start_time = 0;
    # ----------------------------
#    duration = 10

    sum_time = 0
    since = time.time()

    #------------ Get Sensors INFO -----------------
    send_command(ser, 127, com_code)
    since1 = time.time()
    while ser.in_waiting==0:
        pass
    fs_opt, num_of_channels_opt, num_of_bytes_opt = get_sensor_info(ser)
    print('OPT info: fs={}, num_of_channels={}, num_of_bytes={}'.format(fs_opt, num_of_channels_opt, num_of_bytes_opt))
    counter21=0; counter22=0; counter23=0;
    data_ppg1 = np.zeros((int((duration) * fs_opt), num_of_channels_opt + 1), dtype=int)
    data_ppg2 = np.zeros((int((duration) * fs_opt), num_of_channels_opt + 1), dtype=int)
    data_ppg3 = np.zeros((int((duration) * fs_opt), num_of_channels_opt + 1), dtype=int)
    #-----------

    fs_imu, num_of_channels_imu, num_of_bytes_imu = get_sensor_info(ser)
    print('IMU info: fs={}, num_of_channels={}, num_of_bytes={}'.format(fs_imu, num_of_channels_imu, num_of_bytes_imu))
    time_elapsed = time.time() - since1
    print('time_elapsed: {:.1f} sec, duration: {}\n'.format(time_elapsed, duration))
    counter41=0;
    num_of_channels_imu=3*num_of_channels_imu;
    data_imu= np.zeros((int((duration) * fs_imu), num_of_channels_imu + 1), dtype=int)
    sample_counter21=0; sample_counter22=0; sample_counter41=0;

    #----------- START -----------------
    print('Start recording: ESP32')
    since = time.time()
    send_command(ser, 0, com_code) # start + sensors
    # ----------------------------
    sum_time = 0
    since = time.time()
    sample = True
    while sample:
        preamb = int.from_bytes(ser.read(4), byteorder='big')
        if preamb==2857740885:
            # print("preamb: ", preamb)
            sensor_id = int.from_bytes(ser.read(1), byteorder='big')
            # print("sensor_id: ", sensor_id)
            if sensor_id==1:
                sample_counter21 = np.uint8(int.from_bytes(ser.read(1), byteorder='big'))
                if counter21==0:
                    prev_counter21 = sample_counter21
                if sample_counter21-prev_counter21>1:
                    print('counter21: {}, diff1: {}, cur: {}, prev: {}'.format(counter21, sample_counter21-prev_counter21, sample_counter21, prev_counter21))
                prev_counter21 = sample_counter21
                if counter21 < data_ppg1.shape[0]:
                    data_ppg1[counter21, 0] = counter21 + 1
                    for cur_inx1 in range(num_of_channels_opt):
                        current1 = int.from_bytes(ser.read(4), byteorder='little', signed=False)
                        # print('#{}, {}'.format(sensor_id, current1))
                        data_ppg1[counter21, cur_inx1 + 1] = current1
                counter21 += 1

            elif sensor_id==2:
                sample_counter22 = np.uint8(int.from_bytes(ser.read(1), byteorder='big'))
                if counter22==0:
                    prev_counter22 = sample_counter22
                if sample_counter22-prev_counter22>1:
                    print('counter22: {}, diff2: {}, cur: {}, prev: {}'.format(counter22, sample_counter22-prev_counter22, sample_counter22, prev_counter22))
                prev_counter22 = sample_counter22
                if counter22 < data_ppg2.shape[0]:
                    data_ppg2[counter22, 0] = counter22 + 1
                    for cur_inx2 in range(num_of_channels_opt):
                        current2 = int.from_bytes(ser.read(4), byteorder='little', signed=False)
                        # print('#{}, {}'.format(sensor_id,current2))
                        data_ppg2[counter22, cur_inx2 + 1] = current2
                counter22 += 1

            elif sensor_id==3:
                sample_counter23 = np.uint8(int.from_bytes(ser.read(1), byteorder='big'))
                if counter23==0:
                    prev_counter23 = sample_counter23
                if sample_counter23-prev_counter23>1:
                    print('counter23: {}, diff3 {}, cur: {}, prev: {}'.format(counter23, sample_counter23-prev_counter23, sample_counter23, prev_counter23))
                prev_counter23 = sample_counter23
                if counter23 < data_ppg3.shape[0]:
                    data_ppg3[counter23, 0] = counter23 + 1
                    for cur_inx3 in range(num_of_channels_opt):
                        current3 = int.from_bytes(ser.read(4), byteorder='little', signed=False)
                        # print('#{}, {}'.format(sensor_id,current3))
                        data_ppg3[counter23, cur_inx3 + 1] = current3
                counter23 += 1

            elif sensor_id==4:
                sample_counter41 = np.uint8(int.from_bytes(ser.read(1), byteorder='big'))
                if counter41==0:
                    prev_counter41 = sample_counter41
                if sample_counter41-prev_counter41>1:
                    print('counter41: {}, diff4: {}, cur: {}, prev: {}'.format(counter41, sample_counter41-prev_counter41, sample_counter41, prev_counter41))
                prev_counter41 = sample_counter41
                if counter41 < data_imu.shape[0]:
                    data_imu[counter41, 0] = counter41 + 1
                    for cur_inx4 in range(num_of_channels_imu):
                        current4 = int.from_bytes(ser.read(num_of_bytes_imu), byteorder='little', signed=True)
                        data_imu[counter41, cur_inx4 + 1] = current4
                counter41 += 1

            elif sensor_id==255:
                time_esp = int.from_bytes(ser.read(4), byteorder='little', signed=False)
                print("ESP time:{:.1f}".format( time_esp/1000))
                time_elapsed = time.time() - since
                print('time_elapsed: {:.1f}, duration: {}, sum_time:{}\n'.format(time_elapsed, duration, sum_time))
                print('OPT counters:', counter21, counter22, counter23)
                print('IMU counters', counter41)             # send_command(ser, 255, 0)  # stop signal
                sample = False

        if (counter21 >= data_ppg1.shape[0]) and (counter22 >= data_ppg2.shape[0]) and (counter23 >= data_ppg3.shape[0]):
            send_command(ser, 255, 0)  # stop signal

    data_ppg1[0,1] = data_ppg1[1,1]
    data_ppg2[0,1] = data_ppg2[1,1]
    data_ppg3[0,1] = data_ppg3[1,1]

    cols = ['num', 'ppg_sig1', 'ppg_sig2', 'ppg_sig3']
    df_opt1 = pd.DataFrame(data_ppg1)
    df_opt2 = pd.Series(data_ppg2[:,1])
    df_opt3 = pd.Series(data_ppg3[:,1])
    df_data_opt = pd.concat([df_opt1,df_opt2,df_opt3], axis=1)
    df_data_opt.columns=cols
    df_data_opt = df_data_opt.loc[:counter21-1,:]

    print('OPT data shape:', df_data_opt.shape)
    print(df_data_opt[:10])

    cols_imu = ['time_millisec', 'acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z', 'mag_x', 'mag_y', 'mag_z']
    df_data_imu = pd.DataFrame(data_imu, columns=cols_imu)
    print('IMU data shape:', df_data_imu.shape)

    return df_data_opt, df_data_imu
def collect_data(path_opt, path_imu, grid_frame, start_button, duration, fingerprint_path):
#     ports=[];
#     for port in list(serial.tools.list_ports.comports()):
#         ports.append(port.device)
#         time.sleep(0.5)
#         ser = serial.Serial(port=port.device, baudrate=115200, timeout=.1)
#     print('ports:', ports, '\n')

    for i in serial_ports():
        #if i == '/dev/tty.usbserial-51850143861':
        if i == '/dev/tty.usbserial-0001':
            port = i

    ser = serial.Serial(port=port, baudrate=115200, timeout=.1)

    df_data_opt, df_data_imu = receive_data(ser, duration)

    indic = dump_data_esp(df_data_opt, df_data_imu, path_opt, path_imu, grid_frame, start_button, fingerprint_path)
    ser.close()

def save_recording_info_to_db(database_path, path_opt, path_imu, path_fpt, subject_info):
    path_db = database_path + 'metadata.csv'

    cols = ['trial_dir', 'cur_dir', 'record_name', 'age', 'gender', 'duration']
    #df=pd.DataFrame(columns = cols)
    #df.to_csv(path_db, index=False)
    #Excel code
    #writer = pd.ExcelWriter(path_db, engine='xlsxwriter')
    #df.to_excel(writer, sheet_name = "metadata", index=False)
    #xls = pd.ExcelFile(path_db)
    #frames = dict(zip(xls.sheet_names,range(len(xls.sheet_names))))
    print("\nPATH TO DB\n", path_db)
    if not(os.path.isfile(path_db) and os.access(path_db, os.R_OK)):
        messagebox.showerror('Metadata Error', 'Error: Metadata file not found!\n Created a new one')
        cols = ['trial_dir', 'cur_dir', 'record_name', 'age', 'gender', 'duration']
        df=pd.DataFrame(columns = cols)
        df.to_csv(path_db, index=False)
    df = pd.read_csv(path_db)
#    for sheet, frame in frames.items():
#        df_cur= pd.read_excel(path_db, sheet_name=sheet, dtype={'subject': str})
#        df.append(df_cur)
    path_info = path_opt.split('/')
    trial_dir = path_info[-3]
    cur_dir = path_info[-2]
    record_name = (path_info[-1])[:-8]
    duration = subject_info[0]
    age = subject_info[1]
    gender = subject_info[2]
    df.loc[df.shape[0],:] = [trial_dir, cur_dir, record_name, age, gender, duration]

    try:
        #writer = pd.ExcelWriter(path_db, engine='xlsxwriter')
        #for sheet, frame in frames.items():
        #    df[frame].to_excel(writer, sheet_name = sheet, index=False)
        #writer.save()
        df.to_csv(path_db, index=False)
        print('path_db:',path_db)
        messagebox.showinfo('Metadata', 'Metadata saved successfully')
        print('metadata saved')
    except OSError:
        print('File is still open.')


# In[8]:


def start(database_path,recording_folder, duration, gender, age, grid_frame, start_button):

    #For mac
    if(database_path[-1] != '/'):
        database_path = database_path + '/'

    error = False;

    print("Age: ", age)
    #Age
    try:
        if(int(age) < 1 or int(age) > 99):
            messagebox.showerror('Age Error', 'Error: Age is invalid!\n Data not recorded', icon=messagebox.ERROR)
            error = True
    except ValueError:
        messagebox.showerror('Age Error', 'Error: Age must be a number!\n Data not recorded', icon=messagebox.ERROR)
        error = True

    #Database path
    print("Database Path: ", database_path)
    if not os.path.exists(database_path):
        os.makedirs(database_path)
        os.makedirs(str(database_path) + 'Plots/')

    #Recording folder
    print("Recording Folder Name: ", recording_folder)

    #Duration
    print("Duration (sec): ", duration)
    try:
        if(int(duration) < 1 or int(duration) > 120):
            messagebox.showerror('Duration Error', 'Error: Duration is invalid!\n Data not recorded')
            error = True
    except ValueError:
        messagebox.showerror('Duration Error', 'Error: Duration must be a number!\n Data not recorded')
        error = True

    #Gender
    print("Gender: ", gender)

    if(error == False):
        duration = int(duration)

        date = datetime.today().strftime('%y%m%d')
        time = datetime.today().strftime('%H%M%S')

        trial_folder_name = recording_folder
        if (len(age) == 1):
            current_recording_folder = trial_folder_name + '_0' + age + '_' + date
        else:
            current_recording_folder = trial_folder_name + '_' + age + '_' + date
        file_name = datetime.today().strftime('%y%m%d') + '_' + datetime.today().strftime('%H%M%S')

        fingerprint_path = database_path + 'Plots/' + age + "_" + file_name + '.png'

        file_name_opt = file_name + '_OPT.csv'
        file_name_imu = file_name + '_IMU.csv'
        file_name_fpt = file_name + '_FPT.png'

        patient_dir = database_path + trial_folder_name + '/' + current_recording_folder

        path_opt = database_path + trial_folder_name + '/' + current_recording_folder + '/' + file_name_opt
        path_imu = database_path + trial_folder_name + '/' + current_recording_folder + '/' + file_name_imu
        path_fpt = database_path + trial_folder_name + '/' + current_recording_folder + '/' + file_name_fpt

        print("FINAL RESULTS")
        print("Main: ", database_path)
        print("trial folder: ", trial_folder_name)
        print("current rec folder: ", current_recording_folder)
        print("Path_OPT: ", path_opt)
        print("Path_IMU: ", path_imu)
        print("Path_FPT: ", path_fpt)

        if not os.path.exists(patient_dir):
            os.makedirs(patient_dir)

        collect_data(path_opt, path_imu, grid_frame, start_button, duration, fingerprint_path)
        subject_info = [duration, age, gender]
        save_recording_info_to_db(database_path, path_opt, path_imu, path_fpt, subject_info)


# # Main

# In[ ]:


if __name__ == "__main__":

    def show_tooltip(event, text):
        x = event.widget.winfo_rootx() + event.widget.winfo_width()
        y = event.widget.winfo_rooty() + event.widget.winfo_height()
        global tooltip
        tooltip = CTkToplevel(root)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{x}+{y}")
        tooltip_label = CTkLabel(tooltip, text=text, width=10, height=10)
        tooltip_label.grid()
    def hide_tooltip(event, tooltip):
        tooltip.destroy()
    def info():
        information = CTkToplevel(root)
        information.geometry("450x80+0+0")
        information.title("Info")
        # info_frame = CTkFrame(root, fg_color="black")
        # info_frame.place(x=0, y=0)

        version = CTkLabel(information, text_color = "white", text = 'Age Determination v1.0\n This program was created in collaboration with "Tumo Labs" and "Oqni"\n\n Author: Armen Mkrtumyan \n Ⓒ 2023. All rights reserved.', font=('calibre',12, 'bold'),
                             anchor="nw")
        version.place(x=0, y= 0)

    root = CTk()
    root.title("Data logger")
    # Database path
    config = configparser.ConfigParser()
    config.read(r'fingerprint_config.txt')
    default_path = config.get('paths', 'path_recording_mac')
    #default_path = config.get('paths', 'path_recording_windows')

    # Setting the windows size
    root.geometry("500x700+0+0")
    root.minsize(520, 700)
    root.maxsize(520, 700)

    # Declaring string variable for storing Entries
    database_path= StringVar(root)
    recording_folder= StringVar(root)
    duration= StringVar(root)
    gender = StringVar(root)
    age = StringVar(root)

    # Setting entries
    database_path.set(default_path)
    recording_folder.set("BA-001")
    duration.set("2")
    age.set("4")
    gender.set("male")


    root.update()
    img = CTkImage(light_image= Image.open(background) ,
                   size=(520, 635))
    label = CTkLabel(root, image = img, text = "")
    label.image = img
    label.place(x=0,y=100)
    root.update()
    # Creating labels and entries
    grid_frame = CTkFrame(root, fg_color="black")
    grid_frame.place(x=0, y=0)

    database_label = CTkLabel(grid_frame, width = 110, text_color = "white", text = 'Database Path', font=('calibre',12, 'bold'),
                             anchor="w")
    database_entry = CTkEntry(grid_frame, width=260, height = 25, textvariable = database_path,
                              font=('calibre',10,'normal'), corner_radius = 10, border_width = 3)

    recording_label = CTkLabel(grid_frame, width = 70, text_color = "white", text = 'Recording folder', font = ('calibre',12,'bold'),
                               anchor = 'w')
    recording_entry= CTkEntry(grid_frame, width = 110, height = 25, textvariable = recording_folder,
                              font = ('calibre',10,'normal'), corner_radius = 10, border_width = 3)

    Gender_label = CTkLabel(grid_frame, text = 'Gender', text_color = "white",
                        font=('calibre',12, 'bold'), compound = 'left', anchor = 'w')
    gender_dropdown = CTkOptionMenu(grid_frame, dropdown_fg_color = "navy", dropdown_text_color = "white", variable = gender, values = ["male", "female"],fg_color = "navy",
                                    button_hover_color = "cornflowerblue", anchor = 'center', width = 100, height = 20,
                                    dynamic_resizing = True)
    age_entry= CTkEntry(grid_frame, width = 55, height = 25, textvariable = age,
                              font = ('calibre',10,'normal'), corner_radius = 10, border_width = 3)
    age_entry.bind("<Enter>", lambda event: show_tooltip(event, "1-99 years"))
    age_entry.bind("<Leave>", lambda event: hide_tooltip(event, tooltip))
    duration_label = CTkLabel(grid_frame, text = 'Duration',text_color = "white", font = ('calibre',12,'bold'), compound = 'center',
                              anchor = 'center', justify=LEFT)
    duration_entry = CTkEntry(grid_frame, width = 55, height = 25,  font = ('calibre',10,'bold'),
                             corner_radius = 10, border_width = 3, textvariable = duration)
    duration_entry.bind("<Enter>", lambda event: show_tooltip(event, "1-120 seconds"))
    duration_entry.bind("<Leave>", lambda event: hide_tooltip(event, tooltip))

    Age_label = CTkLabel(grid_frame, text = "Age", text_color = "white", font=('calibre',10, 'bold'))


    #Creating buttons

    start_button=CTkButton(grid_frame,text = 'Start          ', font=('calibre',12, 'bold'), fg_color = "navy", hover_color = "cornflowerblue",
                           command = lambda : start(database_path.get(),
                                                    recording_folder.get(),
                                                    duration.get(),
                                                    gender.get(),
                                                    age.get(),
                                                    grid_frame,
                                                    start_button,
                                                    ),
                           width = 110, height = 25,
                          image=CTkImage(light_image= Image.open(startt), size=(25, 25)) , compound = 'right')
    start_button.bind("<Enter>", lambda event: show_tooltip(event, "Start recording"))
    start_button.bind("<Leave>", lambda event: hide_tooltip(event, tooltip))
    browse_button = CTkButton(grid_frame, font=('calibre',12, 'bold'), text="Browse        ", command=lambda: browsefunc(database_path),
                            width = 100, height = 25,fg_color = "navy", hover_color = "cornflowerblue",
                             image=CTkImage(light_image= Image.open(folder) ,
                   size=(25, 25)), compound='right')
    browse_button.bind("<Enter>", lambda event: show_tooltip(event, "Select directory"))
    browse_button.bind("<Leave>", lambda event: hide_tooltip(event, tooltip))
    graph_button = CTkButton(grid_frame, text="Graph       ", font=('calibre',12, 'bold'),
                             command = lambda: select_graph(database_path.get() + recording_folder.get() + '/'),
                              width = 110, height = 25,fg_color = "navy", hover_color = "cornflowerblue",
                             image=CTkImage(light_image= Image.open(plott) ,
                   size=(25, 25)), compound='right')
    graph_button.bind("<Enter>", lambda event: show_tooltip(event, "Select the graph"))
    graph_button.bind("<Leave>", lambda event: hide_tooltip(event, tooltip))
    info_button = CTkButton(grid_frame, font=('calibre',12, 'bold'), text="Info          ", command = info,
                            width = 100, height = 25,fg_color = "navy", hover_color = "cornflowerblue",
                             image=CTkImage(light_image= Image.open(information) ,
                   size=(25, 25)), compound='right')
    browse_button.bind("<Enter>", lambda event: show_tooltip(event, "Additional information"))
    browse_button.bind("<Leave>", lambda event: hide_tooltip(event, tooltip))


    #Putting everything on a grid

    database_label.grid (row=0, column=0, sticky="w", padx=10)
    database_entry.grid (row=0, column=1, sticky="w", columnspan=3)
    recording_label.grid(row=1, column=0, sticky="w", padx=10)
    recording_entry.grid(row=1, column=1, sticky="w")
    duration_label.grid (row=1, column=2, sticky="w")
    duration_entry.grid (row=1, column=3, sticky="w")
    Gender_label.grid   (row=2, column=0, sticky="w", padx=10)
    gender_dropdown.grid(row=2, column=1, sticky="w")
    Age_label.grid      (row=2, column=2, sticky="w")
    age_entry.grid      (row=2, column=3, sticky="w")

    browse_button.grid  (row=0, column=5, sticky="w",padx=10, pady=5)
    start_button.grid   (row=1,column=5, sticky="w",padx=10, pady=5)
    graph_button.grid   (row=2,column=5, sticky="w",padx=10, pady=5)
    info_button.grid    (row=3, column=5, sticky="w", padx=10, pady=5)

    root.mainloop()


# In[ ]:





# In[ ]:





# In[ ]:
