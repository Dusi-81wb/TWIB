"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { settingsService, OmniRouteTestResult } from "@/services/settings.service";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Zap, CheckCircle2, Loader2, Key, Eye, EyeOff, Save, Check, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

interface ProviderPreset {
  id: string;
  name: string;
  badge?: string;
  defaultBaseUrl: string;
  defaultModel: string;
  suggestedModels: string[];
  isRecommended?: boolean;
}

const PROVIDER_PRESETS: ProviderPreset[] = [
  {
    id: "omniroute",
    name: "OmniRoute Gateway",
    badge: "Recommended (Free)",
    defaultBaseUrl: "http://localhost:8080/v1",
    defaultModel: "best-free",
    suggestedModels: ["best-free", "google/gemini-2.0-flash-exp:free", "meta-llama/llama-3.3-70b-instruct:free", "deepseek/deepseek-chat"],
    isRecommended: true,
  },
  {
    id: "openrouter",
    name: "OpenRouter",
    badge: "200+ Models",
    defaultBaseUrl: "https://openrouter.ai/api/v1",
    defaultModel: "openrouter/auto",
    suggestedModels: ["openrouter/auto", "meta-llama/llama-3.3-70b-instruct", "anthropic/claude-3.5-sonnet", "deepseek/deepseek-r1"],
  },
  {
    id: "openai",
    name: "OpenAI Direct",
    badge: "Official API",
    defaultBaseUrl: "https://api.openai.com/v1",
    defaultModel: "gpt-4o-mini",
    suggestedModels: ["gpt-4o-mini", "gpt-4o", "o3-mini"],
  },
  {
    id: "groq",
    name: "Groq Cloud",
    badge: "Fast LPU",
    defaultBaseUrl: "https://api.groq.com/openai/v1",
    defaultModel: "llama-3.3-70b-versatile",
    suggestedModels: ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
  },
  {
    id: "lmstudio",
    name: "LM Studio (Local LLM)",
    badge: "100% Local (OpenAI Compatible)",
    defaultBaseUrl: "http://127.0.0.1:1234/v1",
    defaultModel: "qwen3.5-4b-uncensored-hauhaucs-aggressive",
    suggestedModels: ["qwen3.5-4b-uncensored-hauhaucs-aggressive", "llama-3.2-3b-instruct", "deepseek-r1-distill-qwen-7b"],
  },
  {
    id: "ollama",
    name: "Ollama (Local LLM)",
    badge: "100% Local",
    defaultBaseUrl: "http://localhost:11434/v1",
    defaultModel: "llama3.2",
    suggestedModels: ["llama3.2", "llama3.1:8b", "deepseek-r1:8b", "mistral"],
  },
  {
    id: "custom",
    name: "Custom OpenAI-Compatible",
    badge: "Custom Endpoint",
    defaultBaseUrl: "http://localhost:8000/v1",
    defaultModel: "best-free",
    suggestedModels: ["best-free", "gpt-4o-mini", "llama-3.3-70b-versatile"],
  },
];

