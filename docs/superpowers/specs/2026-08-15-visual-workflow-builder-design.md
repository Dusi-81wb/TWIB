# Visual Workflow Builder & Real-Time Canvas Specification

- **Date**: 2026-08-15
- **Status**: Approved
- **Topic**: Interactive Visual Workflow Builder & Live Telemetry Canvas

---

## 1. Overview & Objectives

The Visual Workflow Builder provides an interactive, drag-and-drop node graph canvas for TWIB (Total Workflow Intelligence Builder). It allows users to:
1. **Generate with AI**: Auto-generate multi-agent DAGs from natural language prompts.
2. **Visually Edit & Orchestrate**: Drag, drop, connect, disconnect, and configure nodes on an infinite canvas with snap-to-grid, minimap, and topological auto-layout.
3. **Extend Beyond Standard Agents**: Incorporate Logic Branching (`If/Else`), Evaluator/Judge (`LLM-as-a-Judge`), Human-in-the-Loop (`Approval Gates`), and External Action (`Webhook`) nodes.
4. **Monitor in Real Time**: Watch live execution with animated neon signal pulses flowing along active edges, real-time node timers, token accumulators, and click-to-inspect streaming reasoning logs.

---

## 2. Architecture & Tech Stack

### 2.1 Technologies
- **Canvas Engine**: `@xyflow/react` (React Flow 12 for Next.js 15 / React 19)
- **Auto-Layout Engine**: `@dagrejs/dagre` for directed acyclic hierarchical layout computation
- **State Management**: Zustand store (`useWorkflowCanvasStore`) with undo/redo history stack
- **Styling**: Tailwind CSS + CSS Variables + Framer Motion/CSS Keyframe edge particle animations
- **Real-Time Bridge**: WebSocket hook (`useWorkflowWebsocket`) streaming backend DAG telemetry directly to node states

### 2.2 Component Hierarchy & Data Flow

```
┌────────────────────────────────────────────────────────────────────────┐
│                        WorkflowCanvasContainer                         │
│  ┌─────────────────────────┐  ┌─────────────────────────────────────┐  │
│  │   NodePaletteSidebar    │  │        InteractiveFlowCanvas        │  │
│  │  - Agent Nodes          │  │  - ReactFlowProvider                │  │
│  │  - Flow & Logic Nodes   │  │  - Background (Dots / Grid)         │  │
│  │  - Evaluator Nodes      │  │  - Controls (Zoom, Fit, Auto-Layout)│  │
│  │  - Human Approval Nodes │  │  - MiniMap                          │  │
│  │  - Webhook Nodes        │  │  - Custom Nodes & Animated Edges    │  │
│  └─────────────────────────┘  └─────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                WorkflowNodeInspector (Slide-Over Drawer)         │  │
│  │  - Tab 1: Config (Prompts, Model Tiers, Retries, Timeouts)       │  │
│  │  - Tab 2: Live Stream (Markdown stdout, tokens, reasoning)       │  │
│  │  - Tab 3: Human Approval (Artifact review, approve/reject/notes) │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Node Specification & Palette

### 3.1 Node Types
1. **`AgentNode`**
   - **Properties**: `agent_id` (planner, research, analyst, architect, validator, optimizer, documentation, supervisor), `model_tier`, `custom_prompt`, `optional`, `timeout_seconds`, `max_retries`.
   - **Handles**: `in` (Target, Left/Top), `out` (Source, Right/Bottom).
   - **Visuals**: Role-based color theme, model badge, status pill, live token count, duration timer.

2. **`LogicBranchNode`**
   - **Properties**: `expression` (JSONPath or boolean condition), `condition_type`.
   - **Handles**: 1 `in` (Target), 2 `out` (Source: `true` [Green], `false` [Red]).
   - **Visuals**: Cyan diamond accent, condition rule snippet preview.

3. **`EvaluatorJudgeNode`**
   - **Properties**: `metric` (accuracy, completeness, safety, format), `min_score` (0–100), `pass_node_id`, `fail_node_id`.
   - **Handles**: 1 `in` (Target), 2 `out` (Source: `pass` [Emerald], `retry` [Amber]).
   - **Visuals**: Shield icon, score gauge bar.

4. **`HumanApprovalNode`**
   - **Properties**: `timeout_seconds`, `default_action` ("auto_approve" | "auto_reject"), `required_roles`.
   - **Handles**: 1 `in` (Target), 1 `out` (Source).
   - **Visuals**: UserCheck icon, amber glowing badge when active, inline Quick-Approve/Reject buttons.

5. **`WebhookActionNode`**
   - **Properties**: `url`, `method` ("POST" | "GET"), `headers`, `payload_template`.
   - **Handles**: 1 `in` (Target), 1 `out` (Source).
   - **Visuals**: Send icon, endpoint URL badge.

---

## 4. Real-Time Telemetry & Edge Signaling

### 4.1 Custom Animated Edge (`AnimatedFlowEdge`)
- **Idle/Pending**: Dim dashed curve (`border-border/60`).
- **Active / Streaming**: Neon cyan gradient stroke with traveling particle pulse animation along the Bézier path.
- **Completed**: Solid emerald `#10b981` stroke.
- **Failed**: Red `#ef4444` stroke with alert tooltip.

