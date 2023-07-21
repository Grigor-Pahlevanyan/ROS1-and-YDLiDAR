#!/usr/bin/env python3

import rospy
from std_msgs.msg import String
from sensor_msgs.msg import PointCloud
from geometry_msgs.msg import Point32

def coordinate_writer(send):
    pub.publish(send)

def coordinate_reader(msg):

    #DATA EXTRACTION
    coordinates = msg.points # Extracting coordinates form the full message (x,y,z)
    time = msg.header.stamp  # Extracting time from message (nano seconds)

    #DATA MANIPULATION
    x_cord = (str(coordinates).split(': ')[1]).split('\n')[0] #x values for a full 360 angle
    y_cord = (str(coordinates).split(': ')[2]).split('\n')[0] #y values for a full 360 angle

    #Note, data manipulation is not good yet.

    x_cord = round(float(x_cord),3)
    y_cord = round(float(y_cord),3)

    # #PRINT STATEMENTS
    # rospy.loginfo("X-value")
    # rospy.loginfo(x_cord)
    # rospy.loginfo("Y-value")
    # rospy.loginfo(y_cord)
    # rospy.loginfo("TIME in ns")
    # rospy.loginfo(time)               #This is my time in NANOSECONDS

    send = Point32()
    send.x = x_cord
    send.y = y_cord
    coordinate_writer(send)

    #NOTES
    #x_cord = (str(coordinates[0:300]).split(': ')[1]).split('\n')[0] #x values for a specific range
    #rospy.loginfo(str(coordinates[0])[15:30])                        #x,y,z values for a specific range

if __name__ == '__main__':
    rospy.init_node('lidar_subscriber')

    rospy.loginfo("So far so good")

    sub = rospy.Subscriber("/point_cloud", PointCloud, coordinate_reader)
    pub = rospy.Publisher("filtered_cloud", Point32, queue_size=10)
    
    rospy.spin()             #Makes program run forever until termination

