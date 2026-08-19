"use client";

import React, { useEffect } from "react";
import { AgentDAGPlan, AgentNode, NodeExecutionRecord } from "@/types/dag";
import { CustomFlowNode } from "@/types/flow";
import { InteractiveFlowCanvas } from "./canvas/interactive-flow-canvas";
import { useWorkflowCanvasStore } from "@/stores/workflow-canvas-store";
import { cn } from "@/lib/utils";

interface DAGVisualizerProps {
  plan?: AgentDAGPlan | null;
  nodeStates?: Record<string, NodeExecutionRecord>;
  activeNodeId?: string | null;
  onSelectNode?: (node: AgentNode, record?: NodeExecutionRecord) => void;
  className?: string;
  isInteractive?: boolean;
}

export function DAGVisualizer({
  plan,
  nodeStates = {},
  activeNodeId,
  onSelectNode,
  className,
  isInteractive = true,
}: DAGVisualizerProps) {
  const { loadPlan, updateNodeExecution, nodes } = useWorkflowCanvasStore();

  // Load initial or changed plan into canvas store
  useEffect(() => {
    if (plan && plan.nodes && plan.nodes.length > 0) {
      loadPlan(plan);
    }
  }, [plan, loadPlan]);

  // Sync execution status from nodeStates and activeNodeId
  useEffect(() => {
    if (!nodeStates || Object.keys(nodeStates).length === 0) return;

    Object.entries(nodeStates).forEach(([nodeId, record]) => {
      updateNodeExecution(nodeId, record);
    });
  }, [nodeStates, updateNodeExecution]);

  const handleSelectNode = (flowNode: CustomFlowNode | null) => {
    if (!flowNode || !plan) return;
    const originalNode = plan.nodes.find((n) => n.node_id === flowNode.id) || {
      node_id: flowNode.id,
      agent_id: (flowNode.data as any)?.agent_id || "planner",
      name: (flowNode.data as any)?.name || flowNode.id,
      dependencies: [],
    };
    const executionRecord = nodeStates[flowNode.id];
    onSelectNode?.(originalNode, executionRecord);
  };

  return (
    <div className={cn("relative w-full", className)}>
      <InteractiveFlowCanvas
        isReadOnly={!isInteractive}
        onSelectNode={handleSelectNode}
        className="h-[480px] lg:h-[540px]"
      />
    </div>
  );
}
