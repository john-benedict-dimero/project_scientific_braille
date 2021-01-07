"""PROJECT BRAILLE

A prototype that functions as a scientific braille calculator.
Its a scientific calculator with voice output,
mechanical braille display, and hdmi LCD display.

Its basic operation is that the result from the scientific
calculator expression will output an answer and will be 
displayed in a mechanical braille display and voice output.
Each press of the keys also produce a voice output. An option
to turn on/off this option will also provided. An HDMI LCD
display is used to verify the output of the braille expression.

"""


import RPi.GPIO as GPIO  # library for using Rpi GPIOs
import Adafruit_GPIO.MCP230xx as MCP230XX  # library use to the pins of MCP230xx

import string  # string library for string related operations
import time  # time library for time related operations

import pyttsx3  # text to speech library for text translation
import alsaaudio  # library to control the volume of Rpi

import tkinter as tk  # library used for creating GUI

from math import *  # library used for all the math related operations


# Pins used in RPi Board for Keyboard
pins_RPI = [
    7, 8, 10,
    11, 12, 13,
    15, 16, 18,
    19, 21, 22,
    23, 24, 26,
    29, 31, 32,
    33, 35, 36,
    37, 38, 40,
    ]


# Pins used in Expansion unit MCP for Keyboard
# Added pins of 6 and 7 for additional 
# functionality {6: delete, 7: toggle on/off volume}
pins_MCP = [
    0, 1, 2,
    3, 4, 5,
    6, 7,
    ]


# Pins used in Expansion unit for linear movement
# pins_MCP_stepper 1 was initially 6,7,8,9
pins_MCP_stepper1 = [
    8, 9, 10, 11
    ]


# Pins used in Expansion unit for rotation
# pins_MCP_stepper 2 was initially 10,11
pins_MCP_stepper2 = [
    12, 13,
    ]

filename = 'databasev2.txt'  # file generated for discs database
input_expression = ''  # initializing the mathematical expression
database_discs = []  # initializing the disc positioning

display = None # initializing GUI display
root = None  # initializing GUI root
frame = None  # initializing GUI frame
entry = None  # initializing GUI entry

control_device = 'PCM'  # initializing PCM for audio control

run = True  # initializing run to True

mcp = MCP230XX.MCP23017()  # setting up Extension GPIO IC
GPIO.setwarnings(False)  # setting up GPIO inputs in RPI-BOARD
GPIO.setmode(GPIO.BOARD)  # setting up GPIO inputs in RPI-BOARD

engine = pyttsx3.init()  # initializing text to speech

m = alsaaudio.Mixer(control_device)  # initializing audio control




