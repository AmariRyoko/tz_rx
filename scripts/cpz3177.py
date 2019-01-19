#! /usr/bin/env python3


import sys
import time
import numpy
import pyinterface

import rospy
from std_msgs.msg import Float64

sis_ch=8
pm_ch=2

if __name__ == '__main__':

    rospy.init_node('cpz3177')
    rate = rospy.get_param('~rate')
    rsw_id = rospy.get_param('~rsw_id')
    node_name = 'cpz3177'

    sis_ch_list = [i for i in range(1, sis_ch + 1)]
    pm_ch_list = [i for i in range(10, pm_ch+10)]

    sis_pub_list = [rospy.Publisher('{0}_rsw{1}_diff{2}'.format(node_name, rsw_id, ch), Float64, queue_size=1)
                       for ch in sis_ch_list]

    pm_pub_list = [rospy.Publisher('{0}_rsw{1}_diff{2}'.format(node_name, rsw_id, ch), Float64, queue_size=1)
                       for ch in pm_ch_list]

    try:
        ad = pyinterface.open(3177, rsw_id)
    except OSError as e:
        rospy.logerr("{e.strerror}. node={node_name}, rsw={rsw_id}".format(**locals()))
        sys.exit()

while not rospy.is_shutdown():

    for ch, pub in zip(pm_ch_list, pm_pub_list):
        ret = ad.input_voltage(ch, "diff")
        msg = Float64()
        msg.data = ret
        pub.publish(msg)

    for ch, pub in zip(sis_ch_list, sis_pub_list):
        ret = ad.input_voltage(ch, "diff")
        msg = Float64()
        msg.data = ret
        pub.publish(msg)
    time.sleep(rate)
    continue

#20181206
#change for Tz
#wriiten by Kondo
