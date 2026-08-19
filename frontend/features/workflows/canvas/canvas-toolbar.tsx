"use client";

import React from "react";
import {
  Maximize2,
  Minimize2,
  ZoomIn,
  ZoomOut,
  Undo2,
  Redo2,
  LayoutGrid,
  Sparkles,
  ShieldAlert,
  ShieldCheck,
  RotateCcw,
  Layers,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useWorkflowCanvasStore } from "@/stores/workflow-canvas-store";
import { detectCycles } from "@/lib/dag-serializer";
import { useReactFlow } from "@xyflow/react";

export function CanvasToolbar({ onAutoPlan }: { onAutoPlan?: () => void }) {
  const { zoomIn, zoomOut, fitView } = useReactFlow();
  const {
    nodes,
    edges,
    canUndo,
    canRedo,
    undo,
    redo,
    applyLayout,
    isDirty,
  } = useWorkflowCanvasStore();

  const isCyclic = detectCycles(nodes, edges);

  return (
    <div className="absolute top-4 left-4 z-10 flex flex-wrap items-center gap-1.5 p-1.5 rounded-xl border border-border/80 bg-card/90 backdrop-blur-md shadow-lg">
      {/* Undo / Redo */}
      <Button
        type="button"
        variant="ghost"
        size="sm"
        disabled={!canUndo}
        onClick={undo}
        className="h-7 w-7 p-0 text-muted-foreground hover:text-foreground"
        title="Undo (Ctrl+Z)"
      >
        <Undo2 className="h-3.5 w-3.5" />
      </Button>

      <Button
        type="button"
        variant="ghost"
        size="sm"
        disabled={!canRedo}
        onClick={redo}
        className="h-7 w-7 p-0 text-muted-foreground hover:text-foreground"
        title="Redo (Ctrl+Y)"
      >
        <Redo2 className="h-3.5 w-3.5" />
      </Button>

      <div className="h-4 w-px bg-border/60 mx-1" />

      {/* Auto-Layout */}
      <Button
        type="button"
        variant="ghost"
        size="sm"
        onClick={() => applyLayout("LR")}
        className="h-7 px-2 text-xs text-muted-foreground hover:text-foreground gap-1.5"
        title="Auto-Arrange Nodes"
      >
        <LayoutGrid className="h-3.5 w-3.5" />
        <span className="hidden sm:inline">Auto-Layout</span>
      </Button>

      {/* Zoom / Fit Controls */}
      <Button
        type="button"
        variant="ghost"
        size="sm"
        onClick={() => zoomIn()}
        className="h-7 w-7 p-0 text-muted-foreground hover:text-foreground"
        title="Zoom In"
      >
        <ZoomIn className="h-3.5 w-3.5" />
      </Button>

      <Button
        type="button"
        variant="ghost"
        size="sm"
        onClick={() => zoomOut()}
        className="h-7 w-7 p-0 text-muted-foreground hover:text-foreground"
        title="Zoom Out"
      >
        <ZoomOut className="h-3.5 w-3.5" />
      </Button>

      <Button
        type="button"
        variant="ghost"
        size="sm"
        onClick={() => fitView({ padding: 0.2, duration: 400 })}
        className="h-7 w-7 p-0 text-muted-foreground hover:text-foreground"
        title="Fit View"
      >
        <Maximize2 className="h-3.5 w-3.5" />
      </Button>

      <div className="h-4 w-px bg-border/60 mx-1" />

      {/* Cycle / DAG Validation Status */}
      {isCyclic ? (
        <Badge className="bg-rose-500/20 text-rose-300 border-rose-500/40 text-[10px] gap-1 py-0.5">
          <ShieldAlert className="h-3 w-3" /> Cyclic Dependency Detected
        </Badge>
      ) : nodes.length > 0 ? (
        <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/30 text-[10px] gap-1 py-0.5">
          <ShieldCheck className="h-3 w-3" /> Valid Acyclic DAG ({nodes.length} nodes)
        </Badge>
      ) : null}

      {/* Optional AI Auto-Plan trigger */}
      {onAutoPlan && (
        <Button
          type="button"
          size="sm"
          onClick={onAutoPlan}
          className="h-7 px-2.5 text-xs bg-primary text-primary-foreground hover:bg-primary/90 gap-1.5 ml-1"
        >
          <Sparkles className="h-3.5 w-3.5" />
          <span>AI Re-Plan</span>
        </Button>
      )}
    </div>
  );
}
