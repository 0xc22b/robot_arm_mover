import sys
import os

from time import sleep

import serial

class RobotArm(object):

    servo_names = [('s1', 1), ('s2', 2), ('s3', 3), ('s4', 4), ('s5', 5), ('s6', 6)]

    possible_positions = {
        1: (-50, 50),
        2: (0, 90),
        3: (-50, 50),
        4: (0, 90),
        5: (-50, -50),
        6: (45, 45)
    }

    marked_msg_positions = {
        1: (),
        2: (2050, 1400, 740),
        3: (2050, 1250, 500),
        4: (-1, 1350, 550),
        5: (2100, 1480, 740),
        6: (2200, 1650, 850)
    }

    def __init__(self):

        self._velocity = 1.0
        self._s1_position = 0
        self._s2_position = 0
        self._s3_position = 0
        self._s4_position = 0
        self._s5_position = 0
        self._s6_position = 0

        self.init_position()

    def init_position(self):

        # First movement of each servo impacts previous servo
        # Workaround is using minimum time, reducing impacts
        # and order might help

        msg, time = self._gen_position_msg(3, 0, 100)
        self._send_msg_and_sleep(msg, time)
        self._s3_position = 0

        msg, time = self._gen_position_msg(2, 10, 100)
        self._send_msg_and_sleep(msg, time)
        self._s2_position = 10

        msg, time = self._gen_position_msg(4, 10, 100)
        self._send_msg_and_sleep(msg, time)
        self._s4_position = 10

    def move(self, positions):

        is_valid, err_msg = self._validate_positions(positions)
        if not is_valid:
            print(err_msg)
            return

        whole_msg = ''
        max_time = 0

        for servo_name, servo_no in RobotArm.servo_names:
            if servo_name in positions:
                position = positions[servo_name]
                msg, time = self._gen_position_msg(servo_no, position)

                whole_msg += msg
                max_time = max(max_time, time)

        self._send_msg_and_sleep(whole_msg, max_time)

    def _validate_positions(self, positions):

        for servo_name, servo_no in RobotArm.servo_names:
            if servo_name in positions:
                position = positions[servo_name]
                if (position < RobotArm.possible_positions[servo_no][0] or
                    position > RobotArm.possible_positions[servo_no][1]):

                    return (False, 'Error: servo no. ' + str(servo_no) + '\'s position is out of range: ' + str(position))

        if 's2' in positions and 's3' in positions:

            s2_position = positions['s2']
            s3_position = positions['s3']

            if ((s2_position < 45 and s3_position < 0) or
                (s2_position > 45 and s3_position > 0)):
                return (False, 'Error: servo no. 2 and 3\'s positions are out of range: ' + str(s2_position) + ', ' + str(s3_position))

        if 's2' in positions and 's4' in positions:

            s2_position = positions['s2']
            s4_position = positions['s4']

            if ((s2_position < 45 and s4_position > s2_position + 10) or
                (s2_position > 45 and s4_position < 45)):
                return (False, 'Error: servo no. 2 and 4\'s positions are out of range: ' + str(s2_position) + ', ' + str(s4_position))

        return (True, None)

    def _gen_position_msg(self, servo_no, position, time=None):

        msg_position = self._get_msg_position(
            position,
            RobotArm.marked_msg_positions[servo_no][1],
            RobotArm.marked_msg_positions[servo_no][2],
            RobotArm.marked_msg_positions[servo_no][0])

        if not time:
            time = 1500

        msg = self._gen_msg(servo_no, msg_position, time)

        return msg, time

    def _get_msg_position(self,
                          position,
                          front_msg_position,
                          right_msg_position,
                          left_msg_position):

        position = float(position)
        front_msg_position = float(front_msg_position)
        right_msg_position = float(right_msg_position)
        left_msg_position = float(left_msg_position)

        if position >= 0.0:
            msg_position = front_msg_position - (position / 90.0 * abs(front_msg_position - right_msg_position))
        else:
            msg_position = front_msg_position + (abs(position) / 90.0 * abs(front_msg_position - left_msg_position))

        return int(msg_position)

    def _gen_msg(self, servo_no, position, time):

        assert(servo_no >= 1 and servo_no <= 6)
        assert(position >= 500 and position <= 2500)
        assert(time > 0)

        msg = '#' + str(servo_no) + 'P' + str(position) + 'T' + str(time)

        return msg

    def _send_msg_and_sleep(self, msg, sleep_time):
        ser = serial.Serial('/dev/ttyACM0', 9600)
        msg = msg + chr(0x0d) + chr(0x0a)
        ser.write(msg.encode('utf-8'))
        ser.close()

        sleep((float(sleep_time) / 1000) + 0.5)

def move_robot_arm1(robot_arm):
    robot_arm.move({
        's2': 10
    })
    robot_arm.move({
        's2': 80
    })
    robot_arm.move({
        's2': 10
    })
    robot_arm.move({
        's2': 80
    })
    # Back to init positions
    robot_arm.move({
        's2': 10
    })

def move_robot_arm2(robot_arm):
    robot_arm.move({
        's3': 0
    })
    robot_arm.move({
        's3': -50
    })
    robot_arm.move({
        's3': 0
    })
    robot_arm.move({
        's3': -50
    })
    # Back to init positions
    robot_arm.move({
        's3': 0
    })

def move_robot_arm3(robot_arm):
    robot_arm.move({
        's2': 10,
        's3': 0
    })
    robot_arm.move({
        's2': 80,
        's3': -50
    })
    robot_arm.move({
        's2': 10,
        's3': 0
    })
    robot_arm.move({
        's2': 80,
        's3': -50
    })
    # Back to init positions
    robot_arm.move({
        's2': 10,
        's3': 0
    })

def move_robot_arm4(robot_arm):
    robot_arm.move({
        's4': 10
    })
    robot_arm.move({
        's4': 80
    })
    robot_arm.move({
        's4': 10
    })
    robot_arm.move({
        's4': 80
    })
    # Back to init positions
    robot_arm.move({
        's4': 10
    })

def move_robot_arm5(robot_arm):
    robot_arm.move({
        's2': 10,
        's3': 0,
        's4': 10
    })
    robot_arm.move({
        's2': 80,
        's3': -50,
        's4': 80
    })
    robot_arm.move({
        's2': 10,
        's3': 0,
        's4': 10
    })
    robot_arm.move({
        's2': 80,
        's3': -50,
        's4': 80
    })
    # Back to init positions
    robot_arm.move({
        's2': 10,
        's3': 0,
        's4': 10
    })

if __name__ == '__main__':

    robot_arm = RobotArm()
#    move_robot_arm1(robot_arm)
#    move_robot_arm2(robot_arm)
#    move_robot_arm3(robot_arm)
#    move_robot_arm4(robot_arm)
    move_robot_arm5(robot_arm)
