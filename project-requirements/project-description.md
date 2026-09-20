---
type: decision
status: current
date: 2026-08-25
tags: [requirements, user-source]
---


# Description of the process of existing code

This description is about the 'Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi', which is the original reference of this revising project.

## 1. Continuous while loop acquisition

In this step, user continuously acquire the image and controls the motor together. By rotating, pulling the magnet and looking at the bead user can decide which beads are target molecule to be experimented.

## 2. Bead selection

After deciding the beads for experiment, user clicks on the target bead on image and pushses 'Done Picking Beads?' button. Normally, user pulls the bead with ~ 7 pN force to confine the motion of magnetic beads before clicking the button.

First click identifies the location of refrence bead which is the polystyrene bead without magnetic response. In other words, 

## 3. Bead raidal profile analysis

After the process 2, the code moves the ASI piezo stage in z-direction. While the bead extension is fixed since the tension on the magnetic bead is fixes, the sample stage itself changes its z-position. By doing so, the off-focus diffraction pattern of the target beads are acquired and processed for every beads selected. This data will be stored as .cal file and will be utilized in the later experiment

## 4. Experiment

At this stage, together with the previous data from step 3, experiment is performed on each beads. For every frames, the acquired image gets processed and converted into numerical array together with the motor information.
Motors including piezo stage, linear stage (magnet position), rotor are continuously commnicating in the while loop. To gain the benefit of consistent experimental data and ease of data acquisition, the time scheduler controls the motor.
Also, the bead tracking and analysis code is performed by sequential for loop, which might turn into parallel looping.


Two while loops exist in the code for parallelization.
Loop 1: motor writing control
Loop 2: all other things (motor reading, image acquisition/processing, scheduling, data saving, printing on the screen)

## 5. Save and termination

If I finished experiment and want to halt the experiment, I click 'stop(end)' button. This will save the data and terminate the code.

If I don't want to save the data, I just simply do LabVIEW Abort Execution.
## 6. Things to be revised

Existing code has penalty in processing multiple beads, or increasing the frame rate to the maximum. Whenever I raise the burden by picking multiple beads, or by raising the frame rate of the bead, I frequently find the frame loss which is given by 'Total Lost Frames'.

I beileve this is basically coming from putting too much process in a sequence. That is the reason why I want to parallelize everything that will take up time during the experimental process while gathering the data. Not a single main stream process in step 4 would be negligible, and thus I might best revise the existing project into parallel version.

Thus, I first want to parallelize every possible process.
After they are done, perhaps I might think about GPU accelerated processing.