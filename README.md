# Carleton University BIT-NET 4th Year Project 2024: Analysis and Implementation of Simulation Tools for Fog Computing with Microservice Support
This repo is a fork of the emulation tool <i><b>Fogify</i></b>, in which new functionality was added for our Capstone project. 

## About the Capstone
Our project had us look into different Fog simulators/emulators and select one of the fog simulators and propose new features that can be added to improve the simulation results for microservice scenarios. From the simulators/emulators tested, we chose <i><b>Fogify</i></b>.

The main scope of the enhancements implemented into Fogify had to do with <b>support for web-based microservice applications</b>, which include:
- Implemented load testing for web based microservice applications using an xK6 container simulating test users.
- Implemented InfluxDB and Grafana to visualize K6 results
- Utilized Prometheus to parse cAdvisor container metrics from the simulated environment
- Implemented new metrics to track microservice application performance (Pulled from Prometheus)
  - Network Latency of the Microservice
  - Network Transmission Packets / Dropped total
  - Network Received Packets / Dropped total
  - Network Transmission Bytes
  - Network Transmission Errors
  - Network Received Bytes
  - Network Received Errors

Along with the additions, some bugs were fixed to do with spinning up the simulator as well as the simulator it self. We also created a simple Microservice Weather Application to be used for testing in the simulator.

The testing environment with the simple Microservice we created can be found [here](https://github.com/OmarMaadarani/fogify/tree/master/examples/microservice-test). There you will find:
- The new compose file to start Fogify with the additions of Grafana, InfluxDB, and Prometheus.
- Provisioning files for Grafana.
- The Microservice Weather App with a build file to create the docker image before simulating.
- Test user folder to build the xK6 image used to test the microservice endpoints.
- The demo files with the Jupyter Notebook and the Fogified compose file to start the simulating the topology.

