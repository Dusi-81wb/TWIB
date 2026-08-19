import { create } from "zustand";
import {
  Connection,
  EdgeChange,
  NodeChange,
  applyNodeChanges,
  applyEdgeChanges,
  addEdge,
} from "@xyflow/react";
import { CustomFlowNode, CustomFlowEdge, AgentNodeData } from "@/types/flow";
import { AgentDAGPlan, DAGNodeStatus, NodeExecutionRecord } from "@/types/dag";
import {
  planToFlow,
  flowToPlan,
  layoutGraphWithDagre,
} from "@/lib/dag-serializer";

const MAX_HISTORY = 30;

interface HistorySnapshot {
  nodes: CustomFlowNode[];
  edges: CustomFlowEdge[];
}

export interface WorkflowCanvasState {
  nodes: CustomFlowNode[];
  edges: CustomFlowEdge[];
  selectedNodeId: string | null;
  activeNodeId: string | null;
  isWorkflowRunning: boolean;
  isDirty: boolean;
  canUndo: boolean;
  canRedo: boolean;
  past: HistorySnapshot[];
  future: HistorySnapshot[];

  // Actions
  setGraph: (
    nodes: CustomFlowNode[],
    edges: CustomFlowEdge[],
    recordHistory?: boolean
  ) => void;
  loadPlan: (plan: AgentDAGPlan) => void;
  exportPlan: (basePlan?: Partial<AgentDAGPlan>) => AgentDAGPlan;
  addNode: (node: CustomFlowNode) => void;
  updateNodeData: (id: string, partialData: Partial<AgentNodeData>) => void;
  removeNode: (id: string) => void;
  connectNodes: (connection: Connection) => void;
  onNodesChange: (changes: NodeChange<CustomFlowNode>[]) => void;
  onEdgesChange: (changes: EdgeChange<CustomFlowEdge>[]) => void;
  selectNode: (id: string | null) => void;
  applyLayout: (direction?: "LR" | "TB") => void;
  undo: () => void;
  redo: () => void;
  updateNodeExecution: (nodeId: string, record: NodeExecutionRecord) => void;
  setWorkflowRunning: (isRunning: boolean) => void;
  resetStore: () => void;
}

