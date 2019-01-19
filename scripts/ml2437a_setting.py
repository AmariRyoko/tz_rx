#! /usr/bin/env python3

import sys
import time

sys.path.append("/home/amigos/ros/src/NASCORX_System-master")
import pymeasure

import pyinterface

import rospy
import threading
import std_msgs
from std_msgs.msg import Float64
from std_msgs.msg import String
from std_msgs.msg import Int32


class ml2437a_controller(object):
    def __init__(self):

        self.pm = ml2437a_driver()

        self.pub_ave_onoff = rospy.Publisher("ml2437a_ave_onoff", Int32, queue_size = 1)
        self.sub_ave_onoff = rospy.Subscriber("ml2437a_ave_onoff_cmd", Int32, self.ave_onoff)
        self.pub_ave_count = rospy.Publisher("ml2437a_ave_count", Int32, queue_size = 1)
        self.sub_ave_count = rospy.Subscriber("ml2437a_ave_count_cmd", Int32, self.ave_count)

        self.rate = rospy.get_param('~rate')
        self.mode = 'diff'
        self.ch = 17

        rsw_id = rospy.get_param('~rsw_id')

        self.pub_power = rospy.Publisher('cpz3177_rsw{0}_{1}{2}'.format(rsw_id, self.mode, self.ch), Float64, queue_size=1)
        node_name = 'cpz3177'
        try:
            self.ad = pyinterface.open(3177, rsw_id)
        except OSError as e:
            rospy.logerr("{e.strerror}. node={node_name}, rsw={rsw_id}".format(**locals()))
            sys.exit()

#method

    def power(self):
        while not rospy.is_shutdown():
            msg = Float64()
            ret = self.ad.input_voltage(self.ch, self.mode)
            msg.data = ret
            self.pub_power.publish(msg)
            time.sleep(self.rate)
            continue

    def ave_onoff(self,q):
        self.pm.set_average_onoff(q.data)
        ret = self.pm.query_average_onoff()
        msg = Int32()
        msg.data = int(ret)
        self.pub_ave_onoff.publish(msg)

    def ave_count(self,q):
        self.pm.set_average_count(q.data)
        ret = self.pm.query_average_count()
        msg = Int32()
        msg.data = int(ret)
        self.pub_ave_count.publish(msg)

    def start_thread(self):
        th1 = threading.Thread(target=self.power)
        th1.setDaemon(True)
        th1.start()


class ml2437a_driver(object):

    def __init__(self, IP='192.168.100.44', GPIB=13, ch=1, resolution=3):
        self.IP = IP
        self.GPIB = GPIB
        self.com = pymeasure.gpib_prologix(self.IP, self.GPIB)
        self.com.open()
        self.com.send('CHUNIT %d, DBM' %(ch))
        self.com.send('CHRES %d, %d' %(ch, resolution))

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
    ctrl = ml2437a_controller()
    ctrl.start_thread()
    rospy.spin()


#2018/11/15
#written by H.Kondo
