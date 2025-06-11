"""测试中文 metadata 的处理"""

from cloudflare_vectorize import CloudflareVectorize
import random
import time

def test_chinese_metadata():
    """测试包含中文字符的 metadata 处理"""
    
    # 使用示例配置，你需要替换为实际的配置
    client = CloudflareVectorize(
        account_id="your-account-id",
        auth_config={"bearer_token": "your-bearer-token"}
    )
    
    print("🇨🇳 测试中文 metadata 处理")
    print("=" * 50)
    
    # 创建包含中文字符的测试向量
    test_id = f"chinese_test_{int(time.time())}"
    test_vector = [random.random() for _ in range(32)]
    
    # 包含中文字符的 metadata
    chinese_metadata = {
        "ImgName": "微信图片_20250610175829.jpg",
        "Title": "这是一个中文标题",
        "Description": "包含中文字符的描述：测试文档",
        "Category": "图片/照片",
        "Tags": ["中文", "测试", "向量数据库"]
    }
    
    # 构建 NDJSON 数据
    import json
    vector_data = {
        "id": test_id,
        "values": test_vector,
        "metadata": chinese_metadata
    }
    vectors_data = json.dumps(vector_data, ensure_ascii=False)
    
    print(f"📄 测试数据:")
    print(f"  ID: {test_id}")
    print(f"  中文文件名: {chinese_metadata['ImgName']}")
    print(f"  中文标题: {chinese_metadata['Title']}")
    
    try:
        # 测试插入包含中文的向量
        print(f"\n⬆️  测试插入向量...")
        result = client.insert_vectors(
            index_name="tutorial-index",  # 替换为你的索引名
            vectors_data=vectors_data
        )
        mutation_id = result['result']['mutationId']
        print(f"  ✅ 插入成功: mutation_id={mutation_id}")
        
        # 等待索引更新
        print(f"  ⏳ 等待索引更新...")
        time.sleep(5)
        
        # 验证向量是否正确存储
        print(f"\n🔍 验证向量存储...")
        get_result = client.get_vectors(
            index_name="tutorial-index",
            vector_ids=[test_id]
        )
        
        if len(get_result['result']) > 0:
            vector = get_result['result'][0]
            stored_metadata = vector.get('metadata', {})
            stored_filename = stored_metadata.get('ImgName', '')
            
            print(f"  ✅ 向量已存储")
            print(f"  📂 存储的文件名: {stored_filename}")
            print(f"  📝 存储的标题: {stored_metadata.get('Title', '')}")
            
            if stored_filename == chinese_metadata['ImgName']:
                print(f"  ✅ 中文字符保存正确!")
            else:
                print(f"  ❌ 中文字符保存错误")
                print(f"     期望: {chinese_metadata['ImgName']}")
                print(f"     实际: {stored_filename}")
        else:
            print(f"  ⏳ 向量还在索引中，请稍后验证")
            
        # 测试 namespace 功能
        print(f"\n🏷️  测试带 namespace 的中文 metadata...")
        namespace_test_id = f"ns_chinese_test_{int(time.time())}"
        namespace_vector_data = {
            "id": namespace_test_id,
            "values": test_vector,
            "metadata": chinese_metadata
        }
        namespace_vectors_data = json.dumps(namespace_vector_data, ensure_ascii=False)
        
        result = client.insert_vectors(
            index_name="tutorial-index",
            vectors_data=namespace_vectors_data,
            namespace="中文测试"
        )
        print(f"  ✅ 带 namespace 的中文 metadata 插入成功")
        
    except UnicodeEncodeError as e:
        print(f"  ❌ 编码错误: {e}")
        print(f"     这表明修复可能不完整")
    except Exception as e:
        print(f"  ❌ 其他错误: {e}")
        
    print(f"\n" + "=" * 50)
    print(f"🎯 中文 metadata 测试完成!")

if __name__ == "__main__":
    test_chinese_metadata() 