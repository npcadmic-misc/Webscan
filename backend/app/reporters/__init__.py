# 报告生成器模块

from app.reporters.html_reporter import generate_html_report
from app.reporters.markdown_reporter import generate_markdown_report

__all__ = ['generate_html_report', 'generate_markdown_report']
