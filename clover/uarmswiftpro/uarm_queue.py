import queue
import threading
import time
import traceback
import sys

from . import uarm_async

CMD_IDX_MIN = 1
CMD_IDX_MAX = 10000

SLOT_COUNT = 2

class UArmQueue:

    def __init__(self, lock=None):
        if lock == None:
            lock = threading.RLock()
        
        self.lock = lock
        self.uaa = uarm_async.UArmAsync()
        self.cmd_queue = queue.Queue()
        self.next_cmd_idx = CMD_IDX_MIN
        self.loop_thread = None

    def connect(self,port=None):
        self.uaa.connect(port)
        self.loop_thread = threading.Thread(target=self._loop)
        self.loop_thread.start()

    def close(self):
        self.cmd_queue.put({'type':'close'})
        if self.loop_thread != None:
            self.loop_thread.join()
        self.uaa.close()

    def wait_ready(self):
        return self.uaa.wait_ready()

    def set_on_msg(self,on_msg):
        self.uaa.on_msg = on_msg

    def _get_next_cmd_idx(self):
        cmd_idx = self.next_cmd_idx
        self.next_cmd_idx += 1
        if self.next_cmd_idx > CMD_IDX_MAX:
            self.next_cmd_idx = CMD_IDX_MIN
        return cmd_idx

    def send_cmd(self,cmd):
        cmd_idx = self._get_next_cmd_idx()
        cmd_unit = {
            'type': 'cmd',
            'idx': cmd_idx,
            'cmd': cmd,
            'future': None,
            'uaa_future': None
        }
        future = _Future(self, cmd_unit)
        cmd_unit['future'] = future
        with self.lock:
            self.cmd_queue.put(cmd_unit)
        return future

    def _loop(self):
        try:
            unit_slot_list = [None]*SLOT_COUNT
            while(True):
                with self.lock:
                    if self.cmd_queue.empty():
                        unit = None
                    else:
                        unit = self.cmd_queue.get(block=False)
                if unit == None:
                    time.sleep(0.01)
                    continue
                if unit['type'] == 'close':
                    return
                if unit['type'] == 'cmd':
                    while(True):
                        slot_id = None
                        for i in range(SLOT_COUNT):
                            if unit_slot_list[i] == None:
                                slot_id = i
                                break
                            if not unit_slot_list[i]['future'].is_busy():
                                slot_id = i
                                break
                        if slot_id != None:
                            break
                        print('APITYUHGFB queue busy',file=sys.stderr)
                        time.sleep(0.01)
                    unit_slot_list[slot_id] = unit
                    unit['uaa_future'] = self.uaa.send_cmd(unit['cmd'])
                    time.sleep(0.1)
        except:
            traceback.print_exc()

    def wait_ready(self):
        self.uaa.wait_ready()
    
class _Future:
    
    def __init__(self,uq,unit):
        self.uq = uq
        self.unit = unit
    
    def wait(self):
        while True:
            if self.unit['uaa_future'] != None:
                break
            time.sleep(0.01)
        return self.unit['uaa_future'].wait()
    
    def is_busy(self):
        if self.unit['uaa_future'] == None:
            return True
        return self.unit['uaa_future'].is_busy()
