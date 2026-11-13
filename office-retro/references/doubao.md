# 豆包 / 豆包工作 适配参考

验证环境：macOS 客户端 2.36.6，2026-11-13。Windows 与飞书内入口未验证，表中已注明。

豆包不是「一个产品两种界面」，而是两套能力面。官方口径：**工作任务模式**面向复杂工作，可自主拆分子步骤、循环调用工具与技能、操作本地电脑与浏览器、配置定时任务；**对话模式**偏一问一答，复杂任务需用户分步引导。复盘必须先认形态，再谈落点。

| | 豆包工作（工作任务模式） | 豆包（对话模式） |
|---|---|---|
| 入口 | 独立豆包工作客户端 / 豆包客户端「新工作任务」/ 飞书内入口 | 豆包客户端或网页版普通对话 |
| 能否读本地文件 | 能（本地电脑模式） | 不能 |
| 技能 | 有（内置 + 企业 + 个人） | 无 |
| 定时任务 | 有（云端 / 本地） | 无 |
| 复盘深度 | 读证据、改文件、建任务、回读验证 | 给候选清单 + 手动步骤 |

## 形态 A：豆包工作（工作模式）

### 安装 office-retro

三条入口，优先级从高到低：

1. **设置页上传（推荐，官方路径）**：客户端左侧「插件·技能·伙伴」→「技能」→ 右上角「＋ 添加」→「上传技能」，选含 `SKILL.md` 的技能文件夹。SKILL.md 开头必须是 YAML，至少含 `name` 与 `description`。装完后在对话框输入 `/` 或 `@` 搜索调用，也可直接描述需求让平台匹配。
2. **目录投放（本机即生效）**：复制到
   `~/Library/Application Support/Doubao/Default/.doubao/agent_mode/workspace/.user_skills/office-retro/`
   重启客户端或下一轮会话加载。官方文档点名 `user_skills` 目录：本地技能与云电脑技能不互通，但 **user_skills 与技能商店上传的技能不受影响**，两边都在。
3. **对话新建 / 迁移导入**：「与豆包对话新建技能」可描述触发场景与执行指令；设置 →「数据导入与同步」能从 ChatGPT、Claude Code、Trae Work、Coze 等产品导入技能、连接器与工作记忆。

不要投 `.../workspace/.skills/`：那是应用内置技能目录（本机 44 个）。这些目录的 mtime 与安装时间不同步（多数是 2026-10-23 客户端落盘时写入，`word` 是 2026-11-11），说明它由应用维护、会随版本变化；自定义技能放这里有被覆盖的风险，也不用它做投放位。

本机另有 `~/Doubao/skills`、`~/.agents/skills` 被声明为技能发现根，但两处内容没有出现在当前会话的已加载清单里。需要「确定生效」时，只用上面前两条路径，并在复盘里区分「已加载」与「目录存在」。

### 常驻指令 = 工作任务偏好指令

设置 →「工作模式设置」→「个性化」→「工作任务偏好指令」，上限 **10,000 字符**，发起工作任务时默认注入。官方示例覆盖输出语言、行文风格、交付格式、需要规避的表述、常用数据口径。

这是豆包工作里唯一等价于 AGENTS/MEMORY 的常驻区，复盘「记忆与常驻指令」类目时它就是预算上限：红线、导航指针、稳定口径写这里；流程步骤、模板、校验方法下沉到 Skill，别把 10,000 字符当免费空间。

### 记忆分五层，别混为一谈

| 层 | 位置 / 入口 | 写什么 | 复盘看点 |
|---|---|---|---|
| 偏好指令 | 设置 → 工作模式设置 → 个性化 → 工作任务偏好指令 | 稳定口径、红线、导航 | 是否膨胀、失效、互相矛盾 |
| 记忆 | 设置 → 记忆 | 用户要求记住的信息 + 自动提取 | 旧口径、过期项目信息是否还活着 |
| 工作记忆 | 设置 → 工作模式设置 → 个性化 → 工作记忆（开关） | 工作任务侧跨会话记忆 | 与「记忆」层是否各说一套 |
| 会话记忆 | `.sessions/<sessionId>/memory/MEMORY.md` | harness 维护，按会话 | 本机实测为空文件，别假设有内容 |
| 经验 | `.../workspace/experience/<slug>.md`（front matter `type: work_experience`、`source: harness`） | 按场景组织的踩坑经验 | 是否重复、是否与当前环境不一致 |

