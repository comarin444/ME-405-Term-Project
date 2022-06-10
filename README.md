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
  
### Switches
One feature we decided to implement in our machine were reference switches. We put a left reference switch for each motor, allowing it to automatically zero itself on powerup. As can be seen in the demo video, the machine will begin with a homing procedure, where it will go backwards until pressing each switch, and then move to a more central starting position. 

<p align="center">
  <img width="460" src="/images/LowerSwitch.jpg">
</p>

<p align="center">
  <img width="460" src="/images/Motor.jpg">
</p>

### Bell/Whistle Feature - Speaker
For our extra bell/whistle feature, we decided to implement a speaker that plays while the code loads. Our code precomputes all of the angles upon running, and stores the values in files which are read piecewise as the motors move. This initial process takes a while, so our speaker plays a song (currently "Take On Me", by A-ha) while it loads. The repetitions and speed of the song can be set in the main file. The speaker operates with PWM running at a 50% duty cycle. To change pitch, the frequency is altered. To create seperation between notes, allowing for more 'staccato' songs, the speaker is set to 0% duty for a moment and returned to 50% between each note. Additionally, the note durations are specified (quarter notes, half notes, etc.) in the buzzer code.

<p align="center">
  <img width="460" src="/images/Nucleo_Speaker.jpg">
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

<p align="center">
  <img width="600" src="/images/BOM.JPG">
</p>

## Software Design
### Main.py
Main.py is the high-level program responsible for initilizing hardware, homing motors, and defining tasks. When it is run on start-up, one queue (posQueue) and two shares (pen_command and drawing_complete) are created. Next, the buzzer file (buzzer.py) is called to run as the hpgl file is simultaneously parsed by HPGL.py to pre-compute every target point in the drawing. This program also homes both motors by running each of them in the negative direction until they trip limit the switches that can be seen in the hardware section above.

Once all of this has been completed, the motors are ready to run. Two tasks are created in main.py that allow for this to occur. First, taskRead handles the reading of the target points from HPGL.py and writes them to posQueue as needed. At the same time, taskMotor reads from the queue and calls driver.py in order to write the positons to the motor. Both of these tasks are given a priority of 1; however, taskmotor is called at twice the frequency of taskRead so that it can be accurate when checking if each position change has completed.
### HPGL.py
HPGL.py first reads raw HPGL file, which is produced by exporting a vector drawing from a suitable editor such as InkScape, and sorts the data into an array of x values, y values, and pen orientations (up or down). To smooth out straight lines when drawing the image, HPGL.py interpolates between positions that are far apart and updates the arrays of positional data. With these new values, HPGL.py uses the modified Newton-Raphson method (described above in System Analysis) to find the inverse kinematic solution for each point and writes the values to an external text document to prevent memory errors on the Nucleo microcontroller.
### Driver.py
Driver.py is primarily responsible for reading and writing from the TMC4210 and TMC 2208 driver chips which control the two stepper motors. When a method is called from main.py, the program creates a 4-byte datagram consisting of the corresponding register address and positional data and writes the datagram to the TMC4201 via Serial Peripheral Interface (SPI). 
### Buzzer.py
Buzzer.py stores the note sequence (frequencies and durations) of song and controls a PWM pin to play on the speaker.
## Testing
### Demonstration Video
Demo Video Link: https://youtu.be/BuNcyO3wXRc
## Conclusion
As can be seen from our video, we haven't gotten the machine to the point where we wanted it to be. The output drawing of the machine isn't very clean, and often will have lines and points that don't make sense. We've calculated the angles and plugged them into our simulations (see System Analysis section), and the results were identical to the .HPGL provided. Due to this, we believe the issue is at the motor level, that the motors aren't doing what we are telling them to do. This is likely an issue of not implementing the TMC4210 stepper drivers properly.

Another area that could be greatly improved is the hardware design of the machine. The motor that rotates the entire arm has to move lots of inertia, and it rotates very quickly. We should have added a gear reduction to allow us to run the motor at a higher speed, as trying to move a heavy load a small amount is difficult. The second way would be to reduce the inertia of the arm with a smaller design and wheel. Third would be to design the solenoid/pen holder better, as the heat from the solenoid loosened the press fit and the pen had lots of backlash.

Despite all of these shortcomings, we have still learned lots from this project. We were able to fully design a system which could draw shapes from vector images. We learned about hardware design and part procurement, which presented their own challenges. We also learned about controlling motors and processing image files. Finally, we improved our ability to simulate mechanisms and perform kinematic analysis. 

## State Transition Diagram

<p align="center">
  <img width="480" src="/images/FSM.jpg">
</p>
