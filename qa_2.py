import sys
import csv
from PySide2 import QtCore, QtScxml
from copy import deepcopy

def info_id(str_info):

    # ユーザのQの受け取り
    text = str_info
    ans_list = ['ありますか' , 'ない' , 'ある' , '情報', 'いくら' , '何円' , '一番安い' , '認識結果' , '検出結果' , '商品リスト' , 'カテゴリリスト' , 'カテゴリーリスト' , '種類']# 応答可能な質問かどうかを調べるためのlist
    flag = 0# 応答可能な質問かどうかを識別するための変数

    for word in ans_list:
        if word in text:
            flag = 1

    return flag

def get_A(D, Q):

    # 必要な情報の辞書とリスト
    info = D          # 辞書の作成
    info_list_name = []# 名前のみのlistの作成
    info_list_val = []# valueのみlistの作成
    info_list_val_name = []# valueの値段を除いた名前のみのlistの作成
    for v in info.keys():# 辞書をリストに変換(key)
        info_list_name.append(v)
    for v in info.values():# 辞書をリストに変換(value)
        info_list_val.extend(v)
    for v in range(len(info_list_val)):# valueの名前だけのlist
        info_list_val_name.append(info_list_val[v][0])
    for v in range(len(info_list_val_name)):
        info_list_name.append(info_list_val_name[v])

    # 識別するための情報の追加
    plus_info = ['他' , '情報' , '認識結果' , '一番安い' , '検出結果' , '種類' , '商品リスト' , 'カテゴリリスト' , 'カテゴリーリスト']
    for v in range(len(plus_info)):
        info_list_val_name.append(plus_info[v])

    # テキストから取得した情報数を返す関数.見つからない場合は0を返す.
    def get_info_num(text):
        flag = 0
        for information_num in info.keys():
            if information_num in text:
                flag += 1
        for information_num in info_list_val_name:
            if information_num in text:
                flag += 1
                if information_num == '他':
                    flag += 100
                if information_num == '一番安い':
                    flag += 1000
        return flag

    # テキストから必要なを抽出する関数．見つからない場合は空文字を返す．
    def get_info(text):
        info_key = 0   # 得られる情報がkeyかどうかを識別する変数
        info_value = 0 # 得られる情報がvalueかどうかを識別する変数
        case = 0       # 質問の種類を識別する変数
        key_name = ""  # 得られる情報(key)の名前を取得
        value_name = ""# 得られる情報(value)の名前を取得
        Q_case = 0     # 質問か読み上げ繰り返しなのかを識別する変数

        for information in info.keys():
            if information in text:
                if information != '他':
                    key_name = information# ユーザーに聞かれた情報(key)の名前を取得
                    info_key = 1
        for information in info_list_val_name:
            if information in text:
                if information != '他':
                    value_name = information# ユーザーに聞かれた情報(value)の名前を取得
                    info_value = 1
                if (value_name == "情報") or (value_name == "認識結果") or (value_name == "検出結果") or (value_name == "種類") or (value_name == "商品リスト") or (value_name == "カテゴリリスト") or (value_name == "カテゴリーリスト"):
                    Q_case = 1
        if info_key == 1 and info_value == 1:
            if value_name == '一番安い':
                pass
            else:
                info_key = 0# keyとvalueの一部がかぶっていた場合,valueを優先する処理
            return information , info_key , info_value , key_name , value_name , Q_case
        else:
            return information , info_key , info_value , key_name , value_name , Q_case
        return "" , info_key , info_value , key_name , value_name , Q_case

    # Qtに関するおまじない
    if not QtCore.QCoreApplication.instance():
        app = QtCore.QCoreApplication()
    else:
        app = QtCore.QCoreApplication.instance()
    el  = QtCore.QEventLoop()

    # SCXMLファイルの読み込み
    sm  = QtScxml.QScxmlStateMachine.fromFile('states_1.scxml')

    # 初期状態に遷移
    sm.start()
    el.processEvents()

    # 状態とシステム発話を紐づけた辞書
    uttdic = {"ask_info": ""}

    # 初期状態の取得
    current_state = sm.activeStateNames()[0]

    # 初期状態に紐づいたシステム発話の取得と出力
    sysutt = uttdic[current_state]


    # ユーザ入力の処理
    while True:
        text = Q# 質問を読み込む
        info_num = 0# 情報数が1or2の識別するための変数
        response_list = []# 返す答えの要素を保存するlist
        response_ans = []# 返す答えを保存するlist

        # ユーザ入力を用いて状態遷移と取得情報数
        if current_state == "ask_info":
            info_num = get_info_num(text)
            ans , info_key , info_value , key_name , value_name , case = get_info(text)
            if ans != "" and info_num == 1:# 情報数が1の場合の状態遷移を実行
                info_case = 1
                sm.submitEvent("ans")
                el.processEvents()
            if ans != "" and info_num == 2:# 情報数が1の場合の状態遷移を実行(keyとvalueの名前のかぶりあり)
                info_case = 1
                sm.submitEvent("ans")
                el.processEvents()
            if ans != "" and info_num > 2 and info_num < 1000:# 情報数が2の場合（カテゴリ＋他　or 商品名＋他）の状態遷移を実行
                info_case = 2
                sm.submitEvent("ans")
                el.processEvents()
            if ans != "" and info_num > 1000:# 情報数が2の場合（カテゴリ＋一番安い）の状態遷移を実行  
                info_case = 3
                sm.submitEvent("ans")
                el.processEvents()


        # 遷移先の状態を取得
        current_state = sm.activeStateNames()[0]

        # 遷移先がtell_infoの場合は情報を伝えて終了
        if current_state == "tell_info":
            # 伝える情報(info_caseにより伝える情報を区別)

            # 得られた情報が1つの場合
            if info_case == 1 and info_key == 1 and info_value == 0 and case == 0:# keyに関して聞かれた場合
                for information in info.keys(): 
                    if information == key_name:# 得られた情報(key)をkeyとして持つvalueを検索,表示
                        response_list = info[information]
                for i in range(len(response_list)):
                    response_ans.append(response_list[i][0])
                response_ans.append('があります')
            
            if info_case == 1 and info_key == 0 and info_value == 1 and case == 0:# valueに関して聞かれた場合(値段に関する質問)
                for information in range(len(info_list_val)):
                    if value_name == info_list_val[information][0]:
                        response_ans.append(str(info_list_val[information][1]) + '円です')

            if info_case == 1 and info_key == 0 and info_value == 1 and case == 1 and (value_name == '認識結果' or value_name == '検出結果' or value_name == '情報' or value_name == '商品リスト'):# 認識結果を返す処理
                for v in info_list_val_name:
                    response_ans.append(v)
                for i in range(len(plus_info)):
                    del response_ans[-1]
            
            if info_case == 1 and info_key == 0 and info_value == 1 and case == 1 and (value_name == '種類' or value_name == 'カテゴリリスト' or value_name == 'カテゴリーリスト'):# 商品の種類を返す処理
                for v in info.keys():
                    response_ans.append(v)

            # 得られた情報が2つの場合
            if info_case == 2 and info_key == 1 and info_value == 0 and case == 0:# あるkeyに関して他に何があるか聞かれた場合の検索,表示(key+他を想定)
                for information in info.keys():
                    if information == key_name:# 得られた情報(key)をkeyとして持つvalueを検索,表示
                        response_list = info[information]
                for i in range(len(response_list)):
                    response_ans.append(response_list[i][0])
                del response_ans[0]
                if response_ans == []:
                    response_ans.append('他にはありません')
                else:
                    response_ans.append('があります')

            if info_case == 2 and info_key == 0 and info_value == 1 and case == 0:# あるkeyに関して他に何があるか聞かれた場合の検索,表示(value+他を想定)
                del_number = 0# かぶっている商品を調べて削除するための変数
                for information in info.keys():
                    if type(info[information]) == list:
                        for i in range(len(info[information])):
                            if value_name in info[information][i][0]:
                                response_list = info[information]
                for i in range(len(response_list)):
                    response_ans.append(response_list[i][0])
                for number in range(len(response_ans)):# かぶっている商品を削除
                    if value_name == response_ans[number]:
                        del_number = number
                del response_ans[del_number]
                if response_ans == []:
                    response_ans.append('他にはありません')
                else:
                    response_ans.append('があります')

            if info_case == 3:# あるkeyに関して一番安い商品を聞かれた場合の検索，表示(key+一番安いを想定)
                if info_key == 0 and info_value == 1:
                    L = []
                    for v in info.values():
                        L.extend(v)
                    L = sorted(L, key=lambda x:x[1])
                    response_ans.append(str(L[0][1]) + '円の' + str(L[0][0]) + 'です')
                else:
                    L = []
                    for k,v in info.items():
                        if k == key_name:
                            L = deepcopy(v)
                    L = sorted(L,key=lambda x:x[1])
                    response_ans.append(str(L[0][1]) + '円の' + str(L[0][0]) + 'です')

            break

        else:
            # その他の遷移先の場合は状態に紐づいたシステム発話を生成
            response_ans.append('ありません')
            break     
    return case , response_ans

