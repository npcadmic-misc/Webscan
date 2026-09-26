"""
CSRF（跨站请求伪造）检测模块
"""
import httpx
from typing import List
from loguru import logger

from app.models.scan_target import ScanConfig
from app.models.vulnerability import Vulnerability, VulnerabilitySeverity


async def detect(url: str, config: ScanConfig) -> List[Vulnerability]:
    """检测CSRF漏洞"""
    vulnerabilities = []
    
    try:
        async with httpx.AsyncClient(timeout=config.timeout) as client:
            # 获取页面内容
            response = await client.get(url)
            
            # 检查是否有表单
            if '<form' in response.text.lower():
                # 检查是否有CSRF token
                csrf_indicators = [
                    'csrf_token',
                    'csrftoken',
                    '_token',
                    'authenticity_token',
                    'xsrf_token'
                ]
                
                has_csrf_protection = any(
                    indicator in response.text.lower() 
                    for indicator in csrf_indicators
                )
                
                if not has_csrf_protection:
                    vuln = Vulnerability(
                        name="CSRF漏洞",
                        severity=VulnerabilitySeverity.MEDIUM,
                        description="表单缺少CSRF token保护",
                        location=url,
                        poc="表单中未找到CSRF token",
                        remediation="在所有表单中添加CSRF token验证",
                        target_url=url,
                        scan_id=""
                    )
                    vulnerabilities.append(vuln)
                    logger.warning(f"发现CSRF漏洞: {url}")
    
    except Exception as e:
        logger.error(f"CSRF检测失败: {str(e)}")
    
    return vulnerabilities
