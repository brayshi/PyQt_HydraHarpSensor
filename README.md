## HydraHarpSensor
Developed using Python 3.9.7, PyQt 5.9.2, and pyqtgraph 0.11.0 to produce a live plot trace for monitoring photon counts with the HydraHarp 400.
When started in the command line, a trace and histogram will start producing values on the graph based on the file it's tailing

## USAGE
- To be used with the HydraHarp 400 for analysis of red and green photon counts.
- Command to start this program is python .\PyQt_Application.py .\<Name_of_PTU_file>.ptu

## Dependencies
- Present in pyqt_sensor_environment.yaml file. Can use this environment using conda and the command below:
- conda env create -f pyqt_sensor_environment.yml

- Once the above environment is created, it can be activated by typing the below command in conda:
- conda activate pyqt_sensor
