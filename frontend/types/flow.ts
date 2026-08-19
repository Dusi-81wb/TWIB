import { Node, Edge } from "@xyflow/react";
import { DAGNodeStatus, NodeExecutionRecord } from "./dag";

export type FlowNodeType =
  | "agentNode"
  | "logicNode"
  | "evaluatorNode"
  | "approvalNode"
  | "webhookNode";

export interface AgentNodeData extends Record<string, unknown> {
  node_id: string;
  agent_id: string;
  name: string;
  description?: string;
  optional?: boolean;
  model_tier?: "fast" | "standard" | "pro";
  model_name?: string;
  temperature?: number;
  input_prompt_override?: string | null;
  max_retries?: number;
  timeout_seconds?: number;
  status?: DAGNodeStatus;
  executionRecord?: NodeExecutionRecord;
  tokenCount?: number;
  costUSD?: number;
  durationSeconds?: number;
  isStreaming?: boolean;
}

export interface LogicBranchNodeData extends Record<string, unknown> {
  node_id: string;
  name: string;
  expression: string;
  condition_type: "jsonpath" | "boolean" | "regex";
  status?: DAGNodeStatus;
  executionRecord?: NodeExecutionRecord;
}

export interface EvaluatorJudgeNodeData extends Record<string, unknown> {
  node_id: string;
  name: string;
  metric: "accuracy" | "completeness" | "safety" | "schema_compliance";
  min_score: number;
  current_score?: number;
  status?: DAGNodeStatus;
  executionRecord?: NodeExecutionRecord;
}

export interface HumanApprovalNodeData extends Record<string, unknown> {
  node_id: string;
  name: string;
  description?: string;
  timeout_seconds: number;
  default_action: "auto_approve" | "auto_reject";
  status?: DAGNodeStatus;
  executionRecord?: NodeExecutionRecord;
  decision?: "approved" | "rejected" | "pending";
  feedback_notes?: string;
}

export interface WebhookActionNodeData extends Record<string, unknown> {
  node_id: string;
  name: string;
  url: string;
  method: "POST" | "GET" | "PUT";
  headers?: Record<string, string>;
  status?: DAGNodeStatus;
  executionRecord?: NodeExecutionRecord;
}

export type CustomFlowNode =
  | Node<AgentNodeData, "agentNode">
  | Node<LogicBranchNodeData, "logicNode">
  | Node<EvaluatorJudgeNodeData, "evaluatorNode">
  | Node<HumanApprovalNodeData, "approvalNode">
  | Node<WebhookActionNodeData, "webhookNode">;

export interface AnimatedEdgeData extends Record<string, unknown> {
  status?: DAGNodeStatus | "active";
  label?: string;
  conditionHandle?: "true" | "false" | "pass" | "retry" | "default";
}

export type CustomFlowEdge = Edge<AnimatedEdgeData>;
