import subprocess
import time
import os

def synthesize_text(text, queue_p_id):
    """Synthesizes speech from the input string of text."""
    from google.cloud import texttospeech

    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)

    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.VoiceSelectionParams(
        language_code="ja-JP",
        name="ja-JP-Wavenet-B",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        request={"input": input_text, "voice": voice, "audio_config": audio_config}
    )

    # The response's audio_content is binary.
    with open("./sound/tmp.mp3", "wb") as out:
        out.write(response.audio_content)
        #print('Audio content written to file "output.mp3"')

    p = subprocess.Popen(['afplay', './sound/tmp.mp3', '-r', '1.4', '-q', '1'], shell=False)
    queue_p_id.put(p.pid)
    p.wait()
    while not queue_p_id.empty():
        queue_p_id.get()
    os.remove('./sound/tmp.mp3')


def read(queue_qa_text, queue_read_text, queue_block_read, queue_stop_read, queue_p_id, qa_sw, announce_sw):
    flag_block = False

    while True:
        # QAの読み上げ対応
        if not queue_qa_text.empty():
            qa_text = queue_qa_text.get()
            if len(qa_text) == 1:
                synthesize_text('無効な質問か、正しく聞き取ることができませんでした', queue_p_id)
            elif len(qa_text) == 3:
                question = qa_text[0]
                answear = qa_text[1]
                case = qa_text[2]
                # すべての認識結果の読み上げ
                if case == 1:
                    #synthesize_text('現在、' + str(len(answear.split('、'))) + '種類認識しています', queue_p_id
                    synthesize_text(answear + 'があります', queue_p_id)
                # QAの読み上げ
                else:
                    #synthesize_text('ご質問は、' + question + '、ですね？', queue_p_id)
                    subprocess.call('afplay ./sound/recognize.mp3 -r 1.4 -q 1', shell=True)
                    synthesize_text(answear, queue_p_id)
            # QA処理後、シグナル削除
            while not queue_block_read.empty():
                queue_block_read.get()
            flag_block = False


        # readの一時停止
        if not queue_stop_read.empty():
            time.sleep(10)
            while not queue_stop_read.empty():
                queue_stop_read.get()


        # 検出の読み上げ
        if not queue_read_text.empty():
            read_text = queue_read_text.get()
            # 音声入力中は読み上げない
            if queue_block_read.empty() and not flag_block:
                if len(read_text) > 0:
                    subprocess.call('afplay ./sound/beep.mp3 -q 1', shell=True)
                    if announce_sw == 'on':
                        # 出力が辞書（concがON）
                        if type(read_text) == dict:
                            for i in read_text:

                                if not queue_stop_read.empty():
                                    time.sleep(10)
                                    while not queue_stop_read.empty():
                                        queue_stop_read.get()
                                if not queue_block_read.empty():
                                    flag_block = True
                                    break

                                # qaがonかoffかで、値段情報まで述べるか変える
                                if qa_sw == 'off':
                                    price = [j[1] for j in read_text[i]]
                                    label = [j[0] for j in read_text[i]]
                                    #synthesize_text(i + 'は' + str(len(read_text[i])) + '種類あり、最も安いのは' + label[price.index(min(price))] + ' ' + min(price) + '円です', queue_p_id)
                                    synthesize_text(i + 'で最も安いのは' + label[price.index(min(price))] + ' ' + min(price) + '円です', queue_p_id)
                                elif qa_sw == 'on':
                                    synthesize_text(i + 'は' + str(len(read_text[i])) + '種類あります', queue_p_id)

                        # 出力がリスト（concがoff）
                        elif type(read_text) == list:
                            chunks = ''
                            for i in read_text:

                                # 一時停止の信号を受け次第、１０秒間停止
                                if not queue_stop_read.empty():
                                    time.sleep(10)
                                    while not queue_stop_read.empty():
                                        queue_stop_read.get()
                                if not queue_block_read.empty():
                                    flag_block = True
                                    break

                                # qaがonかoffかで、値段情報まで述べるか変える
                                if qa_sw == 'off':
                                    chunk = i[0] + ' ' + i[1] + '円、'
                                    chunks += chunk
                                elif qa_sw == 'on':
                                    chunk = i[0] + '、'
                                    chunks += chunk

                            synthesize_text(chunks, queue_p_id)
