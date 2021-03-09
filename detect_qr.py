import cv2
import sys
import os
from pyzbar.pyzbar import decode
import copy
import csv
import time
import numpy as np

def detect_qr(queue_all_data, queue_read_text, queue_stop_all, time_sw, conc_sw, qa_sw, interval, type, food):
    # 番号、商品名、商品名の読み方、上位クラスを、csvから読み込み
    path = './csv/' + food + '/' + food + '_' + type + '.csv'
    print('csv : ', food + '_' + type)
    with open(path, encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        csv_data = {}
        # 例） {1:[綾鷹,あやたか,お茶,130]}
        for i in reader:
            csv_data.setdefault(i[0], []).extend([i[1],i[2],i[3],i[4]])

    # 読み上げたQRコードのテキストと発見時間を保存するリスト
    recorded_time = {}
    # QAの処理に渡すデータ
    all_data = {}

    # 認識した数と最低価格を調べる変数
    all_result = []
    tmp_cnt = 0
    tmp_min = 10000000

    # カメラ映像をキャプチャ
    cap = cv2.VideoCapture(0)
    if cap.isOpened() == False:
        print('can\'t read video!')
        sys.exit()

    # キャプチャした映像を１フレームごとに処理
    while True:
        ret, frame = cap.read()
        if ret:
            # 検出したQRコードのテキストを保存
            result = []
            # 読み上げ用
            read_list = []
            read_dict = {}

            # QRコードを検出
            for qrcode in decode(frame):
                textData = qrcode.data.decode('utf-8')
                # 検出したQRにマーカーを表示
                pts = np.array([qrcode.polygon], np.int32)
                pts = pts.reshape((-1,1,2))
                cv2.polylines(frame, [pts], True, (255,0,255), 5)
                pts2 = qrcode.rect
                if textData.isdecimal():
                    if int(textData) in list(range(25)): # 特定の数字以外が検出されるのを回避
                        result.append(textData)
            #print('result: ', result)

            # result から all_data を作成
            # 例) {お茶:[[綾鷹,130],[伊右衛門,140]],コーヒー:[[クラフトボスラテ,150]]}
            for i in result:
                if csv_data[i][2] in all_data:
                    if not [csv_data[i][0], csv_data[i][3]] in all_data[csv_data[i][2]]:
                        all_data[csv_data[i][2]].append([csv_data[i][0], csv_data[i][3]])
                else:
                    all_data.setdefault(csv_data[i][2], []).append([csv_data[i][0], csv_data[i][3]])

            if qa_sw == 'on':
                queue_all_data.put(all_data)
            #print('all_data: ', all_data)


            for i in result:
                if not i in all_result:
                    all_result.append(i)

            if tmp_cnt != len(all_result):
                print('---------------------------------------------------')
                print('認識済商品数: ', len(all_result))
                tmp_cnt = len(all_result)
                min_price = []
                for i in all_result:
                    min_price.append([int(csv_data[i][3]), csv_data[i][0]])
                min_price.sort()
                if len(min_price) > 2:
                    if min_price[0][0] == min_price[1][0] and min_price[0][0] == min_price[2][0]:
                        print('　　最安　　: ', min_price[0][1], min_price[1][1], min_price[2][1], str(min_price[0][0])+'円')
                    elif min_price[0][0] == min_price[1][0]:
                        print('　　最安　　: ', min_price[0][1], min_price[1][1], str(min_price[0][0])+'円')
                    else:
                        print('　　最安　　: ', min_price[0][1], str(min_price[0][0])+'円')
                elif len(min_price) == 2:
                    if min_price[0][0] == min_price[1][0]:
                        print('　　最安　　: ', min_price[0][1], min_price[1][1], str(min_price[0][0])+'円')
                    else:
                        print('　　最安　　: ', min_price[0][1], str(min_price[0][0])+'円')
                elif len(min_price) == 1:
                        print('　　最安　　: ', min_price[0][1], str(min_price[0][0])+'円')

                tmp_min = min_price[0][0]


            # 以降は取捨選択に合わせて、読み上げる情報を減らす
            # 時間
            if time_sw == 'on':
                for i in result:
                    if not i in recorded_time:
                        read_list.append(i)
                        recorded_time[i] = time.time()
                    elif (time.time()-recorded_time[i]) > interval:
                        read_list.append(i)
                        recorded_time[i] = time.time()
            else:
                read_list = copy.copy(result)
            #print('read_list :', read_list)
            #print('recorded_time', recorded_time)

            # 概念的意味論
            if conc_sw == 'on':
                # resultの中身を変換（例、 {お茶:[[あやたか,130],[いえもん,140],[おーいおちゃ,130]]}）
                for i in read_list:
                    if csv_data[i][2] in read_dict:
                        read_dict[csv_data[i][2]].append([csv_data[i][1], csv_data[i][3]])
                    else:
                        read_dict.setdefault(csv_data[i][2], []).append([csv_data[i][1], csv_data[i][3]])
                #print('read_dict: ', read_dict)
                queue_read_text.put(read_dict)
                #print(read_dict)
            else:
                # resultの中身を変換（例、'1'→'[あやたか,130]'）
                for i in range(len(read_list)):
                    read_list[i] = [csv_data[read_list[i]][1], csv_data[read_list[i]][3]]
                #print('read_list: ', read_list)
                queue_read_text.put(read_list)

            # 映像出力
            height = frame.shape[0]
            width = frame.shape[1]
            cv2.imshow('cap', cv2.resize(frame, (int(width*360//height), 360)))
            if cv2.waitKey(1) & 0xff == ord('q'):
                queue_stop_all.put(1)
                break
            if not queue_stop_all.empty():
                break
        else:
            sys.exit()


    cap.release()
    cv2.destroyAllWindows()
