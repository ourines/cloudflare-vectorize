"""Cloudflare Vectorize API client implementation."""

import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import List, Dict, Union, Optional, Any
from .exceptions import AuthenticationError, APIError
from .utils import validate_response, validate_vector_format

class CloudflareVectorize:
    """Cloudflare Vectorize API 客户端"""
    
    def __init__(self, 
                 account_id: str, 
                 auth_config: Dict[str, str],
                 retry_config: Optional[Dict] = None):
        """
        初始化 Cloudflare Vectorize 客户端
        
        Args:
            account_id: Cloudflare 账户 ID
            auth_config: 认证配置,支持以下字段:
                - bearer_token: Bearer Token认证
                - auth_email: API Email认证
                - auth_key: API Key认证
            retry_config: 重试配置,支持以下字段:
                - total: 最大重试次数 (默认3次)
                - backoff_factor: 重试间隔系数 (默认0.1)
                - status_forcelist: 需要重试的HTTP状态码列表 (默认[500, 502, 503, 504])
                - allowed_methods: 允许重试的HTTP方法 (默认所有方法)
                
        Raises:
            AuthenticationError: 当认证配置无效时
        """
        if not any(k in auth_config for k in ["bearer_token", "auth_email"]):
            raise AuthenticationError("Must provide either bearer_token or auth_email/auth_key")
            
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/vectorize/v2"
        self.headers = {"Content-Type": "application/json"}
        
        # 配置认证方式
        if "bearer_token" in auth_config:
            self.headers["Authorization"] = f"Bearer {auth_config['bearer_token']}"
        if "auth_email" in auth_config:
            self.headers["X-Auth-Email"] = auth_config["auth_email"]
        if "auth_key" in auth_config:
            self.headers["X-Auth-Key"] = auth_config["auth_key"]

        # 配置重试机制
        self.session = requests.Session()
        retry_config = retry_config or {}
        retry = Retry(
            total=retry_config.get('total', 3),
            backoff_factor=retry_config.get('backoff_factor', 0.1),
            status_forcelist=retry_config.get('status_forcelist', [500, 502, 503, 504]),
            allowed_methods=retry_config.get('allowed_methods', None)
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
    def _request(self, method: str, url: str, **kwargs) -> Dict:
        """
        发送HTTP请求的通用方法
        
        Args:
            method: HTTP方法
            url: 请求URL
            **kwargs: 其他请求参数
            
        Returns:
            API响应数据
            
        Raises:
            APIError: 当API返回错误时
            requests.RequestException: 当HTTP请求失败时
        """
        try:
            kwargs['headers'] = kwargs.get('headers', self.headers)
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()  # 检查HTTP状态码
            return validate_response(response.json())
        except requests.exceptions.JSONDecodeError as e:
            raise APIError(f"Invalid JSON response: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise APIError(f"HTTP request failed: {str(e)}")

    def list_indexes(self) -> Dict:
        """
        列出所有向量索引
        
        Returns:
            包含索引列表的响应数据
        """
        url = f"{self.base_url}/indexes"
        return self._request('GET', url)

    def create_index(self, name: str, dimensions: int, metric: str, description: str = "") -> Dict:
        """
        创建新的向量索引
        
        Args:
            name: 索引名称
            dimensions: 向量维度 (1-1536)
            metric: 距离计算方式 (cosine/euclidean/dot-product)
            description: 索引描述
            
        Returns:
            创建的索引信息
        """
        url = f"{self.base_url}/indexes"
        data = {
            "name": name,
            "config": {
                "dimensions": dimensions,
                "metric": metric
            },
            "description": description
        }
        return self._request('POST', url, json=data)

    def delete_index(self, index_name: str) -> Dict:
        """
        删除指定的向量索引
        
        Args:
            index_name: 索引名称
            
        Returns:
            删除操作的响应数据
        """
        url = f"{self.base_url}/indexes/{index_name}"
        return self._request('DELETE', url)

    def get_index(self, index_name: str) -> Dict:
        """
        获取指定索引的信息
        
        Args:
            index_name: 索引名称
            
        Returns:
            索引的详细信息
        """
        url = f"{self.base_url}/indexes/{index_name}"
        return self._request('GET', url)

    def get_index_info(self, index_name: str) -> Dict:
        """
        获取索引的统计信息
        
        Args:
            index_name: 索引名称
            
        Returns:
            索引的统计信息,包括维度、向量数量等
        """
        url = f"{self.base_url}/indexes/{index_name}/info"
        return self._request('GET', url)

    def delete_vectors(self, index_name: str, vector_ids: List[str]) -> Dict:
        """
        通过ID删除向量
        
        Args:
            index_name: 索引名称
            vector_ids: 要删除的向量ID列表
            
        Returns:
            包含mutation_id的响应数据
        """
        url = f"{self.base_url}/indexes/{index_name}/delete_by_ids"
        data = {"ids": vector_ids}
        return self._request('POST', url, json=data)

    def get_vectors(self, index_name: str, vector_ids: List[str]) -> Dict:
        """
        通过ID获取向量
        
        Args:
            index_name: 索引名称
            vector_ids: 要获取的向量ID列表
            
        Returns:
            包含向量数据的响应
        """
        url = f"{self.base_url}/indexes/{index_name}/get_by_ids"
        data = {"ids": vector_ids}
        return self._request('POST', url, json=data)

    def insert_vectors(self, 
                      index_name: str, 
                      vectors_data: str, 
                      unparsable_behavior: str = "error",
                      namespace: Optional[str] = None) -> Dict:
        """
        插入向量
        
        Args:
            index_name: 索引名称
            vectors_data: NDJSON格式的向量数据
            unparsable_behavior: 解析失败处理方式 (error/discard)
            namespace: 命名空间，用于分段管理向量（可选，最大64字符）
            
        Returns:
            包含mutation_id的响应数据
            
        Raises:
            ValueError: 当向量数据格式无效时
            APIError: 当API调用失败时
            
        Note:
            如果指定了namespace参数，会自动为vectors_data中的每个向量添加namespace字段
        """
        # 如果指定了namespace，需要为每个向量添加namespace字段
        if namespace is not None:
            if not namespace:
                raise ValueError("Namespace cannot be empty")
            if len(namespace) > 64:
                raise ValueError("Namespace cannot exceed 64 characters")
            
            # 解析NDJSON并添加namespace
            lines = vectors_data.strip().split('\n')
            updated_lines = []
            for line in lines:
                if line.strip():
                    vector = json.loads(line)
                    vector['namespace'] = namespace
                    updated_lines.append(json.dumps(vector, ensure_ascii=False))
            vectors_data = '\n'.join(updated_lines)
        
        # 确保原始数据也正确处理中文字符
        else:
            # 重新序列化原始数据以确保中文字符正确处理
            lines = vectors_data.strip().split('\n')
            updated_lines = []
            for line in lines:
                if line.strip():
                    vector = json.loads(line)
                    updated_lines.append(json.dumps(vector, ensure_ascii=False))
            vectors_data = '\n'.join(updated_lines)
        
        # 验证向量数据格式
        validate_vector_format(vectors_data)
        
        url = f"{self.base_url}/indexes/{index_name}/insert"
        if unparsable_behavior:
            url += f"?unparsable-behavior={unparsable_behavior}"
            
        headers = self.headers.copy()
        headers["Content-Type"] = "application/x-ndjson; charset=utf-8"
        return self._request('POST', url, headers=headers, data=vectors_data.encode('utf-8'))

    def query_vectors(self, 
                     index_name: str,
                     vector: List[float],
                     top_k: int = 5,
                     filter: Optional[Dict] = None,
                     return_metadata: str = "none",
                     return_values: bool = False,
                     namespace: Optional[str] = None) -> Dict:
        """
        查询最近邻向量
        
        Args:
            index_name: 索引名称
            vector: 查询向量
            top_k: 返回最近邻的数量
            filter: 元数据过滤条件
            return_metadata: 返回元数据类型 (none/indexed/all)
            return_values: 是否返回向量值
            namespace: 命名空间，仅在指定的命名空间内搜索（可选）
            
        Returns:
            包含匹配向量的响应数据
            
        Raises:
            ValueError: 当参数无效时
            APIError: 当API调用失败时
        """
        # 验证参数
        if not isinstance(vector, list) or not all(isinstance(x, (int, float)) for x in vector):
            raise ValueError("Vector must be a list of numbers")
        if return_metadata not in ["none", "indexed", "all"]:
            raise ValueError("return_metadata must be one of: none, indexed, all")
        if not isinstance(top_k, int) or top_k < 1:
            raise ValueError("top_k must be a positive integer")
        if namespace is not None:
            if not namespace:
                raise ValueError("Namespace cannot be empty")
            if len(namespace) > 64:
                raise ValueError("Namespace cannot exceed 64 characters")
            
        url = f"{self.base_url}/indexes/{index_name}/query"
        data = {
            "vector": vector,
            "topK": top_k,
            "returnMetadata": return_metadata,
            "returnValues": return_values
        }
        if filter:
            data["filter"] = filter
        if namespace:
            data["namespace"] = namespace
            
        return self._request('POST', url, json=data)

    def create_metadata_index(self, 
                            index_name: str, 
                            property_name: str, 
                            index_type: str) -> Dict:
        """
        创建元数据索引
        
        Args:
            index_name: 索引名称
            property_name: 元数据属性名
            index_type: 索引类型 (string/number/boolean)
            
        Returns:
            包含mutation_id的响应数据
        """
        url = f"{self.base_url}/indexes/{index_name}/metadata_index/create"
        data = {
            "propertyName": property_name,
            "indexType": index_type
        }
        return self._request('POST', url, json=data)

    def delete_metadata_index(self, index_name: str, property_name: str) -> Dict:
        """
        删除元数据索引
        
        Args:
            index_name: 索引名称
            property_name: 要删除的元数据属性名
            
        Returns:
            包含mutation_id的响应数据
        """
        url = f"{self.base_url}/indexes/{index_name}/metadata_index/delete"
        data = {"propertyName": property_name}
        return self._request('POST', url, json=data)

    def list_metadata_indexes(self, index_name: str) -> Dict:
        """
        列出索引的所有元数据索引
        
        Args:
            index_name: 索引名称
            
        Returns:
            包含元数据索引列表的响应数据
        """
        url = f"{self.base_url}/indexes/{index_name}/metadata_index/list"
        return self._request('GET', url)

    def upsert_vectors(self, 
                      index_name: str, 
                      vectors_data: str, 
                      unparsable_behavior: str = "error",
                      namespace: Optional[str] = None) -> Dict:
        """
        更新或插入向量
        
        Args:
            index_name: 索引名称
            vectors_data: NDJSON格式的向量数据
            unparsable_behavior: 解析失败处理方式 (error/discard)
            namespace: 命名空间，用于分段管理向量（可选，最大64字符）
            
        Returns:
            包含mutation_id的响应数据
            
        Raises:
            ValueError: 当向量数据格式无效时
            APIError: 当API调用失败时
            
        Note:
            如果指定了namespace参数，会自动为vectors_data中的每个向量添加namespace字段
        """
        # 如果指定了namespace，需要为每个向量添加namespace字段
        if namespace is not None:
            if not namespace:
                raise ValueError("Namespace cannot be empty")
            if len(namespace) > 64:
                raise ValueError("Namespace cannot exceed 64 characters")
            
            # 解析NDJSON并添加namespace
            lines = vectors_data.strip().split('\n')
            updated_lines = []
            for line in lines:
                if line.strip():
                    vector = json.loads(line)
                    vector['namespace'] = namespace
                    updated_lines.append(json.dumps(vector, ensure_ascii=False))
            vectors_data = '\n'.join(updated_lines)
        
        # 确保原始数据也正确处理中文字符
        else:
            # 重新序列化原始数据以确保中文字符正确处理
            lines = vectors_data.strip().split('\n')
            updated_lines = []
            for line in lines:
                if line.strip():
                    vector = json.loads(line)
                    updated_lines.append(json.dumps(vector, ensure_ascii=False))
            vectors_data = '\n'.join(updated_lines)
        
        # 验证向量数据格式
        validate_vector_format(vectors_data)
        
        url = f"{self.base_url}/indexes/{index_name}/upsert"
        if unparsable_behavior:
            url += f"?unparsable-behavior={unparsable_behavior}"
            
        headers = self.headers.copy()
        headers["Content-Type"] = "application/x-ndjson; charset=utf-8"
        return self._request('POST', url, headers=headers, data=vectors_data.encode('utf-8'))