"""
XSS（跨站脚本）检测模块
"""
import httpx
from typing import List
from loguru import logger

from app.models.scan_target import ScanConfig
from app.models.vulnerability import Vulnerability, VulnerabilitySeverity


# 常见的XSS payload
XSS_PAYLOADS = [
    '<script>alert("XSS")</script>',
    '<img src=x onerror=alert("XSS")>',
    '"><script>alert("XSS")</script>',
    "javascript:alert('XSS')",
    '<svg onload=alert("XSS")>',
]


async def detect(url: str, config: ScanConfig) -> List[Vulnerability]:
    """检测XSS漏洞"""
    vulnerabilities = []
    
    try:
        async with httpx.AsyncClient(timeout=config.timeout) as client:
            # 测试常见参数名
            param_names = ['q', 'search', 'query', 'name', 'input', 'text']
            
            for param in param_names:
                test_url = f"{url}?{param}="
                
                for payload in XSS_PAYLOADS:
                    try:
                        full_url = test_url + payload
                        response = await client.get(full_url)
                        
                        # 检测payload是否被反射回来
                        if payload in response.text:
                            # 检查是否有适当的过滤或编码
                            vuln = Vulnerability(
                                name="反射型XSS",
                                severity=VulnerabilitySeverity.HIGH,
                                description=f"在参数 {param} 中检测到反射型XSS漏洞",
                                location=full_url,
                                poc=f"Payload: {payload}",
                                remediation="对用户输入进行HTML实体编码",
                                target_url=url,
                                scan_id=""
                            )
                            vulnerabilities.append(vuln)
                            logger.warning(f"发现XSS漏洞: {full_url}")
                            break
                    
                    except Exception as e:
                        logger.debug(f"测试失败: {str(e)}")
                        continue
    
    except Exception as e:
        logger.error(f"XSS检测失败: {str(e)}")
    
    return vulnerabilities
