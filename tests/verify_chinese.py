from cloudflare_vectorize import CloudflareVectorize
import random

client = CloudflareVectorize(
    account_id='your-account-id',
    auth_config={'bearer_token': 'your-bearer-token'}
)

# 查询最近插入的向量
query_vector = [random.random() for _ in range(32)]
result = client.query_vectors(
    index_name='tutorial-index',
    vector=query_vector,
    top_k=10,
    return_metadata='all'
)

print('🔍 查找包含中文字符的向量:')
found_chinese = False
for match in result['result']['matches']:
    metadata = match.get('metadata', {})
    img_name = metadata.get('ImgName', '')
    if '微信图片' in img_name:
        print(f'  ✅ 找到中文文件名: {img_name}')
        print(f'  📝 标题: {metadata.get("Title", "")}')
        print(f'  📂 分类: {metadata.get("Category", "")}')
        print(f'  🏷️ 标签: {metadata.get("Tags", [])}')
        found_chinese = True
        break

if not found_chinese:
    print('  ⏳ 向量可能还在索引中，或者需要更多时间')
    print('  📋 前5个向量的metadata:')
    for i, match in enumerate(result['result']['matches'][:5]):
        metadata = match.get('metadata', {})
        print(f'    {i+1}. ID: {match.get("id", "")}')
        print(f'       metadata: {metadata}') 