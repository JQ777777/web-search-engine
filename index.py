import json
from elasticsearch import Elasticsearch
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 连接到Elasticsearch
USERNAME = "elastic"
PASSWORD = "aYJ-U7SNLSE4X=ZnosE3"
es = Elasticsearch(
    ["http://localhost:9200"],
    basic_auth=(USERNAME, PASSWORD),
    verify_certs=False
)

# 设置Elasticsearch索引的映射和配置
settings = {
    "index": {
        "number_of_replicas": 2,
        "number_of_shards": 1
    },
    "analysis": {
        "filter": {
            "autocomplete_filter": {
                "type": "edge_ngram",
                "min_gram": 1,
                "max_gram": 20
            }
        },
        "analyzer": {
            "autocomplete": {  # 自动补全分析器
                "type": "custom",
                "tokenizer": "ik_smart",
                "filter": [
                    "lowercase",
                    "autocomplete_filter"
                ]
            },
            "ik_max_word_analyzer": {
                "type": "custom",
                "tokenizer": "ik_max_word",
                "filter": ["lowercase"]
            }
        }
    }
}

mappings = {
    "properties": {
        "seq": {"type": "integer"},  # 添加 seq 字段，假设它是整数类型
        "url": {"type": "keyword"},  # 不分词的URL字段
        "title": {
            "type": "text",
            "analyzer": "ik_max_word",  # 分词的标题字段
            "fields": {
                "autocomplete": {  # 为标题添加自动补全字段
                    "type": "text",
                    "analyzer": "autocomplete"
                }
            }
        },
        "keywords": {
            "type": "text",
            "analyzer": "ik_max_word"  # 分词的关键词字段
        },
        "description": {
            "type": "text",
            "analyzer": "ik_max_word"  # 分词的描述字段
        },
        "html_filename": {"type": "keyword"},  # 不分词的HTML文件名字段
        "links": {
            "type": "nested",  # 使用 nested 类型来存储链接数组
            "properties": {
                "link": {"type": "keyword"}  # 每个链接不分词
            }
        },
        "content": {
            "type": "text",
            "analyzer": "ik_max_word"  # 分词的内容字段
        },
        "pr": {"type": "float"}  # 添加 pr 字段，假设它是浮点数类型
    }
}

# 创建Elasticsearch索引（如果不存在）
index_name = "nku_index"
logging.info(f"开始创建或更新索引: {index_name}")

if es.indices.exists(index=index_name):
    logging.info(f"索引 {index_name} 已存在，正在删除...")
    es.options(ignore_status=404).indices.delete(index=index_name)
    logging.info(f"索引 {index_name} 删除成功")

logging.info(f"正在创建索引: {index_name}")
es.indices.create(
    index=index_name,
    body={
        "settings": settings,
        "mappings": mappings
    }
)
logging.info(f"索引 {index_name} 创建成功")

# 从JSON文件中读取数据
json_file_path = 'nankai_data_pagerank.json'
logging.info(f"正在从文件 {json_file_path} 中读取数据...")
with open(json_file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
logging.info(f"成功读取 {len(data)} 条记录")

# 逐条插入文档
success_count = 0
failed_count = 0

for doc in data:
    try:
        # 构建文档内容
        document = {
            "seq": doc.get("seq"),
            "url": doc["url"],
            "title": doc.get("title", ""),
            "keywords": doc.get("keywords", ""),
            "description": doc.get("description", ""),
            "html_filename": doc.get("html_filename", ""),
            "links": [{"link": link} for link in doc.get("links", [])],
            "content": doc.get("content", ""),
            "pr": doc.get("pr", 0.0)
        }

        # 插入文档
        response = es.index(index=index_name, id=doc["url"], document=document)
        if response['result'] == 'created' or response['result'] == 'updated':
            success_count += 1
            logging.info(f"成功插入/更新文档: {doc['url']}")
        else:
            failed_count += 1
            logging.warning(f"插入/更新文档失败: {doc['url']}, 响应: {response}")
    except Exception as e:
        failed_count += 1
        logging.error(f"插入文档时发生错误: {doc['url']}, 错误: {e}")

# 输出总结信息
logging.info(f"总共处理 {len(data)} 条记录，成功插入/更新 {success_count} 条，失败 {failed_count} 条。")