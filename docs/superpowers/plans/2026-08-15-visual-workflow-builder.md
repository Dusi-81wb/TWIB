# Visual Workflow Builder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-grade, interactive visual workflow builder canvas using `@xyflow/react` and Dagre auto-layout in Next.js 15, enabling AI prompt generation, drag-and-drop DAG orchestration, custom node types (Agents, Logic, Evaluators, Human Approval, Webhooks), and live animated execution telemetry.

**Architecture:** A Zustand-powered state store (`useWorkflowCanvasStore`) coordinates bidirectional serialization between TWIB's backend `AgentDAGPlan` and React Flow's node/edge graphs. Custom node components handle distinct agent roles and control logic, while an animated Bézier edge component renders traveling neon signal pulses during live WebSocket execution events.

**Tech Stack:** Next.js 15 (App Router), React 19, TypeScript, `@xyflow/react` (React Flow 12), `@dagrejs/dagre`, Lucide React, Tailwind CSS, Zustand, Vitest / Jest.

**Spec:** [`docs/superpowers/specs/2026-08-15-visual-workflow-builder-design.md`](file:///c:/Users/Samrat/OneDrive/Documents/Samrat-ai/TWIB_Copy/docs/superpowers/specs/2026-08-15-visual-workflow-builder-design.md)

## Global Constraints

- Must be compatible with React 19 and Next.js 15.
- Must preserve full backward compatibility with existing backend `AgentDAGPlan` and `WorkflowResponse` schemas.
- Must maintain dark mode design aesthetics matching TWIB's design tokens and styling guidelines.
- Clean Architecture boundaries: Presentation logic in `frontend/features/workflows/canvas`, state in `frontend/stores`, serializers in `frontend/lib`.

---

### Task 1: Canvas Dependencies, Extended Node Types & Bidirectional Serializer

**Files:**
- Modify: `frontend/package.json`
- Create: `frontend/types/flow.ts`
- Create: `frontend/lib/dag-serializer.ts`
- Create: `frontend/tests/dag-serializer.test.ts`

**Interfaces:**
- Produces:
  - `planToFlow(plan: AgentDAGPlan): { nodes: FlowNode[]; edges: FlowEdge[] }`
  - `flowToPlan(nodes: FlowNode[], edges: FlowEdge[]): AgentDAGPlan`
  - `detectCycles(nodes: FlowNode[], edges: FlowEdge[]): boolean`
  - `layoutGraphWithDagre(nodes: FlowNode[], edges: FlowEdge[], direction?: "LR" | "TB"): { nodes: FlowNode[]; edges: FlowEdge[] }`

- [ ] **Step 1: Install `@xyflow/react` and `@dagrejs/dagre`**

Run in `frontend/`:
```bash
npm install @xyflow/react @dagrejs/dagre
npm install --save-dev @types/dagre
```

- [ ] **Step 2: Write failing unit test for `dag-serializer`**

Write `frontend/tests/dag-serializer.test.ts`:
```typescript
import { describe, it, expect } from "vitest";
import { planToFlow, flowToPlan, detectCycles } from "@/lib/dag-serializer";
import { AgentDAGPlan } from "@/types/dag";

describe("DAG Serializer", () => {
  const samplePlan: AgentDAGPlan = {
    plan_id: "plan-123",
    goal: "Test research and synthesis workflow",
    rationale: "Sequential decomposition",
    nodes: [
      {
        node_id: "step_planner",
        agent_id: "planner",
        name: "Plan Goal",
        description: "Deconstruct objective",
        dependencies: [],
      },
      {
        node_id: "step_research",
        agent_id: "research",
        name: "Gather Data",
        description: "Fetch market trends",
        dependencies: ["step_planner"],
        optional: true,
      },
      {
        node_id: "step_validator",
        agent_id: "validator",
        name: "Validate Results",
        description: "Check output quality",
        dependencies: ["step_research"],
      },
    ],
  };

  it("converts AgentDAGPlan to React Flow nodes and edges correctly", () => {
    const { nodes, edges } = planToFlow(samplePlan);
    expect(nodes.length).toBe(3);
    expect(edges.length).toBe(2);
    expect(nodes[0].id).toBe("step_planner");
    expect(edges[0].source).toBe("step_planner");
    expect(edges[0].target).toBe("step_research");
  });

  it("converts Flow nodes and edges back to AgentDAGPlan cleanly", () => {
    const { nodes, edges } = planToFlow(samplePlan);
    const roundtripPlan = flowToPlan(nodes, edges, {
      plan_id: "plan-123",
      goal: samplePlan.goal,
      rationale: samplePlan.rationale,
    });
    expect(roundtripPlan.nodes.length).toBe(3);
    expect(roundtripPlan.nodes[1].dependencies).toContain("step_planner");
    expect(roundtripPlan.nodes[1].optional).toBe(true);
  });

  it("detects cyclic graphs and throws validation warning", () => {
    const cyclicEdges = [
      { id: "e1", source: "nodeA", target: "nodeB" },
      { id: "e2", source: "nodeB", target: "nodeC" },
      { id: "e3", source: "nodeC", target: "nodeA" },
    ];
    const nodes = [
      { id: "nodeA", position: { x: 0, y: 0 }, data: {} },
      { id: "nodeB", position: { x: 0, y: 0 }, data: {} },
      { id: "nodeC", position: { x: 0, y: 0 }, data: {} },
    ];
    expect(detectCycles(nodes as any, cyclicEdges as any)).toBe(true);
  });
});
```

- [ ] **Step 3: Implement `types/flow.ts` and `lib/dag-serializer.ts`**

Define flow node types, Dagre auto-layout positioning, topological sorting, cycle detection using Kahn's algorithm, and bidirectional serializer.

- [ ] **Step 4: Run unit tests to verify pass**

Run: `npx vitest run tests/dag-serializer.test.ts` or `npm test`
Expected: PASS

- [ ] **Step 5: Commit changes**

```bash
git add frontend/package.json frontend/package-lock.json frontend/types/flow.ts frontend/lib/dag-serializer.ts frontend/tests/dag-serializer.test.ts
git commit -m "feat(workflows): add flow types, Dagre layout engine and dag-serializer"
```

---

### Task 2: Zustand Canvas Store & Undo/Redo Engine

**Files:**
- Create: `frontend/stores/workflow-canvas-store.ts`
- Create: `frontend/tests/workflow-canvas-store.test.ts`

**Interfaces:**
- Consumes: `FlowNode`, `FlowEdge`, `AgentDAGPlan` from `types/flow.ts` and `types/dag.ts`
- Produces: `useWorkflowCanvasStore` with actions:
  - `setGraph(nodes, edges)`
  - `addNode(node)`
  - `updateNodeData(id, partialData)`
  - `removeNode(id)`
  - `connectNodes(connection)`
  - `applyLayout(direction)`
  - `undo()`, `redo()`, `canUndo`, `canRedo`
  - `updateNodeExecution(nodeId, record)`
  - `setWorkflowRunning(isRunning)`

- [ ] **Step 1: Write test for canvas store history and node operations**

Write `frontend/tests/workflow-canvas-store.test.ts`:
```typescript
import { describe, it, expect, beforeEach } from "vitest";
import { useWorkflowCanvasStore } from "@/stores/workflow-canvas-store";

describe("WorkflowCanvasStore", () => {
  beforeEach(() => {
    useWorkflowCanvasStore.getState().resetStore();
  });

  it("adds nodes and records undo history", () => {
    const store = useWorkflowCanvasStore.getState();
    expect(store.nodes.length).toBe(0);

    store.addNode({
      id: "node_1",
      type: "agentNode",
      position: { x: 100, y: 100 },
      data: { agent_id: "planner", label: "Planner" },
    });

    expect(useWorkflowCanvasStore.getState().nodes.length).toBe(1);
    expect(useWorkflowCanvasStore.getState().canUndo).toBe(true);

    useWorkflowCanvasStore.getState().undo();
    expect(useWorkflowCanvasStore.getState().nodes.length).toBe(0);

    useWorkflowCanvasStore.getState().redo();
    expect(useWorkflowCanvasStore.getState().nodes.length).toBe(1);
  });
});
```

- [ ] **Step 2: Implement `workflow-canvas-store.ts`**

Implement Zustand store with immutable past/future history stacks, node selection state, live telemetry mapper, and layout trigger.

- [ ] **Step 3: Run store tests**

Run: `npx vitest run tests/workflow-canvas-store.test.ts`
Expected: PASS

- [ ] **Step 4: Commit changes**

```bash
git add frontend/stores/workflow-canvas-store.ts frontend/tests/workflow-canvas-store.test.ts
git commit -m "feat(workflows): implement Zustand workflow canvas store with undo/redo"
```

---

### Task 3: Custom Node Suite & Animated Edge Components

**Files:**
- Create: `frontend/features/workflows/canvas/nodes/agent-node.tsx`
- Create: `frontend/features/workflows/canvas/nodes/logic-branch-node.tsx`
- Create: `frontend/features/workflows/canvas/nodes/evaluator-node.tsx`
- Create: `frontend/features/workflows/canvas/nodes/human-approval-node.tsx`
- Create: `frontend/features/workflows/canvas/nodes/webhook-node.tsx`
- Create: `frontend/features/workflows/canvas/edges/animated-flow-edge.tsx`
- Create: `frontend/features/workflows/canvas/nodes/index.ts`

**Interfaces:**
- Consumes: NodeProps from `@xyflow/react`, `useWorkflowCanvasStore`
- Produces: `nodeTypes` map (`agentNode`, `logicNode`, `evaluatorNode`, `approvalNode`, `webhookNode`) and `edgeTypes` map (`animatedEdge`).

- [ ] **Step 1: Implement `AnimatedFlowEdge`**

Create `animated-flow-edge.tsx` utilizing SVG `<path>` with Bézier calculations (`getBezierPath`), dynamic color states (Active: glowing cyan gradient + moving particle, Completed: solid emerald `#10b981`, Failed: red `#ef4444`, Default: dashed border).

- [ ] **Step 2: Implement `AgentNode`**

Create `agent-node.tsx` with Left/Right or Top/Bottom handles, role color badges, live running stopwatch ticker, model tier badge, token counter, and optional toggle.

- [ ] **Step 3: Implement `LogicBranchNode` & `EvaluatorNode`**

Create `logic-branch-node.tsx` (with multi-port True/False handles) and `evaluator-node.tsx` (with score threshold indicator).

- [ ] **Step 4: Implement `HumanApprovalNode` & `WebhookNode`**

Create `human-approval-node.tsx` (with inline Quick-Approve/Reject buttons and pulsing amber aura when active) and `webhook-node.tsx` (with endpoint URL pill).

- [ ] **Step 5: Export registry in `nodes/index.ts`**

Export `customNodeTypes` and `customEdgeTypes`.

- [ ] **Step 6: Commit changes**

```bash
git add frontend/features/workflows/canvas/
git commit -m "feat(workflows): create custom node suite and animated flow edge components"
```

---

### Task 4: Palette Sidebar & Interactive Flow Canvas

**Files:**
- Create: `frontend/features/workflows/canvas/node-palette-sidebar.tsx`
- Create: `frontend/features/workflows/canvas/canvas-toolbar.tsx`
- Create: `frontend/features/workflows/canvas/interactive-flow-canvas.tsx`

**Interfaces:**
- Consumes: `useWorkflowCanvasStore`, `customNodeTypes`, `customEdgeTypes`, `layoutGraphWithDagre`
- Produces:
  - `NodePaletteSidebar`: Drag-and-drop node template library.
  - `CanvasToolbar`: Quick actions (Auto-Layout, Zoom In/Out, Fit View, Undo/Redo, Validate Graph, Export).
  - `InteractiveFlowCanvas`: The main React Flow canvas with viewport projection, drop listener, and connection validators.

- [ ] **Step 1: Implement `NodePaletteSidebar`**

Categorized draggable cards with HTML5 `onDragStart={(e) => e.dataTransfer.setData('application/reactflow', type)}` for AI Agents, Logic, Evaluator, Approval, and Webhook.

- [ ] **Step 2: Implement `CanvasToolbar`**

Toolbar with icon buttons for Auto-Arrange (LR/TB), Fit View, Undo, Redo, Reset, and Zoom controls.

- [ ] **Step 3: Implement `InteractiveFlowCanvas`**

Wrap canvas in `ReactFlowProvider`. Handle `onDrop`, `onDragOver`, `onConnect`, `onNodesChange`, `onEdgesChange`, `isValidConnection` (prevent self-loops and duplicate edges), and render background grid & minimap.

- [ ] **Step 4: Commit changes**

```bash
git add frontend/features/workflows/canvas/node-palette-sidebar.tsx frontend/features/workflows/canvas/canvas-toolbar.tsx frontend/features/workflows/canvas/interactive-flow-canvas.tsx
git commit -m "feat(workflows): build node palette sidebar and interactive flow canvas"
```

---

### Task 5: Slide-Over Node Inspector & Telemetry Drawer

**Files:**
- Create: `frontend/features/workflows/canvas/workflow-node-inspector.tsx`

**Interfaces:**
- Consumes: Selected node ID from `useWorkflowCanvasStore`, live telemetry records from `nodeStates`.
- Produces: Slide-over drawer with 3 tabs:
  - Tab 1: **Configuration** (Prompt override, Model tier selection, temperature, timeout, retries).
  - Tab 2: **Live Stream & Logs** (Markdown rendered output, token breakdown, duration, execution history).
  - Tab 3: **Human-in-the-Loop Decisions** (Deliverable review, decision feedback notes, Approve/Reject action handlers).

- [ ] **Step 1: Implement `WorkflowNodeInspector`**

Build drawer using Radix UI / Sheet or slide-over with clean tabbed navigation, form bindings connected directly to Zustand store, and realtime log streaming viewer.

- [ ] **Step 2: Commit changes**

```bash
git add frontend/features/workflows/canvas/workflow-node-inspector.tsx
git commit -m "feat(workflows): implement slide-over node configuration and stream inspector"
```

---

### Task 6: Full Page Integration & Verification

**Files:**
- Modify: `frontend/features/workflows/dynamic-dag-builder.tsx`
- Modify: `frontend/features/workflows/dag-visualizer.tsx`
- Modify: `frontend/app/workflows/new/page.tsx`
- Modify: `frontend/app/workflows/[workflowId]/page.tsx`

**Interfaces:**
- Connects AI DAG Planner directly to the new `InteractiveFlowCanvas`.
- Binds live WebSocket events in `[workflowId]/page.tsx` to the canvas store.

- [ ] **Step 1: Update `dynamic-dag-builder.tsx`**

Replace legacy static SVG with new `InteractiveFlowCanvas` + `NodePaletteSidebar`, allowing users to generate via prompt and then freely drag/drop to customize.

- [ ] **Step 2: Upgrade `[workflowId]/page.tsx` (Monitor Page)**

Enable real-time edge animations, live node stopwatch timers, and inline approval gates connected to the WebSocket event stream.

- [ ] **Step 3: Run frontend build and lint check**

Run:
```bash
npm run lint
npm run build
```
Expected: Build succeeds with 0 errors.

- [ ] **Step 4: Commit changes**

```bash
git add frontend/
git commit -m "feat(workflows): integrate visual canvas into workflow builder and live monitor"
```

---

## Plan Self-Review

1. **Spec Coverage**:
   - AI generation & canvas editing: Covered in Tasks 1, 4, 6.
   - 5 Node Types (Agent, Logic, Evaluator, Human Approval, Webhook): Covered in Task 3.
   - Animated Edge Signaling & Live Telemetry: Covered in Tasks 3, 5, 6.
   - Bidirectional serialization: Covered in Task 1.
   - Slide-over inspector: Covered in Task 5.
2. **No Placeholders**: All tasks contain explicit file paths, interfaces, and concrete steps.
3. **Type Consistency**: `FlowNode`, `FlowEdge`, `AgentDAGPlan` consistently shared across store, serializer, and UI components.
