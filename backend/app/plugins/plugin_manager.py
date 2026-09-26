"""
插件管理器
"""
import importlib
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger


class PluginBase:
    """插件基类"""
    
    name = "base_plugin"
    version = "1.0.0"
    description = "插件基类"
    enabled = True
    
    def __init__(self):
        pass
    
    def activate(self):
        """激活插件"""
        logger.info(f"插件已激活: {self.name}")
    
    def deactivate(self):
        """停用插件"""
        logger.info(f"插件已停用: {self.name}")
    
    def run(self, *args, **kwargs) -> Any:
        """执行插件功能"""
        raise NotImplementedError("子类必须实现run方法")


class PluginManager:
    """插件管理器"""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.plugins: Dict[str, PluginBase] = {}
        self.plugin_metadata: Dict[str, Dict] = {}
        
        # 确保插件目录存在
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
    
    def discover_plugins(self) -> List[str]:
        """发现可用的插件"""
        plugins = []
        
        for plugin_file in self.plugin_dir.glob("*.py"):
            if plugin_file.stem.startswith('_'):
                continue
            
            try:
                module_name = f"plugins.{plugin_file.stem}"
                
                # 动态导入模块
                spec = importlib.util.spec_from_file_location(module_name, str(plugin_file))
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                
                # 查找插件类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, PluginBase) and 
                        attr != PluginBase):
                        
                        plugin_instance = attr()
                        self.plugins[plugin_instance.name] = plugin_instance
                        self.plugin_metadata[plugin_instance.name] = {
                            'name': plugin_instance.name,
                            'version': plugin_instance.version,
                            'description': plugin_instance.description,
                            'enabled': plugin_instance.enabled,
                            'file': str(plugin_file)
                        }
                        plugins.append(plugin_instance.name)
                        logger.info(f"发现插件: {plugin_instance.name} v{plugin_instance.version}")
            
            except Exception as e:
                logger.error(f"加载插件失败 {plugin_file}: {str(e)}")
        
        return plugins
    
    def get_plugin(self, name: str) -> Optional[PluginBase]:
        """获取插件实例"""
        return self.plugins.get(name)
    
    def enable_plugin(self, name: str) -> bool:
        """启用插件"""
        plugin = self.plugins.get(name)
        if not plugin:
            logger.error(f"插件不存在: {name}")
            return False
        
        try:
            plugin.activate()
            plugin.enabled = True
            self.plugin_metadata[name]['enabled'] = True
            logger.info(f"插件已启用: {name}")
            return True
        except Exception as e:
            logger.error(f"启用插件失败 {name}: {str(e)}")
            return False
    
    def disable_plugin(self, name: str) -> bool:
        """禁用插件"""
        plugin = self.plugins.get(name)
        if not plugin:
            logger.error(f"插件不存在: {name}")
            return False
        
        try:
            plugin.deactivate()
            plugin.enabled = False
            self.plugin_metadata[name]['enabled'] = False
            logger.info(f"插件已禁用: {name}")
            return True
        except Exception as e:
            logger.error(f"禁用插件失败 {name}: {str(e)}")
            return False
    
    def list_plugins(self) -> List[Dict]:
        """列出所有插件"""
        return list(self.plugin_metadata.values())
    
    def run_plugin(self, name: str, *args, **kwargs) -> Any:
        """运行插件"""
        plugin = self.plugins.get(name)
        if not plugin:
            logger.error(f"插件不存在: {name}")
            return None
        
        if not plugin.enabled:
            logger.warning(f"插件未启用: {name}")
            return None
        
        try:
            return plugin.run(*args, **kwargs)
        except Exception as e:
            logger.error(f"运行插件失败 {name}: {str(e)}")
            return None
