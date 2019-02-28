import os
from tkinter import *
import tkinter.font
from threading import Timer
import time
import datetime
import requests
import math
import copy
#import RPi.GPIO as GPIO #########################
#GPIO.setmode(GPIO.BCM) #########################
#GPIO.setwarnings(False) #########################
inputPin = 26
outputPin = 20
##GPIO SETUP##

#GPIO.setup(outputPin, GPIO.OUT) #########################
#GPIO.setup(inputPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #########################
#GPIO.output(outputPin, False) #########################

garageIsClosed = 1;
## 1=closed;    0=open

###GET DATA FROM FILE###

file = open("data.txt", 'r')


currSettingsList = []


for x in file:
    print("data = " + x)
    int_line = int(x)
    currSettingsList.append(int_line)

###TIME ARRAYS###
HOURS = [
    12,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11
    
]

MINUTES = [
    "00",
    "05",
    "10",
    "15",
    "20",
    "25",
    "30",
    "35",
    "40",
    "45",
    "50",
    "55"
]

TIMEOUT_MINUTES = [
    "05",
    "10",
    "15",
    "20",
    "30",
    "45",
    "60",
    "75",
    "90"
]

AMPM = [
    "AM",
    "PM"
]



class Settings(object):
    def __init__(self, title, arr, settingType):
        self.title = title
        self.arr = arr
        self.settingType = settingType

settingsList = []
settingsList.append(Settings("Timeout", TIMEOUT_MINUTES, "timeout"))
settingsList.append(Settings("Set Time Hour", HOURS, "setTime"))
settingsList.append(Settings("Set Time Minute", MINUTES, "setTime"))
settingsList.append(Settings("Set Time AM/PM", AMPM, "setTime"))

###GUI DEFINITIONS###
win = Tk()

##remove cursor from fullscreen
#win.config(cursor="none") 

clockFont = tkinter.font.Font(family = "Helvetica", size=14, weight="bold")
myFont = tkinter.font.Font(family = "Helvetica", size= 18, weight = "bold")
titleFont = tkinter.font.Font(family = "Helvetica", size = 40, weight = "bold")

##Lock Fullscreen
win.overrideredirect(True)
win.geometry("{0}x{1}+0+0".format(win.winfo_screenwidth(), win.winfo_screenheight()))

###GLOBAL VARIABLE DECLARATION###
int_cH = 0
int_cM = 0
int_sH = 0
int_sM = 0
int_tH = 0
int_tM = 0

currPage = 0
currListIndex = 0

timeoutState = 1
setTimeState = 1

timeoutValue = ""
setHour = ""
setMinute = ""
setAMPM = ""

###EVENT FUNCTIONS###

def updateVars():
    global timeoutValue
    global setHour
    global setMinute
    global setAMPM
    
    timeoutValue = TIMEOUT_MINUTES[currSettingsList[0]]
    setHour = HOURS[currSettingsList[1]]
    setMinute = MINUTES[currSettingsList[2]]
    setAMPM = AMPM[currSettingsList[3]]
    

def getCurrClock():
    currentDT = datetime.datetime.now()
    global clockHour
    global clockMinute
    global clockAMPM
    clockHour, clockMinute, clockAMPM = updateClock()
    
def saveSetTime():
    global int_cH
    global int_cM
    global int_sH
    global int_sM
    currentDT = datetime.datetime.now()
    cH = currentDT.strftime("%H") ##Current Hour
    cM = currentDT.strftime("%M") ##Current Minute
    sH = setHour ##Set Hour
    sM = setMinute ##Set Minute

    int_sH = int (sH)
    ##Convert to same format as Current Time
    if setAMPM == "PM"  and int_sH != 12:
            AMPMTimeFix = 12
    elif int_sH == 12 and setAMPM == "AM":
        AMPMTimeFix = -12 # 12am is 0 in military time
    else:
        AMPMTimeFix = 0

    
    
    ##Convert str to int
    int_cH = int (cH)
    int_cM = int (cM)
    int_sH += AMPMTimeFix
    int_sM = int (sM)

    

    print("current Time",cH,":",cM)
    print("set Time",int_sH,":",sM)




