"""
For connecting to the AirSim drone environment and testing API functionality
And to learn how to control the drone
"""
import setup_path 
import airsim
import numpy as np
import os
import tempfile
import pprint
import json
import cv2
import sys
import time

# connect to the AirSim simulator
client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)

state = client.getMultirotorState()
position_global_ref = state.gps_location #gps location where the multirotor takes off

# airsim.wait_key('Press any key to takeoff')
client.takeoffAsync().join()
client.moveToPositionAsync(0, 0, -10, 5).join()

# airsim.wait_key('Press any key to move vehicle to (-10, 10, -10) at 5 m/s')
# client.moveToPositionAsync(-10, 10, -10, 5).join()

# client.hoverAsync().join()

state = client.getMultirotorState()
position_local = state.kinematics_estimated.position
print("state: %s" % pprint.pformat(position_local))

position_local = state.kinematics_estimated.position
attitude_q = state.kinematics_estimated.orientation #四元数
position_global = state.gps_location

# airsim.wait_key('Press any key to take images')
def printUsage():
   print("Usage: python camera.py [depth|segmentation|scene]")

cameraType = "depth"

for arg in sys.argv[1:]:
  cameraType = arg.lower()

cameraTypeMap = { 
 "depth": airsim.ImageType.DepthVis,
 "segmentation": airsim.ImageType.Segmentation,
 "seg": airsim.ImageType.Segmentation,
 "scene": airsim.ImageType.Scene,
 "disparity": airsim.ImageType.DisparityNormalized,
 "normals": airsim.ImageType.SurfaceNormals
}

if (not cameraType in cameraTypeMap):
  printUsage()
  sys.exit(0)

print (cameraTypeMap[cameraType])

client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)
client.takeoffAsync().join()

help = False
fontFace = cv2.FONT_HERSHEY_SIMPLEX
fontScale = 0.5
thickness = 2
textSize, baseline = cv2.getTextSize("FPS", fontFace, fontScale, thickness)
print (textSize)
textOrg = (10, 10 + textSize[1])
frameCount = 0
startTime=time.clock()
fps = 0

while True:
    #client.moveByVelocityAsync(0.5,0,0,5).join()
    client.moveByAngleThrottleAsync(10/180*3.14,0,0.5,0,100).join()
    # because this method returns std::vector<uint8>, msgpack decides to encode it as a string unfortunately.
    rawImage = client.simGetImage("0", cameraTypeMap[cameraType])
    if (rawImage == None):
        print("Camera is not returning image, please check airsim for error messages")
        sys.exit(0)
    else:
        png = cv2.imdecode(airsim.string_to_uint8_array(rawImage), cv2.IMREAD_UNCHANGED)
        cv2.putText(png,'FPS ' + str(fps),textOrg, fontFace, fontScale,(255,0,255),thickness)
        cv2.imshow("Depth", png)

    frameCount  = frameCount  + 1
    endTime=time.clock()
    diff = endTime - startTime
    if (diff > 1):
        fps = frameCount
        frameCount = 0
        startTime = endTime
    
    key = cv2.waitKey(1) & 0xFF;
    if (key == 27 or key == ord('q') or key == ord('x')):
        break;

airsim.wait_key('Press any key to reset to original state')

client.armDisarm(False)
client.reset()

# that's enough fun for now. let's quit cleanly
client.enableApiControl(False)
