# 医保政策智能问答系统

## 项目简介
本项目是一个基于人工智能的医保政策智能问答系统，集成了3D数字人交互界面。系统能够智能解答用户关于医保政策的各类问题，并通过3D数字人实现拟人化交互，提供更友好的用户体验。

## 技术架构

### 前端技术
- HTML5 + JavaScript
- Model-viewer（3D模型展示）
- Web Speech API（语音识别和合成）
- Bootstrap 5（UI框架）

### 后端技术
- Python 3.8+
- FastAPI Web框架
- 智谱AI GLM大模型（文本生成）
- Milvus向量数据库（向量检索）
- DashScope（语音合成）

### 知识库
- 医保政策文档库
- 向量化存储
- 语义检索系统

## 目录结构
```
/src
  ├── templates/          # 前端模板文件
  │   └── index.html     # 主页面
  ├── static/            # 静态资源
  │   └── talking_doctor.glb  # 3D数字人模型
  ├── config.py          # 配置文件
  ├── qa_system.py       # 问答系统核心
  ├── web_service.py     # Web服务
  ├── app.py            # 语音合成服务
  └── process_docs_to_milvus.py  # 文档处理工具

/doc                    # 医保政策文档库
  ├── 医保报销比例.docx
  ├── 社会保险经办条例.docx
  └── 其他政策文档.docx
```

## 核心功能

### 1. 智能问答
- 基于文档的精准问答
- 智能降级回答机制
- 多轮对话支持
- 相似度匹配和语义理解

### 2. 3D数字人交互
- 实时语音交互
- 语音识别和合成
- 3D模型动画效果
- 拟人化表情和动作

### 3. 文档管理
- 文档自动向量化
- 语义相似度检索
- 文档实时更新
- 多格式文档支持

## 环境要求

### 系统要求
- Python 3.8+
- Milvus 2.0+
- 现代浏览器（支持WebGL和Web Speech API）

### 依赖安装
```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 配置环境
```python
# 在 config.py 中配置必要的参数
ZHIPUAI_KEY = "your_zhipuai_key"
MILVUS_HOST = "localhost"
MILVUS_PORT = 19530
```

### 2. 初始化知识库
```bash
python process_docs_to_milvus.py
```

### 3. 启动服务
```bash
uvicorn web_service:app --host 0.0.0.0 --port 8000 --reload
```

## API 文档

### 问答接口
```bash
POST /ask
Content-Type: application/json

{
    "question": "医保报销比例是多少？"
}
```

### 文档管理接口
```bash
GET /documents
GET /document/{doc_id}
```

## 使用说明

### 1. 访问系统
- 打开浏览器访问 http://localhost:8000
- 确保浏览器允许使用麦克风（用于语音输入）

### 2. 交互方式
- 文本输入问题
- 语音输入问题
- 查看3D数字人回答
- 语音播报答案

## 开发指南

### 1. 添加新的文档
1. 将文档放入 `/doc` 目录
2. 运行 `process_docs_to_milvus.py` 更新向量库

### 2. 修改配置
- 调整 `config.py` 中的参数
- 更新提示词模板
- 配置相似度阈值

### 3. 自定义开发
- 扩展问答功能
- 优化3D模型动画
- 添加新的API接口

## 常见问题

### 1. 语音识别不工作
- 检查浏览器麦克风权限
- 确认Web Speech API支持
- 检查网络连接

### 2. 3D模型加载失败
- 检查WebGL支持
- 确认模型文件完整性
- 检查浏览器兼容性

## 维护说明

### 1. 日常维护
- 定期更新知识库文档
- 监控API调用限制
- 检查数据库连接状态

### 2. 性能优化
- 优化向量检索效率
- 调整相似度算法
- 优化前端加载速度

## 版本历史
- v1.0.0 (2023-12-27)
  - 初始版本发布
  - 基础问答功能
  - 3D数字人集成

## 贡献指南
1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 许可证
MIT License

## 联系方式
- 项目维护者：[维护者姓名]
- 邮箱：[联系邮箱]
- 问题反馈：请在 GitHub Issues 中提出

## 致谢
- 智谱AI提供的GLM模型支持
- DashScope提供的语音合成服务
- 所有项目贡献者
