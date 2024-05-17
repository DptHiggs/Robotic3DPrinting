
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
import math

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

#Bed probe coordinates
p1 = (0, 0, 2.57608)
p2 = (50, 0, 2.86989)
p3 = (100, 0, 2.94418)
p4 = (150, 0, 2.85357)
p5 = (200, 0, 2.56837)
p6 = (0, 50, 2.55952)
p7 = (50, 50, 2.82228)
p8 = (100, 50, 2.9139)
p9 = (150, 50, 2.80468)
p10 = (200, 50, 2.50553)
p11 = (0, 100, 2.52471)
p12 = (50, 100, 2.82434)
p13 = (100, 100, 2.89199)
p14 = (150, 100, 2.81364)
p15 = (200, 100, 2.54148)
p16 = (0, 150, 2.53342)
p17 = (50, 150, 2.79708)
p18 = (100, 150, 2.88318)
p19 = (150, 150, 2.81295)
p20 = (200, 150, 2.61035)
p21 = (0, 200, 2.55512)
p22 = (50, 200, 2.798938)
p23 = (100, 200, 2.82164)
p24 = (150, 200, 2.75293)
p25 = (200, 200, 2.54133)

#Bed matrices
Q1 = [p1, p2, p6, p7]
Q2 = [p2, p3, p7, p8]
Q3 = [p3, p4, p8, p9]
Q4 = [p4, p5, p9, p10]
Q5 = [p6, p7, p11, p12]
Q6 = [p7, p8, p12, p13]
Q7 = [p8, p9, p13, p14]
Q8 = [p9, p10, p14, p15]
Q9 = [p11, p12, p16, p17]
Q10 = [p12, p13, p17, p18]
Q11 = [p13, p14, p18, p19]
Q12 = [p14, p15, p19, p20]
Q13 = [p16, p17, p21, p22]
Q14 = [p17, p18, p22, p23]
Q15 = [p18, p19, p23, p24]
Q16 = [p19, p20, p24, p25]


#Credit to Amir, https://math.stackexchange.com/questions/2975109/how-to-convert-euler-angles-to-quaternions-and-get-the-same-euler-angles-back-fr

