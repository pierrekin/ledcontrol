# LED Control
Control Blinky Things

# Overview
This repository contains a number of arduino sketches to interact with sensors and lights, as well as a python
project which makes use of these sensors and lights.

## Python Project
The python project is broken into two parts, the `ledcontrol` library, as well as a number of scripts that make use
of this library.

In order to run a script you can do the following:
```
python -m scripts.simple_example
```

## Arduino Sketches
The arduino sketches are compiled and uploaded using the arduino cli.

```
arduino-compile
```