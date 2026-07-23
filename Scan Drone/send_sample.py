import Telemetry_communication_agri as comm
import xml.etree.ElementTree as ET
telemetry_port = "/dev/ttyUSB0"
telemetry_baud = 57600
#21.1288167 79.0559485
#21.1288452 79.0560474
def parse_kml(kml_file):
    """Parse KML file and extract boundary coordinates"""
    """Input is KML file
        Output is lat, lon, alt"""
    try:
        tree = ET.parse(kml_file)
        root = tree.getroot()
        points = []
        for coord in root.iter():
            if coord.tag.endswith("coordinates"):
                for c in coord.text.strip().split():
                    lon, lat, *alt = c.split(',')
                    alt = float(alt[0]) if alt else 0.0
                    points.append((float(lat), float(lon), alt))
        return points
    except Exception as e:
        print(f"Error parsing KML file: {e}")
        return []

radio_link = comm.start_radio(telemetry_port, telemetry_baud)
print("[DEBUG] Sending location by trigger started")
path = "E:/Project/NiDAR/Final_Pipeline_agri/Points.kml"
raw_points = parse_kml(path)
points = [f"{lat},{lon},{alt}" for lat, lon, alt in raw_points]
print(f"Total points extracted: {len(points)}")
command = 0
#while True:
#    command = int(input("Enter: "))
#    if command != 0:
#        x,y,z = points[command-1].split(",")
#        print(x,y)
#        comm.broadcast_info(radio_link, "DROPOFF", x +","+ y)
#        command = 0
#    if command == -1:
#        comm.broadcast_info(radio_link, "FINISH", True)

while True:
    command = int(input("Enter:"))
    if command == 1:
        comm.broadcast_info(radio_link, "DROPOFF", "21.1288977,79.0560169")
        command = 0
    if command == 2:
        comm.broadcast_info(radio_link, "DROPOFF", "21.1289224,79.0560840")
        command = 0
    if command == -1:
       comm.broadcast_info(radio_link, "FINISH", True)
