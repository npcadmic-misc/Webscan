"""
越权访问检测模块
检测明显的权限缺失漏洞
"""
import httpx
from typing import List, Dict
from loguru import logger
from bs4 import BeautifulSoup

from app.models.scan_target import ScanConfig
from app.models.vulnerability import Vulnerability, VulnerabilitySeverity


# 常见的管理路径关键词
ADMIN_PATH_KEYWORDS = [
    'admin', 'manager', 'dashboard', 'console', 'control',
    'settings', 'config', 'user_management', 'system'
]

# 敏感操作路径关键词
SENSITIVE_ACTIONS = [
    'delete', 'update', 'create', 'edit', 'modify',
    'reset', 'change', 'export', 'import', 'backup'
]


async def detect(url: str, config: ScanConfig) -> List[Vulnerability]:
    """检测越权访问漏洞"""
    vulnerabilities = []
    
    try:
        async with httpx.AsyncClient(timeout=config.timeout, follow_redirects=True) as client:
            # 1. 爬取页面，查找可能的管理链接
            response = await client.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 提取所有链接
                links = []
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    links.append(href)
                
                # 检查是否有明显的管理路径
                admin_paths = []
                for link in links:
                    link_lower = link.lower()
                    for keyword in ADMIN_PATH_KEYWORDS:
                        if keyword in link_lower:
                            admin_paths.append(link)
                            break
                
                # 测试这些管理路径是否可以直接访问
                for admin_path in admin_paths:
                    # 构建完整URL
                    if admin_path.startswith('http'):
                        test_url = admin_path
                    elif admin_path.startswith('/'):
                        test_url = f"{url.rstrip('/')}{admin_path}"
                    else:
                        test_url = f"{url.rstrip('/')}/{admin_path}"
                    
                    try:
                        admin_response = await client.get(test_url)
                        
                        # 如果返回200且没有重定向到登录页，可能存在越权
                        if admin_response.status_code == 200:
                            # 检查是否是登录页面
                            if 'login' not in admin_response.url.path.lower():
                                vuln = Vulnerability(
                                    name="潜在越权访问",
                                    severity=VulnerabilitySeverity.HIGH,
                                    description=f"发现可能的管理路径可直接访问: {test_url}",
                                    location=test_url,
                                    poc=f"直接访问: {test_url}\n状态码: {admin_response.status_code}",
                                    remediation="确保所有管理功能都有适当的权限检查",
                                    target_url=url,
                                    scan_id=""
                                )
                                vulnerabilities.append(vuln)
                                logger.warning(f"发现潜在越权访问: {test_url}")
                    
                    except Exception as e:
                        logger.debug(f"测试管理路径失败 {test_url}: {str(e)}")
                        continue
            
            # 2. 检测URL参数中的ID遍历风险
            if '?' in url:
                base_url, params = url.split('?', 1)
                param_pairs = params.split('&')
                
                for param in param_pairs:
                    if '=' in param:
                        key, value = param.split('=', 1)
                        
                        # 检查是否是ID类参数
                        if key.lower() in ['id', 'uid', 'user_id', 'order_id', 'product_id']:
                            # 尝试修改ID值
                            for test_id in ['1', '999999', '-1']:
                                new_params = []
                                for p in param_pairs:
                                    if p.startswith(key + '='):
                                        new_params.append(f"{key}={test_id}")
                                    else:
                                        new_params.append(p)
                                
                                test_url = f"{base_url}?{'&'.join(new_params)}"
                                
                                try:
                                    test_response = await client.get(test_url)
                                    
                                    # 如果能正常返回数据，可能存在水平越权
                                    if test_response.status_code == 200 and len(test_response.text) > 100:
                                        vuln = Vulnerability(
                                            name="潜在水平越权",
                                            severity=VulnerabilitySeverity.MEDIUM,
                                            description=f"参数 {key} 可能存在ID遍历风险",
                                            location=test_url,
                                            poc=f"修改参数 {key} 的值从 {value} 到 {test_id}",
                                            remediation="验证用户是否有权访问请求的资源ID",
                                            target_url=url,
                                            scan_id=""
                                        )
                                        vulnerabilities.append(vuln)
                                        logger.warning(f"发现潜在水平越权: {test_url}")
                                        break  # 只报告一次
                                
                                except Exception as e:
                                    logger.debug(f"测试ID遍历失败: {str(e)}")
                                    continue
    
    except Exception as e:
        logger.error(f"越权访问检测失败: {str(e)}")
    
    return vulnerabilities
