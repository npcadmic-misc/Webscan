"""
漏洞检测模块单元测试
"""
import pytest
from app.models.scan_target import ScanConfig
from app.detectors import sqli_detector, xss_detector, csrf_detector


@pytest.fixture
def sample_config():
    """创建测试配置"""
    return ScanConfig(
        target_url="http://example.com",
        scan_types=["basic"],
        timeout=5
    )


class TestSQLiDetector:
    """SQL注入检测器测试"""
    
    @pytest.mark.asyncio
    async def test_detect_function_exists(self):
        """测试检测函数存在"""
        assert hasattr(sqli_detector, 'detect')
        assert callable(sqli_detector.detect)


class TestXSSDetector:
    """XSS检测器测试"""
    
    @pytest.mark.asyncio
    async def test_detect_function_exists(self):
        """测试检测函数存在"""
        assert hasattr(xss_detector, 'detect')
        assert callable(xss_detector.detect)


class TestCSRFDetector:
    """CSRF检测器测试"""
    
    @pytest.mark.asyncio
    async def test_detect_function_exists(self):
        """测试检测函数存在"""
        assert hasattr(csrf_detector, 'detect')
        assert callable(csrf_detector.detect)
