"""
业务逻辑漏洞检测模块
检测常见的业务逻辑安全问题
"""
import httpx
from typing import List, Dict
from loguru import logger
from bs4 import BeautifulSoup

from app.models.scan_target import ScanConfig
from app.models.vulnerability import Vulnerability, VulnerabilitySeverity


# 敏感参数字段名
SENSITIVE_PARAMS = [
    'price', 'amount', 'quantity', 'count', 'total',
    'discount', 'coupon', 'balance', 'credit', 'money'
]

# 可能的步骤跳过关键词
STEP_SKIP_KEYWORDS = [
    'skip', 'bypass', 'direct', 'force', 'complete'
]


async def detect(url: str, config: ScanConfig) -> List[Vulnerability]:
    """检测业务逻辑漏洞"""
    vulnerabilities = []
    
    try:
        async with httpx.AsyncClient(timeout=config.timeout, follow_redirects=True) as client:
            response = await client.get(url)
            
            if response.status_code != 200:
                return vulnerabilities
            
            # 1. 检测表单中的敏感参数
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for form in soup.find_all('form'):
                action = form.get('action', '')
                method = form.get('method', 'get').lower()
                
                # 提取表单字段
                sensitive_fields = []
                for input_tag in form.find_all('input'):
                    name = input_tag.get('name', '').lower()
                    input_type = input_tag.get('type', 'text').lower()
                    
                    # 检查是否是敏感字段
                    for keyword in SENSITIVE_PARAMS:
                        if keyword in name and input_type not in ['hidden', 'submit', 'button']:
                            sensitive_fields.append({
                                'name': input_tag.get('name'),
                                'type': input_type,
                                'keyword': keyword
                            })
                
                if sensitive_fields:
                    vuln = Vulnerability(
                        name="潜在业务逻辑漏洞",
                        severity=VulnerabilitySeverity.MEDIUM,
                        description=f"表单中存在可被篡改的敏感参数: {', '.join([f['name'] for f in sensitive_fields])}",
                        location=f"{url}{action}" if action else url,
                        poc=f"敏感字段: {[f['name'] for f in sensitive_fields]}\n建议测试: 修改价格、数量等参数值",
                        remediation="在服务端验证所有业务参数的合法性和权限",
                        target_url=url,
                        scan_id=""
                    )
                    vulnerabilities.append(vuln)
                    logger.warning(f"发现潜在业务逻辑漏洞: {url}")
            
            # 2. 检测URL中可能的步骤跳过风险
            url_lower = url.lower()
            for keyword in STEP_SKIP_KEYWORDS:
                if keyword in url_lower:
                    vuln = Vulnerability(
                        name="潜在步骤跳过漏洞",
                        severity=VulnerabilitySeverity.HIGH,
                        description=f"URL中包含可能绕过业务流程的关键词: {keyword}",
                        location=url,
                        poc=f"URL包含关键词: {keyword}\n建议测试是否可以直接访问完成状态",
                        remediation="确保业务流程的每个步骤都有正确的状态验证",
                        target_url=url,
                        scan_id=""
                    )
                    vulnerabilities.append(vuln)
                    break
            
            # 3. 检测重复提交风险（查找表单但没有防重令牌）
            forms = soup.find_all('form')
            for form in forms:
                has_csrf = False
                for input_tag in form.find_all('input'):
                    name = input_tag.get('name', '').lower()
                    if 'token' in name or 'csrf' in name:
                        has_csrf = True
                        break
                
                if not has_csrf:
                    action = form.get('action', '')
                    vuln = Vulnerability(
                        name="潜在重复提交漏洞",
                        severity=VulnerabilitySeverity.LOW,
                        description="表单缺少防重复提交令牌",
                        location=f"{url}{action}" if action else url,
                        poc="表单中未找到token或csrf字段",
                        remediation="添加一次性token防止重复提交",
                        target_url=url,
                        scan_id=""
                    )
                    vulnerabilities.append(vuln)
    
    except Exception as e:
        logger.error(f"业务逻辑漏洞检测失败: {str(e)}")
    
    return vulnerabilities
