# All of the Lights

This repository contains code to display, control and switch between light patterns on a set of led lights (WS2801) attached to a Raspberry Pi.

There is also the option of showing the light patterns in a pygame window if no lights are available.

![The command light console](https://raw.githubusercontent.com/randomsgs/all_of_the_lights/master/media/controller.png)

### Features

* Real time control of light patterns
* Tap tempo syncing
* Controls to double or half tempo
* 5 different light patterns each with an alternate mode
* Ability to control brightness and color palette
* Mute functionality to turn lights off instantly or gradually


## Hardware

Wire your LED lights as according to the diagram in this [blog by AndyPi](https://andypi.co.uk/2014/12/27/raspberry-pi-controlled-ws2801-rgb-leds/)

## Software

### Installing

Clone the repository. Then, in your python3 environment, install dependencies using

```
pip install -r requirements.txt
```

### Starting the Program

```
# To control a set of installed LED lights
python main.py

# To display an animation of the lights
python main.py --no_lights
```

# Controls

* space bar     - tap tempo
* up / down     - double / half speed
* c             - sync phase
* a/s/d/f/g         - choose light pattern
* left / right  - set brightness
* \+ / -         - set saturation
* b             - alt mode
* q/w/e           - choose mute function
* enter         - mute

