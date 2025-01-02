医保政策智能问答系统
====================

项目简介
--------
本项目是一个基于AI的医保政策智能问答系统，集成了3D数字人交互界面。系统能够智能解答用户关于医保政策的各类问题，并通过3D数字人实现拟人化交互。

技术架构
--------
1. 前端技术：
   - HTML5 + JavaScript
   - Model-viewer（3D模型展示）
   - Web Speech API（语音识别和合成）

2. 后端技术：
   - Python 3.8+
   - Flask Web框架
   - 智谱AI GLM大模型
   - Milvus向量数据库

3. 知识库：
   - 医保政策文档库
   - 向量化存储
   - 语义检索

目录结构
--------
/src
  ├── templates/          # 前端模板文件
  │   └── index.html     # 主页面
  ├── static/            # 静态资源
  │   └── talking_doctor.glb  # 3D数字人模型
  ├── config.py          # 配置文件
  ├── qa_system.py       # 问答系统核心
  ├── web_service.py     # Web服务
  ├── app.py            # 应用入口
  └── process_docs_to_milvus.py  # 文档处理工具

/doc                    # 医保政策文档库
  ├── 医保报销比例（暂定）.docx
  ├── 社会保险经办条例.docx
  ├── 医疗保障基金飞行检查管理暂行办法.docx
  ├── 医疗保障基金使用监督管理举报处理暂行办法.docx
  ├── 医疗保障行政处罚程序暂行规定.docx
  ├── 零售药店医疗保障定点管理暂行办法.docx
  ├── 医疗机构医疗保障定点管理暂行办法.docx
  └── 基本医疗保险用药管理暂行办法.docx

核心功能
--------
1. 智能问答
   - 基于文档的精准问答
   - 智能降级回答
   - 多轮对话支持

2. 3D数字人交互
   - 实时语音交互
   - 唇形同步
   - 动画效果

3. 文档管理
   - 文档向量化
   - 语义检索
   - 相似度匹配

环境要求
--------
1. Python 3.8+
2. Milvus 2.0+
3. 现代浏览器（支持WebGL和Web Speech API）

安装步骤
--------
1. 安装Python依赖：
   ```
   pip install -r requirements.txt
   ```

2. 配置环境：
   - 在config.py中配置智谱AI密钥
   - 配置Milvus连接信息
   - 调整相似度阈值等参数

3. 初始化知识库：
   ```
   python process_docs_to_milvus.py
   ```

4. 启动服务：
   ```
   python app.py
   ```

使用说明
--------
1. 访问系统：
   - 打开浏览器访问 http://localhost:8000

2. 交互方式：
   - 文本输入问题
   - 语音输入问题
   - 查看3D数字人回答
   - 语音播报答案

注意事项
--------
1. 确保浏览器支持WebGL和Web Speech API
2. 检查麦克风权限（语音输入需要）
3. 保持网络连接稳定
4. 定期更新知识库文档

维护说明
--------
1. 知识库更新：
   - 将新的医保政策文档放入doc目录
   - 运行process_docs_to_milvus.py更新向量库

2. 模型优化：
   - 在config.py中调整模型参数
   - 更新提示词模板

3. 系统监控：
   - 查看日志文件
   - 监控API调用限制
   - 检查数据库连接状态

联系方式
--------
如有问题请联系系统管理员

版本信息
--------
Version: 1.0
Last Updated: 2023-12-27 
uvicorn web_service:app --host 0.0.0.0 --port 8000 --reload
