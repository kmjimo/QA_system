import contextlib
with contextlib.redirect_stdout(None):
    import pygame
from pygame.locals import *
import sys
import subprocess
import time
import datetime

def button(queue_start_qa, queue_block_read, queue_stop_read, queue_stop_all, queue_stop_timer, queue_p_id, qa_sw):
    pygame.init()
    screen = pygame.display.set_mode((240,180))
    pygame.display.set_caption('button event')

    now = datetime.datetime.now()
    FILE_NAME = './log/' + now.strftime('%Y_%m_%d') + '.txt'

    stop_cnt = 0
    while True:
        screen.fill((0,0,0))  #画面を黒で塗りつぶす
        pygame.display.update() #描画処理を実行

        for event in pygame.event.get():
            if event.type == QUIT:
                queue_stop_timer.put(1)
                queue_block_read.put(1)
                queue_stop_all.put(1)
                print('                           ### Counted Pause ###')
                print('                           ', stop_cnt)
                with open(FILE_NAME, mode='a') as f:
                    f.write('\nstop_cnt : ' + str(stop_cnt))
                if not queue_p_id.empty():
                    subprocess.call(['kill', str(queue_p_id.get())], shell=False)
                time.sleep(0.7)
                subprocess.call('afplay ./sound/stop_all.mp3 -r 1.4 -q 1', shell=True)
                pygame.quit()
                sys.exit()

            if qa_sw == 'on':
                if event.type == KEYDOWN and event.key == K_RIGHT:
                    queue_start_qa.put(1)
                    queue_block_read.put(1)
                    print('                           ### START QA ###')
                    if not queue_p_id.empty():
                        subprocess.call(['kill', str(queue_p_id.get())], shell=False)
                    time.sleep(0.7)
                    subprocess.call('afplay ./sound/start_qa.mp3 -r 1.4 -q 1', shell=True)

            if event.type == KEYDOWN and event.key == K_LEFT:
                queue_stop_read.put(1)
                print('                           ### STOP Read ###')
                if not queue_p_id.empty():
                    subprocess.call(['kill', str(queue_p_id.get())], shell=False)
                time.sleep(0.7)
                subprocess.call('afplay ./sound/stop_read.mp3 -r 1.4 -q 1', shell=True)
                stop_cnt += 1

            if event.type == KEYDOWN and event.key == K_RETURN:
                queue_stop_timer.put(1)
