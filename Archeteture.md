# OpenClaude — Architecture Deep Dive

> **"Claude Code opened to any LLM"** — An open-source coding-agent CLI that unifies 200+ LLM providers under a single, battle-tested tool ecosystem.

---

## Table of Contents

1. [The Big Idea](#1-the-big-idea)
2. [High-Level Architecture](#2-high-level-architecture)
3. [The Tool System (42 Tools)](#3-the-tool-system-42-tools)
4. [The Task System (7 Task Types)](#4-the-task-system-7-task-types)
5. [The Provider Abstraction Layer](#5-the-provider-abstraction-layer)
6. [The Agent Loop](#6-the-agent-loop)
7. [Sub-Agents, Swarms & Teammates](#7-sub-agents-swarms--teammates)
8. [MCP — Model Context Protocol](#8-mcp--model-context-protocol)
9. [107 Slash Commands](#9-107-slash-commands)
10. [Terminal UI (React Reconciler)](#10-terminal-ui-react-reconciler)
11. [Plugin & Skill System](#11-plugin--skill-system)
12. [Permissions & Security](#12-permissions--security)
13. [State Management & Settings Layering](#13-state-management--settings-layering)
14. [Why It's So Powerful](#14-why-its-so-powerful)
15. [Concepts to Learn](#15-concepts-to-learn)

---

## 1. The Big Idea

Most coding AI tools lock you into a single LLM provider. **OpenClaude breaks that lock.**

It takes the entire Claude Code ecosystem — 42 tools, agent loop, terminal UI, MCP integration, slash commands, sub-agent spawning — and makes it work with **any** LLM provider. The same session can switch between Claude, GPT-4o, Gemini 2.5 Pro, DeepSeek, a local Ollama model, or 200+ others via a single environment variable change.

The key architectural insight: **the tool ecosystem is the moat, not the model.** The model is a reasoning engine that orchestrates tools. By decoupling orchestration from inference, OpenClaude makes the tool ecosystem universal.

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   USER TERMINAL                          │
│   openclaude [--provider gemini] [options]              │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              CLI ENTRY POINT (src/main.tsx)              │
│  • Commander.js parses args                              │
│  • Resolves provider (env vars / --provider / profile)   │
│  • Routes to REPL / non-interactive / SSH / connect mode │
└──────────┬──────────────────────────────────────┬────────┘
           │                                      │
┌──────────▼──────────┐          ┌────────────────▼──────────┐
│   REPL SCREEN        │          │  QUERY ENGINE              │
│  (src/screens/REPL)  │◄────────►│  (src/query.ts +          │
│  • React terminal UI │          │   src/QueryEngine.ts)      │
│  • Message history   │          │  • Builds system prompt    │
│  • Tool rendering    │          │  • Calls API (streaming)   │
│  • Permission dialogs│          │  • Processes tool calls    │
│  • Slash commands    │          │  • Handles loops/retries   │
└──────────────────────┘          └───────────┬───────────────┘
                                              │
                    ┌─────────────────────────▼──────────────┐
                    │     PROVIDER ABSTRACTION LAYER         │
                    │  ┌─────────────────────────────────┐   │
                    │  │  Anthropic SDK (native)          │   │
                    │  │  → Bedrock / Vertex / Foundry    │   │
                    │  ├─────────────────────────────────┤   │
                    │  │  OpenAI Shim (openaiShim.ts)     │   │
                    │  │  → GPT-4o, DeepSeek, Ollama,     │   │
                    │  │    Gemini, Groq, Fireworks, etc. │   │
                    │  ├─────────────────────────────────┤   │
                    │  │  Codex Shim (codexShim.ts)       │   │
                    │  │  → Codex / GPTs with Responses   │   │
                    │  │    API format                     │   │
                    │  └─────────────────────────────────┘   │
                    └───────────────────┬───────────────────┘
                                        │
┌───────────────────────────────────────▼────────────────────┐
│                  42 TOOLS + 7 TASKS                       │
│  ┌────────┐ ┌─────────┐ ┌──────┐ ┌─────────┐ ┌────────┐  │
│  │ Bash   │ │ File    │ │Glob  │ │ WebSearch│ │ Agent  │  │
│  │ Tool   │ │ Edit    │ │Grep  │ │ WebFetch │ │ Tool   │  │
│  └────────┘ └─────────┘ └──────┘ └─────────┘ └────────┘  │
│  ┌────────┐ ┌─────────┐ ┌──────┐ ┌─────────┐ ┌────────┐  │
│  │ MCP    │ │ Task*   │ │LSP   │ │ Skill   │ │ Plan   │  │
│  │ Tools  │ │ (6 more)│ │Tool  │ │ Tool    │ │ Mode   │  │
│  └────────┘ └─────────┘ └──────┘ └─────────┘ └────────┘  │
└───────────────────────────────────────────────────────────┘
```

### Flow of a single user interaction

```
1. User types: "Find all TODO comments and fix the security ones"

2. REPL captures input → sends to Query Engine

3. Query Engine:
   a. Builds system prompt (tool definitions, context, user prefs)
   b. Calls the API (via provider shim) with streaming
   c. LLM responds with text + tool calls

4. LLM decides: "I need to use GrepTool first"
   → GrepTool searches for "TODO" across codebase
   → Results flow back as streaming progress

5. LLM analyzes results: "Found 23 TODOs, 5 are security-related"
   → Decides to use FileReadTool on each security-related file

6. LLM reasons about each: "This one has SQL injection"
   → Uses FileEditTool to fix it

7. LLM summarizes: "Fixed 5 security TODOs. Changes: ..."
   → Streams final text to user

8. User asks a follow-up, or the loop continues
```

This loop — **think → decide tool → execute → see result → think again** — is the core pattern. The LLM is an autonomous orchestrator; the tools are its hands.

---

## 3. The Tool System (42 Tools)

Every capability in OpenClaude is a **Tool**. Tools are the fundamental unit of action. The LLM "calls" tools, the runtime executes them, and the results feed back into the conversation.

### Tool Interface (`src/Tool.ts`)

Each tool is a full TypeScript object with these key properties:

```typescript
type Tool = {
  name: string
  aliases?: string[]
  inputSchema: ZodSchema     // JSON Schema for the LLM to fill in
  call(args, context, ...): Promise<ToolResult>
  prompt(options): string    // The system prompt describing this tool

  // Safety & permissions
  isEnabled(): boolean
  isReadOnly(input): boolean
  isDestructive?(input): boolean
  isConcurrencySafe(input): boolean
  checkPermissions(input, context): PermissionResult
  validateInput?(input, context): ValidationResult

  // Streaming UI
  renderToolUseMessage(input, options): ReactNode
  renderToolUseProgressMessage(progress, options): ReactNode
  renderToolResultMessage(output, progress, options): ReactNode
  renderGroupedToolUse?(toolUses, options): ReactNode | null

  // Constraints
  maxResultSizeChars: number  // When exceeded, result saved to disk
  interruptBehavior(): 'cancel' | 'block'

  // MCP support
  isMcp?: boolean
  mcpInfo?: { serverName: string; toolName: string }
}
```

The `buildTool()` helper provides safe defaults for optional methods (e.g., `isEnabled` defaults to `true`, `isReadOnly` defaults to `false`).

### Complete Tool Inventory

#### 🖥️ Shell & System

| Tool | File | What It Does |
|------|------|-------------|
| **BashTool** | `tools/BashTool/` | Execute arbitrary shell commands with timeout, working directory control, and output streaming |
| **PowerShellTool** | `tools/PowerShellTool/` | Windows-specific PowerShell execution (conditionally enabled) |
| **REPLTool** | `tools/REPLTool/` | Internal Read-Eval-Print-Loop VM (Anthropic internal only) |

#### 📂 File Operations

| Tool | File | What It Does |
|------|------|-------------|
| **FileReadTool** | `tools/FileReadTool/` | Read files with line ranges, binary detection, size limits |
| **FileWriteTool** | `tools/FileWriteTool/` | Write/create files with directory auto-creation |
| **FileEditTool** | `tools/FileEditTool/` | Precise string-based edits with diff rendering and undo |
| **GlobTool** | `tools/GlobTool/` | File pattern matching (e.g., `src/**/*.ts`) |
| **GrepTool** | `tools/GrepTool/` | Regex content search across files |
| **NotebookEditTool** | `tools/NotebookEditTool/` | Edit Jupyter notebook cells |

#### 🔍 Search & Web

| Tool | File | What It Does |
|------|------|-------------|
| **WebSearchTool** | `tools/WebSearchTool/` | Web search (via DuckDuckGo, Firecrawl, or custom) |
| **WebFetchTool** | `tools/WebFetchTool/` | Fetch and render web pages as markdown |
| **ToolSearchTool** | `tools/ToolSearchTool/` | Keyword-based tool discovery for deferred tool loading |

#### 🤖 Agent Orchestration

| Tool | File | What It Does |
|------|------|-------------|
| **AgentTool** | `tools/AgentTool/` | **The killer feature** — spawn a sub-agent with its own tools and mission, runs in background or foreground |
| **TaskCreateTool** | `tools/TaskCreateTool/` | Create a long-running background task |
| **TaskGetTool** | `tools/TaskGetTool/` | Get status and output of a task |
| **TaskUpdateTool** | `tools/TaskUpdateTool/` | Update task description or instructions |
| **TaskListTool** | `tools/TaskListTool/` | List all running/completed tasks |
| **TaskStopTool** | `tools/TaskStopTool/` | Stop/kill a running task |
| **TaskOutputTool** | `tools/TaskOutputTool/` | Read task output incrementally |
| **SendMessageTool** | `tools/SendMessageTool/` | Send message to a teammate agent |
| **TeamCreateTool** | `tools/TeamCreateTool/` | Create a team of agents (swarm mode) |
| **TeamDeleteTool** | `tools/TeamDeleteTool/` | Delete a team |

#### 📋 Planning & Mode Control

| Tool | File | What It Does |
|------|------|-------------|
| **EnterPlanModeTool** | `tools/EnterPlanModeTool/` | Enter structured planning mode (read-only exploration) |
| **ExitPlanModeV2Tool** | `tools/ExitPlanModeV2Tool/` | Exit planning mode and summarize plan |
| **EnterWorktreeTool** | `tools/EnterWorktreeTool/` | Enter a git worktree for isolated changes |
| **ExitWorktreeTool** | `tools/ExitWorktreeTool/` | Exit worktree mode |
| **BriefTool** | `tools/BriefTool/` | Set brief/concise mode for responses |
| **VerifyPlanExecutionTool** | `tools/VerifyPlanExecutionTool/` | Verify that a plan was executed correctly |

#### 🌐 MCP Tools

| Tool | File | What It Does |
|------|------|-------------|
| **MCPTool** | `tools/MCPTool/` | Generic MCP tool delegation (dynamic per-server tools) |
| **ListMcpResourcesTool** | `tools/ListMcpResourcesTool/` | List available MCP server resources |
| **ReadMcpResourceTool** | `tools/ReadMcpResourceTool/` | Read a specific MCP server resource |
| **McpAuthTool** | `tools/McpAuthTool/` | MCP server authentication flow |

#### 🛠️ Developer Tooling

| Tool | File | What It Does |
|------|------|-------------|
| **LSPTool** | `tools/LSPTool/` | Language Server Protocol integration (go-to-def, hover, completions) |
| **ConfigTool** | `tools/ConfigTool/` | Read/update tool configuration (Anthropic internal) |
| **TungstenTool** | `tools/TungstenTool/` | Tungsten-specific operations (Anthropic internal) |
| **SleepTool** | `tools/SleepTool/` | Sleep for a duration (proactive/cron mode) |
| **TodoWriteTool** | `tools/TodoWriteTool/` | Write/manage todo lists |
| **BriefTool** | `tools/BriefTool/` | Set response brevity level |

#### 🧪 Testing & Debugging

| Tool | File | What It Does |
|------|------|-------------|
| **TestingPermissionTool** | `tools/testing/` | Testing only — simulates permission flows |
| **OverflowTestTool** | `tools/OverflowTestTool/` | Context overflow testing |
| **CtxInspectTool** | `tools/CtxInspectTool/` | Inspect context window contents |

#### 🔔 Notifications & Communication

| Tool | File | What It Does |
|------|------|-------------|
| **AskUserQuestionTool** | `tools/AskUserQuestionTool/` | Ask the user a question mid-session |
| **PushNotificationTool** | `tools/PushNotificationTool/` | Send push notifications |
| **SubscribePRTool** | `tools/SubscribePRTool/` | Subscribe to PR webhooks |
| **SendUserFileTool** | `tools/SendUserFileTool/` | Send a file to the user |

#### 🎯 Specialized

| Tool | File | What It Does |
|------|------|-------------|
| **SkillTool** | `tools/SkillTool/` | Load and execute installed skills |
| **SuggestBackgroundPRTool** | `tools/SuggestBackgroundPRTool/` | Suggest a PR for background review |
| **RemoteTriggerTool** | `tools/RemoteTriggerTool/` | Trigger remote agent execution |
| **WorkflowTool** | `tools/WorkflowTool/` | Execute workflow scripts |
| **ScheduleCronTool** | `tools/ScheduleCronTool/` | Cron-based scheduling (3 tools: Create, Delete, List) |
| **MonitorTool** | `tools/MonitorTool/` | Monitor resources/processes |
| **SnipTool** | `tools/SnipTool/` | History snippet management |
| **ListPeersTool** | `tools/ListPeersTool/` | List peer agents in UDS inbox mode |
| **TerminalCaptureTool** | `tools/TerminalCaptureTool/` | Capture terminal output for panel |
| **WebBrowserTool** | `tools/WebBrowserTool/` | Headless browser interaction |

### Tool Categories by Behavior

| Category | Tools | Purpose |
|----------|-------|---------|
| **Read-only** | FileRead, Glob, Grep, WebSearch, WebFetch, LSP, ListMcpResources, ReadMcpResource, TaskList, TaskGet, TaskOutput | Safe exploration without side effects |
| **Write** | FileWrite, FileEdit, NotebookEdit | Modify code and files |
| **Execute** | Bash, PowerShell, REPL | Run commands and code |
| **Orchestrate** | Agent, TaskCreate, TaskStop, TaskUpdate, SendMessage, TeamCreate, TeamDelete | Manage sub-agents and tasks |
| **Mode-switch** | EnterPlanMode, ExitPlanMode, EnterWorktree, ExitWorktree | Change the agent's operational mode |
| **Ask** | AskUserQuestion | Human-in-the-loop clarification |
| **Schedule** | ScheduleCron (Create/Delete/List), Sleep, Monitor | Time-based and event-based execution |
| **Extend** | MCPTool, SkillTool, WorkflowTool | Plugin-like dynamic capabilities |

---

## 4. The Task System (7 Task Types)

Tasks are **long-running background processes** that outlive individual tool calls. While tools are synchronous (call → wait → result), tasks can run for minutes, hours, or indefinitely.

### Task Interface (`src/Task.ts`)

```typescript
type Task = {
  name: string
  type: TaskType    // 7 possible types
  kill(taskId, setAppState): Promise<void>
}
```

### Task Lifecycle

```
pending → running → completed
                  → failed
                  → killed
```

Each task has:
- A **unique ID** with a type prefix: `a` (agent), `b` (bash), `r` (remote), `t` (teammate), `w` (workflow), `m` (monitor), `d` (dream)
- An **output file** on disk for streaming results
- A **start time** and optional **end time**
- A **tracked pause duration**
- A **notification flag** for completion alerts

### The 7 Task Types

| Type | Prefix | Implementation | What It Does |
|------|--------|---------------|-------------|
| **local_bash** | `b` | `LocalShellTask` | Run a shell command as a persistent background process. Starts immediately; output streams to disk. Configurable timeout. |
| **local_agent** | `a` | `LocalAgentTask` | Spawn a full sub-agent (with its own LLM calls, tools, and loop) in a background thread. The agent has its own conversation context and tool permissions. |
| **remote_agent** | `r` | `RemoteAgentTask` | Launch an agent on a remote machine (SSH, teleport). The remote agent reports back via the task output system. |
| **in_process_teammate** | `t` | (in-process teammate) | A peer agent that shares the same Node.js process. Communicates via a mailbox system. Can see and respond to messages from other teammates. |
| **local_workflow** | `w` | `LocalWorkflowTask` | Execute a multi-step workflow script (YAML or DSL) with conditional branching, retries, and parallel steps. |
| **monitor_mcp** | `m` | `MonitorMcpTask` | Continuously monitor MCP server health, resource changes, or tool availability. Triggers notifications on state changes. |
| **dream** | `d` | `DreamTask` | A background agent that "dreams" — autonomously explores the codebase, runs tests, and suggests improvements without direct user prompting. |

### Task vs Tool

| Aspect | Tool | Task |
|--------|------|------|
| Duration | Seconds | Minutes to indefinite |
| Visibility | Blocking, visible in UI | Background, checkable via Task* tools |
| State | Stateless per call | Full lifecycle (pending → running → terminal) |
| Persistence | None | Output saved to disk |
| Parallelism | Configurable via `isConcurrencySafe` | Always parallel |
| Cleanup | Automatic | Explicit kill or completion |

---

## 5. The Provider Abstraction Layer

This is the architectural heart of OpenClaude. It provides a transparent translation layer between Anthropic's SDK interface and every other LLM API.

### Architecture

```
                    ┌──────────────────────────┐
                    │   Main Loop (query.ts)    │
                    │   Uses Anthropic SDK      │
                    │   interface exclusively   │
                    └────┬─────────────────┬───┘
                         │                 │
              ┌──────────▼──┐     ┌────────▼─────────┐
              │ Native SDK  │     │   OpenAI Shim     │
              │ (client.ts) │     │ (openaiShim.ts)   │
              │             │     │                   │
              │ • Anthropic │     │ • GPT-4o          │
              │ • Bedrock   │     │ • Gemini          │
              │ • Vertex    │     │ • DeepSeek        │
              │ • Foundry   │     │ • Ollama          │
              │             │     │ • LM Studio       │
              │             │     │ • Groq            │
              │             │     │ • Fireworks       │
              │             │     │ • Together        │
              │             │     │ • Mistral         │
              │             │     │ • OpenRouter      │
              │             │     │ • GitHub Models   │
              └─────────────┘     └────────┬─────────┘
                                           │
                                  ┌────────▼─────────┐
                                  │  Codex Shim      │
                                  │ (codexShim.ts)   │
                                  │                  │
                                  │ • Codex/Responses│
                                  │   API format     │
                                  └──────────────────┘
```

### How the OpenAI Shim Works (`src/services/api/openaiShim.ts`)

The shim intercepts `anthropic.beta.messages.create()` calls and translates:

1. **Messages**: Anthropic's `{role, content}` → OpenAI's `{role, content}` format
   - System messages are extracted to the `system` parameter
   - Tool results are flattened into the OpenAI multi-part message format

2. **Tools**: Anthropic tool definitions → OpenAI function-calling format
   - JSON Schema is sanitized for OpenAI compatibility (`sanitizeSchemaForOpenAICompat`)

3. **Streaming**: OpenAI streaming chunks → Anthropic streaming events
   - The shim emits `content_block_delta`, `content_block_stop`, `message_delta`, etc.
   - The rest of the codebase never knows it's talking to OpenAI

4. **Tool Calls**: OpenAI function calls → Anthropic `tool_use` content blocks
   - Maps `id`, `function.name`, `function.arguments` to Anthropic's format

5. **Usage**: OpenAI `usage` → Anthropic `input_tokens` / `output_tokens`

### Provider Selection Mechanism

Providers are selected through a layered configuration:

```bash
# Environment variables (highest priority)
CLAUDE_CODE_USE_OPENAI=1        # Use OpenAI-compatible
CLAUDE_CODE_USE_GEMINI=1        # Use Gemini
CLAUDE_CODE_USE_BEDROCK=1       # Use AWS Bedrock
CLAUDE_CODE_USE_GITHUB=1        # Use GitHub Models
CLAUDE_CODE_USE_VERTEX=1        # Use GCP Vertex AI
CLAUDE_CODE_USE_FOUNDRY=1       # Use Anthropic Foundry

# API keys
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
GITHUB_TOKEN=ghp_...

# Base URL overrides (for local/Ollama/LM Studio)
OPENAI_BASE_URL=http://localhost:11434/v1

# Model selection
OPENAI_MODEL=gpt-4o
GEMINI_MODEL=gemini-2.5-pro
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# Interactive provider selection
# Use /provider slash command or --provider flag
```

### Provider Config (`src/services/api/providerConfig.ts`)

Resolves the actual transport:

- `chat_completions` → OpenAI-compatible REST API (most providers)
- `codex_responses` → Codex Responses API
- Native Anthropic SDK → Anthropic, Bedrock, Vertex, Foundry

Also maps model aliases, resolves credentials from secure storage, handles GitHub Models token hydration, and manages Gemini credential refresh.

---

## 6. The Agent Loop

The agent loop (`src/query.ts` ~1725 lines) is the central nervous system. Each iteration follows this sequence:

### Query Execution Flow

```
┌─────────────────────────────────────────────────────────┐
│                    NEXT TURN                             │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  1. BUILD SYSTEM PROMPT                                 │
│     • Tool definitions (from Tool.prompt())              │
│     • User context (CLAUDE.md, OS, working directory)    │
│     • Permission rules                                   │
│     • Agent definitions (for AgentTool)                  │
│     • Skills, MCP resources                              │
│     • Custom / appended system prompts                   │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  2. BUILD MESSAGE LIST                                   │
│     • Normalize messages for API                         │
│     • Apply compaction if context is near limit          │
│     • Prepend user context, append system context        │
│     • Handle memory attachments (CLAUDE.md files)        │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  3. CALL API (STREAMING)                                 │
│     • Provider shim translates call                     │
│     • Streams tokens, tool_use blocks, progress          │
│     • Handle errors (retry, fallback, rate limits)       │
│     • Track token usage and cost                         │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  4. PROCESS TOOL CALLS                                   │
│     For each tool_use block:                             │
│     • Find the tool by name                              │
│     • Validate input                                     │
│     • Check permissions (auto-allow / ask / deny)        │
│     • Execute tool                                       │
│     • Stream progress to UI                              │
│     • Handle concurrency (parallel vs serial)            │
│     • Collect results                                    │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  5. CHECK FOR DONE                                      │
│     • If tool results exist → go to step 3 (feed back)   │
│     • If text response + no tools → return to user       │
│     • If error → handle (retry, compact, or abort)       │
└────────────────────────┬────────────────────────────────┘
                         │
                    ┌────▼────┐
                    │  DONE   │
                    └─────────┘
```

### Context Compaction

When the context window approaches its limit, the query engine can auto-compact:
- Summarizes older messages
- Drops non-essential tool results
- Preserves user intents and key decisions
- Configurable thresholds and strategies

### Retry & Fallback

The `withRetry` module wraps API calls with:
- Exponential backoff for rate limits (429)
- Fallback to alternative models/providers
- Graceful degradation when primary API is down

---

## 7. Sub-Agents, Swarms & Teammates

This is one of the most powerful concepts. The `AgentTool` lets any agent spawn a **sub-agent** with its own mission, tools, and LLM calls.

### Sub-Agent Types

| Type | Spawned By | What It Is |
|------|-----------|------------|
| **Sub-agent** | `AgentTool` (in conversation) | A child agent with a specific task. Runs in its own context. Parent waits or continues in parallel. |
| **Background agent** | `TaskCreateTool` (as background task) | An agent that runs as a `local_agent` task. Parent can check on it later; it doesn't block the main thread. |
| **Teammate** | `TeamCreateTool` + `SendMessageTool` | A peer agent in a shared team context. All teammates share a mailbox and can communicate. |
| **Coordinator** | coordinator mode | A special "manager" agent that spawns worker agents, each with restricted tool sets, and coordinates their output. |
| **Fork agent** | implicit (branching conversation) | A copy of the current agent with shared context. Used for exploring alternatives in parallel. |

### The Mailbox System

Teammates communicate through a **mailbox** system:
- Each teammate has an inbox (queue of messages)
- `SendMessageTool` posts to a teammate's inbox
- The teammate's agent loop reads from its inbox and processes
- Responses go back to the sender's inbox

This enables patterns like:
- "Research agent" searches docs → sends findings to "Implementation agent"
- "Review agent" checks code → sends feedback to "Fix agent"
- Multiple agents working on different files simultaneously

### Coordinator Mode

The coordinator (`src/coordinator/coordinatorMode.ts`) is a special meta-agent:
1. User gives a complex task to the coordinator
2. Coordinator breaks it into subtasks
3. Spawns worker agents with restricted tool sets
4. Workers report back to coordinator
5. Coordinator synthesizes the final result

Worker agents in coordinator mode get only the tools they need (e.g., a "search" worker gets Grep+Glob+Read, a "code" worker gets Bash+Edit+Write).

### Agent Routing

Different agent roles can be routed to **different models**:

```json
{
  "agentRouting": {
    "explore": { "model": "gpt-4o-mini" },
    "plan": { "model": "claude-sonnet-4-20250514" },
    "frontend-dev": { "model": "gemini-2.5-pro" }
  }
}
```

This optimizes cost: use cheap models for exploration, expensive models for critical reasoning.

---

## 8. MCP — Model Context Protocol

MCP is an open protocol for connecting LLMs to external tools and data sources. OpenClaude has first-class MCP support with 27 files in `src/services/mcp/`.

### MCP Architecture

```
┌───────────────────────────────────────────────────┐
│                   OPENCLAUDE                       │
│                                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │
│  │ MCP Client 1│  │ MCP Client 2│  │ MCP Client│  │
│  │ (Filesystem)│  │ (Database)  │  │ (GitHub)  │  │
│  └──────┬──────┘  └──────┬──────┘  └─────┬─────┘  │
│         │                │               │         │
│  ┌──────▼────────────────▼───────────────▼──────┐  │
│  │          MCP Manager (connection pool)       │  │
│  │  • Connection lifecycle                      │  │
│  │  • Auth / credential resolution              │  │
│  │  • Health monitoring                         │  │
│  │  • Resource enumeration                      │  │
│  └───────────────────────┬──────────────────────┘  │
│                          │                          │
│  ┌───────────────────────▼──────────────────────┐  │
│  │        MCP Tool Adapter                      │  │
│  │  Converts MCP tool definitions ↔ Tool type   │  │
│  └──────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────┘
```

### MCP Capabilities

| Feature | Description |
|---------|-------------|
| **Tool delegation** | MCP server tools appear alongside built-in tools in the agent's tool list |
| **Resource access** | Read files, database schemas, API docs — anything an MCP server exposes |
| **Authentication** | OAuth, API key, token-based auth flows for MCP servers |
| **Config discovery** | Load MCP configs from `claude_desktop_config.json`, `settings.json`, environment variables |
| **Health monitoring** | Track connection state, auto-reconnect, detect stale servers |
| **Chained MCP** | Use MCP tools as building blocks in the agent's autonomous reasoning |

### What MCP Unlocks

- **Database querying**: "Query the users table" → MCP server connects to Postgres
- **API integration**: "Create a GitHub issue" → MCP server calls GitHub API
- **File system access**: "Read the remote config file" → MCP server on a different machine
- **Custom tools**: Anyone can write an MCP server that exposes custom functionality

---

## 9. 107 Slash Commands

The `/` prefix in the REPL activates one of 107 built-in commands. These cover every aspect of the tool.

### Categories

#### Session & Configuration
`/clear`, `/compact`, `/context`, `/config`, `/env`, `/exit`, `/init`, `/model`, `/provider`, `/reset-limits`, `/resume`, `/session`, `/status`, `/theme`, `/upgrade`, `/version`

#### Development Workflow
`/commit`, `/commit-push-pr`, `/pr_comments`, `/review`, `/security-review`, `/autofix-pr`, `/plan`, `/ultraplan`, `/bug-hunter`, `/buddy`, `/branch`, `/diff`, `/rewind`

#### File & Code
`/files`, `/add-dir`, `/copy`, `/rename`, `/export`, `/summary`, `/good-claude`

#### Agents & Tasks
`/agents`, `/agents-platform`, `/buddy`, `/tasks`, `/dream`, `/fast`, `/thinkback`, `/thinkback-play`

#### Knowledge & Memory
`/memory`, `/context`, `/docs`, `/skills`

#### MCP & Extensions
`/mcp`, `/plugin`, `/reload-plugins`, `/install-github-app`, `/install-slack-app`

#### Permissions & Security
`/permissions`, `/privacy-settings`, `/sandbox-toggle`, `/hooks`

#### Debugging & Diagnostics
`/doctor`, `/cost`, `/usage`, `/stats`, `/heapdump`, `/perf-issue`, `/debug-tool-call`, `/mock-limits`, `/rate-limit-options`

#### Remote & Collaboration
`/remote-env`, `/remote-setup`, `/teleport`, `/ide`, `/desktop`, `/mobile`, `/bridge`, `/bridge-kick`

#### UI & Interaction
`/color`, `/output-style`, `/vim`, `/voice`, `/keybindings`, `/help`, `/stickers`, `/effort`, `/passes`

#### Onboarding & Setup
`/onboarding`, `/onboard-github`, `/login`, `/logout`, `/oauth-refresh`, `/init`

#### Other
`/exit`, `/fast`, `/feedback`, `/release-notes`, `/share`, `/tag`, `/teams`, `/time`

---

## 10. Terminal UI (React Reconciler)

OpenClaude has a **complete custom terminal rendering engine** (`src/ink/`, 51 files) — a fork of the Ink React renderer for terminals.

### How Terminal Rendering Works

1. **React components** describe the UI (messages, tool progress, spinners, dialogs)
2. **React Reconciler** (`react-reconciler`) computes virtual DOM diffs
3. **Layout engine** measures text widths, wraps lines, positions elements
4. **ANSI renderer** outputs ANSI escape codes to the terminal
5. **Input handler** captures keyboard events, mouse events, and terminal resizes

### Key Terminal UI Components

| Component | What It Renders |
|-----------|----------------|
| `App.tsx` | Root component — manages screen routing |
| `Messages.tsx` | Scrollable message history |
| `MessageRow.tsx` | Single message (user, assistant, tool call) |
| `PromptInput/` | Input area with syntax highlighting, auto-complete, multiline |
| `Spinner.tsx` | Animated spinners for in-progress operations |
| `ToolUseLoader.tsx` | Progress animation for running tools |
| `permissions/` | Permission approval dialogs |
| `diff/` | Side-by-side and unified diffs |
| `ui/` | Common UI primitives (buttons, boxes, text) |
| `TextInput.tsx` | Text input with selection, clipboard, history |
| `VimTextInput.tsx` | Vim-mode input with modal editing |
| `Markdown.tsx` | Rendered markdown output |
| `StructuredDiff.tsx` | Structured diff with syntax highlighting |

### Terminal Features

| Feature | Description |
|---------|-------------|
| **Streaming text** | Real-time token-by-token display as LLM generates |
| **Tool progress** | Live updates on tool execution (file reads, bash commands, sub-agents) |
| **Spinners** | Animated progress indicators for long operations |
| **Scrollback** | Full scrollable message history |
| **Search** | `/` search within transcript |
| **Diff rendering** | Syntax-highlighted code diffs |
| **Vim mode** | Modal input (normal/insert/visual) with vim keybindings |
| **Voice mode** | Speech-to-text input |
| **Theme support** | Multiple color themes |
| **Hyperlinks** | Clickable links (iTerm2, Kitty, VSCode terminal) |
| **Fullscreen mode** | Enter/exit fullscreen for tool outputs |
| **History search** | Ctrl+R style reverse search |

---

## 11. Plugin & Skill System

### Plugins (`src/plugins/`)

Dynamic runtime extensions with a full lifecycle:

```
load → initialize → enable → [use] → disable → unload
```

- **Registry**: Central registry of all installed plugins
- **Lifecycle hooks**: `onLoad`, `onInit`, `onEnable`, `onDisable`, `onUnload`
- **Version management**: Compatible version ranges, upgrade paths
- **Config**: Per-plugin configuration merged with global settings
- **Command injection**: Plugins can add new slash commands
- **Tool injection**: Plugins can add new tools

### Skills (`src/skills/`)

Skills are **specialized knowledge bundles** that teach the LLM how to do specific things:

- A skill is a directory with `SKILL.md` (instructions), optional code/files
- Skills are injected into the system prompt when active
- The `SkillTool` loads and activates skills on demand
- Skills can be bundled with OpenClaude or user-installed
- Skill discovery: `/skills` command lists and manages skills

Examples of skills:
- **Supabase**: Instructions for Supabase Database, Auth, Edge Functions, RLS policies
- **Postgres Best Practices**: Query optimization, schema design patterns
- Custom user skills for specific frameworks or workflows

---

## 12. Permissions & Security

### Permission System

The permission system (`src/utils/permissions/`) provides granular control over tool execution:

```
┌──────────────┐     ┌──────────────────┐     ┌───────────┐
│  Tool calls   │────►│  Permission      │────►│  Execute  │
│  (LLM wants   │     │  Checker         │     │  or Deny  │
│   to run)     │     │                  │     │           │
└──────────────┘     └──────────────────┘     └───────────┘
                     ┌──────────────────┐
                     │  Always Allow    │── Auto-approve
                     │  Always Deny     │── Auto-reject
                     │  Always Ask      │── Show dialog
                     │  Classifier      │── ML-based risk
                     │  Hooks           │── Custom rules
                     └──────────────────┘
```

### Permission Rules

Rules can be specified per-tool, per-tool+input-pattern, or globally:

```json
{
  "permissions": {
    "alwaysAllow": ["Bash(git *)", "FileRead(*)"],
    "alwaysDeny": ["Bash(rm -rf *)"],
    "alwaysAsk": ["FileWrite(prod/*)"]
  }
}
```

### Security Features

| Feature | Description |
|---------|-------------|
| **Deny rules** | Blanket deny for entire tools or MCP servers — filtered before model even sees them |
| **Permission dialogs** | Interactive approval in REPL with context about what the tool will do |
| **Auto-classifier** | ML-based risk assessment of tool inputs |
| **Hooks** | Custom `PreToolUse` / `PostToolUse` hooks for enterprise policies |
| **Stripped dangerous rules** | Remove dangerous permissions in sensitive contexts |
| **Denial tracking** | Track consecutive denials and fall back to prompting |
| **Privacy verification** | Built-in `verify-no-phone-hot.ts` script to ensure no data exfiltration |
| **Telemetry opt-out** | Full telemetry control, disabled by default for non-Anthropic builds |

---

## 13. State Management & Settings Layering

### App State (`src/state/`)

A Zustand-like reactive store with React context provider:

```typescript
// AppState is the single source of truth for:
type AppState = {
  messages: Message[]          // All conversation messages
  tools: Tool[]                // Currently available tools
  mcp: { servers, tools }     // MCP connection state
  tasks: TaskStateBase[]       // Running/completed tasks
  settings: Settings           // User settings
  permissions: PermissionState
  session: SessionInfo
  ui: { theme, mode, ... }     // UI state
}
```

The store is accessible via `useAppState()` hook or imperatively via `getAppState()` / `setAppState()` on `ToolUseContext`.

### Settings Layering

Settings are loaded from multiple sources, each overriding the last:

```
1. Policy defaults (lowest priority)
2. User settings (~/.claude/settings.json)
3. Project settings (.claude/settings.json in repo)
4. Environment variables
5. CLI flags (--verbose, --model, --provider)
6. Runtime slash commands (/update settings) (highest priority)
```

### Bootstrap State (`src/bootstrap/state.ts`)

Global mutable state for session parameters that are set at startup and rarely change:
- Provider selection
- API keys
- Model overrides
- Feature flags

---

## 14. Why It's So Powerful

### 1. Provider Agnosticism (The Moats vs Models Insight)

Most AI coding tools are vertically integrated (one provider → one UI → one tool set). OpenClaude decouples these layers. The tool ecosystem (42 tools, MCP, tasks, skills, plugins) represents years of engineering. By making it work with **any** LLM, OpenClaude future-proofs the investment. When a better model comes out, you just change an env var.

### 2. Recursive Agent Architecture

The `AgentTool` spawns sub-agents that can themselves spawn sub-agents. This creates an **infinite recursion of autonomous problem-solving**. A complex task like "refactor this monolith to microservices" can be decomposed hierarchically:
- Main agent plans the refactor
- Spawns 5 sub-agents (one per microservice)
- Each sub-agent spawns its own file-editing agents
- Results bubble up and get synthesized

### 3. MCP Ecosystem

MCP is the "USB-C of AI tools" — any MCP server (database, API, file system, browser, etc.) becomes available to the agent. This means OpenClaude's capability set is **not limited to its 42 built-in tools** — it can dynamically discover and use any MCP-compatible server.

### 4. Streaming-First Everything

Every API call streams tokens. Every tool execution streams progress. The React-based terminal UI renders updates in real-time. This creates a **feeling of live collaboration** rather than batch processing.

### 5. Local-First & Privacy Hardened

Works fully offline with Ollama/LM Studio. Built-in privacy verification scripts. Telemetry disabled by default in the open-source build. Enterprise-ready.

### 6. Task System = Real Autonomy

Tasks let agents do things like:
- "Run the test suite in the background and tell me when it's done"
- "Monitor the production logs for errors and alert me"
- "Every hour, check for dependency updates and create a PR"
- "While I work on feature X, refactor module Y in the background"

### 7. Recursive Tool Use

Tools can call tools can call tools. The `AgentTool` calls any tool — including `AgentTool` again. The `TaskCreateTool` creates tasks that call tools. The `WorkflowTool` executes workflow scripts that orchestrate multiple tools. This composability is what makes the system more powerful than the sum of its parts.

### 8. Slash Commands = Full IDE in a Terminal

107 commands cover everything from `git commit` to `voice mode` to `remote SSH` to `MCP config` to `debug heapdumps`. The terminal becomes a full development environment, not just a chat interface.

### 9. Dead Code Elimination (Feature Flags)

Using `bun:bundle`'s `feature()` function and conditional `require()`, features can be toggled at build time. Internal Anthropic features are stripped from the open-source build. This means a **single codebase** maintains both the Anthropic-internal version and the public open-source version without code drift.

### 10. Cost Optimization via Agent Routing

By routing different agent roles to different models, you can:
- Let the "explore" agent use a cheap model ($0.15/M tokens) for file searching
- Use the premium model ($15/M tokens) only for critical reasoning and code generation
- Potentially save 80-90% on API costs without sacrificing quality

---

## 15. Concepts to Learn

If you want to understand and build on these ideas, master these concepts:

### Core Concepts

| Concept | Why It Matters |
|---------|---------------|
| **Tool-driven agent loop** | The fundamental pattern: LLM reasons → calls tool → sees result → reasons again. This is what makes coding agents autonomous. |
| **Function-calling / Tool use** | How LLMs interface with external systems. Understanding JSON Schema tool definition is essential. |
| **Streaming tokens** | Real-time UX depends on streaming. The architecture must handle partial, incremental responses. |
| **React Reconciler** | Custom renderers for non-DOM environments. This is how terminal UIs, game UIs, and native mobile UIs work with React. |
| **Provider abstraction (Shim pattern)** | Translating between provider formats without changing the consumer. A general pattern for API compatibility layers. |
| **Sub-agent recursion** | Hierarchical decomposition of complex tasks. The `AgentTool` pattern is a powerful design for autonomous systems. |

### Advanced Concepts

| Concept | Why It Matters |
|---------|---------------|
| **MCP (Model Context Protocol)** | The emerging standard for LLM-tool communication. Understanding this is like understanding USB for peripherals. |
| **Context compaction** | How to manage limited context windows — summarization, prioritization, structured forgetting. |
| **Tool result budgeting** | Managing the token cost of tool outputs — truncation, disk persistence, summarization. |
| **Permission classification** | ML-based risk assessment of tool inputs before execution. |
| **Agent routing** | Cost-quality optimization by matching agent roles to model capabilities. |
| **Reactive state management** | The Zustand-like pattern for shared mutable state in event-driven systems. |
| **Dead code elimination via bundler** | Using build-time feature flags to maintain a single codebase for multiple product variants. |
| **Mailbox-based agent communication** | Async message passing between autonomous agents (actor model). |
| **Settings layering** | Multi-source configuration merging (env → file → flags → runtime). |

### Design Patterns Used

| Pattern | Where | Why |
|---------|-------|-----|
| **Strategy pattern** | Provider selection | Swap LLM backends without changing the main loop |
| **Adapter pattern** | OpenAI/Codex shims | Translate between incompatible interfaces |
| **Composite pattern** | AgentTool → sub-agents | Hierarchical decomposition of complex work |
| **Observer pattern** | Streaming events, tool progress | Real-time UI updates from async operations |
| **Command pattern** | 107 slash commands | Uniform interface for diverse actions |
| **Factory pattern** | `buildTool()` | Consistent tool construction with sensible defaults |
| **Plugin architecture** | Plugin + skill system | Dynamic extension without modifying core |
| **Actor model** | Mailbox system | Isolated agents communicating via messages |
| **Feature flags** | Dead code elimination | Single codebase, multiple product variants |
| **Promise-pipeline** | Tool execution chain | Sequential and parallel tool orchestration |

---

> **OpenClaude is not just a tool — it's a reference architecture for autonomous AI coding agents.** The patterns it implements (tool-driven loops, provider abstraction, sub-agent hierarchies, MCP integration, streaming-first UI, permission systems) are becoming the standard for how LLMs interact with the world.