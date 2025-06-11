from cloudflare_vectorize import CloudflareVectorize
import random

# 这是一个简单的namespace功能测试
print("=== 测试 Namespace 功能 ===")

# 演示如何使用namespace
print("\n1. 演示向量数据格式（带namespace）")

# 手动创建带namespace的NDJSON数据
vectors_with_namespace = '''{"id": "text1", "values": [0.1, 0.2, 0.3], "namespace": "documents"}
{"id": "image1", "values": [0.4, 0.5, 0.6], "namespace": "images"}'''

print("手动创建的带namespace的向量数据:")
print(vectors_with_namespace)

# 演示自动添加namespace的功能
print("\n2. 演示自动添加namespace功能")

# 创建不带namespace的向量数据
vectors_without_namespace = '''{"id": "vec1", "values": [0.7, 0.8, 0.9]}
{"id": "vec2", "values": [1.0, 1.1, 1.2]}'''

print("原始向量数据（无namespace）:")
print(vectors_without_namespace)

# 模拟客户端处理
def simulate_namespace_addition(vectors_data, namespace):
    """模拟客户端添加namespace的过程"""
    import json
    lines = vectors_data.strip().split('\n')
    updated_lines = []
    for line in lines:
        if line.strip():
            vector = json.loads(line)
            vector['namespace'] = namespace
            updated_lines.append(json.dumps(vector))
    return '\n'.join(updated_lines)

processed_data = simulate_namespace_addition(vectors_without_namespace, "auto_added")
print(f"\n处理后的向量数据（自动添加namespace='auto_added'）:")
print(processed_data)

# 演示namespace验证
print("\n3. 演示namespace验证")

def validate_namespace(namespace):
    """验证namespace的格式"""
    if not isinstance(namespace, str):
        return False, "Namespace must be a string"
    if len(namespace) > 64:
        return False, "Namespace cannot exceed 64 characters"
    if not namespace:
        return False, "Namespace cannot be empty"
    return True, "Valid namespace"

test_cases = [
    "valid_namespace",
    "",  # 空字符串
    "a" * 65,  # 超长
    "text",
    "images",
]

for namespace in test_cases:
    is_valid, message = validate_namespace(namespace)
    status = "✅" if is_valid else "❌"
    print(f"{status} namespace='{namespace[:20]}{'...' if len(namespace) > 20 else ''}': {message}")

print("\n=== Namespace 功能演示完成 ===")

# 使用说明
print("\n## 使用说明")
print("1. 插入向量时使用namespace:")
print("   client.insert_vectors(index_name, vectors_data, namespace='my_namespace')")
print("\n2. 查询向量时使用namespace:")
print("   client.query_vectors(index_name, query_vector, namespace='my_namespace')")
print("\n3. Namespace限制:")
print("   - 最大64字符")
print("   - 每个索引最多1000个namespace")
print("   - 用于分段管理向量（按客户、类型等）") 