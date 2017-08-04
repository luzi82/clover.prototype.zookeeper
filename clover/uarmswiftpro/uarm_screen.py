import threading
import time
import sys

from . import uarm
from . import screen_arm_position

class UArmScreen:

    def __init__(self, uarm_calibration_filename, lock=None):
        if lock == None:
            lock = threading.Lock()

        self._on_report_position = None
        self.last_report_position = None

        self.lock = lock
        self.uarm = uarm.UArm()
        self.uarm.set_on_report_position(self._uarm_on_report_position)
        self.sap = screen_arm_position.ScreenArmPosition(uarm_calibration_filename)

    def connect(self,port=None):
        self.uarm.connect(port)

    def close(self):
        self.uarm.close()

    def wait_ready(self):
        return self.uarm.wait_ready()

    def set_position(self,pos,f):
        #print('YMKRXBVHWJ set_position',file=sys.stderr)
        arm_x, arm_y = self.sap.screen_to_arm(pos[0],pos[1])
        arm_z = pos[2]*self.sap.json['down_z'] + (1-pos[2])*self.sap.json['up_z']
        return self.uarm.set_position(arm_x,arm_y,arm_z,f)

    def set_report_position(self, enable):
        return self.uarm.set_report_position(enable)

    def get_last_report_position(self):
        with self.lock:
            return self.last_report_position

    def wait_report_position_ready(self):
        while True:
            if self.get_last_report_position():
                break
            time.sleep(0.01)

    def _uarm_on_report_position(self,pos):
        pos_x,pos_y = self.sap.arm_to_screen(pos[0],pos[1])
        pos_z = (pos[2]-self.sap.json['up_z'])/(self.sap.json['down_z']-self.sap.json['up_z'])
        pos = (pos_x,pos_y,pos_z)
        with self.lock:
            self.last_report_position = pos
        if self._on_report_position:
            self._on_report_position(pos)

class _FutureConv:

    def __init__(self, future, func):
        self.future = future
        self.func = func
    
    def wait(self):
        ret = self.future.wait()
        if self.func != None:
            return self.func(ret)
        else:
            return ret

    def is_busy(self):
        return self.future.is_busy()