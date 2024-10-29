# Cloudflare Vectorize Python Client

一个用于与 Cloudflare Vectorize API 交互的 Python 客户端。

## 特性

- 完整支持 Cloudflare Vectorize API
- 类型提示支持
- 完善的错误处理
- 可配置的重试机制
- 详细的文档

## 安装

```bash
pip install cloudflare-vectorize
```

## 快速开始

```python
from cloudflare_vectorize import CloudflareVectorize

# 初始化客户端
client = CloudflareVectorize(
    account_id="your-account-id",
    auth_config={
        "bearer_token": "your-bearer-token"
        # 或者使用 API key 认证:
        # "auth_email": "your-email",
        # "auth_key": "your-api-key"
    },
    retry_config={
        "total": 3,  # 最大重试次数
        "backoff_factor": 0.1,  # 重试间隔系数
        "status_forcelist": [500, 502, 503, 504]  # 需要重试的状态码
    }
)

# 创建索引
response = client.create_index(
    name="example-index",
    dimensions=768,
    metric="cosine",
    description="Example vector index"
)

# 插入向量
vectors_data = """
{"id": "vec1", "values": [0.1, 0.2, 0.3], "metadata": {"category": "test"}}
{"id": "vec2", "values": [0.4, 0.5, 0.6], "metadata": {"category": "test"}}
"""
response = client.insert_vectors("example-index", vectors_data)

# 查询向量
response = client.query_vectors(
    index_name="example-index",
    vector=[0.1, 0.2, 0.3],
    top_k=2,
    filter={"category": "test"},
    return_metadata="all"
)
```

## API 参考

### 索引管理

```python
# 列出所有索引
client.list_indexes()

# 创建索引
client.create_index(
    name="example-index",
    dimensions=768,
    metric="cosine",
    description="Example index"
)

# 获取索引信息
client.get_index("example-index")

# 获取索引统计信息
client.get_index_info("example-index")

# 删除索引
client.delete_index("example-index")
```

### 向量操作

```python
# 插入向量
vectors_data = """
{"id": "vec1", "values": [0.1, 0.2, 0.3]}
{"id": "vec2", "values": [0.4, 0.5, 0.6]}
"""
client.insert_vectors("example-index", vectors_data)

# 更新或插入向量
client.upsert_vectors("example-index", vectors_data)

# 查询向量
client.query_vectors(
    index_name="example-index",
    vector=[0.1, 0.2, 0.3],
    top_k=5,
    filter={"category": "test"},
    return_metadata="all",
    return_values=True
)

# 获取向量
client.get_vectors("example-index", ["vec1", "vec2"])

# 删除向量
client.delete_vectors("example-index", ["vec1", "vec2"])
```

### 元数据索引

```python
# 创建元数据索引
client.create_metadata_index(
    index_name="example-index",
    property_name="category",
    index_type="string"
)

# 列出元数据索引
client.list_metadata_indexes("example-index")

# 删除元数据索引
client.delete_metadata_index("example-index", "category")
```

### 错误处理

```python
from cloudflare_vectorize import CloudflareVectorizeError, APIError

try:
    response = client.query_vectors(
        index_name="example-index",
        vector=[0.1, 0.2, 0.3]
    )
except APIError as e:
    print(f"API错误: {e}")
    print(f"错误详情: {e.errors}")
except CloudflareVectorizeError as e:
    print(f"客户端错误: {e}")
```

## 开发

```bash
# 克隆仓库
git clone https://github.com/ourines/cloudflare-vectorize.git
cd cloudflare-vectorize

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest
```

## 许可证

MIT License

## 作者

ourines (ourines@icloud.com)