def initialization(RPI, MCP, STP1, STP2):
	""" This function initializes all the general purpose
	input/output pins that is used by the prototype.
	This includes setting the RPI GPIOs and MCP GPIOs to function
	as either input or output. 
	"""

    # Iterating over pins and setting whether they
    # will function as input or output
    for x in RPI:
        GPIO.setup(x, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
    
    for y in MCP:
        mcp.setup(y, MCP230XX.GPIO.IN)
        mcp.pullup(y, True)

    for s in STP1:
        mcp.setup(s, MCP230XX.GPIO.OUT)
        mcp.output(s, False)
    
    for t in STP2:
        mcp.setup(t, MCP230XX.GPIO.OUT)
        mcp.output(t, False)

       
def initialize_database(filename, listinput):
	""" This function initializes the database for the
	positioning of the discs and stores it value and 
	saves it to filename.
	"""

    file = open(filename, encoding = 'utf8')
    
    for line in file:
        if len(listinput) > 12:
            break
        else:
            value = line.strip(string.whitespace + string.punctuation)
            listinput.append(int(value))
            
    file.close()
    

def close_database(filename, listinput):
	""" This function closes the open database and saves
	the value of the position of the database discs to 
	the filename.
	"""

    file = open(filename, 'w+', encoding = 'utf8')
    
    for w in range(12):
        file.write(str(listinput[w]) + '\n')
        
    file.close()


def audio_off_on_control(toggle_pin):
    """ This function mutes and unmute the audio built in 
    the raspberry pi with regards to the state of the 
    toggle pin.
    """

    if toggle_pin == True:
        m.setmute(1)
    else:
        m.setmute(0)
    
    
def computation(input_expression):
	""" This function evaluates the mathematical expression
	and strips the answer in the limit of 10 digits and
	convert it to string.
	"""

    try:
        output = eval(input_expression)
        if len(str(output)) > 10:
            if output > 9999999999:
                output = str(output)
                difference = len(str(output))-10
                if difference > 99999999:
                    return 'Syntax Error'
                else:
                    output = output[:10]
                    output = output[:-1*((len(str(difference)))+1)]
                    output += 'e'
                    output += str(difference)
            elif output < -999999999:
                output = str(output)
                difference = len(str(output))-10
                if difference > 9999999:
                    return 'Syntax Error'
                else:
                    output = output[:10]
                    output = output[:-1*((len(str(difference)))+1)]
                    output += 'e'
                    output += str(difference)
            else:
                output = str(output)
                output = output[:10]
        return str(output)
        
    except:
        return 'Syntax Error'
    

def mov_nema_motor(pin_list):
	""" This function moves the NEMA stepper motor
	in the clockwise direction with 15 steps
	"""

    DIR = pin_list[0]  # Direction GPIO Pin
    STEP = pin_list[1]  # Step GPIO Pin
    CW = 1  # Clockwise Rotation
    CCW = 0  # Counterclockwise Rotation
    
    # every step must be calculated by ((360/13)/1.8)
    # SPR = ((360/13)/1.8)
    SPR = 15
    
    step_count = SPR
    delay = 0.005
    
    mcp.output(DIR, CW)
    
    for x in range(step_count):
        mcp.output(STEP, 1)
        time.sleep(delay)
        mcp.output(STEP, 0)
        time.sleep(delay)


def mov_nema_motor_rev(pin_list):
	""" This function moves the NEMA stepper motor 
	in the counter clockwise direction with 15 
	steps.
	"""

    DIR = pin_list[0]  # Direction GPIO Pin
    STEP = pin_list[1]  # Step GPIO Pin
    CW = 1  # Clockwise Rotation
    CCW = 0  # Counterclockwise Rotation
    
    # every step must be calculated by ((360/13)/1.8)
    # SPR = ((360/13)/1.8)
    SPR = 15
    
    step_count = SPR
    delay = 0.005
    
    mcp.output(DIR, CCW)
    
    for x in range(step_count):
        mcp.output(STEP, 1)
        time.sleep(delay)
        mcp.output(STEP, 0)
        time.sleep(delay)
    

def movement_motor(pin_list):
	""" This function moves the 28BYJ-48 stepper motor
	in the clockwise direction using a step sequence
	and referring 53 steps per disc section rotation 
	"""

    one_disc = 53
    
    seq = [
    [1,0,0,0],
    [1,1,0,0],
    [0,1,0,0],
    [0,1,1,0],
    [0,0,1,0],
    [0,0,1,1],
    [0,0,0,1],
    [1,0,0,1], 
    ]
    
    for i in range(one_disc):
        for halfstep in range(8):
            for pin in range(4):
                mcp.output(pin_list[pin], seq[halfstep][pin])
                

def motor_reverse(pin_list):
	""" This function moves the 28BYJ-48 stepper motor
	in the counter-clockwise direction using a step 
	sequence and referring 53 steps per disc section 
	rotation. 
	"""

    one_disc = 53
    
    seq_rev = [
    [1,0,0,1],
    [0,0,0,1],
    [0,0,1,1],
    [0,0,1,0],
    [0,1,1,0],
    [0,1,0,0],
    [1,1,0,0],
    [1,0,0,0], 
    ]
    
    for i in range(one_disc):
        for halfstep in range(8):
            for pin in range(4):
                mcp.output(pin_list[pin], seq_rev[halfstep][pin])
  

def rotation(discs_pos, output_exp, pins1, pins2):
	"""This function defines on how much the rotation of the 
	discs will be made. It is also responsible for the 
	linear movement of the motor.
	"""

    output = output_exp.zfill(10)
    initial = 10
    start = 0
    
    disc_positioning = {
        '0' : 0,
        '1' : 1,
        '2' : 2,
        '3' : 3,
        '4' : 4,
        '5' : 5,
        '6' : 6,
        '7' : 7,
        '8' : 8,
        '9' : 9,
        '.' : 10,
        '-' : 11,
        'e' : 12
        }
    print(discs_pos)
    for o in output:
        diff_cw = abs(disc_positioning[o] - discs_pos[start])
        if diff_cw > 12:
            diff_cw -= 13
        diff_ccw = (discs_pos[start]) + (13 - disc_positioning[o])
        if diff_ccw > 12:
            diff_ccw -= 13
            
        while discs_pos[start] != disc_positioning[o]:
            
            if diff_ccw > diff_cw:
                mov_nema_motor(pins2)
                for i in range(start, 10):
                    discs_pos[i] += 1
                    if discs_pos[i] > 12:
                        discs_pos[i] -= 13
                    else:
                        pass
            else:
                mov_nema_motor_rev(pins2)
                for i in range(start, 10):
                    discs_pos[i] -= 1
                    if discs_pos[i] < 0:
                        discs_pos[i] += 13
                    else:
                        pass
                    
            print(discs_pos)
            time.sleep(0.01)
            
        movement_motor(pins1)
        start += 1
        time.sleep(0.01)
    
    time.sleep(0.01)
    for i in range(9):
        motor_reverse(pins1)
    time.sleep(0.01)


# Initializing GPIO pins and the database
initialize_database(filename, database_discs)
initialization(pins_RPI, pins_MCP, pins_MCP_stepper1, pins_MCP_stepper2)

# Start up message when the program runs
engine.say('Hello there, Welcome to Braille!')
engine.runAndWait()


def poll():
	""" This function host the backend program for running the GUI
	and all the function of the keyboard. This will be the main 
	program that integrates all the function together to make the
	prototype function as a whole
	"""


    global display
    global root
    global frame
    global entry
    global input_expression
        
    if GPIO.input(21) == True:
        output = computation(input_expression)
        display.set(output)
        engine.say(output)
        engine.runAndWait()
        if output != 'Syntax Error':
            '''rotation(database_discs, output, pins_MCP_stepper1, pins_MCP_stepper2)
            print(database_discs)'''
            engine.say('Done')
            engine.runAndWait()
        else:
            pass
        
    elif GPIO.input(7) == True:
        input_expression = ''
        display.set(input_expression)
        engine.say('Clear')
        engine.runAndWait()

    else:   
        if GPIO.input(11) == True:
            input_expression += '-'
            display.set(input_expression)
            engine.say('minus')
            engine.runAndWait()
        
        elif GPIO.input(13) == True:
            input_expression += '+'
            display.set(input_expression)
            engine.say('plus')
            engine.runAndWait()

        elif GPIO.input(15) == True:
            input_expression += '/'
            display.set(input_expression)
            engine.say('divided by')
            engine.runAndWait()

        elif GPIO.input(19) == True:
            input_expression += '*'
            display.set(input_expression)
            engine.say('times')
            engine.runAndWait()

        elif GPIO.input(23) == True:
            input_expression += '9'
            display.set(input_expression)
            engine.say('9')
            engine.runAndWait()

        elif GPIO.input(29) == True:
            input_expression += '6'
            display.set(input_expression)
            engine.say('6')
            engine.runAndWait()
            
        elif GPIO.input(31) == True:
            input_expression += '3'
            display.set(input_expression)
            engine.say('3')
            engine.runAndWait()
        
        elif GPIO.input(33) == True:
            input_expression += '8'
            display.set(input_expression)
            engine.say('8')
            engine.runAndWait()
        
        elif GPIO.input(35) == True:
            input_expression += '5'
            display.set(input_expression)
            engine.say('5')
            engine.runAndWait()

        elif GPIO.input(37) == True:
            input_expression += '2'
            display.set(input_expression)
            engine.say('2')
            engine.runAndWait()

        elif GPIO.input(8) == True:
            input_expression += '.'
            display.set(input_expression)
            engine.say('point')
            engine.runAndWait()

        elif GPIO.input(10) == True:
            input_expression += '7'
            display.set(input_expression)
            engine.say('7')
            engine.runAndWait()
        
        elif GPIO.input(12) == True:
            input_expression += '4'
            display.set(input_expression)
            engine.say('4')
            engine.runAndWait()

        elif GPIO.input(16) == True:
            input_expression += '1'
            display.set(input_expression)
            engine.say('1')
            engine.runAndWait()

        elif GPIO.input(18) == True:
            input_expression += '0'
            display.set(input_expression)
            engine.say('0')
            engine.runAndWait()

        elif GPIO.input(22) == True:
            input_expression += '('
            display.set(input_expression)
            engine.say('open parenthesis')
            engine.runAndWait()

        elif GPIO.input(24) == True:
            input_expression += ')'
            display.set(input_expression)
            engine.say('close paranthesis')
            engine.runAndWait()

        elif GPIO.input(26) == True:
            input_expression += 'log10'
            display.set(input_expression)
            engine.say('logarithm of base 10')
            engine.runAndWait()

        elif GPIO.input(32) == True:
            input_expression += 'log'
            display.set(input_expression)
            engine.say('natural logarithm')
            engine.runAndWait()

        elif GPIO.input(36) == True:
            input_expression += 'sqrt'
            display.set(input_expression)
            engine.say('square root')
            engine.runAndWait()

        elif GPIO.input(38) == True:
            input_expression += '**'
            display.set(input_expression)
            engine.say('raise to')
            engine.runAndWait()

        elif GPIO.input(40) == True:
            input_expression += 'sin'
            display.set(input_expression)
            engine.say('sine')
            engine.runAndWait()

        elif mcp.input(0) == False:
            input_expression += 'cos'
            display.set(input_expression)
            engine.say('cosine')
            engine.runAndWait()

        elif mcp.input(1) == False:
            input_expression += 'tan'
            display.set(input_expression)
            engine.say('tangent')
            engine.runAndWait()

        elif mcp.input(2) == False:
            input_expression += '10**'
            display.set(input_expression)
            engine.say('inverse logarithm')
            engine.runAndWait()

        elif mcp.input(3) == False:
            input_expression += 'asin'
            display.set(input_expression)
            engine.say('inverse sine')
            engine.runAndWait()

        elif mcp.input(4) == False:
            input_expression += 'acos'
            display.set(input_expression)
            engine.say('inverse cosine')
            engine.runAndWait()

        elif mcp.input(5) == False:
            input_expression += 'atan'
            display.set(input_expression)
            engine.say('inverse tangent')
            engine.runAndWait()

        else:
            pass
        
    root.after(10, poll)


# Initializing the root class for the GUI        
root = tk.Tk()
root.title("Braille Display")
root.geometry("500x100")
root.resizable(False, False)

# Creating a frame object with root as parameter
frame = tk.Frame(root)
frame.option_add("*Font", "arial 20 bold")
frame.pack(expand = 1, fill = "both")

# Creating a display for the GUI calculator
display = tk.StringVar()
display.set("Enter an expression..")
entry = tk.Entry(root, relief="ridge", textvariable=display, justify='right'
                 , bd=20, bg="powder blue").pack(side="top", expand=1, fill="both")

# Running the GUI with some delay 10 
root.after(10, poll)
root.mainloop()



        


