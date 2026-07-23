import socket
import struct

IP = "192.168.144.25"
PORT = 37260

def crc16_xmodem(buf: bytes) -> int:
    crc = 0
    for b in buf:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc

def set_gimbal(yaw, pitch, seq=0):
    stx      = b'\x55\x66'
    ctrl     = b'\x01'           # need_ack
    data_len = b'\x04\x00'       # yaw + pitch = 4 bytes
    seq_le   = struct.pack('<H', seq)
    cmd_id   = b'\x0E'

    # pack yaw/pitch as big-endian signed int16
    yaw_be   = bytes(yaw)
    pitch_be = bytes(pitch)

    pkt_wo_crc = stx + ctrl + data_len + seq_le + cmd_id + yaw_be + pitch_be
    crc_le = struct.pack('<H', crc16_xmodem(pkt_wo_crc))
    packet = pkt_wo_crc + crc_le

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(packet, (IP, PORT))
    packet = ' '.join(packet.hex()[i:i+2] for i in range(0, len(packet.hex()), 2))
    print("Packet =", packet)

if __name__ == "__main__":
    yaw, pit = map(int, input("Enter yaw and pitch : ").split())
    Yaw   = (yaw*10).to_bytes(2, byteorder='little', signed=True)
    Pit   = (pit*10).to_bytes(2, byteorder='little', signed=True)
    set_gimbal(Yaw, Pit)

