"""
数据存储模块单元测试
"""
import pytest
from pathlib import Path
from app.storage.file_storage import FileStorage


@pytest.fixture
def storage():
    """创建存储管理器实例"""
    return FileStorage(base_dir="test_data")


class TestFileStorage:
    """文件存储测试"""
    
    def test_init_creates_directories(self, storage):
        """测试初始化时创建目录"""
        assert storage.reports_dir.exists()
        assert storage.history_dir.exists()
        assert storage.logs_dir.exists()
    
    def test_save_and_load_log(self, storage):
        """测试保存和加载日志"""
        log_content = "Test log content"
        storage.save_log(log_content, "test.log")
        
        logs = storage.get_logs()
        assert "test.log" in logs
    
    def teardown_method(self, storage):
        """清理测试数据"""
        import shutil
        if Path("test_data").exists():
            shutil.rmtree("test_data")
