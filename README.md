# QA_system

2020_実験で使用したコード

## 環境構築（m1チップのmacのセットアップを含む）
・xcode、webcam settingのインストール  
・brewが使えるように設定  
　Finder > アプリケーション > ユーティリティ > ターミナル > 情報を見る > Rosettaを使用して開く、にチェック  
　その後は普通にbrewをインストール  
・python3とopencvをbrewでインストール  
・zbar,pyzbar,PySide2,portaudio,pyaudio,termcolorをインストール  


## プログラムについて
| プログラム名 | 役割 |
---|---
| main.py | マルチプロセスを管理 |
| button.py | ボタン入力を検出 |
| qr_detect.py | カメラからQRコードを検出し、整形 |
| s2t.py | 音声認識 |
| qa.py | QAの処理 |
| qa_2.py | QAの処理 |
| read.py | 読み上げの処理 |
| states_1.scxml | 状態遷移の管理 |
