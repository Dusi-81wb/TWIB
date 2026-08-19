"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { BrainCircuit, Sparkles, Cpu, Code2, Network, ShieldCheck } from "lucide-react";

interface HeroEmptyStateProps {
  onSelectSuggestion: (promptText: string) => void;
}

const SUGGESTIONS = [
  {
    icon: Network,
    title: "Consensus Algorithms",
    prompt: "Compare distributed consensus algorithms like Raft, Paxos, and Zab for high-throughput microservices architecture.",
  },
  {
    icon: ShieldCheck,
    title: "Kubernetes Best Practices",
    prompt: "Summarize industry best practices for zero-downtime Kubernetes deployments and service mesh configuration.",
  },
  {
    icon: Code2,
    title: "API Protocols Comparison",
    prompt: "Analyze performance, latency, and developer ergonomics trade-offs between REST, gRPC, and GraphQL.",
  },
  {
    icon: Cpu,
    title: "Caching Strategies",
    prompt: "Explain microservices multi-level caching strategies using Redis, Memcached, and local in-memory caches.",
  },
];

export function HeroEmptyState({ onSelectSuggestion }: HeroEmptyStateProps) {
  const heroRef = useRef<HTMLDivElement>(null);
  const cardsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (heroRef.current && cardsRef.current) {
      gsap.fromTo(
        heroRef.current,
        { opacity: 0, y: 15, scale: 0.98 },
        { opacity: 1, y: 0, scale: 1, duration: 0.6, ease: "power3.out" }
      );

      gsap.fromTo(
        cardsRef.current.children,
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.5, stagger: 0.08, ease: "power2.out", delay: 0.2 }
      );
    }
  }, []);

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 md:p-12 text-center max-w-4xl mx-auto space-y-8 select-none">
      {/* Hero Icon & Title */}
      <div ref={heroRef} className="space-y-4 flex flex-col items-center">
        <div className="relative flex items-center justify-center">
          <div className="absolute inset-0 bg-primary/20 rounded-3xl blur-2xl animate-pulse" />
          <div className="relative rounded-3xl border border-primary/30 bg-primary/10 p-4 shadow-xl backdrop-blur-xl">
            <BrainCircuit className="h-12 w-12 text-primary" />
          </div>
        </div>

        <div className="space-y-2">
          <div className="inline-flex items-center gap-1.5 rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary border border-primary/20">
            <Sparkles className="h-3.5 w-3.5" /> Autonomous Research Agent
          </div>
          <h2 className="text-3xl md:text-4xl font-extrabold tracking-tight text-foreground">
            What should we investigate today?
          </h2>
          <p className="text-sm text-muted-foreground max-w-lg mx-auto">
            Powered by OmniRoute LLM Gateway. Ask any technical query, architectural question, or domain research prompt.
          </p>
        </div>
      </div>

      {/* Suggestion Cards Grid */}
      <div ref={cardsRef} className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 w-full">
        {SUGGESTIONS.map((item, idx) => {
          const Icon = item.icon;
          return (
            <div
              key={idx}
              onClick={() => onSelectSuggestion(item.prompt)}
              className="group text-left p-4 rounded-2xl glass-card border border-white/10 hover:bg-primary/10 hover:border-primary/50 cursor-pointer transition-all duration-200 shadow-sm hover:shadow-md space-y-2"
            >
              <div className="flex items-center gap-2 text-foreground font-semibold text-xs group-hover:text-primary transition-colors">
                <Icon className="h-4 w-4 text-primary shrink-0" />
                <span>{item.title}</span>
              </div>
              <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed font-mono text-[11px]">
                {item.prompt}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
