# By Grigor Pahlevanyan, July 2023
# Autonomous Vehicles Projcet

#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import LaserScan

call = 0
range2 = []
range1 = []

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
    global call                                 # I don't like global variables too :)
    global range1
    global range2

    if call == 0:                               # The Logic here: By storing the data of a single rotation in 1 list, and the 
        call = 1                                # consecutive rotation data in the second list, we can compare the individual points 
    else:                                       # by their indexes. That's the trick.
        call = 0

    if call == 0:                  
        range1 = msg.ranges                     # Range data, each list contains 1 scan (360 deg) of measurments
    else:
        range2 = msg.ranges                     # Range data, each list contains 1 scan (360 deg) of measurments

    length = len(range1)
    sub_list = list()
    for i in range(length):                     # Determining the change in position list (distance list) over 1 rotation of LiDAR
        item = range1[i]-range2[i]
        sub_list.append(round(item,6))          # Creating the new list of distances (change of position), round to 6 decimal places

    clean_list = cleaner(sub_list, length)      # This function will remove outliers from the list

    state = velocity_calc(clean_list, msg.scan_time)    # This function converts the change in position, to velocity

    if state == "Emergency":
        print("EMERGENCY")                      # For now I print EMERGENCY. Once I add more nodes I can publish this data 

    msg.ranges = clean_list    # Publishing the filtered list so it can be viewed on RVIZ
    pub.publish(msg)


if __name__ == '__main__':
    rospy.init_node('lidar_ScanReader')
    rospy.loginfo("Collision Avoidance System Launched...")

    sub = rospy.Subscriber("/scan", LaserScan, scan_reader)
    pub = rospy.Publisher("/filtered_cloud", LaserScan, queue_size=1)  # Not sure what the queue size really does
    
    rospy.spin()             #Makes program run forever until termination

# COMMENTS:
    # Message Definition_________________________________________________________________________________________________
    #msg.time_increment                              # Time between measurements within the same scan [seconds]
    #msg.scan_time                                   # Time between scans [seconds] so time between full 360deg rotations 
    #msg.angle_increment                             # Extracting time from message (nano seconds)
    #msg.range_min                                   # Minimum range value
    #msg.range_max                                   # Maximum range value
    #msg.ranges                                      # Range data, each list contains 1 scan (360 deg) of measurments
    #msg.header                                      # Aquisition of the time of the first ray in the scan
    #msg.intensities                                 # Intensity of the recieved signal
    #msg.range_min                                   # Max depth
    #msg.range_max                                   # Min depth
    #send_msg.ranges = msg.ranges[40:100]            # To modify the range of points published