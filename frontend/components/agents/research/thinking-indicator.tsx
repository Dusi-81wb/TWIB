"use client";

import { useEffect, useState, useRef } from "react";
import gsap from "gsap";
import { BrainCircuit, Loader2, Sparkles } from "lucide-react";

const THINKING_STEPS = [
  "Querying OmniRoute Gateway...",
  "Gathering domain facts & sources...",
  "Synthesizing structured knowledge...",
  "Formatting research insights...",
];

export function ThinkingIndicator() {
  const [stepIndex, setStepIndex] = useState(0);
  const textRef = useRef<HTMLSpanElement>(null);
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (cardRef.current) {
      gsap.fromTo(
        cardRef.current,
        { opacity: 0, y: 10, scale: 0.98 },
        { opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "power2.out" }
      );
    }

    const interval = setInterval(() => {
      if (textRef.current) {
        gsap.to(textRef.current, {
          opacity: 0,
          y: -5,
          duration: 0.25,
          onComplete: () => {
            setStepIndex((prev) => (prev + 1) % THINKING_STEPS.length);
            gsap.fromTo(
              textRef.current,
              { opacity: 0, y: 5 },
              { opacity: 1, y: 0, duration: 0.25 }
            );
          },
        });
      }
    }, 2200);

    return () => clearInterval(interval);
  }, []);

  return (
    <div
      ref={cardRef}
      className="flex items-start gap-3 my-4 max-w-2xl text-xs font-mono select-none"
    >
      {/* Agent Avatar */}
      <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-xl border border-primary/40 bg-primary/10 text-primary shadow-sm">
        <BrainCircuit className="h-4 w-4 animate-pulse" />
      </div>

      {/* Card Content */}
      <div className="flex-1 rounded-2xl border border-border/80 bg-accent/30 p-3.5 shadow-sm space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-primary font-semibold text-[11px]">
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
            <span ref={textRef} className="inline-block">
              {THINKING_STEPS[stepIndex]}
            </span>
          </div>
          <Sparkles className="h-3.5 w-3.5 text-primary/60 animate-bounce" />
        </div>

        {/* Shimmer Progress Line */}
        <div className="relative h-1 w-full bg-accent/60 rounded-full overflow-hidden">
          <div className="absolute inset-y-0 left-0 w-1/3 bg-gradient-to-r from-primary/20 via-primary to-primary/20 rounded-full animate-pulse" />
        </div>
      </div>
    </div>
  );
}
