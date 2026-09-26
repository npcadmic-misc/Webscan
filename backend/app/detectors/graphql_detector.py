"""
GraphQL注入检测模块
"""
import httpx
import json
from typing import List, Dict
from loguru import logger

from app.models.scan_target import ScanConfig
from app.models.vulnerability import Vulnerability, VulnerabilitySeverity


# GraphQL常见注入payload
GRAPHQL_PAYLOADS = [
    # 基本查询
    '{__schema{types{name}}}',
    # 内省查询
    '{__type(name:"Query"){fields{name type{name kind}}}}',
    # 嵌套查询（可能导致DoS）
    '{a:b:c:d:e:f:g:h:i:j{k}}',
    # 别名滥用
    '{a1: __schema { types { name } } a2: __schema { types { name } } a3: __schema { types { name } }}',
]

# GraphQL端点
GRAPHQL_ENDPOINTS = [
    '/graphql',
    '/graphql/',
    '/api/graphql',
    '/api/v1/graphql',
    '/query',
]


async def detect(url: str, config: ScanConfig) -> List[Vulnerability]:
    """检测GraphQL注入漏洞"""
    vulnerabilities = []
    
    try:
        base_url = url.rstrip('/').split('?')[0]
        
        async with httpx.AsyncClient(timeout=config.timeout, follow_redirects=True) as client:
            # 1. 探测GraphQL端点
            graphql_urls = []
            
            for endpoint in GRAPHQL_ENDPOINTS:
                graphql_urls.append(f"{base_url}{endpoint}")
            
            # 也尝试当前URL是否是GraphQL端点
            if 'graphql' in url.lower() or 'query' in url.lower():
                graphql_urls.append(url)
            
            for graphql_url in graphql_urls:
                for payload in GRAPHQL_PAYLOADS:
                    try:
                        # 发送POST请求
                        response = await client.post(
                            graphql_url,
                            json={'query': payload},
                            headers={'Content-Type': 'application/json'}
                        )
                        
                        # 检查是否是有效的GraphQL响应
                        if response.status_code == 200:
                            try:
                                json_response = response.json()
                                
                                # 检查是否有数据或错误信息暴露
                                if 'data' in json_response or 'errors' in json_response:
                                    error_msg = ""
                                    if 'errors' in json_response:
                                        error_msg = str(json_response['errors'][:2])
                                    
                                    vuln = Vulnerability(
                                        name="GraphQL信息泄露",
                                        severity=VulnerabilitySeverity.MEDIUM,
                                        description=f"GraphQL端点返回了敏感信息: {graphql_url}",
                                        location=graphql_url,
                                        poc=f"Query: {payload}\nResponse: {json.dumps(json_response, ensure_ascii=False)[:500]}",
                                        remediation="禁用GraphQL内省功能，限制查询复杂度",
                                        target_url=url,
                                        scan_id=""
                                    )
                                    vulnerabilities.append(vuln)
                                    logger.warning(f"发现GraphQL信息泄露: {graphql_url}")
                                    break  # 只报告一次
                            
                            except json.JSONDecodeError:
                                continue
                        
                        # 检查是否启用了内省
                        if '__schema' in payload and response.status_code == 200:
                            try:
                                json_response = response.json()
                                if 'data' in json_response and '__schema' in json_response.get('data', {}):
                                    vuln = Vulnerability(
                                        name="GraphQL内省启用",
                                        severity=VulnerabilitySeverity.HIGH,
                                        description=f"GraphQL端点启用了内省功能，可获取完整Schema: {graphql_url}",
                                        location=graphql_url,
                                        poc=f"内省查询成功\nSchema信息已暴露",
                                        remediation="在生产环境禁用GraphQL内省功能",
                                        target_url=url,
                                        scan_id=""
                                    )
                                    vulnerabilities.append(vuln)
                                    logger.warning(f"发现GraphQL内省启用: {graphql_url}")
                                    break
                            except json.JSONDecodeError:
                                continue
                    
                    except Exception as e:
                        logger.debug(f"测试GraphQL失败 {graphql_url}: {str(e)}")
                        continue
            
            # 2. 检测批量查询滥用
            for graphql_url in graphql_urls[:1]:  # 只测试第一个端点
                try:
                    batch_payload = json.dumps([
                        {'query': '{__schema{types{name}}}'},
                        {'query': '{__schema{types{name}}}'},
                        {'query': '{__schema{types{name}}}'}
                    ])
                    
                    response = await client.post(
                        graphql_url,
                        content=batch_payload,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if response.status_code == 200:
                        vuln = Vulnerability(
                            name="GraphQL批量查询",
                            severity=VulnerabilitySeverity.LOW,
                            description=f"GraphQL端点支持批量查询，可能被用于DoS攻击: {graphql_url}",
                            location=graphql_url,
                            poc="发送包含多个查询的数组被接受",
                            remediation="限制或禁用GraphQL批量查询功能",
                            target_url=url,
                            scan_id=""
                        )
                        vulnerabilities.append(vuln)
                
                except Exception as e:
                    logger.debug(f"测试批量查询失败: {str(e)}")
                    continue
    
    except Exception as e:
        logger.error(f"GraphQL注入检测失败: {str(e)}")
    
    return vulnerabilities
