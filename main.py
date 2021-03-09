import argparse
from multiprocessing import Process, Queue
import subprocess
import time
import datetime
import os

import button
import detect_qr
import s2t
import qa
import qa_2
import read

if not os.path.isdir('./log'):
    os.mkdir('./log')

now = datetime.datetime.now()
FILE_NAME = './log/' + now.strftime('%Y_%m_%d') + '.txt'
if not os.path.isfile(FILE_NAME):
    with open(FILE_NAME, mode='w'):
        pass

parser = argparse.ArgumentParser()
parser.add_argument('type')
parser.add_argument('food')
args = parser.parse_args()

# 実験条件のバージョン
if args.type == '1':
    time_sw, conc_sw, qa_sw, announce_sw = 'off', 'off', 'off', 'on'
elif args.type == '2':
    time_sw, conc_sw, qa_sw, announce_sw = 'on', 'off', 'off', 'on'
elif args.type == '3':
    time_sw, conc_sw, qa_sw, announce_sw = 'off', 'on', 'off', 'on'
elif args.type == '4':
    time_sw, conc_sw, qa_sw, announce_sw = 'on', 'on', 'off', 'on'
elif args.type == '5':
    time_sw, conc_sw, qa_sw, announce_sw = 'on', 'on', 'on', 'on'
elif args.type == '6':
    time_sw, conc_sw, qa_sw, announce_sw = 'on', 'on', 'on', 'on'
elif args.type == '7':
    time_sw, conc_sw, qa_sw, announce_sw = 'on', 'on', 'on', 'off'
elif args.type == 'test_1':
    time_sw, conc_sw, qa_sw, announce_sw = 'off', 'off', 'off', 'on'
elif args.type == 'test_2':
    time_sw, conc_sw, qa_sw, announce_sw = 'on', 'on', 'on', 'on'

# 次に読み上げるまでの時間（秒）
interval = 300

#################################################################

if __name__ == '__main__':
    print('実験条件: ', args.type)

    start_qa = Queue() # ボタン操作によるQAの開始
    stop_read = Queue() # ボタン操作による読み上げの停止
    stop_all = Queue() # ボタン操作による全てのプロセスの停止
    stop_timer = Queue() # ボタン操作による時間計測の終了

    all_data = Queue() # これまでに認識した全ての結果を保持
    read_text = Queue() # 検出結果として読み上げるテキストを保持

    voice = Queue() # 入力音声を保持
    block_read = Queue() # Q中の検出の読み上げをブロック

    qa_text = Queue() # Qの確認とAの読み上げテキストを保持

    p_id = Queue() # 読み上げをkillするためにプロセスidを保持

    p_button = Process(target=button.button, args=(start_qa, block_read, stop_read, stop_all, stop_timer, p_id, qa_sw,)) # ボタン操作プロセス
    p_detect_qr = Process(target=detect_qr.detect_qr, args=(all_data, read_text, stop_all, time_sw, conc_sw, qa_sw, interval, args.type, args.food,)) # QR検出・整形プロセス
    p_s2t = Process(target=s2t.s2t, args=(voice, start_qa,)) # 音声入力プロセス
    p_qa = Process(target=qa.qa, args=(voice, all_data, qa_text, stop_all, args.type, args.food,)) # QA処理プロセス
    p_qa_2 = Process(target=qa_2.qa, args=(voice, all_data, qa_text, stop_all, args.type, args.food,)) # QA処理プロセス
    p_read = Process(target=read.read, args=(qa_text, read_text, block_read, stop_read, p_id, qa_sw, announce_sw,)) # 読み上げプロセス

    p_button.start()
    p_detect_qr.start()
    if qa_sw == 'on':
        p_s2t.start()
        if args.type == '5' or args.type == 'test_2':
            p_qa.start()
        elif args.type == '6' or args.type == '7':
            p_qa_2.start()
    p_read.start()
    start = time.time()
    print('START... All Processes!')

    while True:
        if not stop_timer.empty():
            run_time = time.time() - start
            print('                           ### Recorded Time ###')
            print('                           ', run_time)
            with open(FILE_NAME, mode='a') as f:
                f.write('\n実験条件' + args.type + '_' + args.food)
                f.write('\nrun_time : ' + str(run_time))
            break

    p_button.join()
    p_detect_qr.join()
    if qa_sw == 'on':
        p_s2t.terminate()
        p_s2t.join()
        if args.type == '5':
            p_qa.terminate()
            p_qa.join()
        elif args.type == '6' or args.type == '7':
            p_qa_2.terminate()
            p_qa_2.join()
    p_read.terminate()
    p_read.join()
    print('STOP... All Processes!')
