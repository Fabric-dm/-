# 个人科研助手

一个基于AI的本地部署科研文档分析助手，支持PDF文档问答、相似性分析和研究建议。

## 功能特性

- 📄 PDF文档自动处理和向量化
- 💬 基于文档内容的智能问答
- 🔍 多文档相似性分析（问题、方法、思路）
- 💡 研究问题和方法的智能推荐
- 🌐 Web图形界面
- 💻 命令行界面

## 系统要求

- Python 3.8+
- 6GB+ 显存（支持量化加载）
- Windows/Linux/MacOS

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 准备文档

将PDF文档放入 `documents/` 文件夹

### 2. 命令行模式

```bash
python main.py --mode cli
```

### 3. Web界面模式

```bash
python main.py --mode web
```

然后在浏览器中访问 `http://localhost:5000`

## 项目结构

```
project/
├── app/
│   ├── core/          # 核心功能模块
│   ├── api/           # API接口
│   ├── web/           # Web界面
│   └── models/        # 模型管理
├── documents/         # PDF文档存放目录
├── main.py            # 主程序入口
├── requirements.txt   # 依赖包
└── report.md          # 项目报告
```

