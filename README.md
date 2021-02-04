# project_scientific_braille
![Screenshot](https://github.com/john-benedict-dimero/project_scientific_braille/blob/main/portfolio-braille-1.jpg)

# Project Overview
### Project Scientific Braille - a prototype that has an integrated braille keypad input and mechanical discs rotating braille display interfaced with a raspberry pi

# Project Features
### 1.) Braille keypad input
This project includes braille keypad input that will be responsible to work as a scientific calculator for the blind. It also supports basic trigonometric functions like sine, cosine, tangent, asin, acos, atan, logarithm, natural logarithm, etc. 
### 2.) Braille Mechanical output display
This project includes a braille mechanical output display that is represented through braille discs which rotate corresponding to the mathematical expresison output. In order for this to function, two stepper motors was used.
### 3.) Voice prompt output (can be interfaced with an auxiliary speakers or headset)
This project also includes a voice prompt ouput whenever there's a keypad input. It has text-to-speech function that translate the expression to speech. This can be turned on or off.
### 4.) Interfaced Basic GUI
This project also provides a basic GUI that served as a screen display for the mathematical expression for checking.

## Additional Features
* Pressing Clear Button for at least 5 seconds will turn on/off mechanical mode -- meaning that the mechanical will or will not function accordingly
* Pressing '0' Button for at least 3 seconds will make the linear motor move (from right-to-left) one disc space

# Algorithm for Rotation
### Output of mathematical expression will serve as input for the rotation
The output of the mathematical expression will be trimmed to 10 digits (add 0 in the beginning to fill to 10 digits). A file database will be used to store the current location of the braille discs (initially they are all at 0 position). This file database will be used to keep track of the location of the braille discs

Since the mechanical assembly is designed to start at the most significant digit (most significant braille disc) to the least significant digit (leas significant braille disc), the software/program must compensate.

The algorithm is designed such that when the more significant braille disc is rotated, the resulting position of the remaining discs that was rotated due to the effect of the rotation of the more significant braille disc is recorded in a database. When the braille disc next to the more significant braille disc will be rotated, a database will be referred to, and from this information will be rotated accordingly.

A dictionary or a key-value pair was used to determine the position of each digit in the braille disc (looks something like this):
```disc_positioning = {
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
        }```

