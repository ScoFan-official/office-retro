# WorkBuddy 适配细节（office-retro v2.3.0）

验证日期 2026-11-13，macOS 客户端本机实测 + 官方文档。云端定时任务、Windows / Linux 路径、企业空间的验证范围另记。

## 证据来源

- [Overview](https://www.workbuddy.cn/docs/workbuddy/Overview)
- [Task-Bar](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Task-Bar) — 工作模式 Agent / Plan / Ask、斜杠命令补全（项目级 `.codebuddy/commands/`）、权限管理
- [Skills-Market](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market) — 上传技能、启用 / 关闭开关、开关状态记录在用户全局配置
- [Memory](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Memory) — 产品记忆每晚更新、设置 → 记忆可管理、支持历史会话检索
- [Connector](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Connector) — 授权失效重连、同一步骤自动重试一次、自定义连接器
- [Automation-Guide](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Automation-Guide) — 定时任务 / 运行记录两标签、配置项、失败原因、执行权限
- [Permission-Modes](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Permission-Modes) — 默认权限 / 完全访问权限、安全中心工具管控
- [Results](https://www.workbuddy.cn/docs/workbuddy/Results) — 产物 / 网页 / 工作空间文件 / 变更四视图

## 环境入口

| 入口 | 位置 |
|---|---|
| 意识文件 | `~/.workbuddy/user-*-personal/{SOUL,IDENTITY,USER,MEMORY}.md` 随会话注入；另有 `~/.workbuddy/MEMORY.md` |
| 技能目录 | `~/.workbuddy/skills/`（用户级）、`<工作区>/.workbuddy/skills/`（项目级）；启用开关在 `~/.workbuddy/settings.json` 的 `skillOverrides` |
| 记忆 | 产品记忆「设置 → 记忆」；本地三层：云端长期画像注入、用户级 MEMORY.md、工作区 `.workbuddy/memory/` 日志与 MEMORY.md；历史会话检索 |
| 定时任务 | 左侧「定时任务」页面，含「定时任务」/「运行记录」；配置含名称、提示词、模型·专家·技能·连接器、工作空间、权限、重复、时间、有效期、推送 |
| 连接器与 MCP | 状态随会话注入；`~/.workbuddy/mcp.json` 为 `mcpServers` / `disabledMcpServers` 双层结构；自定义 MCP 新增后需在自定义连接器入口点「信任」 |
| hooks | `~/.workbuddy/settings.json` 的 `hooks.UserPromptSubmit` 可在每轮注入上下文 |
| 结果区 | 右侧「产物 / 网页 / 工作空间文件 / 变更」四视图 |

`~` 指用户主目录；`~/.workbuddy` 根路径可用 `WORKBUDDY_HOME` 覆盖。

## 复盘步骤 1 的一手材料

| 材料 | 路径 | 用途 |
|---|---|---|
| 会话记录 | `~/.workbuddy/projects/<编码工作区>/<uuid>.jsonl` | 逐条消息；记录含 `type` / `id` / `sessionId` / `timestamp` / `meta` |
| 运行日志 | `~/.workbuddy/logs/YYYY-MM-DD/*.log` | 按天定位，文件名含工作区名 |
| 追踪 | `~/.workbuddy/traces/<id>/trace_*.jsonl` | 调用链与耗时 |
| 审计 | `~/.workbuddy/audit-log/YYYY-MM-DD.jsonl` | 事件哈希链 |
| 任务清单 | `~/.workbuddy/tasks/<uuid>/*.json` | `subject` / `status` / `owner` / 时间戳 |
| 会话元数据 | `~/.workbuddy/sessions/*.json` | `pid` / `cwd` / `mode` / `startedAt` |
| 回滚记录 | `~/.workbuddy/projects/*/*.file-rollback.ndjson` | 自动备份与回退 |
| 交付物与改动 | 结果区「产物 / 变更」视图 | 执行后回读验证 |

## 七类目专属检查点

1. **确定性门禁**：`workbuddy_env_probe.py --strict` 可作环境门禁；交付链路回读走结果区「变更」视图与产物卡片；机械校验落成脚本挂进 Skill。
2. **Skill 覆盖与质量**：在「专家·技能·连接器 → 技能 → 已安装」确认本技能处于启用状态；开关记录在 `settings.json` 的 `skillOverrides`，关闭的技能在新会话停止参与调用，`SKILL.md` 原文保持不变；`disable-model-invocation: true` 在本机应用包内命中该字段名、24 个已装 Skill 使用该字段（2026-11-13 实测）；斜杠命令补全读取项目 `.codebuddy/commands/`。
3. **记忆与常驻指令**：区分产品记忆（每晚从会话提取，可查看 / 编辑 / 删除 / 关闭，依赖前先核验）与本地三层文件；常驻文件逐句做 no-op 测试，并检查记忆层之间的口径冲突。
4. **连接器与工具**：会话注入的连接器状态块标出 connected / disabled；授权失效由「重新连接」卡片处理，同一步骤自动重试一次；安全中心「工具管控」按 MCP 服务或工具粒度启停。
5. **定时任务与自动化**：「运行记录」按成功 / 失败 / 运行中筛选，失败原因含连接器未授权、登录失效、离线错过、模型排队重试耗尽；核对提示词自包含（云端任务在云端沙箱运行，本地任务显式指定工作空间）、工作空间、有效期、权限（默认权限下无人值守会停在等待确认）、模型与技能随任务保存；新建后先用「立即运行」试跑。
6. **信息获取**：优先上表路径与结果区四视图；`hooks.UserPromptSubmit` 每轮注入上下文；历史会话用产品记忆的检索通道。
7. **导航**：适配表 + 探测脚本输出即权威导航；官方文档链接作为争议时的裁决位置。

## 探测脚本

`scripts/workbuddy_env_probe.py` 为只读探测，输出路径、计数、时间戳与结构元信息，凭据字段值留在配置文件内；共 20 项检查，`--strict` 在存在 MISSING 项时返回退出码 1。

```bash
cd ~/.workbuddy/skills/office-retro
python3 scripts/workbuddy_env_probe.py             # Markdown 证据表
python3 scripts/workbuddy_env_probe.py --json      # 结构化输出
python3 scripts/workbuddy_env_probe.py --strict    # 环境门禁
python3 scripts/workbuddy_env_probe.py --workspace /path/to/ws
```

`WORKBUDDY_HOME`、`WORKBUDDY_WORKSPACE` 覆盖默认路径；在复盘的目标工作区运行，或用 `--workspace` 指定。定时任务配置内容由界面与运行记录查看，脚本只提示入口。
