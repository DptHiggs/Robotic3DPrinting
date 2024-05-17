Repository contains all files used as part of the Robotic 3D Printing Project
Project involves retrofitting an ABB IRB 120 robotic arm for basic 3D printing

Python:
Script GCode_to_robtargets is used to convert GCode into movement commands for robot arm
Script GCode_to_robtargets_BLTouch does the same, but accounts for bed levelling data
Both were run in Spyder IDE within Anaconda

Arduino:
PrintHead is the file used to control the print head during normal operation
BLTouch is used to collect bed levelling coordinates
runStepper10 runs the feed stepper for 10s, used for calibration

MATLAB:
BedLevel plots bed level data
bedScan plots scan data
plotTemp plots temperature data

All supporting documents and photos have been include
