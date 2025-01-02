from pathlib import Path
import zhipuai
from pymilvus import connections, Collection
import logging
from config import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class QASystem:
    def __init__(self):
        # 初始化智谱AI
        self.zhipuai_client = zhipuai.ZhipuAI(api_key=ZHIPUAI_KEY)
        
        # 连接Milvus
        connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)
        self.collection = Collection("doc_qa")
        self.collection.load()
        
    def get_embedding(self, text: str) -> list:
        """获取文本的向量嵌入"""
        try:
            response = self.zhipuai_client.embeddings.create(
                model="text_embedding_v2",
                input=text
            )
            if hasattr(response, 'data') and response.data:
                return response.data[0].embedding
            raise Exception(f"智谱AI返回格式异常: {response}")
        except Exception as e:
            raise Exception(f"智谱AI API调用失败: {str(e)}")
    
    def search_similar_contexts(self, query: str, top_k: int = 3):
        """搜索相似文档"""
        logging.info(f"开始搜索相似文档，查询: {query}")
        try:
            query_embedding = self.get_embedding(query)
            
            results = self.collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param={"metric_type": "L2", "params": {"nprobe": 10}},
                limit=top_k,
                output_fields=["content", "file_name"]
            )
            
            contexts = []
            for hits in results:
                for hit in hits:
                    if hit.score <= SIMILARITY_THRESHOLD:  # 使用配置的阈值
                        contexts.append({
                            'content': hit.entity.get('content'),
                            'file_name': hit.entity.get('file_name'),
                            'score': hit.score
                        })
                        logging.info(f"采用文档: {hit.entity.get('file_name')} (相似度得分: {hit.score})")
                    else:
                        logging.info(f"忽略文档: {hit.entity.get('file_name')} (相似度得分: {hit.score} > {SIMILARITY_THRESHOLD})")
            
            return contexts
        except Exception as e:
            logging.error(f"搜索相似文档失败: {str(e)}")
            return []
    
    def get_smart_answer(self, question: str) -> str:
        """使用智谱AI直接回答问题"""
        logging.info("使用智谱AI直接回答问题")
        try:
            prompt = SMART_PROMPT.format(question=question)
            logging.info(f"发送智谱AI请求，提示词: {prompt}")
            
            response = self.zhipuai_client.chat.completions.create(
                model="chatglm_turbo",
                messages=[
                    {"role": "system", "content": "你是一个专业的问答助手，请提供准确、专业的回答。"},
                    {"role": "user", "content": prompt}
                ]
            )
            
            if hasattr(response, 'choices') and response.choices:
                answer = response.choices[0].message.content
                logging.info(f"智谱AI返回答案: {answer}")
                return answer
            
            logging.error("智谱AI返回格式异常")
            return "抱歉，无法生成答案。"
            
        except Exception as e:
            logging.error(f"智谱AI直接回答失败: {str(e)}")
            return "抱歉，系统暂时无法回答这个问题。"
    
    def generate_answer(self, question: str, contexts: list) -> dict:
        """生成数字人回答"""
        try:
            if not contexts:
                if ENABLE_SMART_ANSWER:
                    # 构建系统提示词
                    system_prompt = SYSTEM_PROMPT.format(
                        name=DIGITAL_HUMAN["name"]
                    )
                    
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question}
                    ]
                    
                    response = self.zhipuai_client.chat.completions.create(
                        model="chatglm_turbo",
                        messages=messages
                    )
                    
                    if hasattr(response, 'choices') and response.choices:
                        return {
                            'answer': response.choices[0].message.content,
                            'source': f'{DIGITAL_HUMAN["name"]}的建议'
                        }
                return {
                    'answer': f'抱歉，我需要查阅相关政策后才能准确回答您的问题。您可以换个方式提问，或咨询具体的医保政策问题。',
                    'source': DIGITAL_HUMAN["name"]
                }

            # 使用文档内容生成答案
            prompt = DOC_PROMPT.format(
                content=' '.join([ctx['content'] for ctx in contexts]),
                question=question
            )

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT.format(name=DIGITAL_HUMAN["name"])},
                {"role": "user", "content": prompt}
            ]

            response = self.zhipuai_client.chat.completions.create(
                model="chatglm_turbo",
                messages=messages
            )
            
            if hasattr(response, 'choices') and response.choices:
                return {
                    'answer': response.choices[0].message.content,
                    'sources': [ctx['file_name'] for ctx in contexts]
                }
            raise Exception("智谱AI返回格式异常")
            
        except Exception as e:
            logging.error(f"生成答案失败: {str(e)}")
            raise

def main():
    try:
        qa_system = QASystem()
        logging.info("问答系统初始化完成，开始交互...")
        
        while True:
            question = input("\n请输入您的问题（输入'quit'退出）: ")
            if question.lower() == 'quit':
                break
            
            try:
                # 搜索相关文档
                contexts = qa_system.search_similar_contexts(question)
                
                # 生成答案
                answer = qa_system.generate_answer(question, contexts)
                
                # 输出答案和来源
                print(f"\n回答：{answer}")
                print("\n参考文档：")
                for ctx in contexts:
                    print(f"- {ctx['file_name']}")
                    
            except Exception as e:
                logging.error(f"处理问题时出错: {str(e)}")
                print("\n抱歉，处理您的问题时出现错误，请重试。")
                
    except Exception as e:
        logging.error(f"系统运行出错: {str(e)}")
        raise

if __name__ == "__main__":
    main() 