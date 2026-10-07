This repository contains data files for the results contained in "Contributions of subsurface cortical modulations to discrimination of executed and imagined grasp forces through stereoelectroencephalography".

Four participant's data are contained for each of the conditions described in the paper: executed force trials during power and lateral pinch grasps. Two of the participants also performed imagined force trials. Force trials consisted of participants either executing or imagining making 1 of 3 force targets.

In each folder there are subfolders for NSPdata (raw neural data saved as .ns3 files, files associ) and SLCdata (Simulink game data saved as a .mat file)

See below for the SLCdata structure contained in the .mat file. Structure values used in analysis of the code are indicated with a star and comments are preceeded by '%'.

SLCdata =
 	CAR_ENABLE:  			% Unused Code
               CARchans:		% Unused code
              Enable_DA: 		% Unused code
             Enable_LFP:  		% Unused code
              Enable_NB:		% Unused code
                    LFP: 		% Unused code
                *NSPtime:		% Used to align target information with raw neural data
         classification:		% Unused code
          receivedCGJAs:  		% Unused code
       receivedCGvalues: 		% Unused code
      receivedClockinfo: 		% Time since the visualization started
    receivedControlinfo:	 	% Not used
    * receivedTargetinfo: 		% Only first column used and it gave the target dynamometer value for that timestep

    *receiveddynamometer: 		% Dynamometer value recorded during that time step

               simClock:  		% Time since simulink model started
               sysClock:  		% Time values recorded from the computer's clock