"""
配置管理模块
"""
import json
from pathlib import Path
from typing import Dict, Any
from loguru import logger


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.default_config_file = self.config_dir / "default.json"
        self.user_config_file = self.config_dir / "user.json"
        
        # 加载默认配置
        self.default_config = self._load_config(self.default_config_file)
        
        # 加载用户配置（如果存在）
        self.user_config = self._load_config(self.user_config_file) if self.user_config_file.exists() else {}
        
        # 合并配置（用户配置覆盖默认配置）
        self.config = {**self.default_config, **self.user_config}
    
    def _load_config(self, config_file: Path) -> Dict[str, Any]:
        """加载配置文件"""
        if not config_file.exists():
            logger.warning(f"配置文件不存在: {config_file}")
            return {}
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载配置文件失败 {config_file}: {str(e)}")
            return {}
    
    def get(self, key: str, default=None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_user_config(self):
        """保存用户配置"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.user_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"用户配置已保存: {self.user_config_file}")
        except Exception as e:
            logger.error(f"保存用户配置失败: {str(e)}")
    
    def update_user_config(self, key: str, value: Any):
        """更新用户配置并保存"""
        keys = key.split('.')
        config = self.user_config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.config[key] = value  # 同时更新运行时配置
        
        self.save_user_config()
    
    def get_scanner_config(self) -> Dict[str, Any]:
        """获取扫描器配置"""
        return self.config.get('scanner', {})
    
    def get_report_config(self) -> Dict[str, Any]:
        """获取报告配置"""
        return self.config.get('report', {})
    
    def get_api_config(self) -> Dict[str, Any]:
        """获取API配置"""
        return self.config.get('api', {})
