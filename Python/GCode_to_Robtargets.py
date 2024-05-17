
# Originally Created by: Daniel Aguirre
# Date: 22/02/2019 
# Modified by Louis Huygens
# Date:29/02/2024

# Original file took a GCode from a laser cutter slicer and converted it to 
# Rapid, plotting a 2D path for drawing on paper, with a pen as the tool

# Modifications allow for increases in z height for 3D printing. changes have 
# been made to the parsing command and the generation of the output files.
# The modified program outputs coordinates in X,Y,Z, and writes code for speed 
# and retraction commands.
         


# Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys, getopt
import scipy.io

# GLOBAL VARIABLES
inputfile = "3DBenchy_0.2mm_PLA_NEPTUNE2S_1h33m.gcode"
outputfile_robtargets = "Benchy_robtargets.txt"
outputfile_moveLs = "Benchy_moveLs.txt"

rotation = "[0,0.7071068,-0.7071068,0], "
conf = "[0,0,0,1]"

G90 = True

# Program variables
positions = pd.DataFrame([[0.0,0.0,0.0]], columns=["x","y","z"])
Speed = pd.DataFrame([5], columns=["f"])
Retraction = pd.DataFrame([1], columns=["e"])
robtargets = []
moveLs = []
NumArrays = []
dz = 0.0
de = 1
    

# Extract GCode command specific information
def parseCommand(command, G90):    
    global positions
    global Speed
    global Retraction
    global dz
    global de
    
    temp = command.split()

    if len(temp) == 0:
        temp = [";"]
        
    if temp[0]=="G0" or temp[0]=="G1":

        x = 0.0
        y = 0.0
        z = 0.0
        f = 0.0
        e = 0.0
        dx = 0.0
        dy = 0.0
        df = 0.0
        
        for comp in temp:
            #   look for speed commands
            if comp.startswith("F"):
                df = round(float(comp[1:]) / 100)
                dx = positions.iloc[-1].x
                dy = positions.iloc[-1].y
            #  look for X coordinates      
            if comp.startswith("X"):
                dx = float(comp[1:])
                dz = positions.iloc[-1].z
                df = Speed.iloc[-1].f
            #  look for Y coordinates 
            if comp.startswith("Y"):
                dy = float(comp[1:])
                dz = positions.iloc[-1].z
                df = Speed.iloc[-1].f
            if comp.startswith("Z"):
                dx = positions.iloc[-1].x
                dy = positions.iloc[-1].y
                df = Speed.iloc[-1].f
                dz = float(comp[1:])
            #   look for retraction commands
            if comp.startswith("E-.8"):
                de = 1
                dx = positions.iloc[-1].x
                dy = positions.iloc[-1].y
            #   look for detraction commands
            if comp.startswith("E.8"):
                de = 0
                dx = positions.iloc[-1].x
                dy = positions.iloc[-1].y
                
            x = dx
            y = dy
            z = dz
            f = df
            e = de

        #Write to arrays
        newPosition = pd.DataFrame([[x,y,z]], columns=["x","y","z"])
        positions = pd.concat([positions, newPosition])
        
        newSpeed = pd.DataFrame([f], columns=["f"])
        Speed = pd.concat([Speed, newSpeed])
        
        newRetraction = pd.DataFrame([e], columns=["e"])
        Retraction = pd.concat([Retraction, newRetraction])

# Writes the Robtarget points into a file
def writeRobtarget(i, position):
    x = position.x
    y = position.y
    z = round(position.z + 0.1, 2)
    
    string1 = "CONST robtarget "
    string2 = "d" + str(i)
    string3 = ":= [[" + str(x) + "," + str(y) + "," + str(z) + "], " + rotation + conf + ", [ 9E+9,9E+9, 9E9, 9E9, 9E9, 9E9]];"
    string4 = "\n"
    robtarget = string1 + string2 + string3 + string4
    robtargets.append(robtarget)

# Writes the GCode points into a file
def writeNumArray(i, position):
    x = position.x
    y = position.y
    z = position.z
    string3 = "[" + str(x) + "," + str(y) + "," + str(z) + "], "
    string4 = "\n"
    NumArray = string3 + string4
    NumArrays.append(NumArray)