Agent 侧还有读写工具：`manage_preference`（长期偏好）、`search_memory`（偏好 / 任务史 / 每日记忆）。复盘时这五层要分别取证，任何一层被当成另一层的现状都会写错候选。

### 一手材料（本机验证）

工作区根：`~/Library/Application Support/Doubao/Default/.doubao/agent_mode/workspace/`（下称 `<WS>`）。

- 会话轨迹 `<WS>/.sessions/<sessionId>/agents/<agentId>/system/trajectory.jsonl`：逐行 JSON，含 role、content、tool_calls（含工具名与参数）。这是复盘的主证据源。
- 工具输出落盘 `<WS>/.sessions/<sessionId>/agents/<agentId>/system/tool-results/<tool>_<sha12>.txt`：单次输出过大时溢出到此。
- 后台命令 `<WS>/conversation/<sessionId>/background_history_task/index.json`：command、exitCode、status、输出文件；正文在 `outputs/<uuid>.output`。命令失败与否不用猜，看 exitCode。
- 多 Agent `<WS>/.sessions/<sessionId>/board.md`：任务公告板，含任务 ID、标题、Organizer、状态、产物路径/链接；`agents/<agentId>/system/assignment.md` 是分派单；`socket/briefing.md`、`socket/findings.jsonl` 是协作通道。
- 交付物：项目目录。本地电脑模式支持「通过本地文件夹新建项目」，项目内资料自动作为后续任务上下文。
- 跨形态 `<WS>/../` 没有对话模式的文本转录；对话模式会话要用 `im_list_conversations`（已验证可列）与 `im_get_conversation_messages` / `im_search_message` 读。

### 定时任务

先读 `doubao-cron-scheduler` 技能，再用 `create_cron_job` / `update_cron_job` / `delete_cron_job` / `get_cron_job` / `list_cron_jobs`。

- `runtime_type`：`1` 云端（默认）、`2` 本地。只有任务依赖本地文件、路径、应用、设备时才选本地；「当前对话在本地模式」不构成理由。
- 云端沙箱闲置一段时间自动销毁，装过的 npm 包、CLI 会丢，且与本地环境隔离（`user_skills` 与商店技能除外）。
- 因此云端 cron 的 payload 必须自包含：模板全文、输出目录、上下文一起带上；依赖本地脚本或本地登录态的任务只能走本地。
- 含人工确认的流程不要写成「等用户回复再继续」——每次触发是独立会话，改写成「先产出、再通知」或拆成两个任务。

### 门禁与权限

客户端未提供 Claude Code 式 hooks 配置面（本机 `Default` 下只找到 `cloud_config.json` 等少量配置，未见 settings/hooks 文件）。可用的确定性手段只有三种：

1. Skill 内脚本（`scripts/` + `metadata.requires.bins` 声明依赖）。
2. 交付后回读（写完文档 / 表格 / 页面，读回来核对关键字段与数字）。
3. 定时任务里的周期性校验（如每日核对台账与产物一致性）。

本地电脑模式的「按需确认 / 始终询问 / 全部允许」是操作前的粗粒度闸门，不是交付物校验，别把它算作门禁。

### 运行位置决定你能看见什么

- 本地电脑：能读本地磁盘、跑代码、用本机已装工具与技能；需要开机且客户端运行。
- 云电脑：不开机也能跑，但沙箱闲置销毁，技能与本地不互通。
- 复盘含义：轨迹、交付物、`experience/` 都在本地侧。在云电脑里复盘一次本地会话，只能看到对话上下文，看不到 `<WS>/.sessions` 的旧轨迹——这种情况要在报告里写明「需要切到本地侧复跑」，不要写成「该类目无发现」。

