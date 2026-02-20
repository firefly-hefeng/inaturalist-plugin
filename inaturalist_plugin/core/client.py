"""
iNaturalist API 核心客户端模块

提供与 iNaturalist API 通信的基础功能
API 文档: https://api.inaturalist.org/v1/docs/
"""

import requests
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from urllib.parse import urljoin


@dataclass
class APIConfig:
    """API 配置类"""
    base_url: str = "https://api.inaturalist.org/v1"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    rate_limit_per_second: float = 1.0  # iNaturalist 建议每秒最多1个请求
    api_key: Optional[str] = None  # 可选的 JWT token


class INaturalistAPIError(Exception):
    """iNaturalist API 错误基类"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class RateLimitError(INaturalistAPIError):
    """速率限制错误"""
    pass


class AuthenticationError(INaturalistAPIError):
    """认证错误"""
    pass


class INaturalistClient:
    """
    iNaturalist API 客户端
    
    支持的功能:
    - 自动重试机制
    - 速率限制控制
    - 认证管理
    - 请求/响应日志
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        self.config = config or APIConfig()
        self.session = requests.Session()
        self._last_request_time = 0
        
        # 设置默认请求头
        self.session.headers.update({
            "User-Agent": "iNaturalistPlugin/1.0 (Scientific Research)",
            "Accept": "application/json"
        })
        
        if self.config.api_key:
            self.session.headers["Authorization"] = f"Bearer {self.config.api_key}"
    
    def _apply_rate_limit(self):
        """应用速率限制"""
        min_interval = 1.0 / self.config.rate_limit_per_second
        elapsed = time.time() - self._last_request_time
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self._last_request_time = time.time()
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        执行 HTTP 请求
        
        Args:
            method: HTTP 方法 (GET, POST, PUT, DELETE)
            endpoint: API 端点路径
            params: URL 查询参数
            data: 请求体数据
            headers: 额外请求头
            
        Returns:
            API 响应的 JSON 数据
            
        Raises:
            INaturalistAPIError: API 调用失败
        """
        # 确保 base_url 以 / 结尾，endpoint 不以 / 开头
        base_url = self.config.base_url.rstrip("/") + "/"
        endpoint = endpoint.lstrip("/")
        url = base_url + endpoint
        request_headers = {**(headers or {})}
        
        last_exception = None
        
        for attempt in range(self.config.max_retries):
            try:
                self._apply_rate_limit()
                
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    headers=request_headers,
                    timeout=self.config.timeout
                )
                
                # 处理特定状态码
                if response.status_code == 429:
                    raise RateLimitError("Rate limit exceeded", status_code=429)
                elif response.status_code == 401:
                    raise AuthenticationError("Authentication required", status_code=401)
                
                response.raise_for_status()
                
                if response.content:
                    return response.json()
                return {}
                
            except requests.exceptions.RequestException as e:
                last_exception = e
                if hasattr(e.response, 'status_code'):
                    if e.response.status_code == 429:
                        # 速率限制，等待更长时间
                        time.sleep(self.config.retry_delay * (attempt + 1))
                        continue
                
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay)
                else:
                    raise INaturalistAPIError(
                        f"Request failed after {self.config.max_retries} attempts: {str(e)}",
                        status_code=getattr(e.response, 'status_code', None)
                    )
        
        raise last_exception or INaturalistAPIError("Unknown error occurred")
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """执行 GET 请求"""
        return self._make_request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """执行 POST 请求"""
        return self._make_request("POST", endpoint, data=data)
    
    def paginate(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        per_page: int = 200,
        max_pages: Optional[int] = None,
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        分页获取所有结果
        
        Args:
            endpoint: API 端点
            params: 查询参数
            per_page: 每页数量 (最大 200)
            max_pages: 最大页数限制
            max_results: 最大结果数量限制
            
        Returns:
            所有页面的结果合并列表
        """
        params = params or {}
        params["per_page"] = min(per_page, 200)  # API 限制最大 200
        params["page"] = 1
        
        all_results = []
        total_pages = None
        
        while True:
            response = self.get(endpoint, params)
            
            results = response.get("results", [])
            all_results.extend(results)
            
            # 更新总页数
            if total_pages is None and "total_results" in response:
                total_pages = (response["total_results"] + per_page - 1) // per_page
            
            # 检查是否还有更多结果
            if not results:
                break
            
            # 检查限制
            if max_results and len(all_results) >= max_results:
                all_results = all_results[:max_results]
                break
            
            if max_pages and params["page"] >= max_pages:
                break
            
            if total_pages and params["page"] >= total_pages:
                break
            
            params["page"] += 1
        
        return all_results
    
    def get_total_count(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> int:
        """
        获取查询结果的总数量
        
        Args:
            endpoint: API 端点
            params: 查询参数
            
        Returns:
            总结果数量
        """
        params = params or {}
        params["per_page"] = 0
        response = self.get(endpoint, params)
        return response.get("total_results", 0)


# 便捷函数: 创建默认客户端
def create_client(api_key: Optional[str] = None) -> INaturalistClient:
    """创建默认配置的 iNaturalist 客户端"""
    config = APIConfig(api_key=api_key)
    return INaturalistClient(config)