#quaternion conversion
def euler_to_quaternion(roll, pitch, yaw):
    qx = np.sin(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) - np.cos(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
    qy = np.cos(roll/2) * np.sin(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.cos(pitch/2) * np.sin(yaw/2)
    qz = np.cos(roll/2) * np.cos(pitch/2) * np.sin(yaw/2) - np.sin(roll/2) * np.sin(pitch/2) * np.cos(yaw/2)
    qw = np.cos(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)

    return [round(qw, 7), round(qx, 7), round(qy, 7), round(qz, 7)]

#Bilinear interpolation function
def bilinear_interpolation(x, y, points):
    '''Interpolate (x,y) from values associated with four points.

    The four points are a list of four triplets:  (x, y, value).
    The four points can be in any order.  They should form a rectangle.

        >>> bilinear_interpolation(12, 5.5,
        ...                        [(10, 4, 100),
        ...                         (20, 4, 200),
        ...                         (10, 6, 150),
        ...                         (20, 6, 300)])
        165.0

    '''
    # See formula at:  http://en.wikipedia.org/wiki/Bilinear_interpolation

    points = sorted(points)               # order points by x, then by y
    (x1, y1, q11), (_x1, y2, q12), (x2, _y1, q21), (_x2, _y2, q22) = points

    if x1 != _x1 or x2 != _x2 or y1 != _y1 or y2 != _y2:
        raise ValueError('points do not form a rectangle')
    if not x1 <= x <= x2 or not y1 <= y <= y2:
        raise ValueError('(x, y) not within the rectangle')

    return (q11 * (x2 - x) * (y2 - y) +
            q21 * (x - x1) * (y2 - y) +
            q12 * (x2 - x) * (y - y1) +
            q22 * (x - x1) * (y - y1)
           ) / ((x2 - x1) * (y2 - y1) + 0.0)

#Perform interpolation from an input matrix
def local_interp(n):
    
    matrix = []
    xMax = n[1][0]
    xMin = n[0][0]
    yMax = n[2][1]
    yMin = n[0][1]
    for i in range (yMin, yMax+1):
        b = []
        for j in range(xMin, xMax+1):
            b.append(round(bilinear_interpolation(j, i, n),3))
        matrix.append(b)
    
    return np.flipud(np.array(matrix))

#combine matrices
def genBedMatrix():
    #     np.savetxt('Q1_Matrix.txt', Q1m, fmt='%f')
    
    
    Q1m = local_interp(Q1)
    Q2m = local_interp(Q2)
    Q3m = local_interp(Q3)
    Q4m = local_interp(Q4)
    Q5m = local_interp(Q5)
    Q6m = local_interp(Q6)
    Q7m = local_interp(Q7)
    Q8m = local_interp(Q8)
    Q9m = local_interp(Q9)
    Q10m = local_interp(Q10)
    Q11m = local_interp(Q11)
    Q12m = local_interp(Q12)
    Q13m = local_interp(Q13)
    Q14m = local_interp(Q14)
    Q15m = local_interp(Q15)
    Q16m = local_interp(Q16)
    
    Q2m = np.delete(Q2m, 0, 1)
    Q3m = np.delete(Q3m, 0, 1)
    Q4m = np.delete(Q4m, 0, 1)
    
    Q5m = np.delete(Q5m, 0, 0)
    Q6m = np.delete(Q6m, 0, 1)
    Q6m = np.delete(Q6m, 0, 0)
    Q7m = np.delete(Q7m, 0, 1)
    Q7m = np.delete(Q7m, 0, 0)
    Q8m = np.delete(Q8m, 0, 1)
    Q8m = np.delete(Q8m, 0, 0)
    
    Q9m = np.delete(Q9m, 0, 0)
    Q10m = np.delete(Q10m, 0, 1)
    Q10m = np.delete(Q10m, 0, 0)
    Q11m = np.delete(Q11m, 0, 1)
    Q11m = np.delete(Q11m, 0, 0)  
    Q12m = np.delete(Q12m, 0, 1)
    Q12m = np.delete(Q12m, 0, 0) 
    
    Q13m = np.delete(Q13m, 0, 0)
    Q14m = np.delete(Q14m, 0, 1)
    Q14m = np.delete(Q14m, 0, 0)
    Q15m = np.delete(Q15m, 0, 1)
    Q15m = np.delete(Q15m, 0, 0)  
    Q16m = np.delete(Q16m, 0, 1)
    Q16m = np.delete(Q16m, 0, 0) 
    
    
    R1 = np.hstack((Q1m, Q2m, Q3m, Q4m))
    R2 = np.hstack((Q5m, Q6m, Q7m, Q8m))
    R3 = np.hstack((Q9m, Q10m, Q11m, Q12m))
    R4 = np.hstack((Q13m, Q14m, Q15m, Q16m))
    
    bedMatrix = np.vstack((R4, R3, R2, R1))
    bedMatrix = np.flipud(np.array(bedMatrix))
    return bedMatrix
    

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
    
    # if temp[0] ==";LAYER_CHANGE":
        
    #     dz = round(dz + 0.2, 2)
        
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
            if comp.startswith("E-.8"):
                de = 1
                dx = positions.iloc[-1].x
                dy = positions.iloc[-1].y
            if comp.startswith("E.8"):
                de = 0
                dx = positions.iloc[-1].x
                dy = positions.iloc[-1].y
                
            x = dx
            y = dy
            z = dz
            f = df
            e = de

        newPosition = pd.DataFrame([[x,y,z]], columns=["x","y","z"])
        positions = pd.concat([positions, newPosition])
        
        newSpeed = pd.DataFrame([f], columns=["f"])
        Speed = pd.concat([Speed, newSpeed])
        
        newRetraction = pd.DataFrame([e], columns=["e"])
        Retraction = pd.concat([Retraction, newRetraction])

# Writes the Robtarget points into a file
def writeRobtarget(i, position, matrix):
    x = position.x
    y = position.y
    
    xr = round(x)
    yr = round(y)
    
    #If outside of probed region
    if xr < 17.5 or xr > 217.5 or yr < 17.5 or yr >217.5:
        zr = 2.70 
        Thetax = 0
        Thetay = 0
    #Set height to height from matrix, calculate head angle
    else:
        zr = matrix[round(yr-17.5)][round(xr-17.5)]
        dx1 = matrix[round(yr-18.5)][round(xr-18.5)] - matrix[round(yr-18.5)][round(xr-16.5)]
        dx2 = matrix[round(yr-16.5)][round(xr-18.5)] - matrix[round(yr-16.5)][round(xr-16.5)]
        dy1 = matrix[round(yr-16.5)][round(xr-18.5)] - matrix[round(yr-18.5)][round(xr-18.5)]
        dy2 = matrix[round(yr-16.5)][round(xr-16.5)] - matrix[round(yr-18.5)][round(xr-16.5)]
        
        Thetax = math.atan((dx1+dx2)/4)
        Thetay = math.atan((dy1+dy2)/4)
        
    quart = euler_to_quaternion(-math.pi - Thetax, Thetay, -math.pi/2)
        
    z = round(position.z + zr - 2.85, 2)
    
    string1 = "CONST robtarget "
    string2 = "a" + str(i)
    string3 = ":= [[" + str(x) + "," + str(y) + "," + str(z) + "], " + str(quart) + "," + conf + ", [ 9E+9,9E+9, 9E9, 9E9, 9E9, 9E9]];"
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
    string2 = "a" + str(i)
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
         
    bedMatrix = genBedMatrix()
    

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
        writeRobtarget(i, position, bedMatrix)    
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



