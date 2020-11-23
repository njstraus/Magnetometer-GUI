# Data rate: T = 6.144e-4 seconds *2^x where x cycles from 2 to 11 aprox 407 hz fastest rate
# https://www.tutorialspoint.com/pyqt/pyqt_qinputdialog_widget.htm
# https://www.learnpyqt.com/tutorials/embed-pyqtgraph-custom-widgets-qt-app/

#Blue flashing issue: causes hang (no data to print)


import sys
from numpy import *
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *

from datetime import datetime
import pyqtgraph as pg
import serial
import csv
import time

crnl='\r\n'
key = ['~','$','#','*','#0']

### START QtApp #####
app = QtGui.QApplication([])          # you MUST do this once (initialize things)
widget = QWidget()
widget.resize(600,600)


COM='COM6'
ser = serial.Serial(COM)
ser.baudrate = 115200
ser.timeout = 100 # was 1000

def processData():
    global curve, ptr, Xm, ser #ptr is pointer Xm input values
    # print("Process Data "  + datetime.now().strftime("%H:%M:%S.%f"))
    try: #Nate added this 11/23
        while ser.in_waiting:
            value = read()
            # print("Value = " + str(value))
            if len(value) > 0:
                Xm[:-1] = Xm[1:]      # shift data in the temporal mean 1 sample left
                Xm[-1] = float(value) # vector containing the instantaneous values
                ptr += 1                              # update x position for displaying the curve
    except TypeError:
        pass

    curve.setData(Xm)                     # set the curve with this data
    curve.setPos(ptr,0)

def read():
    data = ser.readlines(1)

    try:
        data = data[0].decode('utf-8').replace('!','') #remove brackets

        # dataLabel.adjustSize()
        # dataLabel.setText(data)

        if '@' in data: #Frequency Data
            data = data.split('@')
            mag = round(int(data[0])/6009)
            return(mag)

        elif set(key) & set(data): #Messages are not plotted
            print("Command: " + data)

        else: #PD data to plot lacks '@'
            return(data)

    except ValueError:
        #print('ValueError')
        pass
    except IndexError:
        #print('ValueError')
        pass



##Button Functions

def action(cmd):
    ser.write(cmd.encode('Windows-1252')) #above unicode point 127 must use

def IsrOff():
    ser.timeout=0 #prevents long wait on plot loop ending, is reset when plot starts
    ser.write('b'.encode())

def Lhtr():
    if LHButton.isChecked(): #off
        action('æ')
        LHButton.setStyleSheet("background-color : lightgrey")
    else:
        action('å')
        LHButton.setStyleSheet("background-color : grey")

def cmd():
    line = entry.text()
    if '~' in line[0]:
        line = line + crnl
        IsrOff()
        time.sleep(.25)
        ser.write(line.encode())
        time.sleep(.25)
    else:
        ser.write(line.encode())

    ser.flushOutput()


##Toggle Buttons Functions
def Chtr():
    if CHButton.isChecked(): #off
        action(',')
        CHButton.setStyleSheet("background-color : lightgrey")
    else:
        action('+')
        CHButton.setStyleSheet("background-color : grey")
##
def Lsr():
    if LButton.isChecked(): #off
        action('#')
        LButton.setStyleSheet("background-color : lightgrey")
    else:
        action('"')
        LButton.setStyleSheet("background-color : grey")
##
def Prim():
    if PLButton.isChecked(): #off
        action('0')
        PLButton.setStyleSheet("background-color : lightgrey")
    else:
        action('/')
        PLButton.setStyleSheet("background-color : grey")
##
def Sec():
    if SLButton.isChecked(): #off
        action('2')
        SLButton.setStyleSheet("background-color : lightgrey")
    else:
        action('1')
        SLButton.setStyleSheet("background-color : grey")
##
def RF():
    if RFButton.isChecked(): #off
        action('C')
        RFButton.setStyleSheet("background-color : lightgrey")
    else:
        action('B')
        RFButton.setStyleSheet("background-color : grey")

def quit():
    global ser, app, timer, widget
    timer.stop()
    widget.close()
    app.quit()
    ser.close()

################################################Control Window#################################################

