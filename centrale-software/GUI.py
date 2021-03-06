#for Python 3
import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
from ctypes import c_uint8
from time import sleep
from Plot import Plot

#Create a dictionary with info about the tabs
deviceInfo = {
    'tab1' : {'mode' : 'manual', 'status' : 'up'},
    'tab2' : {'mode' : 'manual', 'status' : 'up'},
    'tab3' : {'mode' : 'manual', 'status' : 'up'},
    'tab4' : {'mode' : 'manual', 'status' : 'up'},
    'tab5' : {'mode' : 'manual', 'status' : 'up'}
    }

#Create a list of connected devices via ComPort
connectedDevices = []

#Keeps track of the amount of connected Arduinos
amountOfArduinos = 0

ser = 0
Graph1 = 0
Graph2 = 0

#Checks if there are any new devices connected and activates tabs accordingly    
def checkDevices():
    global connectedDevices
    global amountOfArduinos
    global ser

    #Creates a list and adds the comport from every connected device to it
    arduino_ports = [p.device for p in serial.tools.list_ports.comports()
                     if 'Arduino' in p.description
                     ]

    #If there are no devices found a label gets edited and tabs are deactivated
    if not arduino_ports:
        tkLabelTop['text'] = 'No Arduino found!'
        for x in range(5):
            if (notebook.tab(x, option='state') == 'normal'):
                toggleTab(x)
                connectedDevices[:] = []

    #Compares arduino_ports to amountOfArduinos to see if any devices got disconnected
    #Deactivates tabs and decreases amountOfArduinos accordingly
    if len(arduino_ports) < amountOfArduinos:
        temp = connectedDevices
        toggleTab(len(arduino_ports))
        [connectedDevices.remove(i) for i in arduino_ports if i in temp]
        amountOfArduinos -= 1

    #Compares arduino_ports to amountOfArduinos to see if there are any new devices connected
    #Activates tabs and increases amountOfArduinos accordingly
    if len(arduino_ports) > amountOfArduinos:
        tkLabelTop['text'] = ''
        for x in range(len(arduino_ports)):
            if not (arduino_ports[x] in connectedDevices):
                toggleTab(x)
                connectedDevices.append(arduino_ports[x])
                amountOfArduinos += 1

    #Loops through checkDevices() every 3000 milliseconds
    tkgui.after(5000, checkDevices)

#Shuts down the program
def quit():
    global tkgui
    tkgui.destroy()

#Toggles a tab based on the given deviceID and edits the dictionary deviceInfo
def toggleTab(deviceID):
    if(notebook.tab(deviceID, option='state') == 'normal'):
        notebook.tab(deviceID, state='disabled')
    else:
        notebook.tab(deviceID, state='normal')

#Toggles the screen based on the given tabName and portNumber
def toggleScreen(tabName, portNumber):
    global ser
    if(ser == 0):
        ser = serial.Serial(connectedDevices[portNumber], 9600)
        sleep(3)
    if (deviceInfo[tabName]['status'] == 'up'):
        ser.write(c_uint8(int('0x0b', 16))) #0b = rood lampje aan
        deviceInfo[tabName]['status'] = 'down'
    else:
        ser.write(c_uint8(int('0x0a', 16)))
        deviceInfo[tabName]['status'] = 'up'

#Toggles a label manuel/automatic based on given tabName and labelNumber
def toggleMode(tabName, labelNumber):
    if(deviceInfo[tabName]['mode'] == 'manual'):
        deviceInfo[tabName]['mode'] = 'automatic'
        labelNumber['text'] = 'Mode: %s' % (deviceInfo[tabName]['mode'])
    else:
        deviceInfo[tabName]['mode'] = 'manual'
        labelNumber['text'] = 'Mode: %s' % (deviceInfo[tabName]['mode'])

#Fill a frame in a tab with buttons based on given frameNumber, tabName, labelNumber and portNumber
def fillTab(frameNumber, tabName, labelNumber, portNumber):
    global Graph1, Graph2

    tkToggleScreenButton = tk.Button(
        frameNumber,
        text='Toggle Screen',
        command=lambda: toggleScreen(tabName, portNumber))
    tkToggleScreenButton.grid(column=0, row=1, sticky='W')

    tkToggleModeButton = tk.Button(
        frameNumber,
        text='Toggle mode',
        command=lambda: toggleMode(tabName, labelNumber))
    tkToggleModeButton.grid(column=0, row=2, sticky='W')

    tkGetDataButton = tk.Button(
        frameNumber,
        text='Get data',
        command = getData)
    tkGetDataButton.grid(column=0,row=1, sticky='E')

    temperatureLabel = tk.Label(frameNumber, text='Temperature: ')
    temperatureLabel.grid(column=0, row=5, sticky='W')

    brightnessLabel = tk.Label(frameNumber, text='Brightness: ')
    brightnessLabel.grid(column=1, row=5, sticky='W')
    
    Graph1 = Plot(frameNumber, 0, 6)
    Graph2 = Plot(frameNumber, 1, 6)
    
    labelNumber = tk.Label(frameNumber, text='Mode: %s' % (deviceInfo[tabName]['mode']))
    labelNumber.grid(column=0, row=3, sticky='W')

    return Graph1, Graph2

#Checks if comport is opened, if not opens a comport
#Sends a sign to the Arduino and retrieves appropriate data
def getData():
    global ser, Graph1, Graph2
    if not (len(connectedDevices) == 0):
        if(ser == 0):
            ser = serial.Serial('COM5', 9600)
            sleep(3)
        
        for x in range(2):
            ser.write(c_uint8(int(0)))
            s = ser.read()
            if (s.hex() == '0a'):
                s = ser.read()
                print(int(s.hex(), 16))
            elif (s.hex() == '0b'):
                s = ser.read()
                print(int(s.hex(), 16))

#Make a window 
tkgui = tk.Tk()
#set window size
tkgui.geometry('600x500')
#set window title
tkgui.title('Controlsystem')

#make label
tkLabelTop = tk.Label(tkgui, text='')
#pack the label
tkLabelTop.pack()

#create a notebook
notebook = ttk.Notebook(tkgui, width=675)
#Create a frame with a grid for each tab
frame1 = ttk.Frame(notebook)
frame1.grid()
frame2 = ttk.Frame(notebook)
frame2.grid()
frame3 = ttk.Frame(notebook)
frame3.grid()
frame4 = ttk.Frame(notebook)
frame4.grid()
frame5 = ttk.Frame(notebook)
frame5.grid()
#Adds the frames to the notebook, default state disabled
notebook.add(frame1, text='Tab 1', sticky='EW', state='disabled')
notebook.add(frame2, text='Tab 2', sticky='EW', state='disabled')
notebook.add(frame3, text='Tab 3', sticky='EW', state='disabled')
notebook.add(frame4, text='Tab 4', sticky='EW', state='disabled')
notebook.add(frame5, text='Tab 5', sticky='EW', state='disabled')
notebook.pack()

#Executes fillTab() 5 times
fillTab(frame1, 'tab1', 'label1', 0)
fillTab(frame2, 'tab2', 'label2', 1)
fillTab(frame3, 'tab3', 'label3', 2)
fillTab(frame4, 'tab4', 'label4', 3)
fillTab(frame5, 'tab5', 'label5', 4)

#Creates a button to stop the program
tkButtonQuit = tk.Button(
    tkgui,
    text='Quit',
    command=quit)
tkButtonQuit.pack()

#Executes checkDevices on program startup
checkDevices()
#Creates the main loop
tkgui.mainloop()