def saveTimeout():
    currentDT = datetime.datetime.now()
    
    cH = currentDT.strftime("%H") ##Current Hour
    cM = currentDT.strftime("%M") ##Current Minute
    global int_cH
    global int_cM
    global int_tH
    global int_tM
    global timeoutValue

    int_cH = int(cH)
    int_cM = int(cM)
    
    int_tH = int_cH     ##Timeout Hour
    int_tM = int_cM     ##Timeout Minute

    int_timeout = int(timeoutValue)
    int_tM += int_timeout
    int_tH, int_tM = changeTime(int_tH, int_tM)
    
def changeTime(H, M):
    while M > 59:
        M -= 60
        H += 1
        if H == 24:
            H = 0
    return H, M


def checkTime():
    global int_tH
    global int_tM
    global int_sH
    global int_sM
    global garageIsClosed
    ##Get Current Time Every Loop
    currentDT = datetime.datetime.now()
    cH = currentDT.strftime("%H") ##Current Hour
    cM = currentDT.strftime("%M") ##Current Minute
    ##Convert str => int
    int_cH = int (cH)
    int_cM = int (cM)
    int_tH, int_tM = changeTime(int_tH, int_tM)
    #garageIsClosed = GPIO.input(inputPin) #########################
    
    #updateClock()
    ##if garage is not closed / garage is open
    if garageIsClosed == 0:
        print("Checking For Time At",int_cH,":",int_cM)
        print("Looking For",int_sH,":",int_sM)
        if int_tH == 0 and int_tM == 0:
            saveTimeout()
        print("Looking For",int_tH,":",int_tM)
        
        if int_cH == int_tH and int_cM == int_tM:
            if timeoutState ==1:
                while GPIO.input(inputPin) == 0:
                    closeGarage()
                
        
        elif int_cH == int_sH and int_cM == int_sM:
            if setTimeState ==1:
                while GPIO.input(inputPin) == 0:
                    closeGarage()
        else:
            print("Not Right Time")
    else:
        int_tH = 0
        int_tM = 0

    sendDataToFile()
    #updateClockDisplay() ##cant call from other thread :(
    time.sleep(59)
    checkTime()

def sendDataToFile():
    ##Get current time
    currentDT = datetime.datetime.now()
    cH = currentDT.strftime("%H") ##Current Hour
    cM = currentDT.strftime("%M") ##Current Minute
    str_cH = str(cH)
    str_cM = str(cM)
    URL = "https://programming2-rmunroe.c9users.io/garageDoor/dataInput.php"
    doorState = garageIsClosed
    print("garage state is " + str(doorState))
    PARAMS = {'timeout':timeoutValue,'setTimeHour':int_sH, 'setTimeMinute':int_sM ,'state':doorState, 'currTimeHour':str_cH, 'currTimeMinute':str_cM} 
    r = requests.get(url = URL, params = PARAMS) 

def updateClock():
    ##Get Current Time Every Loop
    currentDT = datetime.datetime.now()
    hour = currentDT.strftime("%H") ##Current Hour
    minute = currentDT.strftime("%M") ##Current Minute

    displayHour = hour
    int_hour = int(hour)
    if int_hour > 11:
        displayAMPM = "PM"
        if int_hour != 12: ##12pm is first of PM's, acting as 0
            int_hour = int_hour - 12
            displayHour = str(int_hour)
            if int_hour == 12: ##Midnight
                displayAMPM = "AM"
    else:
        displayHour = hour
        displayAMPM = "AM"
    return displayHour, minute, displayAMPM

    
def updateClockDisplay():
    hour, minute, ampm = updateClock()
    displayInfo = hour+":"+minute+" "+ampm
    print(displayInfo)
    displayClock.config(text=displayInfo)


    
