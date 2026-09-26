# 漏洞检测模块

from app.detectors.sqli_detector import detect as sqli_detect
from app.detectors.xss_detector import detect as xss_detect
from app.detectors.csrf_detector import detect as csrf_detect
from app.detectors.idor_detector import detect as idor_detect
from app.detectors.business_logic_detector import detect as business_logic_detect
from app.detectors.info_leak_detector import detect as info_leak_detect
from app.detectors.rest_api_detector import detect as rest_api_detect
from app.detectors.graphql_detector import detect as graphql_detect
from app.detectors.api_param_detector import detect as api_param_detect

__all__ = [
    'sqli_detect',
    'xss_detect', 
    'csrf_detect',
    'idor_detect',
    'business_logic_detect',
    'info_leak_detect',
    'rest_api_detect',
    'graphql_detect',
    'api_param_detect'
]
