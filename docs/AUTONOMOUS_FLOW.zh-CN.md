# Venture Lab 自动化交付流程

**中文** | [English](AUTONOMOUS_FLOW.md)

> 本文描述当前真实运行的自动化工程控制平面。GitHub Issue 是工作合同；产品仓库负责产品代码与平台 CI；Venture Lab 负责调度、独立 Review、QA、风险门禁和必要的人类升级。

## 1. 这套系统是什么

Venture Lab 是 **control plane（控制平面）**，不是产品代码仓库。

```text
BUILD-ready 计划 → GitHub Issue → Agent Orchestrator
                                   ├─ ready Issue → Builder → PR
                                   └─ 已有 PR → Review Cycle
PR → 产品仓库 CI → Reviewer
                    ├─ 要修改 → Fixer → 新 HEAD → 重新 CI/Review
                    └─ 通过 → QA → Risk Gate
                                   ├─ 常规低风险 → Auto-merge
                                   └─ 敏感/有歧义 → Product Owner → 再继续
```

最重要的边界是 **调度 ≠ 验证证据**。Venture Lab 决定下一步由谁做什么；目标产品仓库及其 CI 提供平台相关的真实证据。例如 AniDream 的 macOS/Xcode workflow 才是 iOS 测试的权威证据，Linux Reviewer/Fixer 不应该假装自己跑过 Xcode。

## 2. 系统里的真相源

### GitHub Issue = Implementation Contract
Builder 只根据 dependency-ready Issue 和 acceptance criteria 工作，做满足合同的最小实现，不能自己扩大产品范围。

### Pull Request = Review Unit
Reviewer 和 QA 审的是**精确 PR HEAD**。Fixer push 新 commit 后，旧 evidence 过期，新 HEAD 必须重新验证。

### 产品仓库 CI = Platform Evidence
build、test、lint、simulator/device 等平台验证属于产品 repo。Venture Lab 读取结果，而不是伪造环境。

### Agent Contract = AI 的职责边界
- `agents/builder.md`：实现 Issue。
- `agents/reviewer.md`：独立检查正确性和 scope，不改代码。
- `agents/fixer.md`：只修 Reviewer/QA 给出的 blocker。
- `agents/qa.md`：独立验证 acceptance criteria 和测试。
- `agents/handoff.md`：真的需要人判断时，翻译成 Product Owner 能回答的问题。

## 3. GitHub Actions 怎么互相交互

### Agent Orchestrator — `.github/workflows/orchestrator.yml`
Orchestrator 刷新 portfolio state，再让 `scripts/orchestrate.py` 判断下一步。它可以：启动 dependency-ready Issue 的 Builder；已有 managed PR 时唤醒 Review Cycle；Builder 连续失败时 Auto-stop；没有 ready work 时保持 idle。

Build 时会 checkout 产品 repo、建立 `agent/issue-<n>`、运行 Builder、保存 checkpoint、commit、创建 PR，然后 dispatch Review Cycle 和 Dashboard refresh。

### 产品仓库自己的 CI
PR 创建/更新后，产品 repo 自己的 Actions 开始跑。结果绑定精确 commit SHA，随后成为 Reviewer/QA 的证据。

### Agent Review Cycle — `.github/workflows/review-cycle.yml`

**Reviewer** 读取 Issue、PR、diff、架构和当前 HEAD 的 CI evidence，输出 `approve` 或 `request_changes`。只有真正的产品意图不明确才升级给人。

**Fixer Loop** 在 blocker 明确且不需要产品决策时自动接手，只修 finding 并 push 新 commit。新 HEAD 必须重新 CI + Review。macOS/Xcode 之类 Linux 没有的执行环境应该交给 platform CI，而不是让 Fixer 无限重试。

**QA** 在 Reviewer approve 后运行，验证 acceptance criteria 和相关测试。精确 HEAD 上成功的 platform CI 可以作为权威证据。

**Risk Gate** 在 Reviewer approve + QA pass 后判断 merge eligibility。常规低风险 change 可以自动 merge；workflow/control-plane、secrets、payment/billing、production release、database/schema migration、entitlement、privacy、legal/terms 等继续 human gate。

**Product Owner Handoff** 是 exception path，不是每个 PR 的审批机器。它应该问产品/UX/风险判断，而不是让 Product Owner 看代码。Decision 后自动流程继续。

**Auto-merge** 在 merge 前再次核对 HEAD；HEAD 变了就拒绝。符合条件则 squash merge 并删除 branch。

## 4. 辅助 Actions

- **Agent Runtime Guard**：限制不健康的自动修复循环，防止 runaway automation。
- **Scope Gate Shadow**：分析 ready Issue 是否足够小、清晰；目前只观察，不 block。
- **Portfolio Dashboard / Checkpoint Dashboard Refresh**：展示状态和 Builder checkpoint；Dashboard 是 observability，不是真相源。

## 5. 必须保持的规则

1. GitHub 是 system of record。
2. Issue 定义 scope；Agent 不能发明产品需求。
3. Reviewer 独立于 Builder。
4. Reviewer approve 后才进入 QA。
5. Evidence 绑定精确 commit SHA。
6. HEAD 变化后旧 approval/evidence 作废。
7. Required CI 真失败 = blocker；Linux 没有平台工具 ≠ 测试失败。
8. Fixer 只修 finding，不扩大 scope。
9. Human escalation 用于真正判断、风险或无法自动完成的外部验证，不用于日常批准。
10. Reviewer + QA + risk policy 都通过才允许 auto-merge。
11. 自动化连续失败必须停止，不能无限循环。

## 6. 正常生命周期

```text
Issue ready → Orchestrator → Builder → PR → 产品 CI → Reviewer
→ [Fixer → 新 HEAD → CI → Reviewer]（需要时循环）
→ Reviewer approve → QA → Risk Gate
→ Auto-merge 或 Product Owner 决策 → merge
→ dependency graph 暴露下一个 ready Issue → Orchestrator 继续
```

## 7. 以后升级流程，文档如何保持同步

采用**两个文件**，而不是一个 Markdown 里切换语言：
- `docs/AUTONOMOUS_FLOW.md` — English
- `docs/AUTONOMOUS_FLOW.zh-CN.md` — 简体中文

两份文件结构一致、顶部互相跳转。

仓库增加 **Documentation Guard**：只要核心 orchestration workflow 或 agent contract 被修改，同一个 change 就必须同步更新**两份**文档，否则 CI fail。

这里故意不让 AI 事后“猜”文档应该怎么变。谁修改 process，谁就在同一个 change 更新对应文档；Agent 可以代写，但 process 与 docs 一起接受 review。这样 Builder、Reviewer、Fixer、QA、human gate、auto-merge 或 orchestration 升级后，文档不会静默过期。

## 8. Source of Truth 对照

| 内容 | 真相源 |
|---|---|
| 产品/实施要求 | 产品 repo GitHub Issue |
| 当前实现 | PR 精确 HEAD |
| 平台 build/test 证据 | 产品 repo Actions/checks |
| 调度与 Builder | `.github/workflows/orchestrator.yml` + `scripts/orchestrate.py` |
| Review/Fix/QA/Merge 状态机 | `.github/workflows/review-cycle.yml` |
| Agent 职责 | `agents/*.md` |
| Portfolio 展示 | 自动生成 dashboard |
| 架构说明 | `docs/AUTONOMOUS_FLOW*.md` |
