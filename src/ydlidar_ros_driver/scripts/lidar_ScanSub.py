#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import LaserScan
import time 

call = 0
range2 = []
range1 = []

def filtered_cloud(send, flip):
    global range1
    global range2
    time_increment = send.time_increment     # Time between measurements within the same scan [seconds]
    scan_time = send.scan_time               # Time between scans [seconds] so time between full 360deg rotations 
    angle_increment = send.angle_increment   # Extracting time from message (nano seconds)
    range_min = send.range_min               # Minimum range value
    range_max = send.range_max               # Maximum range value
    ranges = send.ranges                     # Range data, each list contains 1 scan (360 deg) of measurments
    header = send.header                     # Aquisition of the time of the first ray in the scan
    intensities = send.intensities           # Intensity of the recieved signal
    range_min = send.range_min               # Max depth
    range_max = send.range_max               # Min depth

    if flip == 0:
        print("range 1")
        range1 = send.ranges                     # Range data, each list contains 1 scan (360 deg) of measurments
        #print(len(range1))

    else: 
        print("range 2")
        range2 = send.ranges                     # Range data, each list contains 1 scan (360 deg) of measurments
        #print(len(range2))

    length = len(range1)
    sub_list = list()
    for i in range(length):                      # Determining the change in position list (distance list) over 1 rotation of LiDAR
        item = range1[i]-range2[i]
        sub_list.append(round(item,6))

    clean_list = cleaner(sub_list, length)

    state = velocity_calc(clean_list, scan_time)

    if state == "Emergency":
        print("EMERGENCY")

    send.ranges = clean_list    # Publishing the filtered list so it can be viewed on RVIZ
    pub.publish(send)

def velocity_calc(array, scan_time):                  # Determining the velocity. If its significant, then return "Emergency"
    for i in range(len(array)):
        velocity = array[i]/scan_time
        if(velocity > 5): # threshold hardcoded to 5m/s
            return "Emergency"

def cleaner(sub_list, length):                        # Comparing 2 adjacent points to filter out outlier points. 
    i = 0
    j = 0
    clean_list = list()
    final_list = list()

    while(i < length-1):
        if(sub_list[i]-sub_list[i+1] < 0.01):        #0.1 being the threshold for uncertainty
            clean_list.append(sub_list[i])  
        i = i + 1

    clean_length = len(clean_list)

    while(j < clean_length-1):
        if(clean_list[j]-clean_list[j+1] < 0.01):     #0.1 filtering twice for most optimal results
            final_list.append(clean_list[j])
        j = j + 1

    final_len = len(final_list)
    return final_list                                 # Returning a the filtererd list 

def scan_reader(msg):
    global call

    if call == 0:
        call = 1

    else:
        call = 0

    send_msg = LaserScan()

    #DATA EXTRACTION
    send_msg.time_increment = msg.time_increment     # Time between measurements within the same scan [seconds]
    send_msg.scan_time = msg.scan_time               # Time between scans [seconds] so time between full 360deg rotations 
    send_msg.angle_increment = msg.angle_increment   # Extracting time from message (nano seconds)
    send_msg.range_min = msg.range_min               # Minimum range value
    send_msg.range_max = msg.range_max               # Maximum range value
    send_msg.ranges = msg.ranges                     # Range data, each list contains 1 scan (360 deg) of measurments
    send_msg.header = msg.header                     # Aquisition of the time of the first ray in the scan
    send_msg.intensities = msg.intensities           # Intensity of the recieved signal
    send_msg.range_min = msg.range_min               # Max depth
    send_msg.range_max = msg.range_max               # Min depth
    #send_msg.ranges = msg.ranges[40:100]            # To modify the range of points published
    filtered_cloud(send_msg, call)



if __name__ == '__main__':
    rospy.init_node('lidar_ScanReader')

    rospy.loginfo("So far so good")

    sub = rospy.Subscriber("/scan", LaserScan, scan_reader)
    pub = rospy.Publisher("/filtered_cloud", LaserScan, queue_size=1)  # Not sure what the queue size really does
    
    rospy.spin()             #Makes program run forever until termination

