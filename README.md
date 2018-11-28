# R12
A Python package providing a low-level interface for the ST Robotics R12
robotic arm.

## Install
Install using pip:
```
pip install r12
```

## Shell
The `r12-shell` executable is automatically installed with the package. It
provides a shell interface to the robot arm for testing.

The shell provides the following commands, all of which can also be found by
typing `help` in the shell.
```
connect     Attempt to connect to the arm.
disconnect  Disconnect from the arm.
dump        Print all output arm has queued.
exit        Close the connection and exit the shell.
help        Print this help message.
run         Load and run a FORTH script on the arm.
status      Print information about the arm.
version     Print version information.
```

You must run `connect` to connect to the arm before issuing other commands.

## Manuals
See the ST Robotics manuals on the R12 arm and ROBOFORTH for more information.
* [Arm Manual](http://www.strobotics.com/manuals/R12%20manual.pdf)
* [ROBOFORTH Manual](http://www.strobotics.com/manuals/manual16.htm)
