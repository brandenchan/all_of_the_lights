# All of the Lights

This repository contains code to display, control and switch between light patterns on a set of led lights (WS2801) attached to a Raspberry Pi.

There is also the option of showing the light patterns in a pygame window if no lights are available.


## Hardware

Wire your LED lights as according to the diagram in this blog by AndyPi (https://andypi.co.uk/2014/12/27/raspberry-pi-controlled-ws2801-rgb-leds/
) EXCEPT with the CI and DI outputs of the LEDs going to pins 18 and 23. The exact ports can be recofigured in the pixels.py file.


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
