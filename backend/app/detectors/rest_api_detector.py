"""
REST API未授权访问检测模块
"""
import httpx
import json
from typing import List, Dict
from loguru import logger

from app.models.scan_target import ScanConfig
from app.models.vulnerability import Vulnerability, VulnerabilitySeverity


# 常见的API端点路径
COMMON_API_ENDPOINTS = [
    '/api/users',
    '/api/admin',
    '/api/config',
    '/api/settings',
    '/api/data',
    '/api/v1/users',
    '/api/v1/admin',
    '/api/v2/users',
    '/graphql',
    '/api/graphql',
]

# 常见的HTTP方法
HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']


async def detect(url: str, config: ScanConfig) -> List[Vulnerability]:
    """检测REST API未授权访问"""
    vulnerabilities = []
    
    try:
        base_url = url.rstrip('/').split('?')[0]
        
        async with httpx.AsyncClient(timeout=config.timeout, follow_redirects=True) as client:
            # 1. 探测常见API端点
            for endpoint in COMMON_API_ENDPOINTS:
                api_url = f"{base_url}{endpoint}"
                
                for method in HTTP_METHODS:
                    try:
                        if method == 'GET':
                            response = await client.get(api_url)
                        elif method == 'POST':
                            response = await client.post(api_url, json={})
                        elif method == 'PUT':
                            response = await client.put(api_url, json={})
                        elif method == 'DELETE':
                            response = await client.delete(api_url)
                        elif method == 'PATCH':
                            response = await client.patch(api_url, json={})
                        
                        # 如果返回200或201，可能缺少认证
                        if response.status_code in [200, 201, 204]:
                            # 检查响应内容是否是JSON（可能是API响应）
                            try:
                                json_response = response.json()
                                
                                vuln = Vulnerability(
                                    name="API未授权访问",
                                    severity=VulnerabilitySeverity.HIGH,
                                    description=f"API端点 {endpoint} 可通过 {method} 方法未授权访问",
                                    location=api_url,
                                    poc=f"Method: {method}\nURL: {api_url}\nResponse: {json.dumps(json_response, ensure_ascii=False)[:200]}",
                                    remediation="为API端点添加适当的认证和授权检查",
                                    target_url=url,
                                    scan_id=""
                                )
                                vulnerabilities.append(vuln)
                                logger.warning(f"发现API未授权访问: {api_url} [{method}]")
                            
                            except json.JSONDecodeError:
                                # 不是JSON响应，可能不是API
                                pass
                        
                        # 如果返回405，说明端点存在但方法不允许
                        elif response.status_code == 405:
                            logger.debug(f"API端点存在但方法不允许: {api_url} [{method}]")
                    
                    except Exception as e:
                        logger.debug(f"测试API端点失败 {api_url}: {str(e)}")
                        continue
            
            # 2. 检测API信息泄露（通过OPTIONS方法）
            for endpoint in COMMON_API_ENDPOINTS[:5]:  # 只测试前5个
                api_url = f"{base_url}{endpoint}"
                
                try:
                    options_response = await client.options(api_url)
                    
                    if options_response.status_code == 200:
                        allow_header = options_response.headers.get('Allow', '')
                        
                        if allow_header and ('DELETE' in allow_header or 'PUT' in allow_header):
                            vuln = Vulnerability(
                                name="API危险方法暴露",
                                severity=VulnerabilitySeverity.MEDIUM,
                                description=f"API端点 {endpoint} 暴露了危险方法: {allow_header}",
                                location=api_url,
                                poc=f"OPTIONS {api_url}\nAllow: {allow_header}",
                                remediation="限制API暴露的HTTP方法，仅允许必要的方法",
                                target_url=url,
                                scan_id=""
                            )
                            vulnerabilities.append(vuln)
                
                except Exception as e:
                    logger.debug(f"测试OPTIONS失败: {str(e)}")
                    continue
    
    except Exception as e:
        logger.error(f"REST API检测失败: {str(e)}")
    
    return vulnerabilities
