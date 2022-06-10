# ME 405 Term Project
#### By: Cole Marin and Theo Philliber
<p align="center">
  <img width="800" src="/images/System.jpg">
</p>

## Introduction
For our ME-405 term project, we were tasked with designing and building a 2$1\over2$ degree of freedom pen plotter with the following constraints:

1. The plotter must draw something. The default interpretation of this constatint would be to draw something on a pen or marker on a piece of paper or whiteboard. More creative interpretations of "drawing" can also be explored. 

2. The project must move in two different degrees of freedom; however, it can not use the traditional Cartesian (X and Y) configuration that most standard 3D printers take advantage of. 

This document serves to archive the design process of our pen plotter such that an individual could replicate it themselves if they so desired.
## Hardware Design
### Initial Design
For our initial design, we proposed a system that uses two stepper motors to provide one rotational and one linear degree of freedom. One of the motors will be mounted to a baseboard and will rotate a power screw around one of the ends. The second motor will be used to spin the screw along its center axis, causing a 3D printed carrige holding a pen to translate radially. The half degree of freedom in our design will consist of a solenoid that will be mounted on this carrige and fixed to the pen, such that the pen can be lifted up off the paper as needed. 
<p align="center">
  <img width="460" height="300" src="/images/SystemDrawing.png">
</p>

### Modeling
To aid in the design of our mechanical system, we drafted the parts in Solidworks. We ended up 3D printing most of our parts, so these models were converted to .STL files and printed in PLA. The wheel and rod connector weren't part of the initial CAD model, and created after the initial parts were printed.

<p align='center'>
  <img width="600" src = "/images/CAD.JPG">
</p>
  



### System Analysis
Since the input to the pen plotter's software will be Cartesian coordinates, we needed to first perform kinematic analysis of the system in order to ultimately calculate the inverse kinematic solution for every point. This analysis consisted of determining the equations of motion in terms of the rotations of the two motors, then calculating the system's jacobian matrix and inverse jacobian matrix.
<p align="center">
  <img width="600" src="/images/KinematicAnalysis.png">
</p>

To calculate the $\theta$ and $\alpha$ for a given pair of X and Y points, we adapted the Newton-Raphson method for approximating the roots of a function. This method first finds the slope of a tangent line at a "guessed" value of a given function. Then, the root of that line is calculated and a vertical line is drawn until it intersects with the function curve. At this point, a new tangent line is drawn and the process is repeated. This process can be visualized in the following GIF from Wikimedia (https://commons.wikimedia.org/wiki/File:Newton-Raphson_method.gif): 
<p align="center">
  <img width="600" src="/images/NewtonRaphsonEx.gif">
</p>

However, instead of calculating the roots of the function, we needed to find a vector of angles that is consistent with a given XY coordinate pair. When we adapted the Newton-Raphson method to this problem, we arrived at the following equation:

$$\boldsymbol{\theta}_{n+1} = \boldsymbol{\theta}_n - \left(\frac{\partial \boldsymbol{g}\left(\boldsymbol{\theta}_n\right)}{\partial \boldsymbol{\theta}}\right)^{-1}\boldsymbol{g}\left(\boldsymbol{\theta}_n\right)$$

where

$$\boldsymbol{g}\left(\boldsymbol{\theta}\right) = \boldsymbol{x}_{\text{des}} - \boldsymbol{f}\left(\boldsymbol{\theta}\right)$$

By calculating  $\boldsymbol{\theta}_{n+1}$ for every point, we can easily command the motors to go to a desired XY location. The GIF below demonstrates the plotter drawing a circle using angle values calculated using the Newton-Raphson method described above.

<p align="center">
  <img width="600" src="/images/DrawingGIF.gif">
</p>

### Bill of Materials
## Software Design
### Main.py
Handles initializing hardware, homes and writes to motors, defines tasks, etc.
### HPGL.py
Reads raw HPGL file, converts to lists of XYZ coords, calculates inverse kinematic solution via Newton Raphson method and writes values to text file  
### Driver.py
Writes and receives data from the TMC4210 and TMC2208
## Testing
### Demonstration Video
Demo Video Link: https://youtu.be/BuNcyO3wXRc
## Conclusion