def closeGarage():
    global int_tH
    global int_tM
    int_tH = 0
    int_tM = 0
    print("trying to close garage")
    ##Replicate button click
    #GPIO.output(outputPin, True) ################################
    time.sleep(0.2)
    #GPIO.output(outputPin, False) #################################
    
    time.sleep(18) ##Sleep 18 seconds to make sure garage is finished closing
    
def close():
    #GPIO.cleanup() ##dont call because touchscreen uses GPIO
    win.destroy()


def renderCurrPage(page):
    global currListIndex
    startingIndex = copy.copy(currSettingsList[currPage])
    currListIndex = startingIndex
    settingTitle.config(text=settingsList[page].title)
    updateVars()
    if settingsList[currPage].settingType == "setTime":
        displayVariable.config(text=str(setHour) + " : " + setMinute + " " + setAMPM)
    else:
        displayVariable.config(text=settingsList[currPage].arr[currListIndex])


    
def nextValue():
    global currListIndex

    if currListIndex >= len(settingsList[currPage].arr)-1:
        currListIndex = 0
    else:
        currListIndex += 1

    ##save the values to settings array
    currSettingsList[currPage] = currListIndex
    updateVars()
    if settingsList[currPage].settingType == "setTime":
        displayVariable.config(text=str(setHour) + " : " + setMinute + " " + setAMPM)
    else:
        displayVariable.config(text=settingsList[currPage].arr[currListIndex])


   

    
def prevValue():
    global currListIndex
    
    if currListIndex == 0:
        currListIndex = len(settingsList[currPage].arr)-1
    else:
        currListIndex -= 1
    currSettingsList[currPage] = currListIndex       
    updateVars()
    if settingsList[currPage].settingType == "setTime":
        displayVariable.config(text=str(setHour) + " : " + setMinute + " " + setAMPM)
    else:
        displayVariable.config(text=settingsList[currPage].arr[currListIndex])
        
    


    
def nextSetting():
    global currPage
    print(currPage)
    if currPage < (len(settingsList)-1):
        currPage += 1
        renderCurrPage(currPage)
        if currPage >= (len(settingsList)-1):
            rightSettingButton.config(text="Save")
        else:
            rightSettingButton.config(text="Next") 
    else:
        print("Go to main page")
        currPage = 0
        saveData()
        updateClock()
        renderMainWidgets()
        saveSetTime()
       
    
def prevSetting():
    global currPage
    if currPage > 0:
        currPage -= 1
        renderCurrPage(currPage)
        rightSettingButton.config(text="Next")
        
    else:
        print("Go to main page")
        currPage = 0
        renderMainWidgets()
        saveSetTime()
        


def toggleTimeout():
    global timeoutState
    timeoutState = 1 - timeoutState
    if timeoutState == 1:
        toggleTimeoutButton.config(bg="limegreen", fg="black", activebackground="limegreen", activeforeground="black")
    else:
        toggleTimeoutButton.config(bg="dark red", fg="white", activebackground="dark red", activeforeground="white")

def toggleSetTime():
    global setTimeState
    setTimeState = 1 - setTimeState
    if setTimeState == 1:
        toggleSetTimeButton.config(bg="limegreen", fg="black", activebackground="limegreen", activeforeground="black")
    else:
        toggleSetTimeButton.config(bg="dark red", fg="white", activebackground="dark red", activeforeground="white")

def toggleGarageDoorDisplay():
    if GPIO.input(inputPin) == 1:######################### 
        ##garage is closed
        toggleDoorButton.config(text="Open Garage")##display open garage on button
    else:
        ##garage is opened
        toggleDoorButton.config(text="Close Garage")##display close garage on button

def toggleGarageDoor():
    toggleGarageDoorDisplay()
    ##Replicate button click
    GPIO.output(outputPin, True)
    time.sleep(0.2)
    GPIO.output(outputPin, False)

