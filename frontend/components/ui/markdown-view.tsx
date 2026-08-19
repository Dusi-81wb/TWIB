"use client";

import React from "react";

interface MarkdownViewProps {
  content: string;
  className?: string;
}

export function MarkdownView({ content, className = "" }: MarkdownViewProps) {
  if (!content) return null;

  // Simple, robust markdown parser converting blocks to formatted JSX
  const parseMarkdown = (raw: string) => {
    const lines = raw.split("\n");
    const elements: React.ReactNode[] = [];
    let inCodeBlock = false;
    let codeBuffer: string[] = [];
    let codeLang = "";
    let listBuffer: string[] = [];

    const flushList = () => {
      if (listBuffer.length > 0) {
        elements.push(
          <ul key={`list-${elements.length}`} className="list-disc list-inside space-y-1 my-2 text-foreground/90 pl-2">
            {listBuffer.map((item, idx) => (
              <li key={idx} className="leading-relaxed">
                {renderInline(item)}
              </li>
            ))}
          </ul>
        );
        listBuffer = [];
      }
    };

    lines.forEach((line, index) => {
      // Code block start/end
      if (line.trim().startsWith("```")) {
        if (inCodeBlock) {
          elements.push(
            <div key={`code-${index}`} className="my-3 rounded-lg border border-border/80 bg-zinc-950 p-4 font-mono text-xs overflow-x-auto text-emerald-400 shadow-inner">
              {codeLang && <div className="text-[10px] uppercase text-zinc-500 font-bold mb-2 tracking-wider">{codeLang}</div>}
              <pre className="whitespace-pre">{codeBuffer.join("\n")}</pre>
            </div>
          );
          codeBuffer = [];
          codeLang = "";
          inCodeBlock = false;
        } else {
          flushList();
          inCodeBlock = true;
          codeLang = line.trim().replace(/^```/, "").trim();
        }
        return;
      }

      if (inCodeBlock) {
        codeBuffer.push(line);
        return;
      }

      // Unordered list item
      const listMatch = line.match(/^(\*|-|\+)\s+(.+)$/);
      if (listMatch) {
        listBuffer.push(listMatch[2]);
        return;
      } else {
        flushList();
      }

      // Headings
      if (line.startsWith("# ")) {
        elements.push(
          <h1 key={`h1-${index}`} className="text-xl font-extrabold text-foreground tracking-tight mt-4 mb-2 pb-1 border-b border-border/40">
            {renderInline(line.replace("# ", ""))}
          </h1>
        );
        return;
      }

      if (line.startsWith("## ")) {
        elements.push(
          <h2 key={`h2-${index}`} className="text-lg font-bold text-foreground tracking-tight mt-3 mb-2">
            {renderInline(line.replace("## ", ""))}
          </h2>
        );
        return;
      }

      if (line.startsWith("### ")) {
        elements.push(
          <h3 key={`h3-${index}`} className="text-base font-semibold text-foreground tracking-tight mt-3 mb-1">
            {renderInline(line.replace("### ", ""))}
          </h3>
        );
        return;
      }

      // Blockquotes
      if (line.startsWith("> ")) {
        elements.push(
          <blockquote key={`quote-${index}`} className="my-2 border-l-2 border-primary/70 pl-3 italic text-muted-foreground bg-primary/5 py-1 rounded-r">
            {renderInline(line.replace("> ", ""))}
          </blockquote>
        );
        return;
      }

      // Empty lines
      if (!line.trim()) {
        return;
      }

      // Paragraph
      elements.push(
        <p key={`p-${index}`} className="my-2 text-sm text-foreground/90 leading-relaxed">
          {renderInline(line)}
        </p>
      );
    });

    flushList();
    return elements;
  };

  const renderInline = (text: string): React.ReactNode => {
    // Process inline bold **bold** and code `code`
    const parts = text.split(/(\*\*.*?\*\*|`.*?`)/g);
    return parts.map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return <strong key={i} className="font-bold text-foreground">{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith("`") && part.endsWith("`")) {
        return <code key={i} className="rounded bg-accent/60 px-1.5 py-0.5 font-mono text-[12px] text-primary">{part.slice(1, -1)}</code>;
      }
      return part;
    });
  };

  return <div className={`space-y-1 text-sm ${className}`}>{parseMarkdown(content)}</div>;
}
