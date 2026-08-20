"use client";

import React, { useState, useEffect } from "react";
import { AgentDAGPlan } from "@/types/dag";
import { CustomFlowNode } from "@/types/flow";
import { InteractiveFlowCanvas } from "./canvas/interactive-flow-canvas";
import { NodePaletteSidebar } from "./canvas/node-palette-sidebar";
import { WorkflowNodeInspector } from "./canvas/workflow-node-inspector";
import { useWorkflowCanvasStore } from "@/stores/workflow-canvas-store";
import { agentService } from "@/services/agent.service";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Sparkles,
  Loader2,
  Sliders,
  Layers,
  Info,
  ChevronRight,
  PanelLeftClose,
  PanelLeft,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface DynamicDAGBuilderProps {
  initialGoal?: string;
  onPlanChange?: (plan: AgentDAGPlan) => void;
  className?: string;
}

export function DynamicDAGBuilder({
  initialGoal = "",
  onPlanChange,
  className,
}: DynamicDAGBuilderProps) {
  const [goal, setGoal] = useState(initialGoal);
  const [isPlanning, setIsPlanning] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [selectedNode, setSelectedNode] = useState<CustomFlowNode | null>(null);
  const [isInspectorOpen, setIsInspectorOpen] = useState(false);
  const [aiRationale, setAiRationale] = useState<string | null>(null);

  const {
    nodes,
    edges,
    loadPlan,
    exportPlan,
    selectedNodeId,
  } = useWorkflowCanvasStore();

  useEffect(() => {
    if (initialGoal) setGoal(initialGoal);
  }, [initialGoal]);

  const onPlanChangeRef = React.useRef(onPlanChange);
  useEffect(() => {
    onPlanChangeRef.current = onPlanChange;
  }, [onPlanChange]);

  const lastPlanSignatureRef = React.useRef<string>("");

  // Sync plan changes to parent only when graph content actually changes
  useEffect(() => {
    if (nodes.length > 0) {
      const signature = JSON.stringify({
        nodes: nodes.map((n) => ({
          id: n.id,
          type: n.type,
          data: n.data,
        })),
        edges: edges.map((e) => ({
          id: e.id,
          source: e.source,
          target: e.target,
        })),
        goal: goal || "",
        rationale: aiRationale || "",
      });

      if (signature !== lastPlanSignatureRef.current) {
        lastPlanSignatureRef.current = signature;
        const plan = exportPlan({
          goal: goal || "Custom visual multi-agent workflow",
          rationale: aiRationale || "Visual interactive DAG",
        });
        onPlanChangeRef.current?.(plan);
      }
    }
  }, [nodes, edges, goal, aiRationale, exportPlan]);


  const handleGeneratePlan = async () => {
    const targetGoal = goal?.trim() || initialGoal?.trim();
    if (!targetGoal) return;
    setIsPlanning(true);
    try {
      const plan = await agentService.planDAG(targetGoal);
      setAiRationale(plan.rationale || null);
      loadPlan(plan);
      onPlanChange?.(plan);
    } catch (err) {
      console.error("Failed to plan DAG:", err);
    } finally {
      setIsPlanning(false);
    }
  };

  const handleSelectNode = (node: CustomFlowNode | null) => {
    setSelectedNode(node);
    setIsInspectorOpen(!!node);
  };

  const activeSelectedNode =
    selectedNode || nodes.find((n) => n.id === selectedNodeId) || null;

  return (
    <div className={cn("space-y-4 flex flex-col", className)}>
      {/* Top Banner & Generation Trigger */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-4 rounded-xl border border-primary/20 bg-primary/5 backdrop-blur-xs shadow-xs">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary animate-pulse" />
            <h4 className="text-xs font-bold text-foreground uppercase tracking-wider">
              Visual Multi-Agent Canvas Studio
            </h4>
            <Badge className="bg-primary/20 text-primary border-primary/30 text-[10px]">
              AI + Drag & Drop
            </Badge>
          </div>
          <p className="text-xs text-muted-foreground">
            Generate with AI or drag agents, logic branches, and evaluators onto the canvas.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="gap-1.5 text-xs text-muted-foreground hover:text-foreground"
          >
            {isSidebarOpen ? (
              <>
                <PanelLeftClose className="h-3.5 w-3.5" />
                <span className="hidden sm:inline">Hide Palette</span>
              </>
            ) : (
              <>
                <PanelLeft className="h-3.5 w-3.5" />
                <span className="hidden sm:inline">Show Palette</span>
              </>
            )}
          </Button>

          <Button
            type="button"
            onClick={handleGeneratePlan}
            disabled={isPlanning || !goal.trim()}
            size="sm"
            className="gap-2 shadow-xs bg-primary text-primary-foreground hover:bg-primary/90"
          >
            {isPlanning ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                Planning Graph...
              </>
            ) : (
              <>
                <Sparkles className="h-3.5 w-3.5" />
                {nodes.length > 0 ? "AI Re-Plan DAG" : "AI Generate DAG"}
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Rationale and Strategy Card */}
      {aiRationale && (
        <div className="p-3 rounded-lg bg-muted/30 border border-border/50 text-xs text-muted-foreground flex items-start gap-2.5">
          <Info className="h-4 w-4 text-primary shrink-0 mt-0.5" />
          <div>
            <strong className="text-foreground font-semibold block mb-0.5">
              AI Routing Strategy:
            </strong>
            {aiRationale}
          </div>
        </div>
      )}

      {/* Main Studio Canvas Layout */}
      <div className="flex rounded-xl border border-border/80 bg-card overflow-hidden h-[600px] shadow-sm relative">
        {/* Left Drag-and-Drop Palette */}
        {isSidebarOpen && <NodePaletteSidebar />}

        {/* Interactive Infinite Flow Canvas */}
        <div className="flex-1 h-full relative">
          <InteractiveFlowCanvas
            onAutoPlan={handleGeneratePlan}
            onSelectNode={handleSelectNode}
          />
        </div>

        {/* Slide-over Node Inspector */}
        <WorkflowNodeInspector
          node={activeSelectedNode}
          isOpen={isInspectorOpen && !!activeSelectedNode}
          onClose={() => setIsInspectorOpen(false)}
        />
      </div>
    </div>
  );
}
