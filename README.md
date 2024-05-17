Repository contains all files used as part of the Robotic 3D Printing Project<br />
Project involves retrofitting an ABB IRB 120 robotic arm for basic 3D printing<br />

Python:<br />
Script GCode_to_robtargets is used to convert GCode into movement commands for robot arm<br />
Script GCode_to_robtargets_BLTouch does the same, but accounts for bed levelling data<br />
Both were run in Spyder IDE within Anaconda<br />

Arduino:<br />
PrintHead is the file used to control the print head during normal operation<br />
BLTouch is used to collect bed levelling coordinates<br />
runStepper10 runs the feed stepper for 10s, used for calibration<br />

MATLAB:<br />
BedLevel plots bed level data<br />
bedScan plots scan data<br />
plotTemp plots temperature data<br />

All supporting documents and photos have been include<br />
Credit to Daniel Aguirre for providing the base for the GCode_to_Robtarget converter<br />
https://github.com/DAguirreAg/GCode-to-ABB<br />
