# ME 405 Term Project
#### By: Cole Marin and Theo Philliber
##*INSERT PHOTO OF FINAL DESIGN HERE*
## Introduction
For our ME-405 term project, we were tasked with designing and building a 2$1\over2$ degree of freedom pen plotter with the following constraints:

1. The plotter must draw something. The default interpretation of this constatint would be to draw something on a pen or marker on a piece of paper or whiteboard. More creative interpretations of "drawing" can also be explored. 

2. The project must move in two different degrees of freedom; however, it can not use the traditional Cartesian (X and Y) configuration that most standard 3D printers take advantage of. 

This document serves to archive the design process of our pen plotter such that an individual could replicate it themselves if they so desired.
## Hardware Design
### Initial Design
<p align="center">
  <img width="460" height="300" src="/images/SystemDrawing.png">
</p>

### Analysis
<p align="center">
  <img width="600" src="/images/KinematicAnalysis.png">
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
*INSERT VIDEO DEMO HERE*
## Conclusion