def qa(queue_voice, queue_all_data, queue_qa_text, queue_stop_all, type, food):
    # 商品名の読み方の辞書を作成
    # 例） {綾鷹:あやたか}
    path = './csv/' + food + '/' + food + '_' + type + '.csv'
    with open(path, encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        lab2yomi = {}
        for i in reader:
            lab2yomi[i[1]] = i[2]

    while True:
        if queue_stop_all.empty():
            all_data = queue_all_data.get()
        else:
            break
        #print(all_data)
        if not queue_voice.empty():
            question = queue_voice.get()
            #print(question)
            if info_id(question):
                case, answear = get_A(all_data, question)
                # QAのAは、「綾鷹」なので「あやたか」に変換
                for i in range(len(answear)):
                    tmp = answear[i].split('円の')
                    for j in range(len(tmp)):
                        if tmp[j] in lab2yomi:
                            tmp[j] = lab2yomi[tmp[j]]
                    tmp = '円の'.join(tmp)
                    answear[i] = tmp

                # リストを文字列に変換
                answear = '、'.join(answear)
                print('Q: ', question)
                print('A: ', answear)
                #print('case: ', case)
                queue_qa_text.put([question, answear, case])
            else:
                print('無効な質問です')
                queue_qa_text.put(['無効な質問です'])
