from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from cloudflare_vectorize import CloudflareVectorize, APIError
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = FastAPI(
    title="Cloudflare Vectorize API",
    description="FastAPI wrapper for Cloudflare Vectorize",
    version="0.1.0"
)

# 初始化 Cloudflare Vectorize 客户端
vectorize = CloudflareVectorize(
    account_id=os.getenv("CLOUDFLARE_ACCOUNT_ID"),
    auth_config={
        "bearer_token": os.getenv("CLOUDFLARE_API_TOKEN")
    },
    retry_config={
        "total": 3,
        "backoff_factor": 0.1,
        "status_forcelist": [500, 502, 503, 504]
    }
)

# 请求/响应模型
class IndexCreate(BaseModel):
    name: str = Field(..., description="索引名称")
    dimensions: int = Field(..., description="向量维度", ge=1, le=1536)
    metric: str = Field(..., description="距离计算方式", regex="^(cosine|euclidean|dot-product)$")
    description: Optional[str] = Field(default="", description="索引描述")

class Vector(BaseModel):
    id: str = Field(..., description="向量ID")
    values: List[float] = Field(..., description="向量值")
    metadata: Optional[Dict] = Field(default=None, description="向量元数据")

class VectorQuery(BaseModel):
    vector: List[float] = Field(..., description="查询向量")
    top_k: int = Field(default=5, description="返回最近邻的数量", ge=1)
    filter: Optional[Dict] = Field(default=None, description="元数据过滤条件")
    return_metadata: str = Field(
        default="none", 
        description="返回元数据类型",
        regex="^(none|indexed|all)$"
    )
    return_values: bool = Field(default=False, description="是否返回向量值")

class MetadataIndex(BaseModel):
    property_name: str = Field(..., description="元数据属性名")
    index_type: str = Field(
        ..., 
        description="索引类型",
        regex="^(string|number|boolean)$"
    )

@app.exception_handler(APIError)
async def api_error_handler(request, exc: APIError):
    return {
        "success": False,
        "error": str(exc),
        "details": exc.errors
    }

# 索引管理接口
@app.get("/indexes")
async def list_indexes():
    """列出所有向量索引"""
    return vectorize.list_indexes()

@app.post("/indexes")
async def create_index(index: IndexCreate):
    """创建新的向量索引"""
    return vectorize.create_index(
        name=index.name,
        dimensions=index.dimensions,
        metric=index.metric,
        description=index.description
    )

@app.get("/indexes/{index_name}")
async def get_index(index_name: str):
    """获取指定索引的信息"""
    return vectorize.get_index(index_name)

@app.get("/indexes/{index_name}/info")
async def get_index_info(index_name: str):
    """获取索引的统计信息"""
    return vectorize.get_index_info(index_name)

@app.delete("/indexes/{index_name}")
async def delete_index(index_name: str):
    """删除指定的向量索引"""
    return vectorize.delete_index(index_name)

# 向量操作接口
@app.post("/indexes/{index_name}/vectors")
async def insert_vectors(index_name: str, vectors: List[Vector]):
    """插入向量"""
    vectors_data = "\n".join(v.json() for v in vectors)
    return vectorize.insert_vectors(index_name, vectors_data)

@app.post("/indexes/{index_name}/vectors/query")
async def query_vectors(index_name: str, query: VectorQuery):
    """查询最近邻向量"""
    return vectorize.query_vectors(
        index_name=index_name,
        vector=query.vector,
        top_k=query.top_k,
        filter=query.filter,
        return_metadata=query.return_metadata,
        return_values=query.return_values
    )

@app.get("/indexes/{index_name}/vectors")
async def get_vectors(index_name: str, ids: List[str]):
    """通过ID获取向量"""
    return vectorize.get_vectors(index_name, ids)

@app.delete("/indexes/{index_name}/vectors")
async def delete_vectors(index_name: str, ids: List[str]):
    """通过ID删除向量"""
    return vectorize.delete_vectors(index_name, ids)

# 元数据索引接口
@app.post("/indexes/{index_name}/metadata-indexes")
async def create_metadata_index(index_name: str, metadata_index: MetadataIndex):
    """创建元数据索引"""
    return vectorize.create_metadata_index(
        index_name=index_name,
        property_name=metadata_index.property_name,
        index_type=metadata_index.index_type
    )

@app.get("/indexes/{index_name}/metadata-indexes")
async def list_metadata_indexes(index_name: str):
    """列出索引的所有元数据索引"""
    return vectorize.list_metadata_indexes(index_name)

@app.delete("/indexes/{index_name}/metadata-indexes/{property_name}")
async def delete_metadata_index(index_name: str, property_name: str):
    """删除元数据索引"""
    return vectorize.delete_metadata_index(index_name, property_name)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 