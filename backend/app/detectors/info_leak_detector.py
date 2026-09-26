"""
敏感信息泄露检测模块
检测常见的敏感信息暴露问题
"""
import httpx
import re
from typing import List, Dict
from loguru import logger

from app.models.scan_target import ScanConfig
from app.models.vulnerability import Vulnerability, VulnerabilitySeverity


# 敏感信息模式
SENSITIVE_PATTERNS = {
    'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    'phone': r'1[3-9]\d{9}',
    'id_card': r'[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]',
    'api_key': r'(api[_-]?key|apikey)["\s:=]+["\']?([a-zA-Z0-9_\-]{16,})["\']?',
    'password': r'(password|passwd|pwd)["\s:=]+["\']?([^"\s]{4,})["\']?',
    'secret': r'(secret|token|access_key)["\s:=]+["\']?([a-zA-Z0-9_\-]{16,})["\']?',
    'private_key': r'-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----',
    'aws_key': r'AKIA[0-9A-Z]{16}',
    'jwt_token': r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',
}

# 敏感文件路径
SENSITIVE_FILES = [
    '/.env',
    '/config.json',
    '/database.yml',
    '/wp-config.php',
    '/web.config',
    '/.git/config',
    '/backup.sql',
    '/dump.sql',
    '/debug.log',
    '/error.log',
]


async def detect(url: str, config: ScanConfig) -> List[Vulnerability]:
    """检测敏感信息泄露"""
    vulnerabilities = []
    
    try:
        async with httpx.AsyncClient(timeout=config.timeout, follow_redirects=True) as client:
            # 1. 检测页面内容中的敏感信息
            response = await client.get(url)
            
            if response.status_code == 200:
                content = response.text
                
                for info_type, pattern in SENSITIVE_PATTERNS.items():
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    
                    if matches:
                        # 过滤误报
                        if info_type == 'email' and len(matches) > 10:
                            continue  # 可能是正常的邮箱列表
                        
                        vuln = Vulnerability(
                            name=f"敏感信息泄露 - {info_type}",
                            severity=VulnerabilitySeverity.HIGH if info_type in ['password', 'secret', 'private_key', 'api_key'] else VulnerabilitySeverity.MEDIUM,
                            description=f"页面中检测到{len(matches)}个{info_type}格式的信息",
                            location=url,
                            poc=f"匹配到 {len(matches)} 个 {info_type}\n示例: {matches[0] if matches else 'N/A'}",
                            remediation=f"移除或脱敏显示的{info_type}信息",
                            target_url=url,
                            scan_id=""
                        )
                        vulnerabilities.append(vuln)
                        logger.warning(f"发现敏感信息泄露 ({info_type}): {url}")
            
            # 2. 检测常见敏感文件
            base_url = url.split('?')[0].rstrip('/')
            
            for sensitive_file in SENSITIVE_FILES:
                file_url = f"{base_url}{sensitive_file}"
                
                try:
                    file_response = await client.get(file_url)
                    
                    # 如果文件存在且返回了内容
                    if file_response.status_code == 200 and len(file_response.text) > 50:
                        # 检查是否包含敏感内容
                        has_sensitive = False
                        for pattern in SENSITIVE_PATTERNS.values():
                            if re.search(pattern, file_response.text, re.IGNORECASE):
                                has_sensitive = True
                                break
                        
                        if has_sensitive or sensitive_file in ['.env', 'config.json', 'web.config']:
                            vuln = Vulnerability(
                                name="敏感文件可访问",
                                severity=VulnerabilitySeverity.HIGH,
                                description=f"敏感文件可直接访问: {sensitive_file}",
                                location=file_url,
                                poc=f"访问 {file_url} 返回状态码 {file_response.status_code}",
                                remediation=f"禁止公开访问 {sensitive_file} 文件",
                                target_url=url,
                                scan_id=""
                            )
                            vulnerabilities.append(vuln)
                            logger.warning(f"发现敏感文件可访问: {file_url}")
                
                except Exception as e:
                    logger.debug(f"检测敏感文件失败 {file_url}: {str(e)}")
                    continue
            
            # 3. 检测目录列表
            if url.endswith('/'):
                try:
                    dir_response = await client.get(url)
                    
                    # 简单的目录列表检测（实际应该解析HTML结构）
                    if 'Index of' in dir_response.text or '<title>Directory listing' in dir_response.text:
                        vuln = Vulnerability(
                            name="目录列表泄露",
                            severity=VulnerabilitySeverity.MEDIUM,
                            description="服务器启用了目录列表功能",
                            location=url,
                            poc=f"访问 {url} 返回目录列表",
                            remediation="禁用服务器的目录列表功能",
                            target_url=url,
                            scan_id=""
                        )
                        vulnerabilities.append(vuln)
                        logger.warning(f"发现目录列表泄露: {url}")
                
                except Exception as e:
                    logger.debug(f"检测目录列表失败: {str(e)}")
    
    except Exception as e:
        logger.error(f"敏感信息泄露检测失败: {str(e)}")
    
    return vulnerabilities
