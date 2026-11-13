# office-retro

办公类 AI agent 的会话复盘 Skill。适用于豆包工作、千问办公（QwenWork）、WorkBuddy、Trae、ChatGPT work、Qoder 等办公 agent。

对一次办公会话做复盘：从**确定性门禁、Skill 覆盖、记忆与常驻指令、连接器与工具、定时任务、信息获取、导航**七个类目中找环境改进候选，按严重度呈现，用户逐项确认后才落地。每条候选必须可溯源到具体证据。

改编自 Matt Pocock 的编码版 [retro](https://github.com/mattpocock/skills)，把面向代码仓库的类目（linter / CI / reviewer）替换为办公场景的落点（常驻指令 / Skill / 校验脚本 / 定时任务）。

## 安装

把 `office-retro/` 目录（含 `SKILL.md`；`references/` 为按需读取的适配细节）复制到目标产品的技能目录，或在有技能商店/上传入口的产品里直接上传：

| 产品 | 技能目录 / 入口 | 验证状态 |
|---|---|---|
| 千问办公 QwenWork | `~/.qwenworkcn/skills/` | 已验证 |
| WorkBuddy | `~/.workbuddy/skills/`（用户级）、`<工作区>/.workbuddy/skills/`（项目级）；或「专家·技能·连接器 → 技能 → 添加技能 → 上传技能」 | 已验证（2026-11-13，macOS 客户端） |
| Qoder CN（Desktop/IDE/CLI） | `~/.qoder-cn/skills/` | 已验证 |
| 豆包工作（工作任务模式） | 设置页「插件·技能·伙伴 → 技能 → ＋ 添加 → 上传技能」；或投放到 `~/Library/Application Support/Doubao/Default/.doubao/agent_mode/workspace/.user_skills/` | 已验证（2026-11-13，macOS 2.36.6） |
| 豆包（对话模式） | 不加载技能目录，用法见下节 | 不适用 |
| Trae / ChatGPT work 等 | 见产品设置/帮助 | 待验证 |

```bash
git clone https://github.com/ScoFan-official/office-retro.git
cp -r office-retro/office-retro ~/.qwenworkcn/skills/   # 以千问办公为例：目录投放
cp -r office-retro/office-retro ~/.workbuddy/skills/    # WorkBuddy 用户级
```

豆包工作更推荐走设置页上传：平台会记住调用参数，且上传的技能与 `user_skills` 目录在本地电脑和云电脑两侧都可用。不要投进 `.../workspace/.skills/`——那是应用内置技能目录，由应用维护、会随客户端版本变化。

部分产品需要重启或下一轮会话才能加载新技能。

## 豆包 / 豆包工作：两种模式分开用

豆包不是一个产品两种界面：**豆包工作**是 Agent 形态（有文件、技能、工具、定时任务），**豆包**普通对话是纯对话形态。同一个 Skill 在两边能做的事不同，别用同一套话术。

### 豆包工作（工作任务模式）：能读证据、能落地

- 唤起：对话框输入 `/` 或 `@` 搜 `office-retro`，或直接说「复盘这次会话」。
- 能做什么：读本机会话轨迹、后台命令 exitCode、任务公告板、子 Agent 分派单与交付物；可直接改 Skill 文件、建/改定时任务、写完回读验证。
- 常驻预算：设置 → 工作模式设置 → 个性化 → **工作任务偏好指令**（≤10,000 字符），这是复盘「常驻区是否膨胀」的硬上限。
- 必须在**本地电脑**侧跑：轨迹与交付物都在本地；云电脑沙箱看不到，也不继承本地技能（`user_skills` 与技能商店技能除外）。
- 跨形态：需要复盘对话模式的豆包会话时，工作模式下可用 `im_*` 工具列出并读取这些会话。

### 豆包（对话模式）：只能给清单和手动步骤

- 没有技能目录、文件、工具、定时任务，SKILL.md 装不进去。用法是把 `references/doubao.md` 里的「对话模式最小指令」粘进对话（或把 `SKILL.md` 步骤 0–4 压成一段指令），让豆包只按本轮可见内容复盘。
- 产出只能是：候选清单（每条带对话里的引文证据）+ 你要做的动作（存进 设置 → 记忆、去工作模式建技能、改哪设置项）。不能声称已改文件或已建任务。
- 官方不支持查询历史对话原文，别承诺「我查了你上次那次」；用户没贴的历史视为不可得。
- 记忆是概率性的（动态提炼、可能记错、更新有延迟），只能当线索，不能当门禁。
- 有值得固化的流程时，切到豆包工作用「与豆包对话新建技能」或上传 SKILL.md，那里才是流程的家。

细节（安装三条入口、记忆五层、定时任务云端/本地口径、门禁与权限、运行位置差异、未验证项）见 [`office-retro/references/doubao.md`](office-retro/references/doubao.md)。

## WorkBuddy 适配（v2.3.0）

- 安装后到「专家·技能·连接器 → 技能 → 已安装」确认开关为启用；关闭的技能在新会话停止参与调用，开关状态记录在 `~/.workbuddy/settings.json` 的 `skillOverrides`。
- 复盘时先跑只读环境探测，输出作为入口证据：

```bash
cd ~/.workbuddy/skills/office-retro
python3 scripts/workbuddy_env_probe.py             # Markdown 证据表
python3 scripts/workbuddy_env_probe.py --json      # 结构化输出
python3 scripts/workbuddy_env_probe.py --strict    # 存在缺失项时退出码 1
```

`WORKBUDDY_HOME`、`WORKBUDDY_WORKSPACE` 覆盖默认路径；在复盘的目标工作区运行，或用 `--workspace` 指定。
- 建议 Plan 模式 + 默认权限承载逐项确认，改动落地后用结果区「变更」回读；定时任务类候选以「定时任务 → 运行记录」的失败原因为证据。
- 官方依据：[技能](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)、[记忆](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Memory)、[连接器](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Connector)、[定时任务](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Automation-Guide)、[工作模式与权限](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Task-Bar)、[结果查看](https://www.workbuddy.cn/docs/workbuddy/Results)。环境入口、一手材料与七类目检查点见 [`office-retro/references/workbuddy.md`](office-retro/references/workbuddy.md)。

## 使用

对 agent 说「复盘」「retro」或调用 `/office-retro`（仅用户主动触发，模型不会自行发起；不支持该字段的产品靠 description 措辞兜底）。可指定复盘某次历史会话，不指定则默认当前会话。

产出流程：

1. 判定形态（工作模式 / 对话模式），并说明本次能做到的深度。
2. 读一手材料（会话记录、运行日志、交付物、常驻指令与记忆），每条候选附证据。
3. 按环境适配表确认当前产品的配置入口与运行位置（本地 / 云）；WorkBuddy 上先跑 `scripts/workbuddy_env_probe.py`，用输出作为入口证据。
4. 七类目逐一检查，无发现的类目写「无」。
5. 按严重度排序呈现候选，用户逐项拍板后执行，执行后回读验证；对话模式下改为给出可执行的手动步骤。
6. 自我改进检查：区分**通用能力改进**与**专属适配改进**，经确认后修订本 Skill 并递增版本号。

## 贡献

在任意办公 agent 里跑一次复盘，按 SKILL.md 步骤 5 产出改进：

- **通用能力改进**：类目、步骤、门禁方法，对所有产品生效。
- **专属适配改进**：环境适配表新增/修正一行，只对该产品生效。同一产品分形态时拆成两行，不合成一行。适配表禁止写入未验证的猜测路径；验证后更新并注明日期与验证范围（哪一侧验过）。WorkBuddy 的检查点与 `scripts/workbuddy_env_probe.py` 同步核对。

提 PR 时请附：改进类别、触发它的会话证据、在哪个产品（哪一侧环境）上验证过。

## 版本

- 2.3.0：补全 WorkBuddy 适配。环境适配表对应行由「待验证」改为官方文档 8 页 + macOS 客户端实测的入口清单；新增 `references/workbuddy.md`（证据来源、一手材料、七类目检查点）与只读探测脚本 `scripts/workbuddy_env_probe.py`；复盘流程补上 WorkBuddy 的环境探测、七类目复核，以及 Plan 模式 + 默认权限 + 结果区「变更」回读。保留 v2.1.0 Qoder CN 与 v2.2.0 豆包双形态改动。
- 2.2.0：豆包 / 豆包工作拆成两行适配（工作模式四类入口本机验证，对话模式写明约束面）；新增 `references/doubao.md` 与 README「两种模式分开用」；复盘流程加「判定运行形态」一步，候选落地区分「已执行」与「手动步骤」；记录豆包工作的常驻预算（偏好指令 10,000 字符）、记忆五层、本地/云隔离与无 hooks 面。
- 2.1.0：新增 Qoder CN 适配行（意识文件/技能目录/记忆/定时任务四类入口本机验证），补充会话记录位置、hooks/MCP 配置面与 qoder_cron 要点。
- 2.0.0：办公版首发。七类目办公化，新增环境适配表与自我改进路线。
