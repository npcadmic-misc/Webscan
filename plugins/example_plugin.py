"""
示例插件 - 目录遍历检测
"""
from app.plugins.plugin_manager import PluginBase
import httpx
from loguru import logger


class DirectoryTraversalPlugin(PluginBase):
    """目录遍历检测插件"""
    
    name = "directory_traversal"
    version = "1.0.0"
    description = "检测目录遍历漏洞"
    
    # 常见的目录遍历payload
    TRAVERSAL_PAYLOADS = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\win.ini",
        "....//....//....//etc/passwd",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    ]
    
    def run(self, url: str, timeout: int = 10) -> dict:
        """执行目录遍历检测"""
        results = {
            'vulnerable': False,
            'details': []
        }
        
        try:
            with httpx.Client(timeout=timeout) as client:
                for payload in self.TRAVERSAL_PAYLOADS:
                    test_url = f"{url}?file={payload}"
                    
                    try:
                        response = client.get(test_url)
                        
                        # 简单的检测逻辑（实际应该更复杂）
                        if 'root:' in response.text or '[extensions]' in response.text:
                            results['vulnerable'] = True
                            results['details'].append({
                                'payload': payload,
                                'url': test_url,
                                'response_code': response.status_code
                            })
                            logger.warning(f"发现目录遍历漏洞: {test_url}")
                    
                    except Exception as e:
                        logger.debug(f"测试失败: {str(e)}")
                        continue
        
        except Exception as e:
            logger.error(f"目录遍历检测失败: {str(e)}")
        
        return results
