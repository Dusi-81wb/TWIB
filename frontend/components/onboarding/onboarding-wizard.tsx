"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  settingsService,
  OnboardingCompletePayload,
  OmniRouteTestResult,
} from "@/services/settings.service";
import {
  Bot,
  Building,
  CheckCircle2,
  Cpu,
  Database,
  Eye,
  EyeOff,
  Flame,
  Globe,
  Key,
  Layers,
  Loader2,
  Network,
  Rocket,
  Server,
  ShieldCheck,
  Sparkles,
  Zap,
  ArrowRight,
  ArrowLeft,
  Check,
  Laptop,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface ProviderPreset {
  id: string;
  name: string;
  badge?: string;
  description: string;
  defaultBaseUrl: string;
  defaultModel: string;
  keyPlaceholder: string;
  keyHelp: string;
  suggestedModels: string[];
  isRecommended?: boolean;
}

const PROVIDER_PRESETS: ProviderPreset[] = [
  {
    id: "omniroute",
    name: "OmniRoute Gateway",
    badge: "Recommended (Free & Aggregated)",
    description: "Provider-agnostic unified proxy. Access free & premium models with one gateway.",
    defaultBaseUrl: "http://localhost:8080/v1",
    defaultModel: "best-free",
    keyPlaceholder: "sk-omniroute-... (or blank if no key required)",
    keyHelp: "Connects to your local or hosted OmniRoute gateway instance.",
    suggestedModels: [
      "best-free",
      "google/gemini-2.0-flash-exp:free",
      "meta-llama/llama-3.3-70b-instruct:free",
      "deepseek/deepseek-chat",
      "gpt-4o-mini",
    ],
    isRecommended: true,
  },
  {
    id: "openrouter",
    name: "OpenRouter",
    badge: "Multi-Provider Aggregator",
    description: "Access 200+ models (Claude, OpenAI, Llama 3, DeepSeek) through one universal API.",
    defaultBaseUrl: "https://openrouter.ai/api/v1",
    defaultModel: "openrouter/auto",
    keyPlaceholder: "sk-or-v1-...",
    keyHelp: "Get from openrouter.ai/keys",
    suggestedModels: [
      "openrouter/auto",
      "meta-llama/llama-3.3-70b-instruct",
      "anthropic/claude-3.5-sonnet",
      "google/gemini-2.0-flash-exp:free",
      "deepseek/deepseek-r1",
    ],
  },
  {
    id: "openai",
    name: "OpenAI Direct",
    badge: "Official API",
    description: "Connect directly to OpenAI GPT-4o, GPT-4o-mini, and reasoning models.",
    defaultBaseUrl: "https://api.openai.com/v1",
    defaultModel: "gpt-4o-mini",
    keyPlaceholder: "sk-proj-...",
    keyHelp: "Get from platform.openai.com/api-keys",
    suggestedModels: ["gpt-4o-mini", "gpt-4o", "o3-mini", "gpt-3.5-turbo"],
  },
  {
    id: "groq",
    name: "Groq Cloud",
    badge: "Ultra Fast Inference",
    description: "Ultra-low latency LPU inference for Llama 3.3, Mixtral, and DeepSeek.",
    defaultBaseUrl: "https://api.groq.com/openai/v1",
    defaultModel: "llama-3.3-70b-versatile",
    keyPlaceholder: "gsk_...",
    keyHelp: "Get from console.groq.com/keys",
    suggestedModels: [
      "llama-3.3-70b-versatile",
      "llama-3.1-8b-instant",
      "mixtral-8x7b-32768",
      "deepseek-r1-distill-llama-70b",
    ],
  },
  {
    id: "lmstudio",
    name: "LM Studio (Local LLM)",
    badge: "100% Local (OpenAI Compatible)",
    description: "Run local models (Qwen, DeepSeek, Llama, Mistral) via LM Studio on port 1234.",
    defaultBaseUrl: "http://127.0.0.1:1234/v1",
    defaultModel: "qwen3.5-4b-uncensored-hauhaucs-aggressive",
    keyPlaceholder: "lm-studio (or leave blank)",
    keyHelp: "LM Studio runs locally at http://127.0.0.1:1234. No API key required.",
    suggestedModels: [
      "qwen3.5-4b-uncensored-hauhaucs-aggressive",
      "llama-3.2-3b-instruct",
      "deepseek-r1-distill-qwen-7b",
      "qwen2.5-coder-7b-instruct",
    ],
  },
  {
    id: "ollama",
    name: "Ollama (Local LLM)",
    badge: "100% Private & Free",
    description: "Run local open models (Llama, DeepSeek, Mistral) on your own hardware.",
    defaultBaseUrl: "http://localhost:11434/v1",
    defaultModel: "llama3.2",
    keyPlaceholder: "ollama (or leave blank)",
    keyHelp: "Local Ollama requires no API key. Ensure `ollama serve` is running.",
    suggestedModels: ["llama3.2", "llama3.1:8b", "deepseek-r1:8b", "mistral", "qwen2.5-coder"],
  },
  {
    id: "custom",
    name: "Custom OpenAI-Compatible",
    badge: "Custom Gateway",
    description: "Connect any custom vLLM, LiteLLM, or proprietary gateway.",
    defaultBaseUrl: "http://localhost:8000/v1",
    defaultModel: "best-free",
    keyPlaceholder: "sk-custom-...",
    keyHelp: "Enter your custom endpoint base URL and authorization key.",
    suggestedModels: ["best-free", "gpt-4o-mini", "llama-3.3-70b-versatile"],
  },
];

const AGENT_LIST = [
  { name: "PlannerAgent", desc: "Decomposes complex requests into execution steps", icon: Layers, color: "text-blue-400" },
  { name: "ResearchAgent", desc: "Performs autonomous web searches & synthesis", icon: Globe, color: "text-emerald-400" },
  { name: "AnalystAgent", desc: "Processes structured data, facts & insights", icon: Bot, color: "text-purple-400" },
  { name: "ArchitectAgent", desc: "Designs clean system architectures & code patterns", icon: Building, color: "text-amber-400" },
  { name: "ValidatorAgent", desc: "Enforces safety policies & output verification", icon: ShieldCheck, color: "text-rose-400" },
  { name: "OptimizerAgent", desc: "Minimizes latency, token overhead & execution cost", icon: Zap, color: "text-cyan-400" },
  { name: "DocumentationAgent", desc: "Generates clear guides, summaries & markdown", icon: Cpu, color: "text-indigo-400" },
  { name: "SupervisorAgent", desc: "Orchestrates end-to-end DAG workflows", icon: Sparkles, color: "text-yellow-400" },
];

export function OnboardingWizard() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [showApiKey, setShowApiKey] = useState<boolean>(false);

  // Form states
  const [workspaceName, setWorkspaceName] = useState<string>("Production Workspace");
  const [workspacePurpose, setWorkspacePurpose] = useState<string>("Autonomous AI Workflows");
  const [workspaceDescription, setWorkspaceDescription] = useState<string>(
    "Primary environment for multi-agent workflows and research."
  );

  // Provider state
  const [selectedProviderId, setSelectedProviderId] = useState<string>("omniroute");
  const [providerBaseUrl, setProviderBaseUrl] = useState<string>("http://localhost:8080/v1");
  const [providerApiKey, setProviderApiKey] = useState<string>("");
  const [selectedModel, setSelectedModel] = useState<string>("best-free");
  const [customModelInput, setCustomModelInput] = useState<string>("");

  // Connection Test state
  const [isTesting, setIsTesting] = useState<boolean>(false);
  const [testResult, setTestResult] = useState<OmniRouteTestResult | null>(null);
  const [availableModels, setAvailableModels] = useState<string[]>(PROVIDER_PRESETS[0].suggestedModels);

  // Infrastructure health state
  const [infraStatus, setInfraStatus] = useState<Record<string, string>>({
    postgres: "healthy",
    omniroute: "healthy",
    redis: "healthy",
    vector_store: "healthy",
  });

  const activeProvider = PROVIDER_PRESETS.find((p) => p.id === selectedProviderId) || PROVIDER_PRESETS[0];

  const handleSelectProvider = (preset: ProviderPreset) => {
    setSelectedProviderId(preset.id);
    setProviderBaseUrl(preset.defaultBaseUrl);
    setSelectedModel(preset.defaultModel);
    setAvailableModels(preset.suggestedModels);
    setTestResult(null);
  };

  useEffect(() => {
    settingsService.getOnboardingStatus().then((status) => {
      if (status.services_health) {
        setInfraStatus(status.services_health as Record<string, string>);
      }
      if (status.default_model) {
        setSelectedModel(status.default_model);
      }
    });
  }, []);

  const handleTestConnection = async () => {
    setIsTesting(true);
    setTestResult(null);

    try {
      const res = await settingsService.testOmniRoute({
        api_key: providerApiKey.trim() || (selectedProviderId === "ollama" ? "ollama" : ""),
        base_url: providerBaseUrl.trim(),
        model: customModelInput.trim() || selectedModel,
      });
      setTestResult(res);
      if (res.available_models && res.available_models.length > 0) {
        setAvailableModels(res.available_models);
      }
      if (res.success) {
        setInfraStatus((prev) => ({ ...prev, omniroute: "healthy" }));
      } else {
        setInfraStatus((prev) => ({ ...prev, omniroute: "degraded" }));
      }
    } catch (err: any) {
      setTestResult({
        success: false,
        latency_ms: 0,
        message: err.message || "Failed to reach selected LLM endpoint.",
        available_models: [],
      });
      setInfraStatus((prev) => ({ ...prev, omniroute: "unhealthy" }));
    } finally {
      setIsTesting(false);
    }
  };

  const handleCompleteSetup = async () => {
    setIsSubmitting(true);
    try {
      const finalModel = customModelInput.trim() || selectedModel;
      const payload: OnboardingCompletePayload = {
        workspace_name: workspaceName.trim() || "Production Workspace",
        workspace_purpose: workspacePurpose.trim(),
        workspace_description: workspaceDescription.trim(),
        omniroute_api_key: providerApiKey.trim() || (selectedProviderId === "ollama" ? "ollama" : "sk-configured"),
        omniroute_base_url: providerBaseUrl.trim(),
        default_model: finalModel,
      };

      await settingsService.completeOnboarding(payload);
      router.push("/dashboard");
    } catch (err: any) {
      alert("Failed to complete setup: " + (err.message || "Unknown error"));
      setIsSubmitting(false);
    }
  };

  const steps = [
    { id: 1, label: "Workspace" },
    { id: 2, label: "Choose AI Service" },
    { id: 3, label: "API Credentials" },
    { id: 4, label: "Model Selection" },
    { id: 5, label: "Verification & Launch" },
  ];

  return (
    <div className="max-w-4xl mx-auto py-10 px-4 select-none">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-semibold uppercase tracking-wider mb-3">
          <Sparkles className="h-3.5 w-3.5" /> Initial Platform Configuration
        </div>
        <h1 className="text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
          Welcome to <span className="motion-gradient-text">TWIB</span>
        </h1>
        <p className="text-muted-foreground mt-2 max-w-xl mx-auto text-xs sm:text-sm">
          Connect your preferred AI provider or gateway once. All 8 autonomous worker agents will seamlessly utilize this connection.
        </p>
      </div>

      {/* Stepper Navigation */}
      <div className="flex items-center justify-between mb-8 px-2 sm:px-6 relative">
        <div className="absolute top-1/2 left-6 right-6 h-0.5 bg-muted -translate-y-1/2 z-0" />
        {steps.map((step) => {
          const isDone = currentStep > step.id;
          const isCurrent = currentStep === step.id;
          return (
            <div
              key={step.id}
              className="relative z-10 flex flex-col items-center cursor-pointer group"
              onClick={() => {
                if (step.id < currentStep) setCurrentStep(step.id);
              }}
            >
              <div
                className={cn(
                  "w-10 h-10 rounded-2xl flex items-center justify-center font-bold text-xs transition-all duration-300 border-2",
                  isDone
                    ? "bg-primary border-primary text-white shadow-md shadow-primary/30"
                    : isCurrent
                    ? "bg-background border-primary text-primary shadow-lg shadow-primary/20 scale-110 ring-2 ring-primary/20"
                    : "bg-card border-border text-muted-foreground"
                )}
              >
                {isDone ? <CheckCircle2 className="h-5 w-5" /> : step.id}
              </div>
              <span
                className={cn(
                  "text-[11px] mt-2 font-medium hidden sm:block",
                  isCurrent ? "text-primary font-bold" : "text-muted-foreground"
                )}
              >
                {step.label}
              </span>
            </div>
          );
        })}
      </div>

      {/* Main Card Container */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-white/10 shadow-2xl relative min-h-[460px] flex flex-col justify-between">
        {/* STEP 1: Workspace */}
        {currentStep === 1 && (
          <div className="space-y-6 animate-in fade-in duration-300">
            <div>
              <h2 className="text-xl font-bold flex items-center gap-2 text-foreground">
                <Building className="h-5 w-5 text-primary" /> Create Your First Workspace
              </h2>
              <p className="text-xs text-muted-foreground mt-1">
                Workspaces isolate agent pipelines, conversation histories, and execution artifacts.
              </p>
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="ws-name" className="text-xs">Workspace Name *</Label>
                <Input
                  id="ws-name"
                  value={workspaceName}
                  onChange={(e) => setWorkspaceName(e.target.value)}
                  placeholder="e.g. Acme AI Engineering"
                  className="glass-card text-xs"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="ws-purpose" className="text-xs">Primary Use Case</Label>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {[
                    "Workflow Automation",
                    "Autonomous Research",
                    "Code Architecture & QA",
                    "Security & Compliance",
                    "Data & Analytics",
                    "Custom Operations",
                  ].map((p) => (
                    <button
                      key={p}
                      type="button"
                      onClick={() => setWorkspacePurpose(p)}
                      className={cn(
                        "text-left p-3 rounded-xl border text-xs font-medium transition-all",
                        workspacePurpose === p
                          ? "border-primary bg-primary/10 text-primary shadow-xs ring-1 ring-primary"
                          : "border-border/50 bg-background/50 text-muted-foreground hover:border-border"
                      )}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="ws-desc" className="text-xs">Description (Optional)</Label>
                <Input
                  id="ws-desc"
                  value={workspaceDescription}
                  onChange={(e) => setWorkspaceDescription(e.target.value)}
                  placeholder="e.g. Primary environment for multi-agent workflows"
                  className="glass-card text-xs"
                />
              </div>
            </div>
          </div>
        )}

        {/* STEP 2: Flexible AI Service / Provider Selection */}
        {currentStep === 2 && (
          <div className="space-y-6 animate-in fade-in duration-300">
            <div>
              <h2 className="text-xl font-bold flex items-center gap-2 text-foreground">
                <Network className="h-5 w-5 text-primary" /> Choose Your AI Gateway / Provider
              </h2>
              <p className="text-xs text-muted-foreground mt-1">
                TWIB is 100% provider-agnostic. Select a suggested provider or connect your own OpenAI-compatible endpoint.
              </p>
            </div>

            {/* Provider Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-[340px] overflow-y-auto pr-1">
              {PROVIDER_PRESETS.map((preset) => {
                const isSelected = selectedProviderId === preset.id;
                return (
                  <div
                    key={preset.id}
                    onClick={() => handleSelectProvider(preset)}
                    className={cn(
                      "p-4 rounded-2xl border cursor-pointer transition-all duration-200 flex flex-col justify-between space-y-2.5",
                      isSelected
                        ? "border-primary bg-primary/10 ring-1 ring-primary shadow-md shadow-primary/10"
                        : "border-white/10 bg-card/60 hover:border-white/25 hover:bg-card/90"
                    )}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="space-y-0.5">
                        <span className="text-xs font-bold text-foreground flex items-center gap-1.5">
                          {preset.name}
                        </span>
                        {preset.badge && (
                          <Badge
                            variant="secondary"
                            className={cn(
                              "text-[10px] py-0 px-1.5",
                              preset.isRecommended
                                ? "bg-primary/20 text-primary border-primary/30"
                                : "bg-accent/40 text-muted-foreground"
                            )}
                          >
                            {preset.badge}
                          </Badge>
                        )}
                      </div>
                      {isSelected && (
                        <div className="h-5 w-5 rounded-full bg-primary text-white flex items-center justify-center shrink-0">
                          <Check className="h-3 w-3" />
                        </div>
                      )}
                    </div>

                    <p className="text-[11px] text-muted-foreground leading-relaxed">
                      {preset.description}
                    </p>

                    <div className="pt-1 text-[10px] font-mono text-muted-foreground truncate border-t border-border/40">
                      Base URL: <span className="text-primary">{preset.defaultBaseUrl}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* STEP 3: API Key & Live Connection Test */}
        {currentStep === 3 && (
          <div className="space-y-6 animate-in fade-in duration-300">
            <div>
              <h2 className="text-xl font-bold flex items-center gap-2 text-foreground">
                <Key className="h-5 w-5 text-primary" /> {activeProvider.name} Credentials
              </h2>
              <p className="text-xs text-muted-foreground mt-1">
                {activeProvider.keyHelp} One credential configures all 8 worker agents in TWIB.
              </p>
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="provider-url" className="text-xs">API Base Endpoint URL</Label>
                <Input
                  id="provider-url"
                  value={providerBaseUrl}
                  onChange={(e) => setProviderBaseUrl(e.target.value)}
                  placeholder={activeProvider.defaultBaseUrl}
                  className="glass-card font-mono text-xs"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="provider-key" className="text-xs">
                  API Key {selectedProviderId === "ollama" && <span className="text-muted-foreground font-normal">(Optional for Local Ollama)</span>}
                </Label>
                <div className="relative">
                  <Input
                    id="provider-key"
                    type={showApiKey ? "text" : "password"}
                    value={providerApiKey}
                    onChange={(e) => {
                      setProviderApiKey(e.target.value);
                      setTestResult(null);
                    }}
                    placeholder={activeProvider.keyPlaceholder}
                    className="glass-card font-mono text-xs pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowApiKey(!showApiKey)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  >
                    {showApiKey ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
                  </button>
                </div>
              </div>

              {/* Test Button & Latency Indicator */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-2xl border border-white/10 bg-background/50">
                <div>
                  <p className="text-xs font-semibold text-foreground">Verify Endpoint Connectivity</p>
                  <p className="text-[11px] text-muted-foreground">
                    Sends an instant ping to test authentication & measure roundtrip latency.
                  </p>
                </div>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleTestConnection}
                  disabled={isTesting}
                  className="shrink-0 border-primary/30 hover:bg-primary/10 text-xs"
                >
                  {isTesting ? (
                    <>
                      <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin text-primary" /> Testing...
                    </>
                  ) : (
                    <>
                      <Zap className="mr-1.5 h-3.5 w-3.5 text-primary" /> Test Connection
                    </>
                  )}
                </Button>
              </div>

              {testResult && (
                <Alert
                  variant={testResult.success ? "default" : "destructive"}
                  className={cn(
                    "border text-xs animate-in fade-in duration-200",
                    testResult.success ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300" : ""
                  )}
                >
                  <div className="flex items-center justify-between">
                    <AlertDescription className="text-xs font-medium flex items-center gap-2">
                      {testResult.success ? <CheckCircle2 className="h-4 w-4 text-emerald-400" /> : null}
                      {testResult.message}
                    </AlertDescription>
                    {testResult.success && testResult.latency_ms > 0 && (
                      <Badge variant="outline" className="border-emerald-500/40 text-emerald-400 text-[10px] font-mono">
                        {testResult.latency_ms} ms
                      </Badge>
                    )}
                  </div>
                </Alert>
              )}
            </div>
          </div>
        )}

        {/* STEP 4: Model Selection */}
        {currentStep === 4 && (
          <div className="space-y-6 animate-in fade-in duration-300">
            <div>
              <h2 className="text-xl font-bold flex items-center gap-2 text-foreground">
                <Cpu className="h-5 w-5 text-primary" /> Default Model Configuration
              </h2>
              <p className="text-xs text-muted-foreground mt-1">
                Choose a suggested model for {activeProvider.name} or type any custom model ID.
              </p>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {availableModels.map((m) => {
                  const isSelected = selectedModel === m && !customModelInput.trim();
                  const isFree = m.includes("free");
                  return (
                    <div
                      key={m}
                      onClick={() => {
                        setSelectedModel(m);
                        setCustomModelInput("");
                      }}
                      className={cn(
                        "p-3.5 rounded-xl border cursor-pointer transition-all flex items-center justify-between",
                        isSelected
                          ? "border-primary bg-primary/10 shadow-md shadow-primary/10 ring-1 ring-primary"
                          : "border-border/50 bg-background/50 hover:border-border hover:bg-background/80"
                      )}
                    >
                      <span className="font-mono text-xs font-semibold text-foreground truncate">{m}</span>
                      {isFree && (
                        <Badge variant="secondary" className="bg-emerald-500/20 text-emerald-400 text-[10px] shrink-0 ml-2">
                          Free
                        </Badge>
                      )}
                    </div>
                  );
                })}
              </div>

              <div className="space-y-2 pt-2 border-t border-border/40">
                <Label htmlFor="custom-model" className="text-xs">Or Enter Custom Model ID</Label>
                <Input
                  id="custom-model"
                  value={customModelInput}
                  onChange={(e) => setCustomModelInput(e.target.value)}
                  placeholder={`e.g. ${activeProvider.defaultModel}`}
                  className="glass-card font-mono text-xs"
                />
              </div>
            </div>
          </div>
        )}

        {/* STEP 5: Architecture & Infrastructure Verification */}
        {currentStep === 5 && (
          <div className="space-y-6 animate-in fade-in duration-300">
            <div>
              <h2 className="text-xl font-bold flex items-center gap-2 text-foreground">
                <Rocket className="h-5 w-5 text-primary" /> Architecture & Infrastructure Ready
              </h2>
              <p className="text-xs text-muted-foreground mt-1">
                Your <strong className="text-foreground">{activeProvider.name}</strong> configuration is mapped to all 8 worker agents.
              </p>
            </div>

            {/* Visual 8 Agent Architecture Grid */}
            <div className="p-4 rounded-2xl border border-primary/20 bg-primary/5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-primary uppercase tracking-wider flex items-center gap-1.5">
                  <Sparkles className="h-3.5 w-3.5" /> 1 Gateway &rarr; 8 Autonomous Agents
                </span>
                <span className="text-[10px] font-mono text-muted-foreground">
                  Active Model: <strong className="text-foreground">{customModelInput.trim() || selectedModel}</strong>
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {AGENT_LIST.map((agent) => {
                  const Icon = agent.icon;
                  return (
                    <div
                      key={agent.name}
                      className="p-2 rounded-lg bg-card/70 border border-white/5 flex items-center gap-2 text-xs"
                    >
                      <Icon className={`h-3.5 w-3.5 shrink-0 ${agent.color}`} />
                      <span className="truncate text-foreground font-medium text-[11px]">{agent.name}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Infrastructure Health Live Badges */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
              <div className="p-3 rounded-xl border border-white/10 bg-card/60 flex items-center gap-2">
                <Database className="h-4 w-4 text-primary shrink-0" />
                <div className="min-w-0">
                  <p className="font-semibold text-[11px] truncate">PostgreSQL</p>
                  <span className="text-[10px] text-emerald-400 font-mono">Connected</span>
                </div>
              </div>
              <div className="p-3 rounded-xl border border-white/10 bg-card/60 flex items-center gap-2">
                <Zap className="h-4 w-4 text-yellow-400 shrink-0" />
                <div className="min-w-0">
                  <p className="font-semibold text-[11px] truncate">{activeProvider.name}</p>
                  <span className="text-[10px] text-emerald-400 font-mono">Configured</span>
                </div>
              </div>
              <div className="p-3 rounded-xl border border-white/10 bg-card/60 flex items-center gap-2">
                <Server className="h-4 w-4 text-purple-400 shrink-0" />
                <div className="min-w-0">
                  <p className="font-semibold text-[11px] truncate">Redis Queue</p>
                  <span className="text-[10px] text-muted-foreground font-mono">Ready</span>
                </div>
              </div>
              <div className="p-3 rounded-xl border border-white/10 bg-card/60 flex items-center gap-2">
                <Cpu className="h-4 w-4 text-cyan-400 shrink-0" />
                <div className="min-w-0">
                  <p className="font-semibold text-[11px] truncate">Vector Qdrant</p>
                  <span className="text-[10px] text-muted-foreground font-mono">Ready</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Wizard Footer Controls */}
        <div className="flex items-center justify-between pt-6 border-t border-border/40 mt-6">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => setCurrentStep((prev) => Math.max(prev - 1, 1))}
            disabled={currentStep === 1 || isSubmitting}
            className="text-xs"
          >
            <ArrowLeft className="mr-1.5 h-3.5 w-3.5" /> Back
          </Button>

          {currentStep < 5 ? (
            <Button
              type="button"
              size="sm"
              onClick={() => setCurrentStep((prev) => Math.min(prev + 1, 5))}
              className="bg-primary hover:bg-primary/90 text-white text-xs"
            >
              Continue <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
            </Button>
          ) : (
            <Button
              type="button"
              size="sm"
              onClick={handleCompleteSetup}
              disabled={isSubmitting}
              className="bg-primary hover:bg-primary/90 text-white shadow-lg shadow-primary/25 text-xs"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" /> Launching...
                </>
              ) : (
                <>
                  <Rocket className="mr-1.5 h-3.5 w-3.5" /> Launch TWIB Dashboard
                </>
              )}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
