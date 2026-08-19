"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Play, RotateCcw, Loader2, Sparkles, SlidersHorizontal, Zap, ChevronDown, ChevronUp, Cpu, Code2 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { settingsService } from "@/services/settings.service";
import { cn } from "@/lib/utils";

interface PromptEditorProps {
  onExecute: (params: { prompt: string; model?: string; temperature?: number; context?: Record<string, any> }) => void;
  isExecuting: boolean;
  defaultPrompt?: string;
  agentType?: string;
}

const SUGGESTED_PROMPTS: Record<string, string[]> = {
  PlannerAgent: [
    "Design a 5-stage architecture migration to event-driven microservices with zero downtime.",
    "Plan a high-availability disaster recovery strategy across multi-region cloud clusters.",
    "Deconstruct a distributed AI agent orchestrator with caching and rate limiting.",
  ],
  ResearchAgent: [
    "Synthesize the state of local LLM inference engines (vLLM, Ollama, LM Studio, SGLang).",
    "Analyze modern zero-trust security patterns for Kubernetes workloads.",
    "Compare Vector Database indexing strategies: HNSW vs IVFFlat for 10M embeddings.",
  ],
  AnalystAgent: [
    "Analyze compute cost vs latency trade-offs for self-hosted LLM vs Cloud API gateway.",
    "Evaluate system bottleneck risks for a 100k req/s WebSocket ingestion pipeline.",
    "Benchmark database failover recovery times under high write-throughput.",
  ],
  ArchitectAgent: [
    "Specify component diagrams, message queues, and API contracts for an AI workflow engine.",
    "Architect an asynchronous multi-tenant task scheduler using Redis Streams and Postgres.",
    "Design an edge-caching GraphQL gateway with schema federation.",
  ],
  ValidatorAgent: [
    "Validate API authentication schemas against OWASP Top 10 API Security Risks.",
    "Audit RBAC permission boundaries and token expiration policies.",
    "Verify cryptographic signing and replay attack mitigations for webhooks.",
  ],
  OptimizerAgent: [
    "Optimize prompt token consumption and context caching to reduce inference latency by 40%.",
    "Identify connection pooling and query optimization opportunities in SQLAlchemy.",
    "Propose memory-efficient batching for concurrent DAG topological wave execution.",
  ],
  DocumentationAgent: [
    "Generate comprehensive developer guide, OpenAPI specification, and deployment checklist.",
    "Compile architecture decision records (ADRs) for multi-agent DAG dispatcher.",
    "Synthesize production runbook and telemetry monitoring guide.",
  ],
  SupervisorAgent: [
    "Coordinate autonomous end-to-end audit and optimization pipeline for distributed data lake.",
    "Orchestrate research, architecture design, and security verification for new AI platform.",
  ],
};

