# office-retro

办公类 AI agent 的会话复盘 Skill。适用于千问办公（QwenWork）、豆包工作、WorkBuddy、Trae、ChatGPT work、Qoder 等办公 agent。

对一次办公会话做复盘：从**记忆、Skill、确定性门禁、连接器与工具、定时任务、信息获取、导航**七个类目中找环境改进候选，按严重度呈现，用户逐项确认后才落地。每条候选必须可溯源到具体证据。

改编自 Matt Pocock 的编码版 [retro](https://github.com/mattpocock/skills)，把面向代码仓库的类目（linter / CI / reviewer）替换为办公场景的落点（意识文件 / Skill / 校验脚本 / 定时任务）。

## 安装

把 `office-retro/` 目录（含 `SKILL.md`）复制到目标产品的技能目录：

| 产品 | 技能目录 | 验证状态 |
|---|---|---|
| 千问办公 QwenWork | `~/.qwenworkcn/skills/` | 已验证 |
| WorkBuddy | `~/.workbuddy/skills/` | 已验证 |
| Qoder CN（Desktop/IDE/CLI） | `~/.qoder-cn/skills/` | 已验证 |
| Trae / 豆包工作 / ChatGPT work 等 | 见产品设置/帮助 | 待验证 |

```bash
git clone https://github.com/ScoFan-official/office-retro.git
cp -r office-retro/office-retro ~/.qwenworkcn/skills/   # 以千问办公为例
```

部分产品需要重启或下一轮会话才能加载新技能。

## 使用

对 agent 说「复盘」「retro」或调用 `/office-retro`（仅用户主动触发，模型不会自行发起）。可指定复盘某次历史会话，不指定则默认当前会话。

产出流程：

1. 读一手材料（会话记录、运行日志、交付物、记忆与意识文件），每条候选附证据。
2. 按环境适配表确认当前产品的配置入口。
3. 七类目逐一检查，无发现的类目写「无」。
4. 按严重度排序呈现候选，用户逐项拍板后执行，执行后回读验证。
5. 自我改进检查：区分**通用能力改进**与**专属适配改进**，经确认后修订本 Skill 并递增版本号。

## 贡献

在任意办公 agent 里跑一次复盘，按 SKILL.md 步骤 5 产出改进：

- **通用能力改进**：类目、步骤、门禁方法，对所有产品生效。
- **专属适配改进**：环境适配表新增/修正一行，只对该产品生效。适配表禁止写入未验证的猜测路径；验证后更新并注明日期。

提 PR 时请附：改进类别、触发它的会话证据、在哪个产品上验证过。

## 版本

- 2.1.0：新增 Qoder CN 适配行（意识文件/技能目录/记忆/定时任务四类入口本机验证），补充会话记录位置、hooks/MCP 配置面与 qoder_cron 要点。
- 2.0.0：办公版首发。七类目办公化，新增环境适配表与自我改进路线。