import dashscope
from dashscope.audio.tts_v2 import SpeechSynthesizer  # 注意这里使用 tts_v2
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_voice():
    """测试 CosyVoice 语音合成"""
    try:
        # 设置 API key
        dashscope.api_key = 'sk-ac6239799b084600b91a2da18d2c3a4e'

        # 测试文本
        test_text = """
        欢迎使用医保政策智能助手。
        我可以为您解读医保政策，解答医保相关问题。
        让我们开始对话吧！
        """

        logging.info("\n=== 测试 CosyVoice 语音合成 ===")
        
        # 使用 CosyVoice 模型和龙媛声音
        synthesizer = SpeechSynthesizer(
            model='cosyvoice-v1',  # 使用 CosyVoice 模型
            voice='longyuan'       # 使用龙媛声音
        )
        
        # 调用语音合成
        audio = synthesizer.call(test_text)
        
        # 保存音频文件
        output_file = "voice_sample_longyuan.wav"
        with open(output_file, 'wb') as f:
            f.write(audio)
        logging.info(f"✓ 成功生成: {output_file}")
        logging.info(f"requestId: {synthesizer.get_last_request_id()}")

    except Exception as e:
        logging.error(f"✗ 测试失败: {str(e)}")

if __name__ == "__main__":
    test_voice()