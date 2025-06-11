from cloudflare_vectorize import CloudflareVectorize

client = CloudflareVectorize(
    account_id="xxx",
    auth_config={"bearer_token": "xxxx", "auth_email": "xxx"}
)

# 1. 先列出现有索引
print("=== 列出现有索引 ===")
try:
    indexes = client.list_indexes()
    print("现有索引:")
    for idx in indexes['result']:
        print(f"  - {idx['name']}: {idx['config']['dimensions']}维, {idx['config']['metric']} 距离")
except Exception as e:
    print(f"列出索引失败: {e}")

# 2. 使用现有的 tutorial-index (32维)
print("\n=== 插入向量到 tutorial-index ===")
# 创建32维的测试向量
import random
vector1 = [random.random() for _ in range(32)]
vector2 = [random.random() for _ in range(32)]

vectors_data = f'{{"id": "test_vec1", "values": {vector1}}}' + '\n' + f'{{"id": "test_vec2", "values": {vector2}}}'

try:
    result = client.insert_vectors(
        index_name="tutorial-index",
        vectors_data=vectors_data
    )
    print(f"向量插入成功: {result}")
except Exception as e:
    print(f"插入向量失败: {e}")

# 3. 测试查询向量
print("\n=== 查询向量 ===")
try:
    query_vector = [random.random() for _ in range(32)]
    result = client.query_vectors(
        index_name="tutorial-index",
        vector=query_vector,
        top_k=2
    )
    print(f"查询结果: {result}")
except Exception as e:
    print(f"查询向量失败: {e}")