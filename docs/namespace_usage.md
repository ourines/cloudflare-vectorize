# Cloudflare Vectorize Namespaces 使用指南

## 概述

Namespaces 提供了一种在索引内分段管理向量的方法。您可以按客户、商户、店铺 ID 或任何其他逻辑分组来组织向量。

## 主要特性

- **向量分组**：按命名空间组织向量，便于管理和查询
- **隔离查询**：在特定命名空间内搜索，提高查询精度
- **自动添加**：客户端自动为向量添加命名空间字段
- **灵活管理**：支持最多 1,000 个命名空间per索引

## ⚠️ 重要注意事项：一致性模型

Cloudflare Vectorize 使用**最终一致性**模型：

- **写入延迟**：新插入的向量可能需要几秒到几分钟才能在查询中可见
- **批量优化**：Vectorize 会将多个变更合并为批次处理以提高性能
- **推荐做法**：插入向量后，等待适当时间再进行查询验证

根据 [Cloudflare 官方文档](https://developers.cloudflare.com/vectorize/best-practices/insert-vectors/#improve-write-throughput)：
- 批量处理最多 200,000 个向量或 1,000 个更新操作
- 大量向量的索引可能需要几分钟到几小时完成

## 使用方法

### 1. 插入带命名空间的向量

#### 方法一：自动添加命名空间
```python
from cloudflare_vectorize import CloudflareVectorize

client = CloudflareVectorize(
    account_id="your-account-id",
    auth_config={"bearer_token": "your-token"}
)

# 原始向量数据（不带namespace）
vectors_data = '''{"id": "doc1", "values": [0.1, 0.2, 0.3]}
{"id": "doc2", "values": [0.4, 0.5, 0.6]}'''

# 插入时指定namespace，客户端会自动添加
result = client.insert_vectors(
    index_name="my-index",
    vectors_data=vectors_data,
    namespace="documents"  # 自动为每个向量添加此namespace
)

print(f"插入成功，mutation_id: {result['result']['mutationId']}")

# ⚠️ 等待索引更新（推荐）
import time
time.sleep(5)  # 等待5秒让索引更新
```

#### 方法二：手动在数据中包含命名空间
```python
# 手动创建带namespace的向量数据
vectors_data = '''{"id": "text1", "values": [0.1, 0.2, 0.3], "namespace": "text"}
{"id": "image1", "values": [0.4, 0.5, 0.6], "namespace": "images"}'''

# 直接插入（不需要指定namespace参数）
result = client.insert_vectors(
    index_name="my-index",
    vectors_data=vectors_data
)
```

### 2. 在命名空间内查询向量

```python
# 仅在特定命名空间内搜索
result = client.query_vectors(
    index_name="my-index",
    vector=[0.1, 0.2, 0.3],
    top_k=5,
    namespace="documents"  # 仅搜索documents命名空间
)

# 不指定命名空间则搜索所有向量
result = client.query_vectors(
    index_name="my-index", 
    vector=[0.1, 0.2, 0.3],
    top_k=5
    # 不指定namespace，搜索全部
)
```

### 3. 处理索引延迟的推荐模式

```python
import time

# 插入向量
result = client.insert_vectors(
    index_name="my-index",
    vectors_data=vectors_data,
    namespace="my_namespace"
)

mutation_id = result['result']['mutationId']
print(f"向量插入成功: {mutation_id}")

# 推荐：等待索引更新
def wait_for_indexing(client, index_name, vector_ids, max_wait=60):
    """等待向量被索引"""
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            result = client.get_vectors(index_name, vector_ids)
            if len(result['result']) > 0:
                print("向量已被索引，可以进行查询")
                return True
        except:
            pass
        time.sleep(2)
    print("等待超时，但向量可能仍在处理中")
    return False

# 使用示例
vector_ids = ["doc1", "doc2"]
wait_for_indexing(client, "my-index", vector_ids)

# 现在可以安全地进行命名空间查询
result = client.query_vectors(
    index_name="my-index",
    vector=[0.1, 0.2, 0.3],
    namespace="my_namespace"
)
```

### 4. 更新/插入带命名空间的向量

```python
# 使用upsert方法，支持namespace
result = client.upsert_vectors(
    index_name="my-index",
    vectors_data=vectors_data,
    namespace="updated_docs"
)
```

## 命名空间限制和最佳实践

### 限制
- 命名空间名称最大 **64 字符**
- 每个索引最多 **1,000 个命名空间**
- 命名空间必须是非空字符串

### 最佳实践

#### 1. 按业务逻辑分组
```python
# 按客户分组
client.insert_vectors(index_name, customer_vectors, namespace="customer_123")

# 按内容类型分组  
client.insert_vectors(index_name, text_vectors, namespace="text")
client.insert_vectors(index_name, image_vectors, namespace="images")

# 按时间分组
client.insert_vectors(index_name, vectors, namespace="2024-01")
```

#### 2. 命名空间性能优化
```python
# 命名空间过滤在向量搜索之前应用，提高搜索精度
result = client.query_vectors(
    index_name="large-index",
    vector=query_vector,
    namespace="specific_customer",  # 先过滤，再搜索
    top_k=10
)
```

#### 3. 批量插入优化
```python
# 推荐：批量插入向量以提高性能
large_vectors_data = '\n'.join([
    f'{{"id": "vec_{i}", "values": {[random.random() for _ in range(dimensions)]}}}' 
    for i in range(1000)
])

client.insert_vectors(
    index_name="my-index",
    vectors_data=large_vectors_data,
    namespace="batch_insert"
)
```

#### 4. 元数据配合使用
```python
vectors_data = '''{"id": "doc1", "values": [0.1, 0.2], "namespace": "docs", "metadata": {"category": "tech", "date": "2024-01-15"}}'''
```

## 验证和错误处理

```python
try:
    # 命名空间长度验证
    long_namespace = "a" * 65  # 超过64字符
    client.insert_vectors(index_name, vectors, namespace=long_namespace)
except ValueError as e:
    print(f"命名空间验证失败: {e}")
    
try:
    # 空命名空间验证
    client.insert_vectors(index_name, vectors, namespace="")
except ValueError as e:
    print(f"命名空间不能为空: {e}")

# 处理索引延迟
try:
    result = client.query_vectors(index_name, vector, namespace="my_ns")
    if result['result']['count'] == 0:
        print("未找到结果，可能需要等待索引更新")
except Exception as e:
    print(f"查询失败: {e}")
```

## 故障排除

### 问题：插入成功但查询不到向量

**原因**：Vectorize 使用最终一致性，新插入的向量需要时间索引

**解决方案**：
1. 等待几秒到几分钟后重试
2. 使用 `get_vectors()` 检查向量是否存在
3. 进行全局查询（不指定namespace）验证向量是否在索引中

```python
# 检查向量是否存在
result = client.get_vectors("my-index", ["vector_id"])
if len(result['result']) == 0:
    print("向量还未被索引，请稍后重试")
else:
    print(f"向量存在，namespace: {result['result'][0].get('namespace')}")
```

### 问题：命名空间查询返回空结果

**排查步骤**：
1. 确认向量已被索引
2. 验证namespace名称拼写正确
3. 检查全局查询中向量的实际namespace

```python
# 调试namespace查询
import random

# 1. 全局查询找到现有向量
global_result = client.query_vectors(
    index_name="my-index",
    vector=[random.random() for _ in range(dimensions)],
    top_k=10,
    return_metadata="all"
)

# 2. 查看实际的namespace值
for match in global_result['result']['matches']:
    if 'namespace' in match:
        print(f"ID: {match['id']}, namespace: '{match['namespace']}'")

# 3. 使用确认的namespace进行查询
result = client.query_vectors(
    index_name="my-index",
    vector=[random.random() for _ in range(dimensions)],
    namespace="confirmed_namespace",
    top_k=5
)
```

## 完整示例

```python
from cloudflare_vectorize import CloudflareVectorize
import random
import time

# 初始化客户端
client = CloudflareVectorize(
    account_id="your-account-id",
    auth_config={"bearer_token": "your-token"}
)

# 创建不同类型的向量数据
text_vectors = '''{"id": "text1", "values": [0.1, 0.2, 0.3]}
{"id": "text2", "values": [0.4, 0.5, 0.6]}'''

image_vectors = '''{"id": "img1", "values": [0.7, 0.8, 0.9]}
{"id": "img2", "values": [1.0, 1.1, 1.2]}'''

# 插入到不同命名空间
print("插入文本向量...")
result1 = client.insert_vectors("my-index", text_vectors, namespace="text")
print(f"文本向量插入成功: {result1['result']['mutationId']}")

print("插入图片向量...")
result2 = client.insert_vectors("my-index", image_vectors, namespace="images")
print(f"图片向量插入成功: {result2['result']['mutationId']}")

# 等待索引更新
print("等待索引更新...")
time.sleep(10)

# 在特定命名空间内查询
query_vector = [0.2, 0.3, 0.4]

# 仅搜索文本向量
text_results = client.query_vectors(
    "my-index", query_vector, top_k=2, namespace="text"
)

# 仅搜索图片向量
image_results = client.query_vectors(
    "my-index", query_vector, top_k=2, namespace="images"
)

# 搜索所有向量
all_results = client.query_vectors(
    "my-index", query_vector, top_k=4
)

print(f"文本结果: {text_results['result']['count']} 个匹配")
print(f"图片结果: {image_results['result']['count']} 个匹配") 
print(f"全部结果: {all_results['result']['count']} 个匹配")
```

## 参考文档

- [Cloudflare Vectorize Namespaces 官方文档](https://developers.cloudflare.com/vectorize/best-practices/insert-vectors/#namespaces)
- [Vectorize API 参考](https://developers.cloudflare.com/api/resources/vectorize/subresources/indexes/methods/insert/)
- [Vectorize 性能优化](https://developers.cloudflare.com/vectorize/best-practices/insert-vectors/#improve-write-throughput) 