### 豆包工作特有的复盘检查项

- 技能是不是「装了但没被匹配到」：description 是否缺少触发场景词；`disable-model-invocation` 在本产品不保证生效（内置 44 个技能无一使用该字段），只靠用户主动触发时要在 description 写死「仅当用户说 X 时使用」。
- 长任务是否把半成品留在项目目录却没人回收；`board.md` 里状态是否停在「进行中」而成果已交付。
- 云端任务是否偷偷依赖了本地技能或本地路径（跑一次不带本地的环境即可验证）。
- 偏好指令是否重复了 Skill 正文（同一含义两个权威位置，改一处必漏一处）。

## 形态 B：豆包（对话模式）

对话模式没有技能目录、没有文件、没有工具、没有定时任务。可承诺的只有三件事：

1. 对本次对话做七类目复盘，输出候选清单，每条带引文证据（用户原话 / 模型原话）。
2. 把可复用的稳定信息压成一两句，由用户手动存进 设置 → 记忆。
3. 需要固化的流程，建议切到工作模式：用「与豆包对话新建技能」或上传 SKILL.md。

硬约束，写报告时要守住：

- 官方 FAQ 明确：豆包暂不支持查询历史对话原文。不要承诺「我查了你上周那次会话」；用户没贴的历史，一律视为不可得。
- 记忆是概率性的（动态提炼、非逐字保存、可能记错、更新有延迟）。它是上下文线索，不是确定性门禁，也不是项目台账。
- 关闭记忆开关不会删除已存记忆；删聊天记录也不等于删记忆。复盘里要区分「开关状态」与「内容是否清空」。
- 落地动作只能写成「你要做的动作」，不能写成「我已改好」。

对话模式下可粘贴的最小指令（七类目里只有四类真有落点，剩下三类写「本形态不适用」）：

```text
对本轮对话做一次复盘，只依据本轮真实出现的内容，不要补写我没说的历史。
逐项检查：常驻指令与记忆 / 信息获取 / 导航 / 可固化成技能的流程；其余类目写「本形态不适用」。
每条发现附一句对话原文作为证据，并说明它造成的具体损耗（返工、来回确认、答错）。
按「阻断 > 重复损耗 > 隐患」排序，每条给我下一步动作：存进设置-记忆、改偏好指令、还是去豆包工作建技能。
不要声称你已改动任何设置或文件。
```

## 未验证与待补

- Windows 下 `%APPDATA%\Doubao\...` 的对应路径未验证，按 macOS 的 `Default\.doubao\agent_mode\workspace\` 结构现场探测，确认前不要写进适配表。
- 飞书内入口的功能面与客户端是否一致，未验证（官方说明「不同入口支持的功能与体验可能有所不同」）。
- `.user_skills` 投放后是否「重启即加载」未做隔离实验；本机该目录为空，当前会话未加载任何来自它的技能。
- `im_get_conversation_messages` / `im_search_message` 的正文读取效果未逐条验证，仅验证了 `im_list_conversations` 能列对话模式会话。

## 验证来源

- 豆包工作帮助中心《使用技能》：https://www.doubao.com/work/docs/zh-cn/articles/081010973544-skills
- 豆包工作帮助中心《使用工作任务模式》：https://www.doubao.com/work/docs/zh-cn/articles/047323472965-work-task-mode
- 豆包工作帮助中心《设置豆包工作客户端》：https://www.doubao.com/work/docs/zh-cn/articles/223261648434-configure-app
- 豆包工作帮助中心《打开豆包工作》：https://www.doubao.com/work/docs/zh-cn/articles/462191106451-access
- 豆包《记忆功能 FAQ》：https://www.doubao.com/legal/memory_faq
- 本机文件系统核对：`<WS>/.skills`（44 项）、`<WS>/.user_skills`（空）、`.sessions` 结构、`conversation/<id>/background_history_task/index.json`、`board.md`、`experience/*.md`。