timeout=0
timer = QtCore.QTimer()
timer.timeout.connect(processData)
timer.start(timeout)

##1st Row
button1 = QPushButton(widget) #Create button
button1.setText("Quit")#Title button
button1.move(0,0)  #placement column, row
button1.clicked.connect(quit) #if clicked run button1_clicked()

button0 = QPushButton(widget)
button0.setText("Auto Start")
button0.move(75,0)
button0.clicked.connect(lambda: action('>'))

button7 = QPushButton(widget)
button7.setText("Restart")
button7.move(150,0)
button7.clicked.connect(lambda: action('_'))

#Command Line Entry
entry = QLineEdit(widget)
entry.resize(75,23) #Size
entry.move(250, 0) #row, column

cmdbutton = QPushButton(widget)
cmdbutton.clicked.connect(cmd) #Have button run cmd()
cmdbutton.setText('Send')
#cmdbutton.resize(200,32) #Size
cmdbutton.move(325, 0)

##Print Buttons row 25
button4 = QPushButton(widget)
button4.setText("Print PD0")
button4.move(0,25)
button4.clicked.connect(lambda: action('3'))

button5 = QPushButton(widget)
button5.setText("Print PD1")
button5.move(75,25)
button5.clicked.connect(lambda: action('7'))

button6 = QPushButton(widget)
button6.setText("Print Freq.")
button6.move(150,25)
button6.clicked.connect(lambda: action('4'))

#Data Label
dataLabel = QLabel(widget)
dataLabel.move(250, 24)


##ISR On/Off row 50
ISRbuttonOn = QPushButton(widget)
ISRbuttonOn.setText("ISR ON")
ISRbuttonOn.move(0,50)
ISRbuttonOn.clicked.connect(lambda: action('a'))

ISRbuttonOff = QPushButton(widget)
ISRbuttonOff.setText("ISR OFF")
ISRbuttonOff.move(75,50)
ISRbuttonOff.clicked.connect(IsrOff)


##Laser On/Off row 85
LButton = QPushButton(widget)
LButton.setCheckable(True)
LButton.toggle()
LButton.clicked.connect(Lsr)
LButton.setText("Laser")
LButton.move(0,85)

##Cell Heater
CHButton = QPushButton(widget)
CHButton.setCheckable(True)
CHButton.toggle()
CHButton.clicked.connect(Chtr)
CHButton.setText("Cell Heater")
CHButton.move(75,85)

##Laser Heater
LHButton = QPushButton(widget)
LHButton.setCheckable(True)
LHButton.toggle()
LHButton.clicked.connect(Lhtr)
LHButton.setText("Laser Heater")
LHButton.move(150,85)

##Primary Lock
PLButton = QPushButton(widget)
PLButton.setCheckable(True)
PLButton.toggle()
PLButton.clicked.connect(Prim)
PLButton.setText("Prim. Lock")
PLButton.move(225,85)

##Secondary Lock
SLButton = QPushButton(widget)
SLButton.setCheckable(True)
SLButton.toggle()
SLButton.clicked.connect(Sec)
SLButton.setText("Sec. Lock")
SLButton.move(300,85)

##RF Lock
RFButton = QPushButton(widget)
RFButton.setCheckable(True)
RFButton.toggle()
RFButton.clicked.connect(RF)
RFButton.setText("RF Lock")
RFButton.move(375,85)

####################
pg.setConfigOption('background', (211,211,211))
pg.setConfigOption('foreground', 'k')

# win = pg.GraphicsWindow(title="Python Mag Monitor") # creates a window
# p = widget.addPlot(title="Magnetic Field")  # creates empty space for the plot in the window
p = pg.PlotWidget(widget)
p.move(0,120)
p.resize(500,300)
curve = p.plot(pen=(0,0,255))                        # create an empty "plot" (a curve to plot)

windowWidth = 500
                  # width of the window displaying the curve
Xm = linspace(0,0,windowWidth)          # create array that will contain the relevant time series
ptr = -windowWidth

##Main Widget
# widget.setGeometry(50,50,500,200)
widget.setWindowTitle("Command Center")
widget.show()
app.exec_()

###
# ser.close()