def renderSettingsWidgets():
    ##start on 1st page of settings
    currPage = 0
    renderCurrPage(0)
    ##clear menu widgets
    toggleTimeoutButton.place_forget()
    toggleSetTimeButton.place_forget()
    openSettingsButton.place_forget()
    displayClock.place_forget()
    toggleDoorButton.place_forget()
    ##place settings widgets
    settingTitle.place(x=320, y=50, anchor = tkinter.CENTER)
    displayVariable.place(x=320, y=180, anchor = tkinter.CENTER)
    rightValueButton.place(x=540, y=70, width=100, height=230)
    leftValueButton.place(x=0, y=70, width=100, height=230)
    rightSettingButton.place(x=320, y=380, width=320, height=100)
    leftSettingButton.place(x=0, y=380, width=320, height=100)
    
def renderMainWidgets():
    ##place menu widgets
    toggleTimeoutButton.place(x=320, y=120, width=400, height=100, anchor=tkinter.CENTER)
    toggleSetTimeButton.place(x=320, y=270, width=400, height=100, anchor=tkinter.CENTER)
    openSettingsButton.place(x=450, y=420, width=250, height=100, anchor=tkinter.CENTER)
    toggleDoorButton.place(x=180, y=420, width=250, height=100, anchor=tkinter.CENTER)
    #displayClock.place(x=10, y=10, width=110, height=50)
    ##update text
    updateVars()
    getCurrClock()
    timeoutButtonText = "Close Garage After " + timeoutValue + " Minutes"
    setTimeButtonText = "Close Garage At " + str(setHour) + ":" + setMinute + " " + setAMPM
    toggleTimeoutButton.config(text=timeoutButtonText)
    toggleSetTimeButton.config(text=setTimeButtonText)
    ##clear settings widgets
    displayVariable.place_forget()
    rightValueButton.place_forget()
    leftValueButton.place_forget()
    rightSettingButton.place_forget()
    leftSettingButton.place_forget()
    settingTitle.place_forget()

def saveData():
    file = open("data.txt", 'w')
    str_list = []
    for x in range(4):
        print(x)
        str_list.append(str(currSettingsList[x]))
    file.write('\n'.join(str_list))
###WIDGETS###

##Settings Text##
settingTitle = Label(win, text="Setting Title", font = titleFont, bg="light gray")
displayVariable = Label(win, text="Variable", font = myFont, bg="light gray")

displayClock = Label(win, text="HH:MM AM", bg="dark gray", fg="white", font=clockFont)

updateVars()
timeoutButtonText = "Close Garage After " + timeoutValue + " Minutes"
setTimeButtonText = "Close Garage At " + str(setHour) + ":" + setMinute + " " + setAMPM

###Buttons###

##Settings##
closeButton = Button(win, text="X", font = myFont, command = close, bg = "red")
closeButton.place(x=600, y=0, width=40, height=40)
rightValueButton = Button(win, text=">", font = myFont, command = nextValue)
leftValueButton = Button(win, text="<", font = myFont, command = prevValue)
rightSettingButton = Button(win, text="Next", font = myFont, command = nextSetting)
leftSettingButton = Button(win, text="Previous", font = myFont, command = prevSetting)

##Menu##

toggleTimeoutButton = Button(win, text=timeoutButtonText, font = myFont, command = toggleTimeout, bg="limegreen", activebackground="limegreen")
toggleSetTimeButton = Button(win, text=setTimeButtonText, font = myFont, command = toggleSetTime, bg="limegreen", activebackground="limegreen")
openSettingsButton = Button(win, text="Settings", font = myFont, command = renderSettingsWidgets)
toggleDoorButton = Button(win, text="Open Garage", font = myFont, command = toggleGarageDoor)
##CLEAN EXIT##
win.protocol("WM_DELETE_WINDOW", close)

##LOOP##
updateClockDisplay()


t = Timer(59.0, checkTime)
t.start()

 
 
renderMainWidgets()
saveSetTime()
win.config(bg="light gray")
