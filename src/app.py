# coding=utf-8
import sys
import dashscope
from dashscope.audio.tts import SpeechSynthesizer

def main():
    try:
        # 设置 API key
        dashscope.api_key = 'sk-ac6239799b084600b91a2da18d2c3a4e'

        # 调用语音合成
        result = SpeechSynthesizer.call(
            model='sambert-zhichu-v1',
            text='今天天气怎么样',
            sample_rate=48000,
            format='wav'
        )

        # 检查结果并保存音频
        if result.get_audio_data() is not None:
            with open('output.wav', 'wb') as f:
                f.write(result.get_audio_data())
            print('SUCCESS: get audio data: %dbytes in output.wav' %
                  (sys.getsizeof(result.get_audio_data())))
            return True
        else:
            print('ERROR: response is %s' % (result.get_response()))
            return False

    except Exception as e:
        print(f'Error occurred: {str(e)}')
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f'Unexpected error: {str(e)}')
        sys.exit(1)