# README

This project contains the files associated with the paper "Modular Model-Based Supervisory Controller Design for Wafer Logistics in Lithography Machines".

For questions related to the paper or models please contact Bram van der Sanden: b.v.d.sanden@tue.nl.

## Installing CIF

1. Download the latest version from [the CIF web site](http://update.se.wtb.tue.nl/documentation/install/bundled-ide.html#sedocs-install-bundled-ide)
2. Follow the installation instructions provided on the web page.

## Importing the project

To import the project, right-click in the Package Explorer and choose "Import". Select "Import Existing Projects into Workspace" under "General". Navigate to the place where the project resides, select the project "MODELS2015" and press "Finish".

## Structure of the project

The project consists of three parts:

1. `Models/` contains the models for both the uncontrolled system and controlled system. 
2. `Scripts/` contains the Python scripts that are used to generate the models.
3. `Visualization/` contains the visualization for the (un)controlled system.

## Generating the models

To generate the models, navigate to the folder `Scripts` and run `python main.py x` where x is the number of production wafers. In our models `x` is equal to 7.
The generated model will be placed in the folder `Scripts/generated/x`.

Information related to the generation of supervisors in CIF can be found on [the CIF page about data-based supervisory controller synthesis](http://cif.se.wtb.tue.nl/tools/datasynth.html).

The main reason for using a script to generate the models is that dynamic generation of events is not yet supported in CIF. For now, events have to be explicitly declared. Future work includes the use of a DSL and a model transformation to generate the models.

## Running the visualization

1. Open `Visualization/SystemReference.cif` and uncomment the appropriate model to be loaded (uncontrolled or controlled system). Make sure to comment the other model.
2. Right-click the file `Visualization.cif` and choose `Simulate CIF 3 Specification`.

Additional options that can be used in the simulation are described on [the CIF web site](http://cif.se.wtb.tue.nl/tools/cif3sim/options.html).
