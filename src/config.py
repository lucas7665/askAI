from pathlib import Path

# 基础配置
BASE_DIR = Path(__file__).parent.parent
DOC_DIR = Path("E:/dktPro/千问\springboot-qiniu-openai/otherproject/fenpian/doc")
VECTOR_DIMENSION = 1024  # 智谱AI embedding维度

# Milvus配置
MILVUS_HOST = "localhost"
MILVUS_PORT = 19530

# 智谱AI配置
ZHIPUAI_KEY = "e3aeb66de6e16ba16e9fa84a9e153554.ZblmzSMOhE2GkJVu"

# 相似度阈值配置
SIMILARITY_THRESHOLD = 1.2  # 相似度阈值，大于此值的文档被认为不相关

# 智能回答配置
ENABLE_SMART_ANSWER = False  # 控制是否在找不到相关文档时使用智谱AI直接回答

# 数字人配置
DIGITAL_HUMAN = {
    "name": "医保助手",
    "role": "医保政策专家",
    "personality": "专业、友善、耐心",
    "greeting": "您好，我是医保助手。我可以为您解读医保政策，解答医保相关问题。请问有什么可以帮您？"
}

# 提示词配置
SYSTEM_PROMPT = """你是一个专业的医保政策顾问，名字叫{name}。
你的职责是帮助用户理解医保政策，解答医保相关问题。
请以专业、友善的态度与用户交流，确保回答准确且易于理解。
如果遇到不确定的问题，要诚实地表示不确定。

在回答时请注意：
1. 使用平易近人的语言
2. 必要时举例说明
3. 对复杂政策要分点解释
4. 强调重要信息
5. 提供相关政策依据"""

DOC_PROMPT = """基于以下医保政策文档内容，以医保顾问的身份回答用户问题。
如果无法从文档中找到答案，请说明需要查证后再回答。

文档内容：
{content}

用户问题：{question}

请给出专业、易懂的解答："""

SMART_PROMPT = """请尽可能准确地回答用户的问题。如果不确定，请说明。

问题：{question}

请给出专业、准确的回答："""

# 阿里云配置
ALIYUN = {
    "API_KEY": "sk-6a5e0c27f6e843f9a4a1eb217178f3a8",  # 当前的 key
    "BACKUP_API_KEY": "sk-6a5e0c27f6e843f9a4a1eb217178f3a8",  # 备用 key
    "TTS_MODEL": "cosyvoice-v1",
    "TTS_VOICE": "longyuan",
    "MAX_TEXT_LENGTH": 2000,  # 每段最大字符数
    "RETRY_TIMES": 1,  # 重试次数
    "RETRY_DELAY": 1  # 重试间隔(秒)
}