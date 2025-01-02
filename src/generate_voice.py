from pathlib import Path
import dashscope
from dashscope.audio.tts_v2 import SpeechSynthesizer
import logging
import time
from docx import Document
import json
from datetime import datetime
from config import ALIYUN, DOC_DIR, BASE_DIR

# 配置路径
VOICE_DIR = DOC_DIR / "voice"
LOG_FILE = DOC_DIR / "log.txt"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(DOC_DIR / 'generation.log', encoding='utf-8')
    ]
)

def init_dirs():
    """初始化目录"""
    VOICE_DIR.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.write_text("{}", encoding='utf-8')

def load_processed_files():
    """加载已处理的文件记录"""
    try:
        return json.loads(LOG_FILE.read_text(encoding='utf-8'))
    except:
        return {}

def save_processed_file(filename, status):
    """保存处理记录"""
    records = load_processed_files()
    records[filename] = {
        "status": status,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    LOG_FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')

def get_doc_content(doc_path: Path) -> str:
    """获取文档内容"""
    try:
        doc = Document(str(doc_path))
        content = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        logging.info(f"成功读取文档内容，长度: {len(content)} 字符")
        return content
    except Exception as e:
        logging.error(f"读取文档失败 {doc_path}: {str(e)}")
        raise

def generate_segment(text: str, retry_count=0) -> bytes:
    """生成单个文本段的语音，支持重试"""
    try:
        # 创建 synthesizer 实例
        synthesizer = SpeechSynthesizer(
            model=ALIYUN['TTS_MODEL'],
            voice=ALIYUN['TTS_VOICE']
        )
        
        # 调用语音合成
        audio = synthesizer.call(text.strip())
        
        if audio:
            return audio
        raise Exception("未获取到音频数据")
        
    except Exception as e:
        error_msg = str(e)
        if "Arrearage" in error_msg and retry_count < ALIYUN['RETRY_TIMES']:
            # 账户余额不足，尝试使用备用 key
            logging.warning(f"API 调用失败，尝试使用备用 key (重试 {retry_count + 1}/{ALIYUN['RETRY_TIMES']})")
            dashscope.api_key = ALIYUN['BACKUP_API_KEY']
            time.sleep(ALIYUN['RETRY_DELAY'])
            return generate_segment(text, retry_count + 1)
        raise

def generate_voice(text: str, output_path: Path) -> bool:
    """生成语音文件"""
    try:
        logging.info(f"开始生成语音，文本长度: {len(text)} 字符")
        
        # 设置主 API key
        dashscope.api_key = ALIYUN['API_KEY']

        # 分段处理长文本
        max_length = ALIYUN['MAX_TEXT_LENGTH']
        segments = [text[i:i + max_length] for i in range(0, len(text), max_length)]
        
        logging.info(f"文本已分段，共 {len(segments)} 段")
        
        # 存储所有音频数据
        all_audio_data = bytearray()
        
        # 处理每个文本段
        for i, segment in enumerate(segments, 1):
            logging.info(f"处理第 {i}/{len(segments)} 段，长度: {len(segment)} 字符")
            
            try:
                audio_data = generate_segment(segment)
                if audio_data:
                    data_length = len(audio_data)
                    all_audio_data.extend(audio_data)
                    logging.info(f"第 {i} 段合成成功，数据长度: {data_length} 字节")
                else:
                    raise Exception("未获取到音频数据")
                    
            except Exception as e:
                logging.error(f"第 {i} 段合成出错: {str(e)}")
                return False

        # 保存完整音频
        if all_audio_data:
            total_length = len(all_audio_data)
            with open(output_path, 'wb') as f:
                f.write(all_audio_data)
            logging.info(f"语音文件生成成功: {output_path}，总大小: {total_length} 字节")
            return True
        else:
            logging.error("未生成任何有效的音频数据")
            return False

    except Exception as e:
        logging.error(f"生成语音失败: {str(e)}")
        return False

def main():
    """主函数"""
    try:
        logging.info("=== 开始生成语音文件 ===")
        
        # 初始化目录
        init_dirs()
        
        # 加载已处理文件记录
        processed_files = load_processed_files()
        
        # 获取所有文档
        doc_files = list(BASE_DIR.glob("*.docx"))
        total_files = len(doc_files)
        
        if not doc_files:
            logging.warning(f"未找到任何文档文件在: {BASE_DIR}")
            return
            
        logging.info(f"找到 {total_files} 个文档文件")
        
        # 处理每个文档
        for i, doc_path in enumerate(doc_files, 1):
            try:
                doc_name = doc_path.stem
                voice_path = VOICE_DIR / f"{doc_name}.mp3"  # 使用 mp3 格式
                
                # 检查是否已处理
                if doc_path.name in processed_files and processed_files[doc_path.name]["status"] == "success":
                    logging.info(f"[{i}/{total_files}] 跳过已处理的文件: {doc_name}")
                    continue
                
                logging.info(f"\n[{i}/{total_files}] 处理文档: {doc_name}")
                
                # 获取文档内容并预处理
                content = get_doc_content(doc_path)
                content = content.replace('\n', '。').strip()  # 优化文本处理
                
                # 生成语音
                if generate_voice(content, voice_path):
                    logging.info(f"[OK] 成功生成语音: {doc_name}")
                    save_processed_file(doc_path.name, "success")
                else:
                    logging.error(f"[ERROR] 生成语音失败: {doc_name}")
                    save_processed_file(doc_path.name, "failed")
                    
            except Exception as e:
                logging.error(f"处理文档失败: {str(e)}")
                save_processed_file(doc_path.name, "error")
                continue
                
        logging.info("\n=== 所有文档处理完成 ===")
        
    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}")
        raise

if __name__ == "__main__":
    main() 