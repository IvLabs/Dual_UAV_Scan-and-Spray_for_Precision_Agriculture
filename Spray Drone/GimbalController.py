"""
Gimbal control service
----------------------
Single responsibility:
- Send yaw / pitch commands to gimbal over UDP

Usage:
    from mav.gimbal_controller import set_gimbal
    set_gimbal(yaw_deg=0, pitch_deg=-90)
"""

import socket
import struct

# ================= CONFIG =================
GIMBAL_IP = "192.168.144.25"
GIMBAL_PORT = 37260


# ================= CRC =================
def crc16_xmodem(buf: bytes) -> int:
    crc = 0
    for b in buf:
        crc ^= b << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


# ================= LOW-LEVEL SEND =================
def _send_gimbal_packet(yaw_raw: bytes, pitch_raw: bytes, seq: int = 0):
    """
    yaw_raw, pitch_raw : int16 little-endian bytes (already scaled by x10)
    """

    stx      = b'\x55\x66'
    ctrl     = b'\x01'           # need_ack
    data_len = b'\x04\x00'       # yaw + pitch
    seq_le   = struct.pack('<H', seq)
    cmd_id   = b'\x0E'

    pkt_wo_crc = (
        stx +
        ctrl +
        data_len +
        seq_le +
        cmd_id +
        yaw_raw +
        pitch_raw
    )

    crc_le = struct.pack('<H', crc16_xmodem(pkt_wo_crc))
    packet = pkt_wo_crc + crc_le

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(packet, (GIMBAL_IP, GIMBAL_PORT))


# ================= PUBLIC API =================
def set_gimbal(yaw_deg: float, pitch_deg: float, seq: int = 0):
    """
    Set gimbal yaw & pitch in DEGREES

    yaw_deg   : float  (-180 to +180)
    pitch_deg : float  (-90 to +30 typically)

    Internally converts to int16 * 10 format
    """

    yaw_int   = int(yaw_deg * 10)
    pitch_int = int(pitch_deg * 10)

    yaw_bytes = yaw_int.to_bytes(2, byteorder='little', signed=True)
    pit_bytes = pitch_int.to_bytes(2, byteorder='little', signed=True)

    _send_gimbal_packet(yaw_bytes, pit_bytes, seq)

