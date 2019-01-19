#! /usr/bin/env python3

import sys
import time

sys.path.append("/home/amigos/ros/src/NASCORX_System-master")
import pymeasure

import rospy
import threading
import std_msgs
from std_msgs.msg import Float64
from std_msgs.msg import String
from std_msgs.msg import Int32


class ml2437a_controller(object):
    def __init__(self):

        self.pm = ml2437a_driver()

        self.sub_power = rospy.Subscriber("topic_sub_power", Int32, self.power_switch)
        self.pub_power = rospy.Publisher("topic_pub_power", Float64, queue_size = 1)
        self.pub_ave_onoff = rospy.Publisher("topic_pub_ave_onoff", Int32, queue_size = 1)
        self.sub_ave_onoff = rospy.Subscriber("topic_sub_ave_onoff", Int32, self.ave_onoff)
        self.pub_ave_count = rospy.Publisher("topic_pub_ave_count", Int32, queue_size = 1)
        self.sub_ave_count = rospy.Subscriber("topic_sub_ave_count", Int32, self.ave_count)

#flag
        self.power_flag = 1

#switch
    def power_switch(self,q):
        self.power_flag = q.data
        return

#method
    def power(self):
        while not rospy.is_shutdown():
            while self.power_flag == 0 :
                continue
            while self.power_flag == 1 :
                ret = self.pm.measure()
                msg = Float64()
                msg.data = float(ret)
                self.pub_power.publish(msg)
                continue
            continue

    def ave_onoff(self,q):
        self.power_flag = 0
        time.sleep(1)

        self.pm.set_average_onoff(q.data)

        ret = self.pm.query_average_onoff()
        msg = Int32()
        msg.data = int(ret)
        self.pub_ave_onoff.publish(msg)

        self.power_flag = 1

    def ave_count(self,q):
        self.power_flag = 0
        time.sleep(1)

        self.pm.set_average_count(q.data)
        ret = self.pm.query_average_count()
        msg = Int32()
        msg.data = int(ret)
        self.pub_ave_count.publish(msg)

        self.power_flag = 1

    def start_thread(self):
        th1 = threading.Thread(target=self.power)
        th1.setDaemon(True)
        th1.start()


class ml2437a_driver(object):

    def __init__(self, ch=1, resolution=3):
        self.IP = IP
        self.GPIB = GPIB
        self.com = pymeasure.gpib_prologix(self.IP, self.GPIB)
        self.com.open()
        self.com.send('CHUNIT %d, DBM' %(ch))
        self.com.send('CHRES %d, %d' %(ch, resolution))

    def measure(self, ch=1, resolution=3):
        '''
        DESCRIPTION
        ================
        This function queries the input power level.

        ARGUMENTS
        ================
        1. ch: the sensor channel number.
            Number: 1-2
            Type: int
            Default: 1
        2. resolution: the sensor order of the resolution.
            Number: 1-3
            Type: int
            Default: 3

        RETURNS
        ================
        1. power: the power value [dBm]
            Type: float
        '''
        self.com.send('o %d' %(ch))
        ret = self.com.readline()
        power = float(ret)
        return power

    def set_average_onoff(self, onoff, sensor='A'):
        '''
        DESCRIPTION
        ================
        This function switches the averaging mode.

        ARGUMENTS
        ================
        1. onoff: averaging mode
            Number: 0 or 1
            Type: int
            Default: Nothing.

        2. sensor: averaging sensor.
            Number: 'A' or 'B'
            Type: string
            Default: 'A'

        RETURNS
        ================
        Nothing.
        '''

        if onoff == 1:
            self.com.send('AVG %s, RPT, 60' %(sensor))
        else:
            self.com.send('AVG %s, OFF, 60' %(sensor))
        return

    def query_average_onoff(self):
        '''
        DESCRIPTION
        ================
        This function queries the averaging mode.

        ARGUMENTS
        ================
        Nothing.

        RETURNS
        ================
        1. onoff: averaging mode
            Number: 0 or 1
            Type: int
        '''

        self.com.send('STATUS')
        ret = self.com.readline()
        if ret[17] == '0':
            ret = 0
        else:
            ret = 1
        return ret

    def set_average_count(self, count, sensor='A'):
        '''
        DESCRIPTION
        ================
        This function sets the averaging counts.

        ARGUMENTS
        ================
        1. count: averaging counts
            Type: int
            Default: Nothing.

        2. sensor: averaging sensor.
            Number: 'A' or 'B'
            Type: string
            Default: 'A'

        RETURNS
        ================
        Nothing.
        '''

        self.com.send('AVG %s, RPT, %d' %(sensor, count))

        return

    def query_average_count(self):
        '''
        DESCRIPTION
        ================
        This function queries the averaging counts.

        ARGUMENTS
        ================
        Nothing.

        RETURNS
        ================
        1. count: averaging counts
            Type: int
        '''
        self.com.send('STATUS')
        ret = self.com.readline()
        count = int(ret[19:23])

        return count


if __name__ == "__main__" :
    rospy.init_node("ml2437a")
    GPIB = rospy.get_param('~port')
    IP = rospy.get_param('~host')
    ctrl = ml2437a_controller()
    ctrl.start_thread()
    rospy.spin()

#2018/11/01
#written by H.Kondo
