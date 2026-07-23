from pymavlink import mavutil

def start_radio(port, baud):
    return mavutil.mavlink_connection(port, baud=baud, source_system=255)

def broadcast_info(radio_link, category, data_str):
    if radio_link is None: return
    msg_text = f"{category}:{data_str}"[:49]
    radio_link.mav.statustext_send(mavutil.mavlink.MAV_SEVERITY_INFO, msg_text.encode())

def listen_telemetry(radio_link, m_state):
    if radio_link is None: return
    msg = radio_link.recv_match(type='STATUSTEXT', blocking=False)
    if msg:
        #print(msg)
        try:
            parts = str(msg.text).split(":")
            if len(parts) < 2: return
            cat, content = parts[0], parts[1]

            if cat == "DROPOFF":
                lat, lon = map(float, content.split(","))
                m_state['drop_location'].append({"lat": lat, "lon": lon})
            elif cat == "FINISH":
                m_state['scan_finished'] = True
        except:
            pass
