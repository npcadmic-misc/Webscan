# Web漏洞扫描系统

一个功能完整的Web应用程序漏洞扫描系统，支持基础扫描、深度扫描和API扫描。

## 功能特性

- **多种扫描类型**：OWASP Top 10、越权访问、业务逻辑漏洞、API安全
- **双界面支持**：CLI命令行界面 + Web图形界面
- **灵活认证**：支持Cookie/Token手动配置，多角色切换
- **报告生成**：HTML和Markdown格式可选
- **插件系统**：支持自定义扫描模块和规则
- **完整审计**：操作日志、扫描历史、漏洞去重

## 技术栈

- **后端**：Python + FastAPI
- **前端**：Vue.js + Node.js
- **数据库**：本地文件系统（JSON）

## 快速开始

### 🚀 一键启动（推荐）

**Windows用户：**

1. **环境检测**：双击运行 `check_env.bat` 检查系统环境
2. **启动系统**：双击运行 `启动系统.bat` 打开启动管理器

启动管理器提供5个选项：
- **[1]** 仅启动后端 (FastAPI)
- **[2]** 仅启动前端 (Vue开发服务器)
- **[3]** 同时启动后端和前端 ⭐推荐
- **[4]** CLI模式扫描
- **[5]** 检查服务状态

### 环境要求

- Python 3.8+
- Node.js 16+
- Windows

### 手动安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd ./
```

#### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 3. 安装前端依赖

```bash
cd frontend
npm install
```

#### 4. 启动服务

**启动后端：**
```bash
cd backend
python -m app.main
```

**启动前端开发服务器：**
```bash
cd frontend
npm run dev
```

**或使用CLI模式：**
```bash
cd backend
python cli.py
```

## 项目结构

```
/
├── backend/              # Python后端
│   ├── app/             # 应用代码
│   │   ├── main.py      # FastAPI入口
│   │   ├── scanner/     # 扫描引擎
│   │   ├── detectors/   # 漏洞检测模块
│   │   ├── reporters/   # 报告生成器
│   │   └── ...
│   ├── tests/           # 测试文件
│   └── requirements.txt # Python依赖
├── frontend/            # Vue前端
│   ├── src/            # 源代码
│   ├── public/         # 静态资源
│   └── package.json    # Node依赖
├── config/             # 配置文件
├── plugins/            # 插件目录
├── data/               # 数据目录
│   ├── reports/        # 扫描报告
│   ├── history/        # 扫描历史
│   └── logs/           # 日志文件
├── docs/               # 文档
└── examples/           # 示例配置
```

## 使用文档

- [用户手册](docs/user-guide.md)
- [API文档](http://localhost:8000/docs)
- [开发者文档](docs/developer-guide.md)

## 许可证

MIT License
