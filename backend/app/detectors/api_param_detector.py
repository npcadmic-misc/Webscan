"""
API参数污染检测模块
"""
import httpx
from typing import List, Dict
from loguru import logger

from app.models.scan_target import ScanConfig
from app.models.vulnerability import Vulnerability, VulnerabilitySeverity


async def detect(url: str, config: ScanConfig) -> List[Vulnerability]:
    """检测API参数污染漏洞"""
    vulnerabilities = []
    
    try:
        # 只对有参数的URL进行检测
        if '?' not in url:
            return vulnerabilities
        
        base_url, params = url.split('?', 1)
        param_pairs = params.split('&')
        
        async with httpx.AsyncClient(timeout=config.timeout, follow_redirects=True) as client:
            # 1. 检测重复参数名
            param_names = []
            for param in param_pairs:
                if '=' in param:
                    name = param.split('=')[0]
                    param_names.append(name)
            
            # 检查是否有重复的参数名
            duplicate_params = [name for name in param_names if param_names.count(name) > 1]
            
            if duplicate_params:
                vuln = Vulnerability(
                    name="API参数重复",
                    severity=VulnerabilitySeverity.LOW,
                    description=f"URL中存在重复的参数名: {set(duplicate_params)}",
                    location=url,
                    poc=f"重复参数: {set(duplicate_params)}\n服务器可能只处理第一个或最后一个值",
                    remediation="确保后端正确处理重复参数，或使用唯一的参数名",
                    target_url=url,
                    scan_id=""
                )
                vulnerabilities.append(vuln)
            
            # 2. 测试参数覆盖（发送相同参数多次）
            unique_params = list(set(param_names))
            
            for param_name in unique_params[:5]:  # 只测试前5个参数
                # 构造带有重复参数的URL
                test_params = []
                for param in param_pairs:
                    if param.startswith(param_name + '='):
                        test_params.append(param)
                        test_params.append(f"{param_name}=test_value")  # 添加重复
                    else:
                        test_params.append(param)
                
                test_url = f"{base_url}?{'&'.join(test_params)}"
                
                try:
                    original_response = await client.get(url)
                    test_response = await client.get(test_url)
                    
                    # 如果响应不同，可能存在参数污染
                    if (original_response.status_code != test_response.status_code or
                        len(original_response.text) != len(test_response.text)):
                        
                        vuln = Vulnerability(
                            name="潜在参数污染",
                            severity=VulnerabilitySeverity.MEDIUM,
                            description=f"参数 {param_name} 的重复可能导致意外行为",
                            location=test_url,
                            poc=f"原始URL: {url}\n测试URL: {test_url}\n响应差异: 状态码 {original_response.status_code} vs {test_response.status_code}",
                            remediation="明确定义重复参数的处理策略",
                            target_url=url,
                            scan_id=""
                        )
                        vulnerabilities.append(vuln)
                        logger.warning(f"发现潜在参数污染: {param_name}")
                
                except Exception as e:
                    logger.debug(f"测试参数污染失败: {str(e)}")
                    continue
            
            # 3. 检测数组参数注入
            for param_name in unique_params[:3]:
                # 尝试将参数转换为数组格式
                array_params = []
                for param in param_pairs:
                    if param.startswith(param_name + '='):
                        array_params.append(f"{param_name}[]=value1")
                        array_params.append(f"{param_name}[]=value2")
                    else:
                        array_params.append(param)
                
                test_url = f"{base_url}?{'&'.join(array_params)}"
                
                try:
                    response = await client.get(test_url)
                    
                    if response.status_code == 200 and 'error' not in response.text.lower():
                        vuln = Vulnerability(
                            name="数组参数接受",
                            severity=VulnerabilitySeverity.LOW,
                            description=f"API接受数组格式的参数 {param_name}[]",
                            location=test_url,
                            poc=f"参数 {param_name} 被转换为数组格式",
                            remediation="验证参数类型，避免意外的数组解析",
                            target_url=url,
                            scan_id=""
                        )
                        vulnerabilities.append(vuln)
                
                except Exception as e:
                    logger.debug(f"测试数组参数失败: {str(e)}")
                    continue
    
    except Exception as e:
        logger.error(f"API参数污染检测失败: {str(e)}")
    
    return vulnerabilities