export const useWorkflowCanvasStore = create<WorkflowCanvasState>((set, get) => ({
  nodes: [],
  edges: [],
  selectedNodeId: null,
  activeNodeId: null,
  isWorkflowRunning: false,
  isDirty: false,
  canUndo: false,
  canRedo: false,
  past: [],
  future: [],

  setGraph: (nodes, edges, recordHistory = true) => {
    const { nodes: currentNodes, edges: currentEdges, past } = get();
    const newPast = recordHistory
      ? [...past, { nodes: currentNodes, edges: currentEdges }].slice(
          -MAX_HISTORY
        )
      : past;

    set({
      nodes,
      edges,
      isDirty: true,
      past: newPast,
      future: recordHistory ? [] : get().future,
      canUndo: newPast.length > 0,
      canRedo: false,
    });
  },

  loadPlan: (plan) => {
    const { nodes, edges } = planToFlow(plan);
    set({
      nodes,
      edges,
      selectedNodeId: null,
      activeNodeId: null,
      isDirty: false,
      past: [],
      future: [],
      canUndo: false,
      canRedo: false,
    });
  },

  exportPlan: (basePlan) => {
    const { nodes, edges } = get();
    return flowToPlan(nodes, edges, basePlan);
  },

  addNode: (node) => {
    const { nodes, edges, past } = get();
    const newPast = [...past, { nodes, edges }].slice(-MAX_HISTORY);
    const newNodes = [...nodes, node];

    set({
      nodes: newNodes,
      selectedNodeId: node.id,
      isDirty: true,
      past: newPast,
      future: [],
      canUndo: true,
      canRedo: false,
    });
  },

  updateNodeData: (id, partialData) => {
    const { nodes, edges, past } = get();
    const newPast = [...past, { nodes, edges }].slice(-MAX_HISTORY);
    const newNodes = nodes.map((n) =>
      n.id === id ? { ...n, data: { ...n.data, ...partialData } } : n
    ) as CustomFlowNode[];

    set({
      nodes: newNodes,
      isDirty: true,
      past: newPast,
      future: [],
      canUndo: true,
      canRedo: false,
    });
  },

  removeNode: (id) => {
    const { nodes, edges, past, selectedNodeId } = get();
    const newPast = [...past, { nodes, edges }].slice(-MAX_HISTORY);
    const newNodes = nodes.filter((n) => n.id !== id);
    const newEdges = edges.filter((e) => e.source !== id && e.target !== id);

    set({
      nodes: newNodes,
      edges: newEdges,
      selectedNodeId: selectedNodeId === id ? null : selectedNodeId,
      isDirty: true,
      past: newPast,
      future: [],
      canUndo: true,
      canRedo: false,
    });
  },

  connectNodes: (connection) => {
    const { nodes, edges, past } = get();
    if (!connection.source || !connection.target) return;
    if (connection.source === connection.target) return;

    // Check if edge already exists
    const exists = edges.some(
      (e) => e.source === connection.source && e.target === connection.target
    );
    if (exists) return;

    const newPast = [...past, { nodes, edges }].slice(-MAX_HISTORY);
    const newEdge: CustomFlowEdge = {
      ...connection,
      id: `e-${connection.source}-${connection.target}`,
      type: "animatedEdge",
      data: { status: "pending" },
    } as CustomFlowEdge;

    const newEdges = addEdge(newEdge, edges) as CustomFlowEdge[];

    set({
      edges: newEdges,
      isDirty: true,
      past: newPast,
      future: [],
      canUndo: true,
      canRedo: false,
    });
  },

  onNodesChange: (changes) => {
    const { nodes } = get();
    const updatedNodes = applyNodeChanges(
      changes,
      nodes
    ) as CustomFlowNode[];
    set({ nodes: updatedNodes });
  },

  onEdgesChange: (changes) => {
    const { edges } = get();
    const updatedEdges = applyEdgeChanges(
      changes,
      edges
    ) as CustomFlowEdge[];
    set({ edges: updatedEdges });
  },

  selectNode: (id) => {
    set({ selectedNodeId: id });
  },

  applyLayout: (direction = "LR") => {
    const { nodes, edges, past } = get();
    const newPast = [...past, { nodes, edges }].slice(-MAX_HISTORY);
    const layouted = layoutGraphWithDagre(nodes, edges, direction);

    set({
      nodes: layouted.nodes,
      edges: layouted.edges,
      isDirty: true,
      past: newPast,
      future: [],
      canUndo: true,
      canRedo: false,
    });
  },

  undo: () => {
    const { past, future, nodes, edges } = get();
    if (past.length === 0) return;

    const previous = past[past.length - 1];
    const newPast = past.slice(0, past.length - 1);
    const newFuture = [{ nodes, edges }, ...future].slice(0, MAX_HISTORY);

    set({
      nodes: previous.nodes,
      edges: previous.edges,
      past: newPast,
      future: newFuture,
      canUndo: newPast.length > 0,
      canRedo: true,
      isDirty: true,
    });
  },

  redo: () => {
    const { past, future, nodes, edges } = get();
    if (future.length === 0) return;

    const next = future[0];
    const newFuture = future.slice(1);
    const newPast = [...past, { nodes, edges }].slice(-MAX_HISTORY);

    set({
      nodes: next.nodes,
      edges: next.edges,
      past: newPast,
      future: newFuture,
      canUndo: true,
      canRedo: newFuture.length > 0,
      isDirty: true,
    });
  },

  updateNodeExecution: (nodeId, record) => {
    const { nodes, edges } = get();
    const newNodes = nodes.map((n) => {
      if (n.id === nodeId) {
        return {
          ...n,
          data: {
            ...n.data,
            status: record.status,
            executionRecord: record,
            durationSeconds: record.duration_seconds,
          },
        };
      }
      return n;
    }) as CustomFlowNode[];

    // Also update edge active/completed glow
    const newEdges = edges.map((e) => {
      if (e.source === nodeId) {
        if (record.status === "completed") {
          return {
            ...e,
            data: { ...e.data, status: "completed" as DAGNodeStatus },
          };
        } else if (record.status === "running") {
          return {
            ...e,
            data: { ...e.data, status: "running" as DAGNodeStatus },
          };
        }
      }
      return e;
    }) as CustomFlowEdge[];

    set({
      nodes: newNodes,
      edges: newEdges,
      activeNodeId: record.status === "running" ? nodeId : get().activeNodeId,
    });
  },

  setWorkflowRunning: (isRunning) => {
    set({ isWorkflowRunning: isRunning });
  },

  resetStore: () => {
    set({
      nodes: [],
      edges: [],
      selectedNodeId: null,
      activeNodeId: null,
      isWorkflowRunning: false,
      isDirty: false,
      canUndo: false,
      canRedo: false,
      past: [],
      future: [],
    });
  },
}));
