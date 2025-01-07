from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from qa_system import QASystem
from config import DIGITAL_HUMAN, DOC_DIR  # 导入 DOC_DIR
import logging
import uvicorn
from typing import List, Optional
from pathlib import Path
import os
from docx import Document
from fastapi.middleware.cors import CORSMiddleware

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 创建FastAPI应用
app = FastAPI(title="医保政策智能助手")

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取当前文件所在目录
BASE_DIR = Path(__file__).parent

# 创建static目录（如果不存在）
static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)

# 设置静态文件目录
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 设置模板目录
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# 定义请求和响应模型
class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    answer: str
    sources: Optional[List[str]] = None
    source: Optional[str] = None

# 全局QA系统实例
qa_system = None

# 设置静态文件目录
VOICE_DIR = Path("E:/dktPro/qianwen/springboot-qiniu-openai/otherproject/fenpian/doc/voice")
app.mount("/voice", StaticFiles(directory=str(VOICE_DIR)), name="voice")

@app.on_event("startup")
async def startup_event():
    """启动时初始化QA系统"""
    global qa_system
    try:
        qa_system = QASystem()
        logging.info("问答系统初始化完成")
    except Exception as e:
        logging.error(f"初始化问答系统失败: {str(e)}")
        raise

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """返回主页"""
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request,
            "DIGITAL_HUMAN": DIGITAL_HUMAN  # 传递配置到模板
        }
    )

@app.post("/ask", response_model=QuestionResponse)
async def ask(question_request: QuestionRequest):
    """处理问答请求"""
    try:
        question = question_request.question.strip()
        logging.info(f"收到问题请求: {question}")
        
        if not question:
            logging.warning("收到空问题")
            raise HTTPException(status_code=400, detail="请输入问题")
        
        # 搜索相关文档
        logging.info("开始搜索相关文档")
        contexts = qa_system.search_similar_contexts(question)
        logging.info(f"找到 {len(contexts)} 个相关文档")
        
        # 生成答案
        logging.info("开始生成答案")
        result = qa_system.generate_answer(question, contexts)
        logging.info(f"生成答案结果: {result}")
        
        # 构造响应
        if 'sources' in result:
            response = QuestionResponse(
                answer=result['answer'],
                sources=result['sources']
            )
        else:
            response = QuestionResponse(
                answer=result['answer'],
                source=result.get('source', '系统提示')
            )
            
        logging.info(f"返回响应: {response.dict()}")
        return response
        
    except Exception as e:
        logging.error(f"处理问题时出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def get_documents():
    """获取文档列表"""
    try:
        documents = []
        # 确保 DOC_DIR 存在
        if not DOC_DIR.exists():
            logging.warning(f"文档目录不存在: {DOC_DIR}")
            return documents
            
        for file_name in os.listdir(DOC_DIR):
            if file_name.endswith('.docx'):
                doc_id = file_name.replace('.docx', '')
                documents.append({
                    'id': doc_id,
                    'name': file_name
                })
        logging.info(f"找到 {len(documents)} 个文档")
        return documents
    except Exception as e:
        logging.error(f"获取文档列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取文档列表失败")

@app.get("/document/{doc_id}")
async def get_document(doc_id: str):
    """获取文档内容"""
    try:
        file_name = f"{doc_id}.docx"
        file_path = DOC_DIR / file_name
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="文档不存在")
            
        doc = Document(str(file_path))
        content = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        
        return {
            "id": doc_id,
            "name": file_name,
            "content": content
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"获取文档内容失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取文档内容失败")

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 