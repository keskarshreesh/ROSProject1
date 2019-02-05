import roslib; 
import rospy
import numpy as np
import os
from std_msgs.msg import String, Bool
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from math import tanh

roslib.load_manifest('follower_bark') #To use open source library for signaling between master and slave

#Slave Class
class follower:
    def __init__(self, follow_Distance=2, stop_Distance=1, max_speed=0.6, min_speed=0.01 ):
        
		#follow_Distance gives distance within which bot will follow master
		#bot will stop following master for distance less than stop_Distance
		#for stop_Distance = 1, follow_Distance = 2, error is minimized
		self.sub = rospy.Subscriber('scan', LaserScan, self.laser_callback)
        self.pub = rospy.Publisher('mobile_base/commands/velocity', Twist)

        self.stopDistance = stop_Distance
        self.max_speed = max_speed
        self.min_speed = min_speed
	
		self.followDist = follow_Distance #When distance increases beyond threshold value, following will start

		self.closest = 0 #Where is the closest turtlebot?
		self.position = 0 #Absolute position in the array?
        
        self.command = Twist()
        self.command.linear.x = 0.0 #x position will be set later, initializing to a default value
        self.command.linear.y = 0.0
        self.command.linear.z = 0.0
        self.command.angular.x = 0.0
        self.command.angular.y = 0.0
        self.command.angular.z = 0.0

    def laser_callback(self, scan):
		
		self.getPosition(scan) 
		rospy.logdebug('position: {0}'.format(self.position))

		#if there's something within self.followDist from us, start following.
		
		if (self.closest < self.followDist):
			self.pubbark = rospy.Publisher('follow', String)
			self.pubbark.publish(String("Bark"))
			self.follow()
		#else doesn't run
		else:
			self.stop() 

        rospy.logdebug('Distance: {0}, speed: {1}, angular: {2}'.format(self.closest, self.command.linear.x, self.command.angular.z))
		self.pub.publish(self.command)

	#Starts following the nearest object.
    def follow(self):
	self.command.linear.x = tanh(5 * (self.closest - self.stopDistance)) * self.max_speed
	#turn faster the further we're turned from master.
	self.command.angular.z = ((self.position-320.0)/320.0)
		
	#if bot is going slower than min_speed stop.
	if abs(self.command.linear.x) < self.min_speed:
    	    self.command.linear.x = 0.0  

    def stop(self):
        self.command.linear.x = 0.0
		self.command.angular.z = 0.0

    def getPosition(self, scan):
    #remove nan objects
	nArr = []
	for dist in scan.ranges:
	    if not np.isnan(dist):
			nArr.append(dist)
	#make numpy array
	dArr = scan.ranges[:]

	#If nArr is empty all objects are nan,no reading obtained, too close to master.
	#thus establish our distance/position to nearest object as "0".
	if len(nArr) == 0:
	    self.closest = 0
	    self.position = 0
	else:
	    self.closest = min(depths)
	    self.position = dArr.index(self.closest)

# listening for possible master movements		
def listener():
	print "I am listening"
	rospy.Subscriber("move", Bool, callback)
	rospy.spin()

def callback(data):
	#move.py sends signal, detected by tracking.py, if so, bot starts to move
	if str(data) == "data: True":
		follower()

if __name__ == "__main__":
	#initialize rospy node as follower
    rospy.init_node('follow', log_level=rospy.DEBUG, anonymous=True)
    listener()