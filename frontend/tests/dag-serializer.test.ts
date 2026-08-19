import { describe, it, expect } from "vitest";
import { planToFlow, flowToPlan, detectCycles } from "../lib/dag-serializer";
import { AgentDAGPlan } from "../types/dag";
import { CustomFlowNode, CustomFlowEdge } from "../types/flow";

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
    const researchNode = roundtripPlan.nodes.find((n) => n.node_id === "step_research");
    expect(researchNode).toBeDefined();
    expect(researchNode?.dependencies).toContain("step_planner");
    expect(researchNode?.optional).toBe(true);
  });

  it("detects cyclic graphs and returns true", () => {
    const cyclicEdges: CustomFlowEdge[] = [
      { id: "e1", source: "nodeA", target: "nodeB" },
      { id: "e2", source: "nodeB", target: "nodeC" },
      { id: "e3", source: "nodeC", target: "nodeA" },
    ];
    const nodes: CustomFlowNode[] = [
      { id: "nodeA", type: "agentNode", position: { x: 0, y: 0 }, data: { node_id: "nodeA", agent_id: "planner", name: "A" } },
      { id: "nodeB", type: "agentNode", position: { x: 0, y: 0 }, data: { node_id: "nodeB", agent_id: "research", name: "B" } },
      { id: "nodeC", type: "agentNode", position: { x: 0, y: 0 }, data: { node_id: "nodeC", agent_id: "validator", name: "C" } },
    ];
    expect(detectCycles(nodes, cyclicEdges)).toBe(true);
  });

  it("detects acyclic graphs and returns false", () => {
    const validEdges: CustomFlowEdge[] = [
      { id: "e1", source: "nodeA", target: "nodeB" },
      { id: "e2", source: "nodeA", target: "nodeC" },
      { id: "e3", source: "nodeB", target: "nodeD" },
      { id: "e4", source: "nodeC", target: "nodeD" },
    ];
    const nodes: CustomFlowNode[] = [
      { id: "nodeA", type: "agentNode", position: { x: 0, y: 0 }, data: { node_id: "nodeA", agent_id: "planner", name: "A" } },
      { id: "nodeB", type: "agentNode", position: { x: 0, y: 0 }, data: { node_id: "nodeB", agent_id: "research", name: "B" } },
      { id: "nodeC", type: "agentNode", position: { x: 0, y: 0 }, data: { node_id: "nodeC", agent_id: "analyst", name: "C" } },
      { id: "nodeD", type: "agentNode", position: { x: 0, y: 0 }, data: { node_id: "nodeD", agent_id: "validator", name: "D" } },
    ];
    expect(detectCycles(nodes, validEdges)).toBe(false);
  });
});
