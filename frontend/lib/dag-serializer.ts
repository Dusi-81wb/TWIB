import dagre from "@dagrejs/dagre";
import { AgentDAGPlan, AgentNode } from "@/types/dag";
import {
  CustomFlowNode,
  CustomFlowEdge,
  AgentNodeData,
  FlowNodeType,
} from "@/types/flow";

export const NODE_WIDTH = 260;
export const NODE_HEIGHT = 140;

/**
 * Computes an automated topological / hierarchical layout using Dagre
 */
export function layoutGraphWithDagre(
  nodes: CustomFlowNode[],
  edges: CustomFlowEdge[],
  direction: "LR" | "TB" = "LR"
): { nodes: CustomFlowNode[]; edges: CustomFlowEdge[] } {
  if (!nodes.length) return { nodes: [], edges: [] };

  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  dagreGraph.setGraph({
    rankdir: direction,
    nodesep: 50,
    ranksep: 90,
    align: "UL",
  });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: NODE_WIDTH, height: NODE_HEIGHT });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const layoutedNodes: CustomFlowNode[] = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    return {
      ...node,
      position: {
        x: nodeWithPosition.x - NODE_WIDTH / 2,
        y: nodeWithPosition.y - NODE_HEIGHT / 2,
      },
    };
  });

  return { nodes: layoutedNodes, edges };
}

/**
 * Converts backend AgentDAGPlan into React Flow nodes and edges with Dagre layout
 */
export function planToFlow(
  plan: AgentDAGPlan,
  direction: "LR" | "TB" = "LR"
): { nodes: CustomFlowNode[]; edges: CustomFlowEdge[] } {
  if (!plan || !plan.nodes || plan.nodes.length === 0) {
    return { nodes: [], edges: [] };
  }

  const rawNodes: CustomFlowNode[] = plan.nodes.map((n) => {
    if (n.agent_id === "evaluator") {
      return {
        id: n.node_id,
        type: "evaluatorNode",
        position: { x: 0, y: 0 },
        data: {
          node_id: n.node_id,
          name: n.name || "LLM Judge Evaluator",
          metric: "accuracy",
          min_score: 80,
          status: "pending",
        },
      };
    }

    if (n.agent_id === "logic") {
      return {
        id: n.node_id,
        type: "logicNode",
        position: { x: 0, y: 0 },
        data: {
          node_id: n.node_id,
          name: n.name || "Conditional Branch",
          expression: "score >= 80",
          condition_type: "boolean",
          status: "pending",
        },
      };
    }

    if (n.agent_id === "approval") {
      return {
        id: n.node_id,
        type: "approvalNode",
        position: { x: 0, y: 0 },
        data: {
          node_id: n.node_id,
          name: n.name || "Human Review Gate",
          timeout_seconds: 300,
          default_action: "auto_approve",
          status: "pending",
        },
      };
    }

    if (n.agent_id === "webhook") {
      return {
        id: n.node_id,
        type: "webhookNode",
        position: { x: 0, y: 0 },
        data: {
          node_id: n.node_id,
          name: n.name || "External Webhook",
          url: "https://api.domain.com/events",
          method: "POST",
          status: "pending",
        },
      };
    }

    return {
      id: n.node_id,
      type: "agentNode",
      position: { x: 0, y: 0 },
      data: {
        node_id: n.node_id,
        agent_id: n.agent_id,
        name: n.name || n.agent_id,
        description: n.description,
        optional: n.optional ?? false,
        input_prompt_override: n.input_prompt_override ?? null,
        max_retries: n.max_retries ?? 2,
        model_tier: "standard",
        status: "pending",
        tokenCount: 0,
        durationSeconds: 0,
      },
    };
  });

  const rawEdges: CustomFlowEdge[] = [];
  plan.nodes.forEach((targetNode) => {
    if (targetNode.dependencies && targetNode.dependencies.length > 0) {
      targetNode.dependencies.forEach((sourceId) => {
        rawEdges.push({
          id: `e-${sourceId}-${targetNode.node_id}`,
          source: sourceId,
          target: targetNode.node_id,
          type: "animatedEdge",
          data: { status: "pending" },
        });
      });
    }
  });

  return layoutGraphWithDagre(rawNodes, rawEdges, direction);
}

/**
 * Serializes current React Flow canvas nodes & edges back into a valid AgentDAGPlan
 */
export function flowToPlan(
  nodes: CustomFlowNode[],
  edges: CustomFlowEdge[],
  basePlan?: Partial<AgentDAGPlan>
): AgentDAGPlan {
  const dependenciesMap = new Map<string, string[]>();
  nodes.forEach((n) => dependenciesMap.set(n.id, []));

  edges.forEach((edge) => {
    const existing = dependenciesMap.get(edge.target) || [];
    if (!existing.includes(edge.source)) {
      existing.push(edge.source);
    }
    dependenciesMap.set(edge.target, existing);
  });

  const agentNodes: AgentNode[] = nodes.map((n) => {
    const data = n.data as AgentNodeData;
    return {
      node_id: n.id,
      agent_id: data.agent_id || "planner",
      name: data.name || n.id,
      description: data.description,
      dependencies: dependenciesMap.get(n.id) || [],
      optional: !!data.optional,
      input_prompt_override: data.input_prompt_override || null,
      max_retries: data.max_retries ?? 2,
      retry_delay_seconds: 2,
    };
  });

  return {
    plan_id: basePlan?.plan_id || `plan-${Date.now()}`,
    goal: basePlan?.goal || "Custom visual workflow execution",
    rationale: basePlan?.rationale || "Configured via interactive visual canvas",
    nodes: agentNodes,
    execution_strategy: basePlan?.execution_strategy || "dynamic_dag",
    metadata: {
      ...basePlan?.metadata,
      visual_editor_version: "2.0",
      layout_direction: "LR",
    },
  };
}

/**
 * Cycle detection using Kahn's algorithm (topological sort)
 * Returns true if a cycle exists (invalid DAG), false if acyclic (valid DAG)
 */
export function detectCycles(
  nodes: CustomFlowNode[],
  edges: CustomFlowEdge[]
): boolean {
  if (nodes.length <= 1) return false;

  const inDegree = new Map<string, number>();
  const adjList = new Map<string, string[]>();

  nodes.forEach((n) => {
    inDegree.set(n.id, 0);
    adjList.set(n.id, []);
  });

  edges.forEach((e) => {
    if (inDegree.has(e.target) && adjList.has(e.source)) {
      inDegree.set(e.target, (inDegree.get(e.target) || 0) + 1);
      adjList.get(e.source)!.push(e.target);
    }
  });

  const queue: string[] = [];
  inDegree.forEach((deg, nodeId) => {
    if (deg === 0) queue.push(nodeId);
  });

  let visitedCount = 0;
  while (queue.length > 0) {
    const current = queue.shift()!;
    visitedCount++;

    const neighbors = adjList.get(current) || [];
    for (const neighbor of neighbors) {
      const updatedDeg = (inDegree.get(neighbor) || 0) - 1;
      inDegree.set(neighbor, updatedDeg);
      if (updatedDeg === 0) {
        queue.push(neighbor);
      }
    }
  }

  // If visited count < total nodes, there is a cycle!
  return visitedCount !== nodes.length;
}
