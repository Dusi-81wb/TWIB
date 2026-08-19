"use client";

import { useState, useEffect, useRef } from "react";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { Sidebar } from "@/components/dashboard/sidebar";
import { TopBar } from "@/components/dashboard/top-bar";
import {
  agentService,
  ConversationItem,
  ConversationMessageTurn,
} from "@/services/agent.service";
import { StatusHeader } from "@/components/agents/research/status-header";
import { ConversationSidebar, HistoryItem } from "@/components/agents/research/conversation-sidebar";
import { HeroEmptyState } from "@/components/agents/research/hero-empty-state";
import { MessageBubble, ChatTurn } from "@/components/agents/research/message-bubble";
import { ThinkingIndicator } from "@/components/agents/research/thinking-indicator";
import { Composer } from "@/components/agents/research/composer";
import { AlertTriangle } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

export default function ResearchAgentPage() {
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [activeId, setActiveId] = useState<string | undefined>(undefined);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Status Header Metrics
  const [latestProvider, setLatestProvider] = useState<string>("omniroute");
  const [latestModel, setLatestModel] = useState<string>("best-fast");
  const [latestLatency, setLatestLatency] = useState<number | undefined>(undefined);
  const [latestTokens, setLatestTokens] = useState<
    { prompt_tokens: number; completion_tokens: number; total_tokens: number } | undefined
  >(undefined);
  const [isHealthRefreshing, setIsHealthRefreshing] = useState(false);

  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Load persistent conversations on mount
  useEffect(() => {
    loadConversations();
  }, []);

  // Auto-scroll chat to bottom
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTo({
        top: chatContainerRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [turns, isLoading]);

  const loadConversations = async () => {
    try {
      const items = await agentService.getConversations();
      const mapped: HistoryItem[] = items.map((item: ConversationItem) => ({
        id: item.id,
        prompt: item.title,
        timestamp: new Date(item.updated_at).toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
        snippet: item.last_message_snippet,
      }));
      setHistory(mapped);
    } catch {
      // Non-blocking history fetch error
    }
  };

  const handleSendPrompt = async (params: {
    prompt: string;
    model: string;
    temperature: number;
    systemPrompt?: string;
  }) => {
    setError(null);
    setIsLoading(true);

    const userTurnId = `user-${Date.now()}`;
    const userTurn: ChatTurn = {
      id: userTurnId,
      role: "user",
      content: params.prompt,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setTurns((prev) => [...prev, userTurn]);
    setLatestModel(params.model);

    try {
      const targetConvId = activeId || "new";
      const assistantMessage: ConversationMessageTurn = await agentService.sendConversationMessage(
        targetConvId,
        {
          prompt: params.prompt,
          model: params.model,
          temperature: params.temperature,
        }
      );

      // Set active conversation ID from backend response
      setActiveId(assistantMessage.conversation_id);

      const meta = assistantMessage.metadata || {};
      const assistantTurn: ChatTurn = {
        id: assistantMessage.id,
        role: "assistant",
        content: assistantMessage.content,
        timestamp: new Date(assistantMessage.created_at).toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
        provider: meta.provider || "omniroute",
        model: meta.model || params.model,
        latencyMs: meta.latency_ms,
        tokens: meta.usage,
      };

      setTurns((prev) => [...prev, assistantTurn]);

      // Update Header metrics
      if (meta.provider) setLatestProvider(meta.provider);
      if (meta.model) setLatestModel(meta.model);
      if (meta.latency_ms !== undefined) setLatestLatency(meta.latency_ms);
      if (meta.usage) setLatestTokens(meta.usage);

      // Refresh sidebar conversation list
      loadConversations();
    } catch (err: unknown) {
      const msg =
        err && typeof err === "object" && "message" in err
          ? (err as { message: string }).message
          : "OmniRoute service is currently unavailable. Please try again.";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectHistoryItem = async (item: HistoryItem) => {
    setActiveId(item.id);
    setError(null);
    try {
      const details = await agentService.getConversationDetails(item.id);
      const mappedTurns: ChatTurn[] = details.messages.map((msg) => ({
        id: msg.id,
        role: msg.role === "user" ? "user" : "assistant",
        content: msg.content,
        timestamp: new Date(msg.created_at).toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
        provider: msg.metadata?.provider,
        model: msg.metadata?.model,
        latencyMs: msg.metadata?.latency_ms,
        tokens: msg.metadata?.usage,
      }));
      setTurns(mappedTurns);
    } catch {
      setError("Failed to load conversation messages.");
    }
  };

  const handleDeleteHistoryItem = async (id: string) => {
    try {
      await agentService.deleteConversation(id);
      if (id === activeId) {
        setTurns([]);
        setActiveId(undefined);
      }
      loadConversations();
    } catch {
      // Non-blocking delete error
    }
  };

  const handleNewResearch = () => {
    setTurns([]);
    setActiveId(undefined);
    setError(null);
  };

  const handleClearTurns = () => {
    setTurns([]);
    setError(null);
  };

  const handleRefreshHealth = async () => {
    setIsHealthRefreshing(true);
    try {
      await loadConversations();
    } catch {
      // Ignored
    } finally {
      setIsHealthRefreshing(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="flex h-screen overflow-hidden bg-background">
        {/* Global Navigation Sidebar */}
        <Sidebar />

        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          {/* TopBar */}
          <TopBar />

          {/* Top Status Header Ribbon */}
          <StatusHeader
            provider={latestProvider}
            model={latestModel}
            latencyMs={latestLatency}
            tokens={latestTokens}
            onRefreshHealth={handleRefreshHealth}
            isRefreshing={isHealthRefreshing}
          />

          {/* Main Conversational Layout */}
          <div className="flex-1 flex overflow-hidden">
            {/* Left Research History Sidebar */}
            <ConversationSidebar
              history={history}
              activeId={activeId}
              onSelect={handleSelectHistoryItem}
              onNewResearch={handleNewResearch}
              onDelete={handleDeleteHistoryItem}
              isOpen={sidebarOpen}
              onToggleOpen={() => setSidebarOpen(!sidebarOpen)}
            />

            {/* Center Chat Workspace */}
            <main className="flex-1 flex flex-col min-w-0 h-full bg-background/50 relative">
              {/* Error Notification Alert */}
              {error && (
                <div className="p-3 px-4 bg-destructive/10 border-b border-destructive/30 animate-in fade-in duration-200">
                  <Alert variant="destructive" className="border-none p-0 bg-transparent">
                    <AlertTriangle className="h-4 w-4 text-destructive" />
                    <AlertDescription className="text-xs font-semibold text-destructive ml-2">
                      {error}
                    </AlertDescription>
                  </Alert>
                </div>
              )}

              {/* Chat Turn Messages Container */}
              <div
                ref={chatContainerRef}
                className="flex-1 overflow-y-auto p-4 sm:p-6 md:p-8 space-y-4"
              >
                {turns.length === 0 ? (
                  <HeroEmptyState
                    onSelectSuggestion={(promptText) =>
                      handleSendPrompt({
                        prompt: promptText,
                        model: latestModel,
                        temperature: 0.3,
                      })
                    }
                  />
                ) : (
                  <div className="max-w-4xl mx-auto space-y-4">
                    {turns.map((turn, idx) => (
                      <MessageBubble
                        key={turn.id}
                        turn={turn}
                        isLast={idx === turns.length - 1}
                      />
                    ))}

                    {/* Animated Thinking Card while waiting for LLM Gateway */}
                    {isLoading && <ThinkingIndicator />}
                  </div>
                )}
              </div>

              {/* Bottom ChatGPT-Style Composer */}
              <div className="max-w-4xl mx-auto w-full">
                <Composer
                  onSend={handleSendPrompt}
                  isLoading={isLoading}
                  onClear={turns.length > 0 ? handleClearTurns : undefined}
                  defaultModel={latestModel}
                />
              </div>
            </main>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
