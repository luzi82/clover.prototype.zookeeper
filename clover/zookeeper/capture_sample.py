from clover.video_input import video_capture
import random
import os
import time
import sys
import cv2

FFMPEG_EXEC_PATH = os.path.join('dependency','Ffmpeg','ffmpeg')
MAIN_WIDTH = 120
MAIN_HEIGHT = 213

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='video capture')
    parser.add_argument('src_name', help='src_name')
    #parser.add_argument('output_folder', help='output_folder')
    parser.add_argument('--disable_sleep', action='store_true', help='disable_sleep')
    parser.add_argument('--scm_path', nargs='?', help='state classifier model path')
    parser.add_argument('--scm_score', nargs='?', type=float, help='score to output img')
    parser.add_argument('--scm_img_path', nargs='?', help='scm img path')
    args = parser.parse_args()

    assert( (not args.disable_sleep) or ( args.scm_score != None ) )
    assert( (args.scm_score != None) == (args.scm_path != None) )
    assert( (args.scm_img_path != None) == (args.scm_path != None) )

    output_folder = os.path.join('dependency','zookeeper_screen_recognition','raw_image')

    t = int(time.time()*1000)
    #output_folder = os.path.join(args.output_folder,str(t))
    output_folder = os.path.join(output_folder,str(t))
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    state_clr = None
    if args.scm_path:
        import classifier_state
        state_clr = classifier_state.StateClassifier(args.scm_path)
        scm_img_path = os.path.join(args.scm_img_path,str(t))

    vc = video_capture.VideoCapture(FFMPEG_EXEC_PATH,args.src_name,MAIN_WIDTH,MAIN_HEIGHT)
    vc.start()
    vc.wait_data_ready()
    while True:
        t = int(time.time()*1000)
        t0 = int(t/100000)
        ndata = vc.get_frame()
        write_ok = True
        if state_clr:
            label, score = state_clr.get_state(ndata.astype('float32')*2/255-1)
            print('{} {}'.format(label,score),file=sys.stderr)
            write_ok = write_ok and (score < args.scm_score)
            if write_ok:
                ffn_dir = os.path.join(scm_img_path, label)
                ffn = os.path.join(ffn_dir,'{}.png'.format(t))
                if not os.path.isdir(ffn_dir):
                    os.makedirs(ffn_dir)
                print(ffn,file=sys.stderr)
                cv2.imwrite(ffn,ndata)
        if write_ok:
            fn_dir = os.path.join(output_folder,str(t0))
            fn = os.path.join(fn_dir,'{}.png'.format(t))
            if not os.path.isdir(fn_dir):
                os.makedirs(fn_dir)
            print(fn,file=sys.stderr)
            cv2.imwrite(fn,ndata)
        vc.release_frame()
        if not args.disable_sleep:
            time.sleep(0.05+0.05*random.random())
    vc.close()
