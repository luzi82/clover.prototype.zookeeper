import pygame
import sys
import cv2
import numpy as np
from clover.video_input import video_capture
import os
import threading
import collections

FFMPEG_EXEC_PATH = os.path.join('dependency','FFmpeg','ffmpeg')

SCREEN_SIZE = 400, 255
VIDEO_SIZE = 120, 213
WHITE = 255,255,255

class Bot:

    def __init__(self):
        pass
    
    def main(self, src_name):
        self.lock = threading.Lock()
    
        self.vc = video_capture.VideoCapture(FFMPEG_EXEC_PATH,src_name,VIDEO_SIZE[0],VIDEO_SIZE[1])
        self.vc.start()
        self.vc.wait_data_ready()

        img_surf = pygame.pixelcopy.make_surface(np.zeros((VIDEO_SIZE[0],VIDEO_SIZE[1],3),dtype=np.uint8))
        screen = pygame.display.set_mode(SCREEN_SIZE)
    
        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break
    
            if not run: break
    
            img = self.vc.get_frame()
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.vc.release_frame()
            img = np.swapaxes(img,0,1)
            pygame.pixelcopy.array_to_surface(img_surf,img)
                
            #print(img.shape)
            
            screen.fill(WHITE)
            screen.blit(img_surf,(0,0))
            pygame.display.flip()
    
        self.vc.close()

    def logic_run(self):
        

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='video capture')
    parser.add_argument('src_name', help='src_name')
    args = parser.parse_args()

    bot = Bot()
    bot.main(args.src_name)
