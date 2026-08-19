"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { settingsService, ApiKeyItem } from "@/services/settings.service";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Key, Plus, Trash2, Copy, Check, X, ShieldAlert } from "lucide-react";

export function ApiKeysSection() {
  const { data: keys = [], refetch } = useQuery({
    queryKey: ["api-keys"],
    queryFn: () => settingsService.getApiKeys(),
  });

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [keyName, setKeyName] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [createdSecret, setCreatedSecret] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!keyName.trim()) return;
    setIsCreating(true);
    try {
      const res = await settingsService.createApiKey({ name: keyName });
      setCreatedSecret(res.api_key);
      setKeyName("");
      refetch();
    } catch {
      // Fallback
    } finally {
      setIsCreating(false);
    }
  };

  const handleRevoke = async (keyId: string) => {
    try {
      await settingsService.revokeApiKey(keyId);
      refetch();
    } catch {
      // Fallback
    }
  };

  const handleCopySecret = () => {
    if (createdSecret) {
      navigator.clipboard.writeText(createdSecret);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <Card className="border-border/80 shadow-sm space-y-4">
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="text-base font-bold">API Key Management</CardTitle>
          <CardDescription className="text-xs">
            Generate and revoke API keys for TWIB CLI and automated pipeline authentication.
          </CardDescription>
        </div>
        <Button size="sm" onClick={() => setIsModalOpen(true)}>
          <Plus className="mr-2 h-4 w-4" /> Create API Key
        </Button>
      </CardHeader>

      <CardContent>
        <div className="overflow-x-auto rounded-xl border border-border/80">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-border bg-accent/30 text-muted-foreground font-semibold uppercase tracking-wider text-[10px]">
              <tr>
                <th className="py-3 px-4">Key Name</th>
                <th className="py-3 px-4">Key Prefix</th>
                <th className="py-3 px-4">Created</th>
                <th className="py-3 px-4">Last Used</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60">
              {keys.map((k) => (
                <tr key={k.id} className="hover:bg-accent/20 transition-colors">
                  <td className="py-3 px-4 font-semibold text-foreground flex items-center gap-2">
                    <Key className="h-3.5 w-3.5 text-primary" /> {k.name}
                  </td>
                  <td className="py-3 px-4 font-mono text-[11px] text-muted-foreground">{k.key_prefix}</td>
                  <td className="py-3 px-4 font-mono text-[11px] text-muted-foreground">{k.created_at}</td>
                  <td className="py-3 px-4 text-muted-foreground">{k.last_used_at || "Never"}</td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => handleRevoke(k.id)}
                      className="text-muted-foreground hover:text-destructive transition-colors p-1"
                      title="Revoke Key"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Modal for Create API Key */}
        {isModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm p-4">
            <Card className="w-full max-w-md p-6 border-border shadow-xl space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Key className="h-5 w-5 text-primary" />
                  <h3 className="text-base font-bold">Create API Key</h3>
                </div>
                <button
                  onClick={() => {
                    setIsModalOpen(false);
                    setCreatedSecret(null);
                  }}
                  className="text-muted-foreground hover:text-foreground"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              {createdSecret ? (
                <div className="space-y-4">
                  <Alert variant="warning" className="border-amber-500/50 bg-amber-500/10">
                    <ShieldAlert className="h-4 w-4 text-amber-500" />
                    <AlertDescription className="text-amber-600 dark:text-amber-400 text-xs">
                      Copy your API secret key now. It will never be shown again!
                    </AlertDescription>
                  </Alert>

                  <div className="space-y-2">
                    <Label>Generated Secret Key</Label>
                    <div className="flex items-center gap-2">
                      <Input value={createdSecret} readOnly className="font-mono text-xs bg-accent/40" />
                      <Button size="icon" variant="outline" onClick={handleCopySecret}>
                        {copied ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                      </Button>
                    </div>
                  </div>

                  <Button
                    className="w-full"
                    onClick={() => {
                      setIsModalOpen(false);
                      setCreatedSecret(null);
                    }}
                  >
                    Done
                  </Button>
                </div>
              ) : (
                <form onSubmit={handleCreate} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="key-name">API Key Name</Label>
                    <Input
                      id="key-name"
                      placeholder="e.g. CI/CD Deployment Key"
                      value={keyName}
                      onChange={(e) => setKeyName(e.target.value)}
                      required
                    />
                  </div>

                  <div className="flex justify-end gap-2 pt-2">
                    <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>
                      Cancel
                    </Button>
                    <Button type="submit" disabled={isCreating}>
                      {isCreating ? "Generating..." : "Generate Key"}
                    </Button>
                  </div>
                </form>
              )}
            </Card>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
