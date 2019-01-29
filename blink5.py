from tkinter import *
import tkinter.font
from threading import Timer
import time
import datetime
#import asyncio
#import async_timeout
import math
import copy
#   import RPi.GPIO as GPIO
#   GPIO.setmode(GPIO.BCM)
#   GPIO.setwarnings(False)

##GPIO SETUP##
#   GPIO.setup(4, GPIO.OUT)
#GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#   GPIO.output(4, False)

garageIsOpen = True;


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

AMPM = [
    "AM",
    "PM"
]

class Settings(object):
    def __init__(self, title, arr, setTime):
        self.title = title
        self.arr = arr
        self.setTime = setTime

settingsList = []
settingsList.append(Settings("Timeout", MINUTES, False))
settingsList.append(Settings("Set Time", HOURS, True))
settingsList.append(Settings("Set Time", MINUTES, True))
settingsList.append(Settings("Set Time", AMPM, True))
    

###GUI DEFINITIONS###
win = Tk()
win.title("Pulse Time Input")
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
    timeoutValue = MINUTES[currSettingsList[0]]
    setHour = HOURS[currSettingsList[1]]
    setMinute = MINUTES[currSettingsList[2]]
    setAMPM = AMPM[currSettingsList[3]]

def saveSetTime():
    currentDT = datetime.datetime.now()
    
    cH = currentDT.strftime("%H") ##Current Hour
    cM = currentDT.strftime("%M") ##Current Minute
    sH = setHour ##Set Hour
    sM = setMinute ##Set Minute
    
    ##Add 12 to convert to same format as Current Time
    if setAMPM == "PM":
        AMPMTimeFix = 12;
    else:
        AMPMTimeFix = 0;

    global int_cH
    global int_cM
    global int_sH
    global int_sM
    
    ##Convert str to int
    int_cH = int (cH)
    int_cM = int (cM)
    int_sH = int (sH) + AMPMTimeFix
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
    
    int_tH = int_cH     ##Timeout Hour
    int_tM = int_cM     ##Timeout Minute

    int_timeout = int(timeoutValue)
    int_tM += int_timeout
    changeTime(int_tH, int_tM)
    
def changeTime(H, M):
    if M > 59:
        M -= 60
        H += 1
    if H > 23:
        H = 1
        
def checkTime():
    global int_tH
    global int_tM
    global int_sH
    global int_sM
    ##Get Current Time Every Loop
    currentDT = datetime.datetime.now()
    cH = currentDT.strftime("%H") ##Current Hour
    cM = currentDT.strftime("%M") ##Current Minute
    ##Convert str => int
    int_cH = int (cH)
    int_cM = int (cM)
    print("Checking For Time At",int_cH,":",int_cM)
    print("Looking For",int_tH,":",int_tM)
    print("Looking For",int_sH,":",int_sM)


    if garageIsOpen:
        if int_tH == 0 and int_tM == 0:
            saveTimeout()

            
        if int_cH == int_tH and int_cM == int_tM:
            if timeoutState ==1:
                closeGarage()
        elif int_cH == int_sH and int_cM == int_sM:
            if setTimeState ==1:
                closeGarage()
        else:
            print("Not Right Time")
    else:
        int_tH = 0
        int_tM = 0

    time.sleep(59)
    checkTime()




def closeGarage():
    print("Closing Garage")
    time.sleep(5)
    print("Garage Closed")
    
def close():
    #   GPIO.cleanup()
    win.destroy()


def renderCurrPage(page):
    global currListIndex
    startingIndex = copy.copy(currSettingsList[currPage])
    currListIndex = startingIndex
    settingTitle.config(text=settingsList[page].title)
    updateVars()
    if settingsList[currPage].setTime:
        displayVariable.config(text=str(setHour) + " : " + setMinute + " " + setAMPM)
    else:
        displayVariable.config(text=settingsList[currPage].arr[currListIndex])
    
def nextValue():
    global currListIndex
    
    if currListIndex >= len(settingsList[currPage].arr)-1:
        currListIndex = 0
    else:
        currListIndex += 1
    currSettingsList[currPage] = currListIndex
    updateVars()
    if settingsList[currPage].setTime:
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
    if settingsList[currPage].setTime:
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
        toggleTimeoutButton.config(bg="limegreen", fg="black")
    else:
        toggleTimeoutButton.config(bg="dark red", fg="white")

def toggleSetTime():
    global setTimeState
    setTimeState = 1 - setTimeState
    if setTimeState == 1:
        toggleSetTimeButton.config(bg="limegreen", fg="black")
    else:
        toggleSetTimeButton.config(bg="dark red", fg="white")



    

def renderSettingsWidgets():
    ##start on 1st page of settings
    currPage = 0
    renderCurrPage(0)
    ##clear menu widgets
    toggleTimeoutButton.place_forget()
    toggleSetTimeButton.place_forget()
    openSettingsButton.place_forget()
    ##place settings widgets
    settingTitle.place(x=320, y=50, anchor = tkinter.CENTER)
    displayVariable.place(x=320, y=180, anchor = tkinter.CENTER)
    rightValueButton.place(x=540, y=70, width=100, height=230)
    leftValueButton.place(x=0, y=70, width=100, height=230)
    rightSettingButton.place(x=320, y=380, width=320, height=100)
    leftSettingButton.place(x=0, y=380, width=320, height=100)
    
def renderMainWidgets():
    ##place menu widgets
    toggleTimeoutButton.place(x=320, y=100, width=400, height=100, anchor=tkinter.CENTER)
    toggleSetTimeButton.place(x=320, y=250, width=400, height=100, anchor=tkinter.CENTER)
    openSettingsButton.place(x=320, y=420, width=400, height=100, anchor=tkinter.CENTER)

    ##update text
    updateVars()
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

toggleTimeoutButton = Button(win, text=timeoutButtonText, font = myFont, command = toggleTimeout, bg="limegreen")
toggleSetTimeButton = Button(win, text=setTimeButtonText, font = myFont, command = toggleSetTime, bg="limegreen")
openSettingsButton = Button(win, text="Settings", font = myFont, command = renderSettingsWidgets)
##CLEAN EXIT##
win.protocol("WM_DELETE_WINDOW", close)

##LOOP##
t = Timer(59.0, checkTime)
t.start()

renderMainWidgets()
saveSetTime()
win.config(bg="light gray")
