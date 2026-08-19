"use client";

import React, { useCallback, useRef } from "react";
import {
  ReactFlow,
  ReactFlowProvider,
  Background,
  MiniMap,
  BackgroundVariant,
  useReactFlow,
  Connection,
  Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { customNodeTypes, customEdgeTypes } from "./nodes";
import { CanvasToolbar } from "./canvas-toolbar";
import { useWorkflowCanvasStore } from "@/stores/workflow-canvas-store";
import { CustomFlowNode, FlowNodeType } from "@/types/flow";
import { cn } from "@/lib/utils";

interface InteractiveFlowCanvasProps {
  className?: string;
  isReadOnly?: boolean;
  onAutoPlan?: () => void;
  onSelectNode?: (node: CustomFlowNode | null) => void;
}

function FlowCanvasInternal({
  className,
  isReadOnly = false,
  onAutoPlan,
  onSelectNode,
}: InteractiveFlowCanvasProps) {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const { screenToFlowPosition } = useReactFlow();

  const {
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    connectNodes,
    addNode,
    selectNode,
  } = useWorkflowCanvasStore();

  const onConnect = useCallback(
    (connection: Connection) => {
      if (isReadOnly) return;
      connectNodes(connection);
    },
    [isReadOnly, connectNodes]
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      if (isReadOnly) return;

      const type = event.dataTransfer.getData(
        "application/reactflow/type"
      ) as FlowNodeType;
      const rawData = event.dataTransfer.getData("application/reactflow/data");

      if (!type) return;

      let customData = {};
      try {
        if (rawData) customData = JSON.parse(rawData);
      } catch (err) {
        console.error("Failed to parse node data on drop:", err);
      }

      const position = screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const uniqueId = `node_${Date.now()}`;
      const newNode: CustomFlowNode = {
        id: uniqueId,
        type,
        position,
        data: {
          node_id: uniqueId,
          name: `${type.replace("Node", "")}`,
          status: "pending",
          ...customData,
        } as any,
      };

      addNode(newNode);
      selectNode(uniqueId);
      onSelectNode?.(newNode);
    },
    [isReadOnly, screenToFlowPosition, addNode, selectNode, onSelectNode]
  );

  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      selectNode(node.id);
      onSelectNode?.(node as CustomFlowNode);
    },
    [selectNode, onSelectNode]
  );

  const handlePaneClick = useCallback(() => {
    selectNode(null);
    onSelectNode?.(null);
  }, [selectNode, onSelectNode]);

  return (
    <div
      ref={reactFlowWrapper}
      className={cn(
        "relative w-full h-[520px] lg:h-[600px] rounded-xl border border-border/80 bg-slate-950/60 overflow-hidden shadow-inner",
        className
      )}
      onDragOver={onDragOver}
      onDrop={onDrop}
    >
      <CanvasToolbar onAutoPlan={onAutoPlan} />

      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={isReadOnly ? undefined : onNodesChange}
        onEdgesChange={isReadOnly ? undefined : onEdgesChange}
        onConnect={onConnect}
        onNodeClick={handleNodeClick}
        onPaneClick={handlePaneClick}
        nodeTypes={customNodeTypes}
        edgeTypes={customEdgeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        snapToGrid={true}
        snapGrid={[16, 16]}
        nodesDraggable={!isReadOnly}
        nodesConnectable={!isReadOnly}
        elementsSelectable={true}
        proOptions={{ hideAttribution: true }}
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={20}
          size={1.2}
          color="#334155"
        />

        <MiniMap
          nodeStrokeWidth={2}
          nodeColor={(n) => {
            if (n.type === "agentNode") return "#8b5cf6";
            if (n.type === "logicNode") return "#06b6d4";
            if (n.type === "evaluatorNode") return "#f59e0b";
            if (n.type === "approvalNode") return "#f97316";
            if (n.type === "webhookNode") return "#0ea5e9";
            return "#64748b";
          }}
          maskColor="rgba(15, 23, 42, 0.75)"
          className="!bg-slate-900/90 !border !border-border/60 !rounded-lg !shadow-md"
        />
      </ReactFlow>
    </div>
  );
}

export function InteractiveFlowCanvas(props: InteractiveFlowCanvasProps) {
  return (
    <ReactFlowProvider>
      <FlowCanvasInternal {...props} />
    </ReactFlowProvider>
  );
}
