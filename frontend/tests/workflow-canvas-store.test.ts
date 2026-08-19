import { describe, it, expect, beforeEach } from "vitest";
import { useWorkflowCanvasStore } from "../stores/workflow-canvas-store";
import { CustomFlowNode } from "../types/flow";

describe("WorkflowCanvasStore", () => {
  beforeEach(() => {
    useWorkflowCanvasStore.getState().resetStore();
  });

  it("adds nodes and records undo history", () => {
    const store = useWorkflowCanvasStore.getState();
    expect(store.nodes.length).toBe(0);

    const testNode: CustomFlowNode = {
      id: "node_1",
      type: "agentNode",
      position: { x: 100, y: 100 },
      data: {
        node_id: "node_1",
        agent_id: "planner",
        name: "Goal Planner",
      },
    };

    store.addNode(testNode);

    expect(useWorkflowCanvasStore.getState().nodes.length).toBe(1);
    expect(useWorkflowCanvasStore.getState().canUndo).toBe(true);

    useWorkflowCanvasStore.getState().undo();
    expect(useWorkflowCanvasStore.getState().nodes.length).toBe(0);
    expect(useWorkflowCanvasStore.getState().canRedo).toBe(true);

    useWorkflowCanvasStore.getState().redo();
    expect(useWorkflowCanvasStore.getState().nodes.length).toBe(1);
  });

  it("connects nodes and removes nodes with connected edges", () => {
    const store = useWorkflowCanvasStore.getState();
    store.addNode({
      id: "n1",
      type: "agentNode",
      position: { x: 0, y: 0 },
      data: { node_id: "n1", agent_id: "planner", name: "A" },
    });
    store.addNode({
      id: "n2",
      type: "agentNode",
      position: { x: 300, y: 0 },
      data: { node_id: "n2", agent_id: "research", name: "B" },
    });

    store.connectNodes({ source: "n1", target: "n2", sourceHandle: null, targetHandle: null });
    expect(useWorkflowCanvasStore.getState().edges.length).toBe(1);
    expect(useWorkflowCanvasStore.getState().edges[0].id).toBe("e-n1-n2");

    // Remove n1 should also cascade remove edge e-n1-n2
    store.removeNode("n1");
    expect(useWorkflowCanvasStore.getState().nodes.length).toBe(1);
    expect(useWorkflowCanvasStore.getState().edges.length).toBe(0);
  });

  it("updates live node telemetry during workflow execution", () => {
    const store = useWorkflowCanvasStore.getState();
    store.addNode({
      id: "agent_analyst",
      type: "agentNode",
      position: { x: 0, y: 0 },
      data: { node_id: "agent_analyst", agent_id: "analyst", name: "Analyst" },
    });

    store.updateNodeExecution("agent_analyst", {
      node_id: "agent_analyst",
      agent_id: "analyst",
      status: "running",
      duration_seconds: 1.5,
      retry_attempts: 0,
    });

    const updatedNode = useWorkflowCanvasStore.getState().nodes.find((n) => n.id === "agent_analyst");
    expect(updatedNode?.data.status).toBe("running");
    expect(updatedNode?.data.durationSeconds).toBe(1.5);
    expect(useWorkflowCanvasStore.getState().activeNodeId).toBe("agent_analyst");
  });
});
