# 开发者文档

## 目录

1. [项目架构](#项目架构)
2. [核心模块说明](#核心模块说明)
3. [插件开发指南](#插件开发指南)
4. [API接口文档](#api接口文档)
5. [代码规范](#代码规范)

## 项目架构

### 目录结构

```
新测试/
├── backend/                    # Python后端
│   ├── app/                   # 应用代码
│   │   ├── main.py            # FastAPI入口
│   │   ├── scanner/           # 扫描引擎
│   │   │   └── engine.py      # 核心扫描引擎
│   │   ├── detectors/         # 漏洞检测模块
│   │   │   ├── sqli_detector.py    # SQL注入检测
│   │   │   ├── xss_detector.py     # XSS检测
│   │   │   └── csrf_detector.py    # CSRF检测
│   │   ├── reporters/         # 报告生成器
│   │   │   ├── html_reporter.py    # HTML报告
│   │   │   └── markdown_reporter.py # Markdown报告
│   │   ├── storage/           # 数据存储
│   │   │   └── file_storage.py    # 文件存储管理
│   │   ├── config/            # 配置管理
│   │   │   └── settings.py        # 配置管理器
│   │   ├── plugins/           # 插件系统
│   │   │   └── plugin_manager.py  # 插件管理器
│   │   ├── models/            # 数据模型
│   │   │   ├── scan_target.py     # 扫描目标模型
│   │   │   └── vulnerability.py   # 漏洞模型
│   │   └── routes/            # API路由
│   │       ├── scan.py            # 扫描相关API
│   │       └── report.py          # 报告相关API
│   ├── tests/               # 测试文件
│   ├── cli.py               # CLI入口
│   └── requirements.txt     # Python依赖
├── frontend/                # Vue前端
│   ├── src/                 # 源代码
│   │   ├── views/           # 页面组件
│   │   ├── router/          # 路由配置
│   │   └── api/             # API服务
│   └── package.json         # Node依赖
├── plugins/                 # 插件目录
├── data/                    # 数据目录
│   ├── reports/             # 扫描报告
│   ├── history/             # 扫描历史
│   └── logs/                # 日志文件
├── config/                  # 配置文件
└── docs/                    # 文档
```

### 技术栈

- **后端**: Python + FastAPI + httpx
- **前端**: Vue 3 + Element Plus + Pinia
- **数据存储**: 本地文件系统（JSON）
- **报告生成**: Jinja2 (HTML) + 原生Markdown

## 核心模块说明

### 扫描引擎 (ScannerEngine)

位于 `backend/app/scanner/engine.py`

主要功能：
- 管理扫描任务生命周期
- 协调各个检测模块
- 控制并发和速率限制

使用方法：
```python
from app.scanner.engine import ScannerEngine
from app.models.scan_target import ScanConfig

engine = ScannerEngine()
config = ScanConfig(target_url="https://example.com", scan_types=["basic"])
scan_id = await engine.start_scan(config)
```

### 漏洞检测模块 (Detectors)

位于 `backend/app/detectors/`

每个检测模块需要实现 `detect(url, config)` 函数，返回 `List[Vulnerability]`。

示例：
```python
async def detect(url: str, config: ScanConfig) -> List[Vulnerability]:
    vulnerabilities = []
    # 检测逻辑
    return vulnerabilities
```

### 报告生成器 (Reporters)

位于 `backend/app/reporters/`

支持两种格式：
- HTML: 使用Jinja2模板
- Markdown: 原生生成

使用方法：
```python
from app.reporters import generate_html_report, generate_markdown_report

html_path = generate_html_report(scan_result)
md_path = generate_markdown_report(scan_result)
```

### 数据存储 (Storage)

位于 `backend/app/storage/file_storage.py`

主要功能：
- 保存和加载扫描历史
- 管理报告文件
- 更新漏洞状态

## 插件开发指南

### 创建插件

1. 在 `plugins/` 目录创建新的Python文件
2. 继承 `PluginBase` 类
3. 实现 `run()` 方法

示例：
```python
from app.plugins.plugin_manager import PluginBase

class MyPlugin(PluginBase):
    name = "my_plugin"
    version = "1.0.0"
    description = "我的插件"
    
    def run(self, *args, **kwargs):
        # 插件逻辑
        return result
```

### 插件生命周期

- `activate()`: 插件激活时调用
- `deactivate()`: 插件停用时调用
- `run()`: 执行插件功能

### 注册插件

插件文件放在 `plugins/` 目录后，系统会自动发现并加载。

## API接口文档

### 扫描相关

#### POST /scan/start
启动扫描任务

请求体：
```json
{
  "target_url": "https://example.com",
  "scan_types": ["basic", "deep", "api"],
  "max_concurrency": 10,
  "rate_limit": 50
}
```

响应：
```json
{
  "scan_id": "SCAN-1234567890",
  "message": "扫描任务已创建",
  "status": "pending"
}
```

#### GET /scan/{scan_id}/status
获取扫描任务状态

#### POST /scan/{scan_id}/stop
停止扫描任务

#### GET /scan/history
获取扫描历史列表

### 报告相关

#### GET /report/{scan_id}
获取扫描报告

#### POST /report/generate
生成扫描报告

#### GET /report/list
列出所有报告

## 代码规范

### Python

- 使用 Black 格式化代码
- 使用 Flake8 检查代码风格
- 遵循 PEP 8 规范
- 函数和类需要添加文档字符串

### JavaScript/Vue

- 使用 ESLint 检查代码
- 使用 Prettier 格式化代码
- 组件命名使用 PascalCase
- 变量命名使用 camelCase

### 提交规范

- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 重构
- test: 测试相关
- chore: 构建/工具链相关
