"""
配置管理模块单元测试
"""
import pytest
from app.config.settings import ConfigManager


@pytest.fixture
def config_manager():
    """创建配置管理器实例"""
    return ConfigManager(config_dir="../config")


class TestConfigManager:
    """配置管理器测试"""
    
    def test_get_default_value(self, config_manager):
        """测试获取默认配置值"""
        value = config_manager.get('scanner.max_concurrency')
        assert value is not None
    
    def test_set_and_get_value(self, config_manager):
        """测试设置和获取配置值"""
        config_manager.set('test.key', 'test_value')
        value = config_manager.get('test.key')
        assert value == 'test_value'
    
    def test_get_nonexistent_key(self, config_manager):
        """测试获取不存在的键"""
        value = config_manager.get('nonexistent.key', default='default')
        assert value == 'default'
