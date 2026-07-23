# Dual UAV Scan-and-Spray for Precision Agriculture
## Abstract
Precision agriculture relies mainly on site-specific crop management to minimize agrochemical waste. However, existing UAV systems typically depend on sequential, single-drone workflows and offline data processing, causing significant delays between disease detection and treatment. To address this, the paper presents an autonomous, decentralized dual-UAV framework for real-time crop monitoring and targeted spraying. The system integrates a lightweight scanningUAV equipped with edge-computing (NVIDIA Jetson Orin) and a high-payload spraying UAV, operating synchronously to eliminate idle hovering and reduce mission time. The scanning UAV utilizes an onboard Hue-Saturation- Value (HSV) color segmentation pipeline, enhanced by dualregion masking and a Neutral Density (ND) filter, to ensure robust target identification under varying sunlight. Upon detection, a photogrammetric geotagging algorithm instantly translates 2D image coordinates into global GPS positions and dynamically transmits these targets to the sprayer. To ensure accurate chemical deposition, the spraying UAV then employs a vision-assisted centering control algorithm to compensate for wind drift and GPS inaccuracies. The complete framework was validated through real-world experiments on a 2-acre agricultural field. The onboard detection pipeline achieved approximately 95% recall (true positives among all detections) with minimal false positives. Decentralized communication between UAVs was reliable up to 300 meters, yielding an initial localization accuracy of 2 to 3 meters. After centering, the visual controller successfully refined the spraying drone positioning from the initial 2 to 3 meters down to a steady-state error of just 1–10 cm, providing the precision necessary for precision chemical application. These results validate the proposed dual-UAV architecture as a scalable, autonomous solution for precision agricultural intervention.

## Drones Design
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

## System Design
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

## System Architecture
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

<table align="center">
  <tr>
    <td align="center" width="50%">
      <img src="https://github.com/user-attachments/assets/449c3f88-b76e-4191-9c95-a50e2c780c88" alt="Simulation Result 2" width="95%"><br>
      <b>Fig. 9.</b> Lawnmower Algorithm
    </td>
  </tr>
</table>

<table align="center">
  <tr>
    <td align="center" width="50%">
      <img src="https://github.com/user-attachments/assets/429b6e90-f870-49a7-8160-e355b50e0e85" alt="Simulation Result 2" width="95%"><br>
      <b>Fig. 10.</b> Vision Pipeline flowchart
    </td>
  </tr>
</table>

## Results
<table align="center">
  <tr>
    <td align="center" width="33%">
      <img src="https://github.com/user-attachments/assets/9e413136-6807-434a-acb6-f82480e5c352" alt="Simulation Result 2" width="95%"><br>
      <b>Fig. 11.a. </b> Yellow Detection (Testing 1)
    </td>
    <td align="center" width="33%">
      <img src="https://github.com/user-attachments/assets/5ed17dcf-d219-47fc-a3c1-a359e4159b49" alt="Simulation Result 2" width="95%"><br>
      <b>Fig. 11.b. </b> Yellow Detection (Testing 2)
    </td>
    <td align="center" width="33%">
      <img src="https://github.com/user-attachments/assets/fcfeb478-3417-47ed-8c53-865be5dd93de" alt="Simulation Result 2" width="95%"><br>
      <b>Fig. 11.c. </b> Yellow Detection (Testing 3)
    </td>
  </tr>
</table>