export function AIProvidersSection() {
  const queryClient = useQueryClient();
  const [apiKey, setApiKey] = useState("");
  const [baseUrl, setBaseUrl] = useState("http://localhost:8080/v1");
  const [defaultModel, setDefaultModel] = useState("best-free");
  const [customModel, setCustomModel] = useState("");
  const [showKey, setShowKey] = useState(false);

  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<OmniRouteTestResult | null>(null);

  const { data: config, isLoading } = useQuery({
    queryKey: ["omniroute-config"],
    queryFn: () => settingsService.getOmniRouteConfig(),
  });

  const { data: models = [] } = useQuery({
    queryKey: ["omniroute-models"],
    queryFn: () => settingsService.getOmniRouteModels(),
  });

  useEffect(() => {
    if (config) {
      if (config.base_url) setBaseUrl(config.base_url);
      if (config.default_model) setDefaultModel(config.default_model);
    }
  }, [config]);

  const updateMutation = useMutation({
    mutationFn: (payload: { omniroute_api_key?: string; omniroute_base_url?: string; default_model?: string }) =>
      settingsService.updateOmniRouteConfig(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["omniroute-config"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-metrics"] });
      alert("AI Provider Gateway configuration saved successfully.");
    },
    onError: (err: any) => {
      alert("Failed to update configuration: " + err.message);
    },
  });

  const handleApplyPreset = (preset: ProviderPreset) => {
    setBaseUrl(preset.defaultBaseUrl);
    setDefaultModel(preset.defaultModel);
    setCustomModel("");
    setTestResult(null);
  };

  const handleTest = async () => {
    setIsTesting(true);
    setTestResult(null);
    try {
      const activeModel = customModel.trim() || defaultModel;
      const res = await settingsService.testOmniRoute({
        api_key: apiKey.trim() || (config?.is_configured ? "active-saved-key" : ""),
        base_url: baseUrl.trim(),
        model: activeModel,
      });
      setTestResult(res);
    } catch (err: any) {
      setTestResult({
        success: false,
        latency_ms: 0,
        message: err.message || "Failed to reach AI service endpoint.",
        available_models: [],
      });
    } finally {
      setIsTesting(false);
    }
  };

  const handleSave = () => {
    const activeModel = customModel.trim() || defaultModel;
    updateMutation.mutate({
      omniroute_api_key: apiKey.trim() ? apiKey.trim() : undefined,
      omniroute_base_url: baseUrl.trim(),
      default_model: activeModel.trim(),
    });
  };

  if (isLoading) {
    return (
      <Card className="p-8 text-center text-xs text-muted-foreground">
        <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2 text-primary" />
        Loading AI provider gateway configuration...
      </Card>
    );
  }

  return (
    <Card className="border-border/80 shadow-sm space-y-6">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-base font-bold flex items-center gap-2">
              <Zap className="h-4 w-4 text-primary" /> Universal AI Provider Gateway
            </CardTitle>
            <CardDescription className="text-xs mt-0.5">
              Connect OmniRoute (recommended free gateway), OpenRouter, OpenAI, Groq, Ollama, or any OpenAI-compatible API.
            </CardDescription>
          </div>
          <Badge
            variant="secondary"
            className={cn(
              "text-xs",
              config?.is_configured ? "bg-emerald-500/20 text-emerald-400" : "bg-amber-500/20 text-amber-400"
            )}
          >
            {config?.is_configured ? "Gateway Connected" : "Needs API Key"}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Provider Presets */}
        <div className="space-y-2">
          <Label className="text-xs font-semibold">Quick Switch Provider Presets</Label>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {PROVIDER_PRESETS.map((p) => {
              const isMatch = baseUrl.includes(new URL(p.defaultBaseUrl).hostname);
              return (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => handleApplyPreset(p)}
                  className={cn(
                    "p-2.5 rounded-xl border text-left text-xs transition-all flex flex-col justify-between space-y-1",
                    isMatch
                      ? "border-primary bg-primary/10 text-primary ring-1 ring-primary"
                      : "border-border/60 bg-card hover:border-border text-foreground"
                  )}
                >
                  <div className="flex items-center justify-between font-bold">
                    <span>{p.name}</span>
                    {isMatch && <Check className="h-3.5 w-3.5 shrink-0" />}
                  </div>
                  {p.badge && (
                    <span className="text-[10px] text-muted-foreground font-mono">{p.badge}</span>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Gateway URL */}
        <div className="space-y-1.5">
          <Label htmlFor="base-url" className="text-xs">Gateway / Endpoint Base URL</Label>
          <Input
            id="base-url"
            value={baseUrl}
            onChange={(e) => setBaseUrl(e.target.value)}
            placeholder="http://localhost:8080/v1"
            className="font-mono text-xs"
          />
        </div>

        {/* API Key */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <Label htmlFor="api-key" className="text-xs">
              API Authorization Key {config?.is_configured && <span className="text-muted-foreground font-normal">({config.masked_api_key})</span>}
            </Label>
          </div>
          <div className="relative">
            <Input
              id="api-key"
              type={showKey ? "text" : "password"}
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder={config?.is_configured ? "Leave blank to keep existing active key" : "sk-... (or leave blank for local Ollama)"}
              className="font-mono text-xs pr-10"
            />
            <button
              type="button"
              onClick={() => setShowKey(!showKey)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              {showKey ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
            </button>
          </div>
        </div>

        {/* Model Selection */}
        <div className="space-y-2">
          <Label htmlFor="default-model" className="text-xs">Default Model / Routing Strategy</Label>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {models.slice(0, 6).map((m) => (
              <button
                key={m}
                type="button"
                onClick={() => {
                  setDefaultModel(m);
                  setCustomModel("");
                }}
                className={cn(
                  "p-2.5 rounded-lg border text-left text-xs font-mono transition-all flex items-center justify-between",
                  defaultModel === m && !customModel
                    ? "border-primary bg-primary/10 text-primary ring-1 ring-primary"
                    : "border-border/60 bg-card hover:border-border text-foreground"
                )}
              >
                <span className="truncate">{m}</span>
                {defaultModel === m && !customModel && <CheckCircle2 className="h-3.5 w-3.5 shrink-0" />}
              </button>
            ))}
          </div>

          <div className="pt-1.5">
            <Input
              id="custom-model"
              value={customModel}
              onChange={(e) => setCustomModel(e.target.value)}
              placeholder={`Or type custom model name (current: ${defaultModel})`}
              className="font-mono text-xs"
            />
          </div>
        </div>

        {/* Connection Test & Save */}
        <div className="pt-3 flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-border/60">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={handleTest}
            disabled={isTesting}
            className="w-full sm:w-auto text-xs"
          >
            {isTesting ? <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" /> : <Zap className="mr-1.5 h-3.5 w-3.5 text-primary" />}
            Test Endpoint Connection
          </Button>

          <Button
            type="button"
            size="sm"
            onClick={handleSave}
            disabled={updateMutation.isPending}
            className="w-full sm:w-auto text-xs bg-primary hover:bg-primary/90 text-white"
          >
            {updateMutation.isPending ? <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" /> : <Save className="mr-1.5 h-3.5 w-3.5" />}
            Save Gateway Settings
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
            <AlertDescription className="flex items-center justify-between">
              <span>{testResult.message}</span>
              {testResult.latency_ms > 0 && <span className="font-mono">{testResult.latency_ms}ms</span>}
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}
