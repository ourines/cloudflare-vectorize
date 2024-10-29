"""Utility functions for the Cloudflare Vectorize client."""

from typing import Dict, Any, Optional
from .exceptions import APIError
import json

def validate_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证 API 响应
    
    Args:
        response: API 响应数据
        
    Returns:
        验证后的响应数据
        
    Raises:
        APIError: 当API返回错误时,包含以下情况:
            - success 字段不存在或为 False
            - errors 字段包含错误信息
            - result 字段不存在
    """
    # 验证响应格式
    if not isinstance(response, dict):
        raise APIError("Invalid response format: not a dictionary")
        
    # 验证 success 字段
    if 'success' not in response:
        raise APIError("Invalid response format: missing 'success' field")
    
    if not response['success']:
        errors = response.get('errors', [])
        messages = response.get('messages', [])
        
        # 构建详细的错误信息
        error_details = []
        
        # 处理 errors 列表
        for error in errors:
            if isinstance(error, dict):
                code = error.get('code', 'Unknown code')
                message = error.get('message', 'Unknown error')
                error_details.append(f"Error {code}: {message}")
                
        # 处理 messages 列表
        for message in messages:
            if isinstance(message, dict):
                code = message.get('code', 'Unknown code')
                msg = message.get('message', 'Unknown message')
                error_details.append(f"Message {code}: {msg}")
                
        # 如果没有详细错误信息,使用通用错误消息
        if not error_details:
            error_details = ["API request failed without specific error details"]
            
        raise APIError("\n".join(error_details), errors)
    
    # 验证 result 字段存在
    if 'result' not in response:
        raise APIError("Invalid response format: missing 'result' field")
    
    # 对特定响应类型进行额外验证
    result = response['result']
    
    # 验证列表类型的响应
    if isinstance(result, list):
        for item in result:
            if not isinstance(item, dict):
                raise APIError("Invalid response format: result list contains non-object items")
    
    # 验证对象类型的响应
    elif isinstance(result, dict):
        # 特定字段的验证可以在这里添加
        pass
    
    # 验证 mutation ID (如果存在)
    if isinstance(result, dict) and 'mutationId' in result:
        if not isinstance(result['mutationId'], str):
            raise APIError("Invalid response format: mutationId is not a string")
            
    return response

def validate_vector_format(vector_data: str) -> None:
    """
    验证向量数据的NDJSON格式
    
    Args:
        vector_data: NDJSON格式的向量数据
        
    Raises:
        ValueError: 当向量数据格式无效时
    """
    try:
        lines = vector_data.strip().split('\n')
        for line in lines:
            if line.strip():  # 跳过空行
                vector = json.loads(line)
                if not isinstance(vector, dict):
                    raise ValueError("Each line must be a JSON object")
                if 'values' not in vector:
                    raise ValueError("Each vector must contain 'values' field")
                if not isinstance(vector['values'], list):
                    raise ValueError("Vector values must be an array")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")