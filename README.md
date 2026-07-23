# Dual UAV Scan-and-Spray for Precision Agriculture
## Abstract
This project presents an autonomous, decentralized dual-UAV framework for real-time crop monitoring and targeted spraying. The system integrates a lightweight scanning UAV equipped with edge-computing (NVIDIA Jetson Orin) and a high-payload spraying UAV, operating synchronously to eliminate idle hovering and reduce mission time. The scanning UAV utilizes an onboard Hue-Saturation- Value (HSV) color segmentation pipeline, enhanced by dual region masking and a Neutral Density (ND) filter, to ensure robust target identification under varying sunlight. Upon detection, a photogrammetric geotagging algorithm instantly translates 2D image coordinates into global GPS positions and dynamically transmits these targets to the sprayer. To ensure accurate chemical deposition, the spraying UAV then employs a vision-assisted centering control algorithm to compensate for wind drift and GPS inaccuracies. The complete framework was validated through real-world experiments on a 2-acre agricultural field.

## Overview
Conventional agricultural UAV workflows often require a single drone to complete scanning and spraying sequentially or rely on offline image processing, increasing mission time and reducing operational efficiency. This project addresses these limitations by introducing a decentralized dual-drone system consisting of:

* **Scan UAV:** Performs autonomous field scanning and onboard crop anomaly detection using an NVIDIA Jetson Orin and an HSV-based computer vision pipeline.
* **Spray UAV:** Receives target GPS coordinates in real time, autonomously navigates to the detected locations, and performs precision spraying using vision-assisted target centering.

## Drones Design
### Scan Drone
The scanning drone frame is built using two 3D-printed ABS plates connected by 16 mm square carbon-fibre rods. A stainless steel plate is added at high-load regions to handle structural stresses during flight. An F550 landing gear is used to support safe takeoff and landing. The frame includes custom 3D-printed mounts for mounting the camera and flight computer, ensuring proper alignment and mechanical support.
### Spray Drone
The spraying drone frame is constructed using carbon-fiber rods positioned between two carbon-fiber plates. The propulsion system consists of X6 motors powered by two 6S batteries connected in series. The landing gear is built using aluminium rods with custom mounts, providing ground clearance and structural support. A 10-litre pesticide tank is mounted between the landing gear legs.
<table align="center">
  <tr>
    <td align="center" width="50%">
      <img src="https://github.com/user-attachments/assets/bb8623e2-168b-45a4-ae94-f53290d85136" alt="Scan Drone" width="95%"><br>
      <b>Fig. 1.</b> Scan Drone
    </td>
    <td align="center" width="50%">
      <img src="https://github.com/user-attachments/assets/69f18848-175a-4154-8009-be545d072467" alt="CAD Model of Scan Drone" width="95%"><br>
      <b>Fig. 2.</b> CAD model of Scan Drone
    </td>
  </tr>
</table>

<br>

<table align="center">
  <tr>
    <td align="center" width="50%">
      <img src="https://github.com/user-attachments/assets/0ca4ffe8-bdd5-4f3d-a18f-2a03b322ffe9" alt="Spraying Drone" width="95%"><br>
      <b>Fig. 3.</b> Spraying Drone
    </td>
    <td align="center" width="50%">
      <img src="https://github.com/user-attachments/assets/0324a989-4368-4b44-ac92-8ea20aa75630" alt="CAD Model of Spraying Drone" width="95%"><br>
      <b>Fig. 4.</b> CAD model of Spraying Drone
    </td>
  </tr>
</table>

