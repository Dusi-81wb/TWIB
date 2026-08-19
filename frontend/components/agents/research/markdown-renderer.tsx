"use client";

import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeKatex from "rehype-katex";
import rehypeHighlight from "rehype-highlight";
import "katex/dist/katex.min.css";
import { Check, Copy, Code2 } from "lucide-react";
import { Button } from "@/components/ui/button";

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

/** Helper function to safely extract raw string text from React AST children trees. */
function extractRawText(node: React.ReactNode): string {
  if (node === null || node === undefined) return "";
  if (typeof node === "string") return node;
  if (typeof node === "number") return String(node);
  if (Array.isArray(node)) return node.map(extractRawText).join("");
  if (typeof node === "object" && node !== null && "props" in node) {
    const reactElem = node as { props?: { children?: React.ReactNode } };
    return extractRawText(reactElem.props?.children);
  }
  return "";
}

export function MarkdownRenderer({ content, className = "" }: MarkdownRendererProps) {
  if (!content) return null;

  let displayMarkdown = content;

  // Auto-convert legacy raw JSON strings to clean Markdown if JSON is passed
  const trimmed = content.trim();
  if (trimmed.startsWith("{") && trimmed.endsWith("}") && trimmed.includes('"summary"')) {
    try {
      const parsed = JSON.parse(trimmed);
      if (parsed && typeof parsed === "object") {
        const parts: string[] = [];
        if (parsed.topic) parts.push(`# ${parsed.topic}\n`);
        if (parsed.summary) parts.push(`${parsed.summary}\n`);
        if (Array.isArray(parsed.key_findings) && parsed.key_findings.length > 0) {
          parts.push(
            `## Key Findings\n` +
              parsed.key_findings.map((f: string) => `- ${f}`).join("\n") +
              "\n"
          );
        }
        if (Array.isArray(parsed.best_practices) && parsed.best_practices.length > 0) {
          parts.push(
            `## Recommended Best Practices\n` +
              parsed.best_practices.map((b: string) => `- ${b}`).join("\n") +
              "\n"
          );
        }
        if (Array.isArray(parsed.risks) && parsed.risks.length > 0) {
          parts.push(
            `## Key Risks\n` +
              parsed.risks.map((r: string) => `- ${r}`).join("\n") +
              "\n"
          );
        }
        if (Array.isArray(parsed.references) && parsed.references.length > 0) {
          parts.push(
            `## References\n` +
              parsed.references.map((rf: string) => `- ${rf}`).join("\n") +
              "\n"
          );
        }
        if (parts.length > 0) {
          displayMarkdown = parts.join("\n");
        }
      }
    } catch {
      // Fall back to original content if parsing fails
    }
  }

  return (
    <div className={`prose dark:prose-invert max-w-none text-sm leading-relaxed ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeKatex, rehypeHighlight]}
        components={{
          code({ className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || "");
            const language = match ? match[1] : "";
            const rawText = extractRawText(children).replace(/\n$/, "");
            const isInline = !match && !rawText.includes("\n");

            if (isInline) {
              return (
                <code
                  className="rounded-md bg-accent/70 px-1.5 py-0.5 font-mono text-[12px] text-primary border border-border/40 font-semibold"
                  {...props}
                >
                  {children}
                </code>
              );
            }

            return (
              <CodeBlock
                language={language}
                value={rawText}
              />
            );
          },
          table({ children }) {
            return (
              <div className="my-4 overflow-x-auto rounded-xl border border-border/70 bg-card/40 shadow-sm">
                <table className="w-full text-left text-xs border-collapse">
                  {children}
                </table>
              </div>
            );
          },
          thead({ children }) {
            return (
              <thead className="bg-accent/40 text-foreground font-semibold border-b border-border/70">
                {children}
              </thead>
            );
          },
          th({ children }) {
            return <th className="px-3.5 py-2.5 font-bold">{children}</th>;
          },
          td({ children }) {
            return <td className="px-3.5 py-2 border-t border-border/40 text-foreground/90">{children}</td>;
          },
          blockquote({ children }) {
            return (
              <blockquote className="my-3 border-l-2 border-primary/80 pl-4 italic text-muted-foreground bg-primary/5 py-1.5 rounded-r-xl">
                {children}
              </blockquote>
            );
          },
          a({ href, children }) {
            return (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary underline underline-offset-4 font-medium hover:text-primary/80 transition-colors"
              >
                {children}
              </a>
            );
          },
        }}
      >
        {displayMarkdown}
      </ReactMarkdown>
    </div>
  );
}

function CodeBlock({ language, value }: { language: string; value: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative my-4 rounded-xl border border-border/80 bg-zinc-950 text-zinc-100 shadow-md overflow-hidden font-mono text-xs">
      {/* Code Header Bar */}
      <div className="flex items-center justify-between px-3.5 py-2 bg-zinc-900/90 border-b border-zinc-800 text-[11px] select-none text-zinc-400">
        <div className="flex items-center gap-1.5 font-bold uppercase tracking-wider text-zinc-300">
          <Code2 className="h-3.5 w-3.5 text-primary" />
          <span>{language || "code"}</span>
        </div>
        <Button
          size="sm"
          variant="ghost"
          onClick={handleCopy}
          className="h-7 px-2 text-[11px] gap-1 hover:bg-zinc-800 hover:text-zinc-100 text-zinc-400"
        >
          {copied ? (
            <>
              <Check className="h-3 w-3 text-emerald-400" />
              <span className="text-emerald-400">Copied</span>
            </>
          ) : (
            <>
              <Copy className="h-3 w-3" />
              <span>Copy</span>
            </>
          )}
        </Button>
      </div>

      {/* Code Content */}
      <div className="p-4 overflow-x-auto leading-relaxed">
        <pre className="whitespace-pre">
          <code>{value}</code>
        </pre>
      </div>
    </div>
  );
}
