"""
测试配置示例

使用方法：
1. 复制此文件为 config.py
2. 填入你的真实配置信息
3. config.py 文件会被 .gitignore 忽略，不会提交到仓库

或者使用环境变量：
1. 复制 .env.example 为 .env
2. 在 .env 文件中填入真实配置
3. 使用 python-dotenv 加载环境变量
"""

import os
from cloudflare_vectorize import CloudflareVectorize

def get_client():
    """获取配置好的客户端"""
    
    # 方法1: 直接配置（需要创建 config.py 文件）
    try:
        from . import config
        return CloudflareVectorize(
            account_id=config.ACCOUNT_ID,
            auth_config={"bearer_token": config.BEARER_TOKEN}
        )
    except ImportError:
        pass
    
    # 方法2: 从环境变量读取
    account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
    bearer_token = os.getenv('CLOUDFLARE_BEARER_TOKEN')
    
    if account_id and bearer_token:
        return CloudflareVectorize(
            account_id=account_id,
            auth_config={"bearer_token": bearer_token}
        )
    
    # 方法3: 手动配置（仅用于本地测试，不要提交到仓库）
    print("⚠️  请配置你的 Cloudflare 凭据:")
    print("   选项1: 创建 tests/config.py 文件")
    print("   选项2: 设置环境变量 CLOUDFLARE_ACCOUNT_ID 和 CLOUDFLARE_BEARER_TOKEN")
    print("   选项3: 直接修改下面的代码（注意不要提交到仓库）")
    
    return CloudflareVectorize(
        account_id="your-account-id",
        auth_config={"bearer_token": "your-bearer-token"}
    )

# 示例配置文件 (tests/config.py)
"""
# 将此内容保存为 tests/config.py
ACCOUNT_ID = "你的-account-id"
BEARER_TOKEN = "你的-bearer-token"
AUTH_EMAIL = "你的-email@example.com"  # 可选
AUTH_KEY = "你的-api-key"  # 可选
INDEX_NAME = "tutorial-index"  # 测试用的索引名
""" 