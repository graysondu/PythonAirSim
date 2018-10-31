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
import threading

# connect to the AirSim simulator
client = airsim.MultirotorClient(ip="127.0.0.1")
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)

state = client.getMultirotorState()
position_global_ref = state.gps_location #gps location where the multirotor takes off

# airsim.wait_key('Press any key to takeoff')
# client.takeoffAsync().join()
client.moveToPositionAsync(0, 0, -10, 5).join()

state = client.getMultirotorState()
position_local = state.kinematics_estimated.position
print("state: %s" % pprint.pformat(position_local))

position_local = state.kinematics_estimated.position
attitude_q = state.kinematics_estimated.orientation #四元数
position_global = state.gps_location

mutex = threading.Lock()

def showImages():
    global mutex, client

    cameraType = "scene"

    cameraTypeMap = { 
    "depth": airsim.ImageType.DepthVis,
    "segmentation": airsim.ImageType.Segmentation,
    "seg": airsim.ImageType.Segmentation,
    "scene": airsim.ImageType.Scene,
    "disparity": airsim.ImageType.DisparityNormalized,
    "normals": airsim.ImageType.SurfaceNormals
    }

    print (cameraTypeMap[cameraType])
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
    i = 0

    while True:
        #client.moveByVelocityAsync(1,0,0,100) #.join()等待程序执行完毕，不加则不等待
        # because this method returns std::vector<uint8>, msgpack decides to encode it as a string unfortunately.
        if mutex.acquire():
            rawImage = client.simGetImage("0", cameraTypeMap[cameraType])        
        mutex.release()

        if (rawImage == None):
            print("Camera is not returning image, please check airsim for error messages")
            sys.exit(0)
        else:
            png = cv2.imdecode(airsim.string_to_uint8_array(rawImage), cv2.IMREAD_UNCHANGED)
            cv2.putText(png,'FPS ' + str(fps),textOrg, fontFace, fontScale,(255,0,255),thickness)
            cv2.imshow("Scene", png)

        frameCount  = frameCount  + 1
        endTime=time.clock()
        diff = endTime - startTime
        if (diff > 1):
            fps = frameCount
            frameCount = 0
            startTime = endTime

        time.sleep(0.01)    
        key = cv2.waitKey(1) & 0xFF;
        if (key == 27 or key == ord('q') or key == ord('x')):
            break

def moveDrone():
    global mutex, client
    while True:
        if mutex.acquire():
            client.moveByVelocityAsync(3,0,0,5)
        mutex.release()
        time.sleep(0.01)    
        key = cv2.waitKey(1) & 0xFF;
        if (key == 27 or key == ord('q') or key == ord('x')):
            break

threads = []
t1 = threading.Thread(target=moveDrone)
threads.append(t1)
t2 = threading.Thread(target=showImages)
threads.append(t2)

if __name__ == '__main__':

    #airsim.wait_key('Press any key to reset to original state')
    for t in threads:
        t.setDaemon(True)
        t.start()
    
    t.join()

    client.armDisarm(False)
    client.reset()

    # that's enough fun for now. let's quit cleanly
    client.enableApiControl(False)
