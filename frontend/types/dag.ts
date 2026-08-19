/**
 * Multi-Agent Dynamic DAG Types and Layout Definitions for TWIB Frontend.
 */

export type DAGNodeStatus = "pending" | "running" | "completed" | "failed" | "skipped";

export interface AgentNode {
  node_id: string;
  agent_id: string;
  name: string;
  description?: string;
  dependencies: string[];
  input_prompt_override?: string | null;
  optional?: boolean;
  max_retries?: number;
  retry_delay_seconds?: number;
}

export interface AgentDAGPlan {
  plan_id: string;
  goal: string;
  rationale?: string;
  nodes: AgentNode[];
  execution_strategy?: string;
  metadata?: Record<string, any>;
}

export interface NodeExecutionRecord {
  node_id: string;
  agent_id: string;
  status: DAGNodeStatus;
  duration_seconds: number;
  retry_attempts: number;
  result?: any;
  error?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
}

export interface DAGExecutionResult {
  plan_id: string;
  goal: string;
  status: DAGNodeStatus;
  node_results: Record<string, NodeExecutionRecord>;
  final_result?: any;
  summary?: string;
  total_duration_seconds: number;
  execution_graph: Record<string, string[]>;
}

export interface DAGLayoutNode {
  node: AgentNode;
  status: DAGNodeStatus;
  record?: NodeExecutionRecord;
  x: number;
  y: number;
  width: number;
  height: number;
  wave: number;
}

export interface DAGLayoutEdge {
  id: string;
  fromNodeId: string;
  toNodeId: string;
  fromPoint: { x: number; y: number };
  toPoint: { x: number; y: number };
  isActive: boolean;
}