### 4.2 Telemetry Event Mapping
- `node_started`: Transitions node status to `running`, triggers glowing aura ring, initializes live duration timer.
- `token_stream`: Increments node's token accumulator, streams markdown content into inspector drawer.
- `node_completed`: Transitions node status to `completed`, displays final latency and token count, triggers active pulse on downstream edge.
- `node_failed`: Transitions node status to `failed`, displays error banner and retry action.
- `approval_required`: Transitions node status to `waiting_approval`, triggers pulsing amber alert, exposes decision prompt.

---

## 5. Bidirectional Serialization (`dag-serializer.ts`)

- **`planToFlow(plan: AgentDAGPlan)`**:
  1. Computes topological waves with Kahn's algorithm.
  2. Positions nodes on the 2D grid with dagre layout (rankDir: "LR").
  3. Constructs React Flow nodes with custom types and input/output handles.
  4. Generates edges with connection IDs `e-${src}-${tgt}`.
- **`flowToPlan(nodes, edges)`**:
  1. Validates that the graph is a Directed Acyclic Graph (cycle check).
  2. Extracts agent definitions, dependencies, logic rules, and custom parameters.
  3. Outputs clean `AgentDAGPlan` for FastAPI backend execution.

---

## 6. Integration Points in TWIB

1. **Workflow Creator (`frontend/app/workflows/new/page.tsx`)**:
   - Replaces the static layout with the full interactive visual builder.
   - Allows users to prompt the AI to generate a plan OR build from scratch using the palette.
2. **Workflow Monitor (`frontend/app/workflows/[workflowId]/page.tsx`)**:
   - Upgrades `DAGVisualizer` to the interactive `@xyflow/react` canvas.
   - Shows live animated pulses, step-by-step progress, and inline human-in-the-loop approvals.
3. **Export & Sharing**:
   - One-click export of workflow graphs to JSON / YAML / PNG screenshot.

---

## 7. Verification & Testing Strategy

1. **Unit & Serialization Tests**:
   - Test `dag-serializer.ts`: bidirectional `planToFlow` and `flowToPlan` consistency.
   - Test cycle detection and invalid connection prevention.
2. **Interactive UI Tests**:
   - Drag and drop from palette onto canvas creates new node at exact pointer coordinates.
   - Connecting handles creates validated directed edges.
   - Auto-layout button neatly organizes complex multi-branch graphs.
3. **Realtime WebSocket Verification**:
   - Simulating execution events triggers correct edge particle animations and node state badge updates.
