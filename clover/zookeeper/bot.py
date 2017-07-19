import pygame
import sys
import cv2
import numpy as np
from clover.video_input import video_capture
import os
import threading
import collections
from . import bot_logic
import traceback
from clover.common import async_read_write_judge

FFMPEG_EXEC_PATH = os.path.join('dependency','FFmpeg','ffmpeg')

SCREEN_SIZE = 400, 255
VIDEO_SIZE = 120, 213
WHITE = 255,255,255

class Bot:

    def __init__(self):
        pass
    
    def main(self, src_name):
        self.lock = threading.RLock()

        self.run = True
    
        self.vc = video_capture.VideoCapture(FFMPEG_EXEC_PATH,src_name,VIDEO_SIZE[0],VIDEO_SIZE[1])
        self.vc.start()
        self.vc.wait_data_ready()

        img_surf = pygame.pixelcopy.make_surface(np.zeros((VIDEO_SIZE[0],VIDEO_SIZE[1],3),dtype=np.uint8))
        screen = pygame.display.set_mode(SCREEN_SIZE)

        self.logic_img_buf = [np.zeros((VIDEO_SIZE[1],VIDEO_SIZE[0],3),dtype=uint8) for _ in range(async_read_write_judge.BUFFER_COUNT)]
        self.logic_result_buf = [None] * async_read_write_judge.BUFFER_COUNT
        self.logic_result_arwj = async_read_write_judge.AsyncReadWriteJudge(self.lock)
        self.logic = bot_logic.BotLogic()
        self.logic_thread = thread.Thread(self.logic_run)
        self.logic_thread.start()

        img = np.zeros((VIDEO_SIZE[1],VIDEO_SIZE[0],3),dtype=uint8)

        while self.run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                    break
    
            if not self.run: break

            screen.fill(WHITE)
    
            with self.lock:
                tmp_img = self.vc.get_frame()
                np.copyto(img, tmp_img)
                self.vc.release_frame()
            tmp_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            tmp_img = np.swapaxes(tmp_img,0,1)
            pygame.pixelcopy.array_to_surface(img_surf,tmp_img)
            screen.blit(img_surf,(0,0))

            logic_read_idx = self.logic_result_arwj.get_read_idx()
            np.copyto(img, self.logic_img_buf[logic_read_idx])
            tmp_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            tmp_img = np.swapaxes(tmp_img,0,1)
            pygame.pixelcopy.array_to_surface(img_surf,tmp_img)
            screen.blit(img_surf,(120,0))
            self.logic.draw(screen,self.logic_result_buf[logic_read_idx])
            self.logic_result_arwj.release_read_idx()
            
            pygame.display.flip()
    
        self.logic_thread.join()
        self.vc.close()

    def logic_run(self):
        try:
            while self.run:
                write_idx = self.logic_result_arwj.get_write_idx()
                img = self.logic_img_buf[write_idx]
                with self.lock:
                    tmp_img = self.vc.get_frame()
                    np.copyto(img, tmp_img)
                    self.vc.release_frame()
                logic_result = self.logic.tick(img)
                self.logic_result_buf[write_idx] = logic_result
                self.logic_result_arwj.release_write_idx()
        except:
            traceback.print_exc()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='video capture')
    parser.add_argument('src_name', help='src_name')
    args = parser.parse_args()

    bot = Bot()
    bot.main(args.src_name)