## System Architecture
### Spraying Mechanism
The spraying system was designed to support both precision and wide-area applications using a dual-nozzle configuration. Solid-cone axial-flow nozzles were selected because they provide uniform droplet distribution and effective canopy penetration. A 45° cone-angle nozzle was used for precision spraying, while a 120° cone-angle nozzle provided wider area coverage. The nozzles were mounted on opposite ends of the landing gear and oriented inward to ensure accurate spraying at the center of the target plant. It is also equipped with an [adaptive dual-nozzle spraying system](https://github.com/HarshalKolhe02/Adaptive-Dual-Nozzle-Sprayer), enabling dynamic selection between different spray patterns during operation. The spraying maneuver is controlled using a custom PCB controlled using a Raspberry Pi 5, which actuates relays for nozzle selection and pump control. The system integrates both manual triggering via an RC switch and autonomous operation based on geotagged target location received from the scan drone. On reaching the target location, the onboard controller deploys the selected nozzle followed by the pump to initiate spraying.

<table align="center">
  <tr>
    <td align="center" width="35%">
      <img src="https://github.com/user-attachments/assets/acad7870-98b3-44b9-86c7-888b51dc266c" alt="System Architecture" width="90%"><br>
      <b>Fig. 5.</b> Nozzle Placement in spraying system
    </td>
    <td align="center" width="65%">
      <img src="https://github.com/user-attachments/assets/e7f9146e-5462-4115-bce3-49760f715202" alt="System Workflow" width="95%"><br>
      <b>Fig. 6.</b> Spray triggering PCB circuit
    </td>
  </tr>
</table>

### Electronics Architecture
The dual-UAV system consists of two independently operating drones connected through real-time telemetry. The **Scan Drone** uses an NVIDIA Jetson Orin Nano for onboard crop detection, while the **Spray Drone** uses a Raspberry Pi 5 to control the spraying mechanism. Both drones are equipped with a CubeOrange+ flight controller, Here 4 GPS, SIYI A8 Mini gimbal, and telemetry modules for autonomous navigation, communication, and coordinated precision spraying.

<table align="center">
  <tr>
    <td align="center" width="50%">
      <img src="https://github.com/user-attachments/assets/35500c56-01fd-4a52-9957-665e4f77f2a4" alt="Simulation Result 1" width="95%"><br>
      <b>Fig. 7.</b> Scan Drone system
    </td>
    <td align="center" width="50%">
      <img src="https://github.com/user-attachments/assets/7f38bf39-f60b-4f66-9936-59fa738e0b04" alt="Simulation Result 2" width="95%"><br>
      <b>Fig. 8.</b> Spray Drone system
    </td>
  </tr>
</table>

### Communication Architecture
The dual-UAV system uses a **433 MHz telemetry link** for direct communication between the **Scan Drone** and **Spray Drone**, enabling real-time transmission of target coordinates. Both drones are independently connected to the **Ground Station** via **915 MHz telemetry**, allowing simultaneous mission monitoring, status updates, and manual intervention when required.

## System Algorithm
### Lawn Mower
The Scan Drone follows a **Lawn Mower path planning algorithm**, where it traverses the field in parallel back-and-forth lines to ensure complete coverage with minimal overlap. This systematic coverage pattern improves scanning efficiency while reducing flight time and energy consumption.

<table align="center">
  <tr>
    <td align="center" width="50%">
      <img src="https://github.com/user-attachments/assets/449c3f88-b76e-4191-9c95-a50e2c780c88" alt="Simulation Result 2" width="95%"><br>
      <b>Fig. 9.</b> Lawnmower Algorithm
    </td>
  </tr>
</table>

### Detection and Vision pipeline
The Scan Drone captures RGB images through an **ND (Neutral Density) filter**, which minimizes uneven illumination, glare, and white spots caused by direct sunlight. The images are then converted to the HSV color space for robust color-based segmentation, followed by masking, filtering, and clustering to identify target regions. Finally, the centroid of each detected target is computed and converted into GPS coordinates for autonomous precision spraying.
<table align="center">
  <tr>
    <td align="center" width="50%">
      <img src="https://github.com/user-attachments/assets/429b6e90-f870-49a7-8160-e355b50e0e85" alt="Simulation Result 2" width="95%"><br>
      <b>Fig. 10.</b> Vision Pipeline flowchart
    </td>
  </tr>
</table>

<table align="center">
  <tr>
    <td align="center" width="33%">
      <img src="https://github.com/user-attachments/assets/7557d5ff-ac77-484e-b8ae-e0b6f2a6a95b" alt="Simulation Result 2" width="95%"><br>
      <b>Fig. 11.a. </b> Simple Mask
    </td>
    <td align="center" width="33%">
      <img src="https://github.com/user-attachments/assets/390c80d5-3acb-4fef-9458-3e1e8292a5f6" alt="Simulation Result 2" width="95%"><br>
      <b>Fig. 11.b. </b> Simple Mask with ND filter
    </td>
    <td align="center" width="33%">
      <img src="https://github.com/user-attachments/assets/81d440b0-915b-4181-b6fa-1fffe7afc2be" alt="Simulation Result 2" width="95%"><br>
      <b>Fig. 11.c. </b> New upgraded mask with ND filter
    </td>
  </tr>
</table>

## Results
The proposed dual-UAV system was successfully validated through real-world experiments on a **2-acre agricultural field**. The onboard vision pipeline achieved **~95% detection recall** with minimal false positives under varying lighting conditions. Reliable decentralized communication was maintained between the Scan Drone and Spray Drone over distances of **up to 300 m**, providing an initial target localization accuracy of **2–3 m**. Using the vision-assisted target centering algorithm, the Spray Drone further refined its position to a **steady-state error of 5–20 cm**, enabling highly accurate and efficient precision chemical application.
<table align="center">
  <tr>
    <td align="center" width="33%">
      <img src="https://github.com/user-attachments/assets/9e413136-6807-434a-acb6-f82480e5c352" alt="Simulation Result 2" width="95%"><br>
      <b>Fig. 12.a. </b> Yellow Target Detection – Trial 1
    </td>
    <td align="center" width="33%">
      <img src="https://github.com/user-attachments/assets/5ed17dcf-d219-47fc-a3c1-a359e4159b49" alt="Simulation Result 2" width="95%"><br>
      <b>Fig. 12.b. </b> Yellow Target Detection – Trial 2
    </td>
    <td align="center" width="33%">
      <img src="https://github.com/user-attachments/assets/fcfeb478-3417-47ed-8c53-865be5dd93de" alt="Simulation Result 2" width="95%"><br>
      <b>Fig. 12.c. </b> Yellow Target Detection – Trial 3
    </td>
  </tr>
</table>

## Installation
### 1. Clone the Repository
```bash
git clone https://github.com/IvLabs/Dual_UAV_Scan-and-Spray_for_Precision_Agriculture.git
cd ~
```

### 2. Create a Virtual Environment (Optional but Recommended)
**Linux/macOS**
```bash
python3 -m venv venv
source venv/bin/activate
```
**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Getting Started
### 1. Start the Scan Drone
On the Scan Drone (NVIDIA Jetson Orin Nano), execute:

```bash
./run_system.sh
```
This script initializes the onboard vision pipeline, establishes telemetry communication, and starts the autonomous scanning mission.

### 2. Start the Spray Drone
On the Spray Drone (Raspberry Pi 5), execute:
```bash
python3 Final_full_spray.py
```
The Spray Drone receives target GPS coordinates from the Scan Drone, autonomously navigates to each target, performs vision-assisted target centering, and executes precision spraying.

### 3. Monitor the Mission
Use **Mission Planner** to monitor both UAVs through the **915 MHz telemetry** link.

## Contributors
* Spruha Kshirsagar
* Rajasi Deshmukh
* Harshal Kolhe
* Samiron Biswas
* Mrunmayee Limaye
* Kumar Ayush
* Sanchet Dhalwar
* Ishani Khaty
* Abhinav Anand
* Sunil Watgule
* Vishnu Swaminathan
* Tarun Kayala

## Publication
The full research paper for this project will be made available here after publication.

**Paper:** *Coming Soon*
