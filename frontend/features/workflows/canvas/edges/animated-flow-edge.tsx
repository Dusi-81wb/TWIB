"use client";

import React from "react";
import { BaseEdge, EdgeProps, getBezierPath } from "@xyflow/react";
import { AnimatedEdgeData } from "@/types/flow";

export function AnimatedFlowEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  markerEnd,
  data,
}: EdgeProps) {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const edgeData = data as AnimatedEdgeData | undefined;
  const status = edgeData?.status;
  const isActive = status === "running" || status === "active";
  const isCompleted = status === "completed";
  const isFailed = status === "failed";

  // Compute stroke color based on status
  let strokeColor = "#334155"; // slate-700
  let strokeWidth = 2;
  let strokeDasharray = "5,5";

  if (isActive) {
    strokeColor = "#06b6d4"; // cyan-500
    strokeWidth = 2.5;
    strokeDasharray = "none";
  } else if (isCompleted) {
    strokeColor = "#10b981"; // emerald-500
    strokeWidth = 2;
    strokeDasharray = "none";
  } else if (isFailed) {
    strokeColor = "#ef4444"; // red-500
    strokeWidth = 2;
    strokeDasharray = "4,4";
  }

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        markerEnd={markerEnd}
        style={{
          ...style,
          stroke: strokeColor,
          strokeWidth,
          strokeDasharray,
          transition: "stroke 0.3s ease, stroke-width 0.3s ease",
        }}
      />

      {/* Traveling neon particle when active/running */}
      {isActive && (
        <circle r="4" fill="#22d3ee" className="filter drop-shadow-[0_0_8px_#06b6d4]">
          <animateMotion
            dur="1.5s"
            repeatCount="indefinite"
            path={edgePath}
            rotate="auto"
          />
        </circle>
      )}

      {/* Optional edge label */}
      {edgeData?.label && (
        <foreignObject
          width={80}
          height={24}
          x={labelX - 40}
          y={labelY - 12}
          className="pointer-events-none"
        >
          <div className="flex items-center justify-center h-full">
            <span
              className={`text-[10px] px-1.5 py-0.5 rounded font-mono font-medium border shadow-xs ${
                edgeData.conditionHandle === "true" || edgeData.conditionHandle === "pass"
                  ? "bg-emerald-950/80 text-emerald-300 border-emerald-500/40"
                  : edgeData.conditionHandle === "false" || edgeData.conditionHandle === "retry"
                  ? "bg-rose-950/80 text-rose-300 border-rose-500/40"
                  : "bg-slate-900/80 text-slate-300 border-slate-700"
              }`}
            >
              {edgeData.label}
            </span>
          </div>
        </foreignObject>
      )}
    </>
  );
}
