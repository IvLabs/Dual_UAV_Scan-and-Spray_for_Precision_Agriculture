
import cv2
import numpy as np
from scipy.spatial.transform import Rotation

def distance(x,y):
    return (x**2 + y**2)**0.5

K = np.array([[725, 0.00000000e+00, 960],
     [0.00000000e+00, 725, 540],
     [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
dist = np.array([0, 0, 0, 0, 0])

'''
Takes the 
pixel coordinates (u,v), 
altitude of camera(H), 
RPY (roll, pitch, yaw), 
and the camera parameters (K, dist) 
to return the offset of the detected pixel from the camera in the real world (x_world, y_world) in meters
'''
def pixel2meter(u, v, drone_H, roll, drone_pitch, drone_yaw, K=K, dist=dist, gimbal_offset=0, gimbal_pitch=-90, gimbal_yaw=0):
    undistorted = cv2.undistortPoints(np.array([[[u, v]]], dtype=np.float32), K, dist)
    x, y = undistorted[0][0]
    ray_camera = [x, y, 1]  # Forward direction is +Z in camera coordinates

    H       = drone_H - gimbal_offset
    pitch   = 90 + gimbal_pitch
    yaw     = drone_yaw     + gimbal_yaw

    rpy_deg = [roll, pitch, yaw]
    R_cam_to_world = Rotation.from_euler('xyz', rpy_deg, degrees=True).as_matrix()

    ray_world = R_cam_to_world @ ray_camera

    scale = H / ray_world[2]

    x_world = ray_world[0] * scale
    y_world = ray_world[1] * scale

    return (x_world, y_world)

from pyproj import Transformer

'''
Takes GPS coordinates (lat_gps, lon_gps), 
Distance from camera (x_img, y_img) in meters
and offset of camera from GPS (x_cam_offset, y_cam_offset)
to return the GPS coordinates of the target
'''
def offset_to_gps(lat_gps, lon_gps, x_img, y_img, x_cam_offset=0.0, y_cam_offset=0.0):
    zone = int((lon_gps + 180) / 6) + 1
    if lat_gps >= 0:
        epsg = 32600 + zone  # Northern Hemisphere
    else:
        epsg = 32700 + zone  # Southern Hemisphere

    # Convert GPS position to UTM
    transformer_to_utm = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)
    transformer_to_wgs = Transformer.from_crs(f"EPSG:{epsg}", "EPSG:4326", always_xy=True)
    e_gps, n_gps = transformer_to_utm.transform(lon_gps, lat_gps)

    # Apply camera offset
    x_total = x_img + x_cam_offset
    y_total = y_img + y_cam_offset

    # Convert final (easting, northing) to lat/lon
    e_target = e_gps + x_total
    n_target = n_gps + y_total
    lon_target, lat_target = transformer_to_wgs.transform(e_target, n_target)

    return lat_target, lon_target