# Writes the ABB move commands into a file
def writeMoveL(i, Speed, Retraction):
    f = int(Speed.f)
    r = round(Retraction.e)
    if r == 1:
        fb = 0;
    if r == 0:
        fb = f;
    fb = format(fb, '07b')

    f64 = fb[::-1][6]
    f32 = fb[::-1][5]
    f16 = fb[::-1][4]
    f8 = fb[::-1][3]
    f4 = fb[::-1][2]
    f2 = fb[::-1][1]
    f1 = fb[::-1][0]
    
    string1 = "MoveL "
    string2 = "d" + str(i)
    string3 = ",v" + str(f) +", fine, Hemera\WObj:=PrintBed;"
    string4 = "\n"
    string5 = "setDO D652_10_DO10, " + str(f64) + "; "
    string6 = "setDO D652_10_DO11, " + str(f32) + "; "
    string7 = "setDO D652_10_DO12, " + str(f16) + "; "
    string8 = "setDO D652_10_DO13, " + str(f8) + "; "
    string9 = "setDO D652_10_DO14, " + str(f4) + "; "
    string10 = "setDO D652_10_DO15, " + str(f2) + "; "
    string11 = "setDO D652_10_DO16, " + str(f1) + "; "
    string12 = "setDO D652_10_DO9, " + str(r) + "; "
    
    moveL =  string5 + string6 + string7 + string8 + string9 + string10 + string11 + string12 + string4 + string1 + string2 + string3 + string4 
    moveLs.append(moveL)

def plotPath(proyection="2d"):    
    x = np.array(positions.x, dtype=pd.Series)
    y = np.array(positions.y, dtype=pd.Series)
    z = np.array(positions.z, dtype=pd.Series)

    x0 = np.array([1,])
    y0 = np.array([1,])
         
    fig = plt.figure()

    if (proyection == "3d"):
        ax = Axes3D(fig)
        ax.plot(x,y,z)

    else:
        ax = fig.add_subplot(111)
        ax.plot(x,y,"red")
        ax.scatter(x,y)

    plt.show()


################## MAIN ##################
def main(argv):

    global inputfile, outputfile_robtargets, outputfile_moveLs, rotation, conf

    try:
         opts, args = getopt.getopt(argv,"hi:o:r:c:",["help","ifile=","ofile="])
    except getopt.GetoptError:
         print('Error')
         sys.exit(2)
    

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("Usage: GCode_to_Robtargets [-h | -i <inputfile> -o <outputfile>] ")
            print('Options and arguments:')
            print("-h     : Print this help message and exit")
            print("-i arg : Input the file to be converted into ABB instructions (also --ifile)")
            print("-o arg : Output filename containing the ABB instructions (also --ofile)")
            print("-r arg : Specify the rotation of the robtargets (also --rot). Default: [-1, 0, 0, 0]")
            print("-c arg : Specify the axis configuration of the robtargets (also --conf). Default: [-1, 0, 1, 0]")
            sys.exit()
            
        elif opt in ("-i", "--ifile"):
            inputfile = arg
            
        elif opt in ("-o", "--ofile"):
            outputfile_robtargets = arg + "_robtargets.txt"
            outputfile_moveLs = arg + "_moveLs.txt"
            
        elif opt in ("-r", "--rot"):
            rotation = arg

        elif opt in ("-c", "--conf"):
            conf = arg


    # Check if Input file has been defined
    if inputfile == None:
         print("Inputfile not defined")
         sys.exit(2)
    
    # Load GCode and obtain XYZ coordinates
    file = open(inputfile,"r")
    with open(inputfile,"r") as file:
        line = file.readline()
        lineNumberCount = 1
        while line:
            print("Line: " + str(lineNumberCount))
            line = file.readline()       
            parseCommand(line, G90)
            lineNumberCount += 1
    
    # Write Robtargets and MoveL to a txt file
    for i in range(0, positions.shape[0]-1):    
        position = positions.iloc[i]
        speed = Speed.iloc[i]
        retraction = Retraction.iloc[i]
        writeRobtarget(i, position)    
        writeMoveL(i, speed, retraction)

    with open(outputfile_robtargets,"w") as file:
        for line in robtargets:
            file.writelines(line)

    with open(outputfile_moveLs,"w") as file:
        for line in moveLs:
            file.writelines(line)

    print("Conversion finished")
    
    # Plot expected result
    plotPath()
    
    
if __name__ == "__main__":
   main(sys.argv[1:])



