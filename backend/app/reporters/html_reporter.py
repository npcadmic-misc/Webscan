"""
HTML报告生成器
"""
from jinja2 import Template
from typing import List
from datetime import datetime
from pathlib import Path

from app.models.vulnerability import ScanResult, Vulnerability


# HTML报告模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>漏洞扫描报告 - {{ scan_id }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #409eff;
            padding-bottom: 10px;
        }
        h2 {
            color: #409eff;
            margin-top: 30px;
        }
        .info-box {
            background-color: #ecf5ff;
            border-left: 4px solid #409eff;
            padding: 15px;
            margin: 20px 0;
        }
        .summary {
            display: flex;
            gap: 20px;
            margin: 20px 0;
        }
        .summary-item {
            flex: 1;
            padding: 15px;
            border-radius: 4px;
            text-align: center;
        }
        .high {
            background-color: #fef0f0;
            border: 1px solid #f56c6c;
        }
        .medium {
            background-color: #fdf6ec;
            border: 1px solid #e6a23c;
        }
        .low {
            background-color: #f4f4f5;
            border: 1px solid #909399;
        }
        .count {
            font-size: 32px;
            font-weight: bold;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #409eff;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .severity-high {
            color: #f56c6c;
            font-weight: bold;
        }
        .severity-medium {
            color: #e6a23c;
            font-weight: bold;
        }
        .severity-low {
            color: #909399;
        }
        .poc {
            background-color: #f5f7fa;
            padding: 10px;
            border-radius: 4px;
            font-family: monospace;
            overflow-x: auto;
        }
        .footer {
            margin-top: 40px;
            text-align: center;
            color: #999;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Web漏洞扫描报告</h1>
        
        <div class="info-box">
            <p><strong>扫描ID:</strong> {{ scan_id }}</p>
            <p><strong>目标URL:</strong> {{ target_url }}</p>
            <p><strong>开始时间:</strong> {{ start_time }}</p>
            <p><strong>结束时间:</strong> {{ end_time }}</p>
            <p><strong>状态:</strong> {{ status }}</p>
        </div>
        
        <h2>漏洞统计</h2>
        <div class="summary">
            <div class="summary-item high">
                <div class="count">{{ summary.high }}</div>
                <div>高危漏洞</div>
            </div>
            <div class="summary-item medium">
                <div class="count">{{ summary.medium }}</div>
                <div>中危漏洞</div>
            </div>
            <div class="summary-item low">
                <div class="count">{{ summary.low }}</div>
                <div>低危漏洞</div>
            </div>
        </div>
        
        <h2>漏洞列表</h2>
        <table>
            <thead>
                <tr>
                    <th>严重程度</th>
                    <th>漏洞名称</th>
                    <th>位置</th>
                    <th>状态</th>
                </tr>
            </thead>
            <tbody>
                {% for vuln in vulnerabilities %}
                <tr>
                    <td class="severity-{{ vuln.severity }}">{{ vuln.severity }}</td>
                    <td>{{ vuln.name }}</td>
                    <td>{{ vuln.location }}</td>
                    <td>{{ vuln.status }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <h2>漏洞详情</h2>
        {% for vuln in vulnerabilities %}
        <div style="margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 4px;">
            <h3>{{ vuln.name }}</h3>
            <p><strong>严重程度:</strong> <span class="severity-{{ vuln.severity }}">{{ vuln.severity }}</span></p>
            <p><strong>位置:</strong> {{ vuln.location }}</p>
            <p><strong>描述:</strong> {{ vuln.description }}</p>
            <p><strong>修复建议:</strong> {{ vuln.remediation }}</p>
            {% if vuln.poc %}
            <p><strong>POC:</strong></p>
            <div class="poc">{{ vuln.poc }}</div>
            {% endif %}
        </div>
        {% endfor %}
        
        <div class="footer">
            <p>Generated by Web漏洞扫描系统 v1.0.0</p>
            <p>Report generated at: {{ generated_at }}</p>
        </div>
    </div>
</body>
</html>
"""


def generate_html_report(scan_result: ScanResult, output_dir: str = "data/reports") -> str:
    """生成HTML报告"""
    template = Template(HTML_TEMPLATE)
    
    html_content = template.render(
        scan_id=scan_result.scan_id,
        target_url=scan_result.target_url,
        start_time=scan_result.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        end_time=scan_result.end_time.strftime("%Y-%m-%d %H:%M:%S") if scan_result.end_time else "进行中",
        status=scan_result.status,
        summary=scan_result.summary,
        vulnerabilities=scan_result.vulnerabilities,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    # 保存报告
    output_path = Path(output_dir) / f"{scan_result.scan_id}.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content, encoding='utf-8')
    
    return str(output_path)
