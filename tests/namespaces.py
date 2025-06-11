from cloudflare_vectorize import CloudflareVectorize
import random

client = CloudflareVectorize(
    account_id="xxx",
    auth_config={"bearer_token": "xxxx", "auth_email": "xxx"}
)

print("=== Namespace 功能演示 ===")

# 1. 创建不同命名空间的向量数据
print("\n1. 准备不同命名空间的向量数据")

# 为text命名空间创建向量
text_vectors = []
for i in range(3):
    vector_data = [random.random() for _ in range(32)]
    text_vectors.append(f'{{"id": "text_{i}", "values": {vector_data}}}')

text_vectors_data = '\n'.join(text_vectors)

# 为images命名空间创建向量
image_vectors = []
for i in range(3):
    vector_data = [random.random() for _ in range(32)]
    image_vectors.append(f'{{"id": "image_{i}", "values": {vector_data}}}')

image_vectors_data = '\n'.join(image_vectors)

print(f"准备了 {len(text_vectors)} 个text向量和 {len(image_vectors)} 个image向量")

# 2. 插入带有命名空间的向量
print("\n2. 插入带有命名空间的向量")

try:
    # 插入text命名空间的向量
    result1 = client.insert_vectors(
        index_name="tutorial-index",
        vectors_data=text_vectors_data,
        namespace="text"
    )
    print(f"Text向量插入成功: {result1['result']['mutationId']}")
    
    # 插入images命名空间的向量
    result2 = client.insert_vectors(
        index_name="tutorial-index", 
        vectors_data=image_vectors_data,
        namespace="images"
    )
    print(f"Images向量插入成功: {result2['result']['mutationId']}")
    
except Exception as e:
    print(f"插入向量失败: {e}")

# 3. 在特定命名空间中查询向量
print("\n3. 在特定命名空间中查询向量")

try:
    # 创建查询向量
    query_vector = [random.random() for _ in range(32)]
    
    # 仅在text命名空间中查询
    print("\n在 'text' 命名空间中查询:")
    result_text = client.query_vectors(
        index_name="tutorial-index",
        vector=query_vector,
        top_k=2,
        namespace="text"
    )
    print(f"Text命名空间查询结果: {result_text['result']}")
    
    # 仅在images命名空间中查询
    print("\n在 'images' 命名空间中查询:")
    result_images = client.query_vectors(
        index_name="tutorial-index",
        vector=query_vector,
        top_k=2,
        namespace="images"
    )
    print(f"Images命名空间查询结果: {result_images['result']}")
    
    # 不指定命名空间查询（搜索所有向量）
    print("\n不指定命名空间查询（搜索所有向量）:")
    result_all = client.query_vectors(
        index_name="tutorial-index",
        vector=query_vector,
        top_k=4
    )
    print(f"全局查询结果: {result_all['result']}")
    
except Exception as e:
    print(f"查询向量失败: {e}")

# 4. 演示namespace验证
print("\n4. 演示namespace验证")

try:
    # 测试超长的namespace
    long_namespace = "a" * 65  # 超过64字符限制
    client.insert_vectors(
        index_name="tutorial-index",
        vectors_data='{"id": "test", "values": [1,2,3]}',
        namespace=long_namespace
    )
except ValueError as e:
    print(f"✅ 正确捕获了超长namespace错误: {e}")

print("\n=== Namespace 功能演示完成 ===") 