"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { AUTH_TOKEN_STORAGE_KEY } from "@/lib/constants";

export interface WorkflowRealtimeEvent {
  workflow_id: string;
  event_type: string;
  timestamp: string;
  current_state?: string;
  current_agent?: string;
  progress?: number;
  message?: string;
  data?: Record<string, unknown>;
}

export type ConnectionStatus = "connecting" | "connected" | "disconnected" | "error";

export function useWorkflowWebsocket(workflowId: string | null) {
  const [status, setStatus] = useState<ConnectionStatus>("disconnected");
  const [events, setEvents] = useState<WorkflowRealtimeEvent[]>([]);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (!workflowId || typeof window === "undefined") return;

    const token = localStorage.getItem(AUTH_TOKEN_STORAGE_KEY) || "";
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = process.env.NEXT_PUBLIC_WS_HOST || "localhost:8000";
    const wsUrl = `${protocol}//${host}/api/v1/ws/workflows/${workflowId}?token=${token}`;

    setStatus("connecting");

    try {
      const socket = new WebSocket(wsUrl);
      socketRef.current = socket;

      socket.onopen = () => {
        setStatus("connected");
        // Set up 15-second heartbeat ping
        pingIntervalRef.current = setInterval(() => {
          if (socket.readyState === WebSocket.OPEN) {
            socket.send("ping");
          }
        }, 15000);
      };

      socket.onmessage = (event) => {
        if (event.data === "pong" || event.data === '{"type":"pong"}') {
          return;
        }

        try {
          const parsed: WorkflowRealtimeEvent = JSON.parse(event.data);
          if (parsed.event_type) {
            setEvents((prev) => [parsed, ...prev]);
          }
        } catch {
          // Plain text message
        }
      };

      socket.onerror = () => {
        setStatus("error");
      };

      socket.onclose = () => {
        setStatus("disconnected");
        if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);

        // Schedule auto reconnect after 5 seconds if workflow is active
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 5000);
      };
    } catch {
      setStatus("error");
    }
  }, [workflowId]);

  useEffect(() => {
    connect();

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
    };
  }, [connect]);

  const clearEvents = () => setEvents([]);

  return {
    status,
    events,
    clearEvents,
    reconnect: connect,
  };
}
