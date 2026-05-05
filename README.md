# Code Review / Tech Debt Governance Agent MVP

这是一个可直接运行的代码评审 / 技术债治理 Agent MVP，包含：

- FastAPI 后端 API
- React 前端控制台
- 多 Agent 协同流程
- 内置任务队列
- SQLite 数据库
- 飞书 Webhook 通知占位
- 任务创建、运行、报告生成完整链路

## 1. 项目解决的核心痛点

研发团队在代码评审和技术债治理中经常遇到这些问题：

1. 代码规范依赖人工 Review，效率低且容易遗漏。
2. 技术债分散在历史代码中，缺少持续扫描机制。
3. 安全风险、坏味道、可维护性问题缺少统一分级。
4. 评审结论难以沉淀为结构化报告。
5. 研发负责人无法快速看到项目风险趋势。

这个 MVP 用 Agent 化流程把“扫描、分析、分级、建议、通知”串成闭环。

## 2. 核心逻辑流

```text
用户在前端创建任务
        ↓
FastAPI 写入 SQLite
        ↓
任务进入队列
        ↓
ScannerAgent 扫描代码文件
        ↓
TechDebtAgent 识别技术债
SecurityAgent 识别安全风险
QualityAgent 识别质量问题
        ↓
ReportAgent 汇总风险分、问题清单、修复建议
        ↓
报告写入 SQLite
        ↓
飞书通知占位输出
        ↓
前端展示报告
```

## 3. 项目结构

```text
code-review-agent-mvp/
  backend/
    app/
      agents/
        scanner_agent.py
        debt_agent.py
        security_agent.py
        quality_agent.py
        report_agent.py
      services/
        orchestrator.py
        queue.py
        notifier.py
      sample_repo/
        legacy_service.py
      main.py
      models.py
      schemas.py
      database.py
      config.py
    requirements.txt
    .env.example
  frontend/
    src/
      main.jsx
      api.js
      styles.css
    package.json
    index.html
    .env.example
```

## 4. 后端运行

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

后端 API 文档：

```text
http://localhost:8000/docs
```

## 5. 前端运行

新开一个终端：

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

访问：

```text
http://localhost:5173
```

## 6. 快速验证

1. 启动后端。
2. 启动前端。
3. 在前端点击 `Create and Run`。
4. 默认会扫描 `backend/app/sample_repo`。
5. 等待 3 秒左右，任务状态变为 `completed`。
6. 右侧会显示风险分、问题清单和修复建议。

## 7. API 示例

创建任务：

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Scan sample repo","repo_path":"./app/sample_repo","branch":"main"}'
```

运行任务：

```bash
curl -X POST http://localhost:8000/tasks/1/run
```

查看报告：

```bash
curl http://localhost:8000/tasks/1/report
```

## 8. 飞书通知配置

当前是占位逻辑，未配置时会在后端控制台打印：

```text
[Feishu placeholder] Code Review Agent started: ...
```

接入真实飞书机器人：

1. 在飞书群创建自定义机器人。
2. 复制 Webhook URL。
3. 写入 `backend/.env`：

```env
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
```

4. 重启后端。

## 9. 后续可扩展方向

### 接 Git 平台

- GitHub / GitLab / Gitee Pull Request 扫描
- 自动评论 PR
- 自动生成修复建议
- 按模块负责人派发问题

### 接 CI/CD

- 在 CI 中运行 Agent
- 对高风险 PR 阻断合并
- 生成风险评分趋势

### 接 LLM

当前 MVP 使用规则型 Agent，便于本地运行。后续可以替换或增强为：

- LLM 代码解释 Agent
- 架构一致性 Agent
- 自动重构 PR Agent
- 单元测试生成 Agent

### 接企业协作平台

- 飞书通知
- 企业微信群通知
- 多维表格写入风险清单
- Jira / Linear 创建技术债任务

## 10. 可用于评审填写的成果描述

我构建了一个代码评审与技术债治理 Agent MVP，用于解决研发团队在历史代码治理、代码规范检查和安全风险识别中的重复劳动问题。系统由多个 Agent 协同完成：ScannerAgent 负责扫描仓库代码，TechDebtAgent 识别技术债和坏味道，SecurityAgent 识别潜在密钥泄露和危险调用，QualityAgent 分析可维护性问题，ReportAgent 汇总风险分、问题清单和修复建议。任务通过 FastAPI 创建并进入队列，结果写入 SQLite，同时预留飞书 Webhook 通知能力。当前 MVP 已支持任务创建、异步运行、报告生成和前端可视化展示，后续可接入 Git 平台、CI/CD、企业微信、飞书和多维表格，实现持续化代码治理闭环。
