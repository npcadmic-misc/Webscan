"""
核心扫描引擎
"""
import asyncio
import time
from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger
import httpx

from app.models.scan_target import ScanConfig
from app.models.vulnerability import Vulnerability, ScanResult
from app.auth.session_manager import AuthManager
from app.utils.error_handler import ErrorHandler, CrashRecovery
from app.monitor.progress_manager import ProgressManager, ScanStatus


class ScannerEngine:
    """扫描引擎主类"""
    
    def __init__(self):
        self.active_scans: Dict[str, ScanResult] = {}
        self.max_concurrency = 10
        self.rate_limiter = RateLimiter(50)  # 默认50 req/s
        self.auth_manager = AuthManager()
        self.error_handler = ErrorHandler(max_retries=3, retry_delay=1.0)
        self.crash_recovery = CrashRecovery()
        self.progress_manager = ProgressManager()
    
    async def start_scan(self, config: ScanConfig) -> str:
        """启动扫描任务"""
        scan_id = f"SCAN-{int(time.time())}"
        
        # 创建扫描结果对象
        scan_result = ScanResult(
            scan_id=scan_id,
            target_url=config.target_url,
            start_time=datetime.now(),
            status="running"
        )
        
        self.active_scans[scan_id] = scan_result
        
        # 在后台启动扫描任务
        asyncio.create_task(self._run_scan(scan_id, config))
        
        logger.info(f"扫描任务已启动: {scan_id}, 目标: {config.target_url}")
        return scan_id
    
    async def _run_scan(self, scan_id: str, config: ScanConfig):
        """执行扫描任务"""
        # 创建进度跟踪
        progress = self.progress_manager.create_progress(scan_id)
        self.progress_manager.set_status(scan_id, ScanStatus.RUNNING)
        
        try:
            scan_result = self.active_scans[scan_id]
            
            # 1. 爬取目标网站
            self.progress_manager.update_progress(
                scan_id,
                current_module="URL爬取",
                message="开始爬取目标网站..."
            )
            
            urls = await self.error_handler.handle_async_error_gracefully(
                self.crawl_urls,
                config,
                default_value=[config.target_url],
                error_context="URL爬取"
            )
            
            progress.total_urls = len(urls)
            self.progress_manager.update_progress(
                scan_id,
                message=f"发现 {len(urls)} 个URL",
                progress_percentage=10
            )
            
            # 2. 执行基础扫描
            if "basic" in config.scan_types:
                self.progress_manager.update_progress(
                    scan_id,
                    current_module="基础扫描",
                    message="开始OWASP Top 10检测...",
                    progress_percentage=15
                )
                
                vulns = await self.error_handler.handle_async_error_gracefully(
                    self.run_basic_scan,
                    urls, config,
                    default_value=[],
                    error_context="基础扫描"
                )
                
                scan_result.vulnerabilities.extend(vulns)
                progress.vulnerabilities_found += len(vulns)
                self.progress_manager.update_progress(
                    scan_id,
                    message=f"基础扫描完成，发现 {len(vulns)} 个漏洞",
                    progress_percentage=40
                )
            
            # 3. 执行深度扫描
            if "deep" in config.scan_types:
                self.progress_manager.update_progress(
                    scan_id,
                    current_module="深度扫描",
                    message="开始越权、业务逻辑检测...",
                    progress_percentage=45
                )
                
                vulns = await self.error_handler.handle_async_error_gracefully(
                    self.run_deep_scan,
                    urls, config,
                    default_value=[],
                    error_context="深度扫描"
                )
                
                scan_result.vulnerabilities.extend(vulns)
                progress.vulnerabilities_found += len(vulns)
                self.progress_manager.update_progress(
                    scan_id,
                    message=f"深度扫描完成，发现 {len(vulns)} 个漏洞",
                    progress_percentage=70
                )
            
            # 4. 执行API扫描
            if "api" in config.scan_types:
                self.progress_manager.update_progress(
                    scan_id,
                    current_module="API扫描",
                    message="开始REST/GraphQL API检测...",
                    progress_percentage=75
                )
                
                vulns = await self.error_handler.handle_async_error_gracefully(
                    self.run_api_scan,
                    urls, config,
                    default_value=[],
                    error_context="API扫描"
                )
                
                scan_result.vulnerabilities.extend(vulns)
                progress.vulnerabilities_found += len(vulns)
                self.progress_manager.update_progress(
                    scan_id,
                    message=f"API扫描完成，发现 {len(vulns)} 个漏洞",
                    progress_percentage=95
                )
            
            # 检查是否有严重错误
            if self.error_handler.has_critical_errors():
                scan_result.status = "failed"
                self.progress_manager.set_status(scan_id, ScanStatus.FAILED)
                logger.error(f"[{scan_id}] 扫描因严重错误而失败")
            else:
                # 更新扫描状态
                scan_result.end_time = datetime.now()
                scan_result.status = "completed"
                self.progress_manager.set_status(scan_id, ScanStatus.COMPLETED)
                
                scan_result.summary = {
                    "total_vulnerabilities": len(scan_result.vulnerabilities),
                    "high": sum(1 for v in scan_result.vulnerabilities if v.severity == "高"),
                    "medium": sum(1 for v in scan_result.vulnerabilities if v.severity == "中"),
                    "low": sum(1 for v in scan_result.vulnerabilities if v.severity == "低")
                }
                
                logger.info(f"[{scan_id}] 扫描任务完成")
            
            self.progress_manager.update_progress(
                scan_id,
                progress_percentage=100,
                message="扫描任务已完成"
            )
            
            # 保存检查点
            await self.crash_recovery.save_checkpoint(scan_id, {
                'status': scan_result.status,
                'vulnerabilities_count': len(scan_result.vulnerabilities)
            })
            
        except Exception as e:
            logger.error(f"[{scan_id}] 扫描任务失败: {str(e)}")
            if scan_id in self.active_scans:
                self.active_scans[scan_id].status = "failed"
            self.progress_manager.set_status(scan_id, ScanStatus.FAILED)
            self.progress_manager.update_progress(
                scan_id,
                message=f"扫描失败: {str(e)}"
            )
    
    async def crawl_urls(self, config: ScanConfig) -> List[str]:
        """爬取目标网站的URL"""
        urls = [config.target_url]
        
        try:
            # 使用认证客户端
            client = self.auth_manager.create_authenticated_client(
                config.auth_config.dict() if config.auth_config else None,
                timeout=config.timeout
            )
            
            async with client as c:
                response = await c.get(config.target_url)
                
                if response.status_code == 200:
                    # 简单的URL提取（从链接中）
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    base_url = config.target_url.rstrip('/')
                    for a_tag in soup.find_all('a', href=True):
                        href = a_tag['href']
                        
                        # 构建完整URL
                        if href.startswith('http'):
                            urls.append(href)
                        elif href.startswith('/'):
                            urls.append(f"{base_url}{href}")
                        elif not href.startswith('#') and not href.startswith('javascript'):
                            urls.append(f"{base_url}/{href}")
                    
                    # 去重
                    urls = list(set(urls))
            
        except Exception as e:
            logger.error(f"爬取URL失败: {str(e)}")
        
        return urls
    
    async def run_basic_scan(self, urls: List[str], config: ScanConfig) -> List[Vulnerability]:
        """执行基础扫描（OWASP Top 10）"""
        vulnerabilities = []
        
        # 导入检测模块
        from app.detectors import sqli_detector, xss_detector, csrf_detector
        
        for url in urls:
            # SQL注入检测
            sqli_vulns = await sqli_detector.detect(url, config)
            vulnerabilities.extend(sqli_vulns)
            
            # XSS检测
            xss_vulns = await xss_detector.detect(url, config)
            vulnerabilities.extend(xss_vulns)
            
            # CSRF检测
            csrf_vulns = await csrf_detector.detect(url, config)
            vulnerabilities.extend(csrf_vulns)
        
        return vulnerabilities
    
    async def run_deep_scan(self, urls: List[str], config: ScanConfig) -> List[Vulnerability]:
        """执行深度扫描"""
        vulnerabilities = []
        
        # 导入深度扫描模块
        from app.detectors import idor_detector, business_logic_detector, info_leak_detector
        
        for url in urls:
            # 越权访问检测
            idor_vulns = await idor_detector.detect(url, config)
            vulnerabilities.extend(idor_vulns)
            
            # 业务逻辑漏洞检测
            logic_vulns = await business_logic_detector.detect(url, config)
            vulnerabilities.extend(logic_vulns)
            
            # 敏感信息泄露检测
            leak_vulns = await info_leak_detector.detect(url, config)
            vulnerabilities.extend(leak_vulns)
        
        return vulnerabilities
    
    async def run_api_scan(self, urls: List[str], config: ScanConfig) -> List[Vulnerability]:
        """执行API扫描"""
        vulnerabilities = []
        
        # 导入API扫描模块
        from app.detectors import rest_api_detector, graphql_detector, api_param_detector
        
        for url in urls:
            # REST API未授权访问检测
            rest_vulns = await rest_api_detector.detect(url, config)
            vulnerabilities.extend(rest_vulns)
            
            # GraphQL注入检测
            graphql_vulns = await graphql_detector.detect(url, config)
            vulnerabilities.extend(graphql_vulns)
            
            # API参数污染检测
            param_vulns = await api_param_detector.detect(url, config)
            vulnerabilities.extend(param_vulns)
        
        return vulnerabilities
    
    async def stop_scan(self, scan_id: str):
        """停止扫描任务"""
        if scan_id in self.active_scans:
            self.active_scans[scan_id].status = "stopped"
            self.active_scans[scan_id].end_time = datetime.now()
            logger.info(f"扫描任务已停止: {scan_id}")
    
    def get_scan_status(self, scan_id: str) -> Optional[ScanResult]:
        """获取扫描任务状态"""
        return self.active_scans.get(scan_id)


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, max_requests_per_second: int = 50):
        self.max_rps = max_requests_per_second
        self.requests = []
    
    async def wait_if_needed(self):
        """如果需要则等待"""
        now = time.time()
        
        # 移除1秒前的请求记录
        self.requests = [t for t in self.requests if now - t < 1]
        
        if len(self.requests) >= self.max_rps:
            wait_time = 1 - (now - self.requests[0])
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        self.requests.append(now)
