#PROTEC - A - GARAGE#
##High School PLTW Engineering Project##

Through the touch screen, the user is able to configure when they would like to ensure their garage door is closed. The user can set the garage to close x minutes after it was opened or to close at a specified time. Both of these functions are individually toggleable and easily configurable. The data is then sent to a website to allow the user to monitor the state of the garage door, the times the garage is set to close at, and every time the garage  was opened or closed. This project spanned from August 2018 to April 2019 and was fully documented along the way. Protec-a-Garage runs in parallel to all existing garage door openers and follows all of the same safety features of the garage door.  



##Data File##
data.txt file structure located on Raspberry Pi
This is used to retain the users previous settings if the program were to shut off.

1: index of timeout
2: index of setHour
3: index of setMinute
4: index of SetAMPM