export function PromptEditor({
  onExecute,
  isExecuting,
  defaultPrompt = "",
  agentType,
}: PromptEditorProps) {
  const [prompt, setPrompt] = useState(defaultPrompt);
  const [selectedModel, setSelectedModel] = useState("best-free");
  const [customModel, setCustomModel] = useState("");
  const [temperature, setTemperature] = useState(0.2);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [contextJson, setContextJson] = useState("");
  const [jsonError, setJsonError] = useState<string | null>(null);

  const { data: config } = useQuery({
    queryKey: ["omniroute-config"],
    queryFn: () => settingsService.getOmniRouteConfig(),
  });

  const { data: models = [] } = useQuery({
    queryKey: ["omniroute-models"],
    queryFn: () => settingsService.getOmniRouteModels(),
  });

  useEffect(() => {
    if (config?.default_model) {
      setSelectedModel(config.default_model);
    }
  }, [config]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    let parsedContext: Record<string, any> = {};
    if (contextJson.trim()) {
      try {
        parsedContext = JSON.parse(contextJson);
        setJsonError(null);
      } catch (err: any) {
        setJsonError("Invalid JSON in context: " + err.message);
        return;
      }
    }

    const activeModel = customModel.trim() || selectedModel;
    onExecute({
      prompt: prompt.trim(),
      model: activeModel,
      temperature,
      context: Object.keys(parsedContext).length > 0 ? parsedContext : undefined,
    });
  };

  const handleClear = () => {
    setPrompt("");
    setContextJson("");
    setJsonError(null);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-3xl glass-panel border border-white/10 p-5 shadow-xl">
      {/* Top Header with Live Model Selector & Provider Info */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-border/40">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-primary" />
          <span className="text-xs font-bold uppercase tracking-wider text-foreground">
            Agent Prompt & Live Model Execution
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* Live Model Badge */}
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/25 text-emerald-400 font-mono text-[11px]">
            <Zap className="h-3 w-3" />
            <span>{customModel.trim() || selectedModel}</span>
          </div>

          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="h-7 px-2 text-xs gap-1 font-mono text-muted-foreground hover:text-foreground"
          >
            <SlidersHorizontal className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Settings</span>
            {showAdvanced ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
          </Button>
        </div>
      </div>

      {/* Advanced Settings Drawer (Live Models, Temperature, Context) */}
      {showAdvanced && (
        <div className="p-4 rounded-2xl bg-card/60 border border-white/10 space-y-4 text-xs animate-in fade-in duration-200">
          {/* Model Selection */}
          <div className="space-y-2">
            <Label className="text-xs font-semibold flex items-center gap-1.5">
              <Cpu className="h-3.5 w-3.5 text-primary" /> Select Live Model from Gateway
            </Label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {models.map((m) => (
                <button
                  key={m}
                  type="button"
                  onClick={() => {
                    setSelectedModel(m);
                    setCustomModel("");
                  }}
                  className={cn(
                    "p-2 rounded-lg border text-left font-mono text-[11px] truncate transition-all",
                    selectedModel === m && !customModel
                      ? "border-primary bg-primary/10 text-primary ring-1 ring-primary"
                      : "border-border/60 bg-background/50 hover:border-border text-foreground"
                  )}
                >
                  {m}
                </button>
              ))}
            </div>
            <Input
              value={customModel}
              onChange={(e) => setCustomModel(e.target.value)}
              placeholder="Or specify custom model name..."
              className="font-mono text-xs h-8 bg-background/60"
            />
          </div>

          {/* Temperature Slider */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs font-semibold">
              <Label>Temperature: <span className="font-mono text-primary">{temperature.toFixed(2)}</span></Label>
              <span className="text-[10px] text-muted-foreground font-mono">0.0 (Precise) &rarr; 1.0 (Creative)</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="1.5"
              step="0.05"
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              className="w-full accent-primary cursor-pointer h-1.5 bg-accent rounded-lg"
            />
          </div>

          {/* Execution Context JSON */}
          <div className="space-y-1.5">
            <Label className="text-xs font-semibold flex items-center gap-1.5">
              <Code2 className="h-3.5 w-3.5 text-purple-400" /> Optional Structured Context (JSON)
            </Label>
            <textarea
              rows={2}
              value={contextJson}
              onChange={(e) => setContextJson(e.target.value)}
              placeholder='{"system_architecture": "microservices", "target_audience": "developers"}'
              className="w-full rounded-xl border border-input bg-background/60 p-2 font-mono text-[11px] placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"
            />
            {jsonError && <p className="text-[11px] text-rose-400 font-mono">{jsonError}</p>}
          </div>
        </div>
      )}

      {/* Main Prompt Textarea */}
      <div className="space-y-2">
        <textarea
          id="agent-prompt"
          rows={5}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder={`Enter detailed instructions for ${agentType || "this agent"}... (e.g. 'Perform an in-depth architecture evaluation for a real-time event streaming pipeline...')`}
          disabled={isExecuting}
          className="flex w-full rounded-2xl border border-white/10 bg-card/70 px-4 py-3 text-sm shadow-inner transition-all placeholder:text-muted-foreground focus:border-primary/50 focus:ring-2 focus:ring-primary/20 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50 font-sans leading-relaxed"
        />

        {/* Suggested Quick Prompts */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
          <span className="text-[11px] font-mono text-muted-foreground shrink-0 flex items-center gap-1">
            <Sparkles className="h-3 w-3 text-primary" /> Suggestions:
          </span>
          {(SUGGESTED_PROMPTS[agentType || "PlannerAgent"] || SUGGESTED_PROMPTS.PlannerAgent).map((sug, i) => (
            <button
              key={i}
              type="button"
              onClick={() => setPrompt(sug)}
              className="px-2.5 py-1 rounded-lg bg-accent/30 hover:bg-accent/70 border border-white/5 text-[11px] text-muted-foreground hover:text-foreground transition-all shrink-0 max-w-[280px] truncate text-left"
              title={sug}
            >
              {sug}
            </button>
          ))}
        </div>

        <div className="flex items-center justify-between text-[11px] text-muted-foreground font-mono px-1">
          <span>{prompt.length} characters</span>
          <span>Shift + Enter for new line</span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-1">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handleClear}
          disabled={isExecuting || (!prompt && !contextJson)}
          className="text-xs glass-card border-white/10"
        >
          <RotateCcw className="mr-1.5 h-3.5 w-3.5" /> Clear
        </Button>

        <Button
          type="submit"
          size="sm"
          disabled={isExecuting || !prompt.trim()}
          className="bg-primary hover:bg-primary/90 text-white shadow-lg shadow-primary/25 text-xs font-semibold px-4"
        >
          {isExecuting ? (
            <>
              <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" />
              Executing with {customModel.trim() || selectedModel}...
            </>
          ) : (
            <>
              <Play className="mr-1.5 h-3.5 w-3.5" /> Execute Agent
            </>
          )}
        </Button>
      </div>
    </form>
  );
}
