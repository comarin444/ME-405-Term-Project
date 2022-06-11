# -*- coding: utf-8 -*-
"""
Created on Thu May 12 08:42:01 2022

@author: melab15
"""
#from ulab
from ulab import numpy as np


# define g which is the difference between target and current position
def g(X, theta, n):
    fOfTheta = np.array([[n*theta[1]*np.cos(2*np.pi*theta[0])],
                         [n*theta[1]*np.sin(2*np.pi*theta[0])]])
    return X-fOfTheta

# define dg_dtheta which is the derivative of g
def dg_dtheta(theta, n):
    jacobian = np.array([[-2*np.pi*n*theta[1]*np.sin(2*np.pi*theta[0]), n*np.cos(2*np.pi*theta[0])],
                         [2*np.pi*n*theta[1]*np.cos(2*np.pi*theta[0]), n*np.sin(2*np.pi*theta[0])]])
    return -jacobian

# define NewtonRaphson which computes inverse kinematic solution with iteration
def NewtonRaphson(theta, X, n, thresh=1e-5):
    while True:
        if np.sqrt(sum(i**2 for i in g(X, theta, n))) > thresh:
            nextTheta = np.array([[theta[0]],[theta[1]]]) - np.dot(np.linalg.inv(dg_dtheta(theta, n)),g(X, theta, n))
            newTheta = str(nextTheta[0][0])
            newAlpha = str(nextTheta[1][0])
            theta = np.array([float(newTheta),float(newAlpha)])
        return theta

def run():
    
    # reads raw HPGL file and converts data into usable lists of XYZ coordinates
    file = open('quartercircle.hpgl', 'r')
    rawdata = file.read()
    rawdata = (rawdata.split(';')[3:-4])
    rawdata = str(rawdata).replace("[",'').replace("]",'').replace(" ",'').replace("'",'').replace("P",'').split(',')
    x_coords=[]
    y_coords=[]
    z_coords=[]
    
    for i in range(len(rawdata)):
        if i%2==0:
            x_coords.append(rawdata[i])
        else:
            y_coords.append(rawdata[i])
            
        
    #1016 = default scaling (dpi) from InkScape
    xscaling = 1016
    yscaling = xscaling
    xoffset = 25
    yoffset = xoffset
    
    for i in range(len(x_coords)):
        if x_coords[i][0] == "U":
            z_coords.append(x_coords[i][0])
            x_coords[i] = x_coords[i].replace("U","")
        elif x_coords[i][0] == "D":
            z_coords.append(x_coords[i][0])
            x_coords[i] = x_coords[i].replace("D","")
        else:
            z_coords.append("S")
        x_coords[i] = round(int(x_coords[i])*25.4/xscaling + xoffset, 3) 
        y_coords[i] = round(int(y_coords[i])*25.4/yscaling + yoffset, 3) 
    

    n = 8 #pitch
    theta = np.array([.125,6]) #initial "guess" for Newton Raphson calc
    z_val = []
    
    # initialize text files to store position data
    x_file = open("theta_positions.txt", "w")
    y_file = open("alpha_positions.txt", "w")
    
    # compute straight-line distance from one point to the next to determine
    # if iteration is requried between two given points
    for i in range(0, len(x_coords)-1):
        x = x_coords[i+1]-x_coords[i]
        y = y_coords[i+1]-y_coords[i]
        mag = int(np.sqrt(x**2 + y**2) / 0.5)
        
        # proceed with iteration if distance between points is sufficiently 
        # large
        if not mag == 0:
            x_val = x_coords[i]
            y_val = y_coords[i]
            z_val.append(z_coords[i])
            
            for j in range(1,mag):
                x_val = round(x_coords[i] + x*(j/mag),3)
                y_val = round(y_coords[i] + y*(j/mag),3)
                z_val.append('S')
                theta = NewtonRaphson(theta, np.array([[x_val],[y_val]]), n)
                x_file.write(str(theta[0]) + "\n")
                y_file.write(str(theta[1]) + "\n")
                
        else:
            x_val = x_coords[i]
            y_val = y_coords[i]
            z_val.append(z_coords[i])
            
        theta = NewtonRaphson(theta, np.array([[x_val],[y_val]]), n)
        x_file.write(str(theta[0]) + "\n")
        y_file.write(str(theta[1]) + "\n")
        
    x_file.close()
    y_file.close()    
    return (z_val)
        
    
    
    
    
    
    
