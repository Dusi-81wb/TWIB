import { NodeTypes, EdgeTypes } from "@xyflow/react";
import { AgentNode } from "./agent-node";
import { LogicBranchNode } from "./logic-branch-node";
import { EvaluatorNode } from "./evaluator-node";
import { HumanApprovalNode } from "./human-approval-node";
import { WebhookNode } from "./webhook-node";
import { AnimatedFlowEdge } from "../edges/animated-flow-edge";

export const customNodeTypes: NodeTypes = {
  agentNode: AgentNode,
  logicNode: LogicBranchNode,
  evaluatorNode: EvaluatorNode,
  approvalNode: HumanApprovalNode,
  webhookNode: WebhookNode,
};

export const customEdgeTypes: EdgeTypes = {
  animatedEdge: AnimatedFlowEdge,
};

export * from "./agent-node";
export * from "./logic-branch-node";
export * from "./evaluator-node";
export * from "./human-approval-node";
export * from "./webhook-node";
export * from "../edges/animated-flow-edge";
