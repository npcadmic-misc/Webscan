"""
文件存储模块 - 管理扫描历史、报告和日志
"""
import json
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
from loguru import logger

from app.models.vulnerability import ScanResult


class FileStorage:
    """文件系统存储管理器"""
    
    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)
        self.reports_dir = self.base_dir / "reports"
        self.history_dir = self.base_dir / "history"
        self.logs_dir = self.base_dir / "logs"
        
        # 确保目录存在
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def save_scan_result(self, scan_result: ScanResult):
        """保存扫描结果到历史记录"""
        history_file = self.history_dir / f"{scan_result.scan_id}.json"
        
        data = {
            "scan_id": scan_result.scan_id,
            "target_url": scan_result.target_url,
            "start_time": scan_result.start_time.isoformat(),
            "end_time": scan_result.end_time.isoformat() if scan_result.end_time else None,
            "status": scan_result.status,
            "summary": scan_result.summary,
            "vulnerabilities": [
                {
                    "id": v.id,
                    "name": v.name,
                    "severity": v.severity.value if hasattr(v.severity, 'value') else v.severity,
                    "description": v.description,
                    "location": v.location,
                    "poc": v.poc,
                    "remediation": v.remediation,
                    "status": v.status.value if hasattr(v.status, 'value') else v.status,
                    "detected_at": v.detected_at.isoformat(),
                    "target_url": v.target_url,
                    "scan_id": v.scan_id
                }
                for v in scan_result.vulnerabilities
            ]
        }
        
        history_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
        logger.info(f"扫描结果已保存: {history_file}")
    
    def load_scan_history(self) -> List[Dict]:
        """加载扫描历史列表"""
        history_list = []
        
        for history_file in sorted(self.history_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                data = json.loads(history_file.read_text(encoding='utf-8'))
                history_list.append(data)
            except Exception as e:
                logger.error(f"加载历史记录失败 {history_file}: {str(e)}")
        
        return history_list
    
    def get_scan_result(self, scan_id: str) -> Optional[ScanResult]:
        """获取特定扫描结果"""
        history_file = self.history_dir / f"{scan_id}.json"
        
        if not history_file.exists():
            return None
        
        try:
            data = json.loads(history_file.read_text(encoding='utf-8'))
            
            # TODO: 将字典转换为ScanResult对象
            return data
        except Exception as e:
            logger.error(f"加载扫描结果失败 {scan_id}: {str(e)}")
            return None
    
    def delete_scan_result(self, scan_id: str) -> bool:
        """删除扫描结果"""
        history_file = self.history_dir / f"{scan_id}.json"
        report_html = self.reports_dir / f"{scan_id}.html"
        report_md = self.reports_dir / f"{scan_id}.md"
        
        deleted = False
        
        if history_file.exists():
            history_file.unlink()
            deleted = True
        
        if report_html.exists():
            report_html.unlink()
            deleted = True
        
        if report_md.exists():
            report_md.unlink()
            deleted = True
        
        if deleted:
            logger.info(f"扫描结果已删除: {scan_id}")
        
        return deleted
    
    def update_vulnerability_status(self, scan_id: str, vuln_id: str, new_status: str) -> bool:
        """更新漏洞状态"""
        history_file = self.history_dir / f"{scan_id}.json"
        
        if not history_file.exists():
            return False
        
        try:
            data = json.loads(history_file.read_text(encoding='utf-8'))
            
            for vuln in data.get('vulnerabilities', []):
                if vuln.get('id') == vuln_id or vuln.get('location') == vuln_id:
                    vuln['status'] = new_status
                    if new_status == '已确认':
                        vuln['confirmed_at'] = datetime.now().isoformat()
                    break
            
            history_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
            logger.info(f"漏洞状态已更新: {vuln_id} -> {new_status}")
            return True
        
        except Exception as e:
            logger.error(f"更新漏洞状态失败: {str(e)}")
            return False
    
    def save_log(self, log_content: str, filename: str = None):
        """保存日志文件"""
        if not filename:
            filename = f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        log_file = self.logs_dir / filename
        log_file.write_text(log_content, encoding='utf-8')
        logger.info(f"日志已保存: {log_file}")
    
    def get_logs(self) -> List[str]:
        """获取日志文件列表"""
        return [f.name for f in sorted(self.logs_dir.glob("*.txt"), key=lambda x: x.stat().st_mtime, reverse=True)]
