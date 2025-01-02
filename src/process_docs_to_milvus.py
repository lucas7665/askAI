from pathlib import Path
import os
from docx import Document
import zhipuai
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
import logging

# 配置
DOC_DIR = Path("E:/dktPro/fenpian/doc")
MILVUS_HOST = "localhost"
MILVUS_PORT = 19530
VECTOR_DIMENSION = 1024  # 智谱AI embedding维度
ZHIPUAI_KEY = "e3aeb66de6e16ba16e9fa84a9e153554.ZblmzSMOhE2GkJVu"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 初始化智谱AI客户端
zhipuai_client = zhipuai.ZhipuAI(api_key=ZHIPUAI_KEY)

def extract_text_from_docx(file_path: str) -> str:
    """从Word文档中提取文本"""
    logging.info(f"开始提取文档内容: {file_path}")
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    logging.info(f"文档内容提取完成，长度: {len(text)} 字符")
    return text

def get_embedding(text: str) -> list:
    """获取文本的向量嵌入"""
    logging.info(f"开始获取文本向量，文本长度: {len(text)}")
    try:
        response = zhipuai_client.embeddings.create(
            model="text_embedding_v2",
            input=text
        )
        if hasattr(response, 'data') and response.data:
            embedding = response.data[0].embedding
            logging.info(f"成功获取向量，维度: {len(embedding)}")
            return embedding
        raise Exception(f"智谱AI返回格式异常: {response}")
    except Exception as e:
        logging.error(f"获取向量失败: {str(e)}")
        raise

def setup_milvus_collection():
    """设置Milvus集合"""
    logging.info(f"开始连接Milvus: {MILVUS_HOST}:{MILVUS_PORT}")
    connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)
    collection_name = "doc_qa"
    
    if collection_name in utility.list_collections():
        logging.info(f"集合 {collection_name} 已存在，准备删除")
        Collection(name=collection_name).drop()
    
    logging.info("创建新集合")
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="file_name", dtype=DataType.VARCHAR, max_length=200),
        FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIMENSION)
    ]
    schema = CollectionSchema(fields=fields, description="文档问答系统的向量存储")
    collection = Collection(name=collection_name, schema=schema)
    
    logging.info("创建索引")
    index_params = {
        "metric_type": "L2",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 1024}
    }
    collection.create_index(field_name="embedding", index_params=index_params)
    logging.info("集合设置完成")
    return collection

def get_processed_files(collection):
    """从Milvus获取已处理的文件列表"""
    collection.load()
    results = collection.query(
        expr="file_name != ''",
        output_fields=["file_name"]
    )
    return {item['file_name'] for item in results}

def process_document(collection, file_path, file_name):
    """处理单个文档"""
    try:
        # 提取文本
        content = extract_text_from_docx(str(file_path))
        
        # 获取向量嵌入
        embedding = get_embedding(content)
        
        # 插入新记录
        collection.insert([
            [file_name],
            [content],
            [embedding]
        ])
        return True
    except Exception as e:
        logging.error(f"处理文件 {file_name} 时出错: {str(e)}")
        return False

def main():
    try:
        # 设置Milvus集合
        logging.info("正在连接Milvus...")
        collection = setup_milvus_collection()
        
        # 获取已处理的文件列表
        processed_files = get_processed_files(collection)
        
        # 处理所有文档
        logging.info(f"开始处理文档目录: {DOC_DIR}")
        new_files_count = 0
        skipped_files_count = 0
        
        for file_name in os.listdir(DOC_DIR):
            if not file_name.endswith('.docx'):
                continue
                
            file_path = DOC_DIR / file_name
            
            # 检查文件是否已处理
            if file_name in processed_files:
                logging.info(f"文件已存在，跳过处理: {file_name}")
                skipped_files_count += 1
                continue
            
            # 处理新文件
            new_files_count += 1
            logging.info(f"处理新文件: {file_name}")
            
            if process_document(collection, file_path, file_name):
                logging.info(f"成功处理并存储文件: {file_name}")
        
        # 刷新集合
        collection.flush()
        
        logging.info(f"处理完成！新增文件：{new_files_count}，跳过文件：{skipped_files_count}")
        
    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}")
        raise
    finally:
        # 释放集合
        if 'collection' in locals():
            collection.release()

if __name__ == "__main__":
    main() 