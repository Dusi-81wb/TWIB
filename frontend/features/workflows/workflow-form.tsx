"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useRouter } from "next/navigation";
import { workflowService, WorkflowTemplateItem } from "@/services/workflow.service";
import { TemplateSelector } from "./template-selector";
import { PipelinePreview } from "./pipeline-preview";
import { DynamicDAGBuilder } from "./dynamic-dag-builder";
import { ExecutionOptions } from "./execution-options";
import { WorkflowSummary } from "./workflow-summary";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, AlertCircle, Play, FileCheck, Sparkles, Layers } from "lucide-react";
import { AgentDAGPlan } from "@/types/dag";
import { cn } from "@/lib/utils";

const workflowBuilderSchema = z.object({
  workflow_name: z.string().min(2, "Workflow name must be at least 2 characters"),
  category: z.string().optional(),
  user_request: z.string().min(5, "Objective prompt must be at least 5 characters"),
  template_id: z.string().default("none"),
  start_immediately: z.boolean().default(true),
  require_approval: z.boolean().default(false),
});

type WorkflowFormValues = z.infer<typeof workflowBuilderSchema>;

export function WorkflowForm() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [selectedTemplateName, setSelectedTemplateName] = useState<string>("Custom / No Template");
  const [isDynamicDAG, setIsDynamicDAG] = useState<boolean>(true);
  const [dagPlan, setDagPlan] = useState<AgentDAGPlan | null>(null);

  const router = useRouter();

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<WorkflowFormValues>({
    resolver: zodResolver(workflowBuilderSchema),
    defaultValues: {
      workflow_name: "",
      category: "engineering",
      user_request: "",
      template_id: "none",
      start_immediately: true,
      require_approval: false,
    },
  });

  const watchedValues = watch();

  const handleSelectTemplate = (template: WorkflowTemplateItem | null) => {
    if (template) {
      setValue("template_id", template.id);
      setValue("workflow_name", template.name);
      setValue("category", template.category);
      if (template.suggested_prompt) {
        setValue("user_request", template.suggested_prompt);
      }
      setSelectedTemplateName(template.name);
    } else {
      setValue("template_id", "none");
      setSelectedTemplateName("Custom / No Template");
    }
  };

  const onSubmit = async (values: WorkflowFormValues) => {
    setFormError(null);
    setIsSubmitting(true);
    try {
      const res = await workflowService.createWorkflow({
        workflow_name: values.workflow_name,
        user_request: values.user_request,
        category: values.category,
        template_id: values.template_id,
        start_immediately: values.start_immediately,
      });

      if (values.start_immediately) {
        router.push(`/monitoring?workflow_id=${res.workflow_id}`);
      } else {
        router.push("/workflows");
      }
    } catch (err: unknown) {
      const msg =
        err && typeof err === "object" && "message" in err
          ? (err as { message: string }).message
          : "Failed to create workflow. Please check input parameters.";
      setFormError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6" noValidate>
      {formError && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{formError}</AlertDescription>
        </Alert>
      )}

      {/* Section 1: Template Selection */}
      <TemplateSelector
        selectedTemplateId={watchedValues.template_id}
        onSelectTemplate={handleSelectTemplate}
      />

      {/* Section 2: Workflow Information */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-2 space-y-2">
          <Label htmlFor="workflow_name">Workflow Name *</Label>
          <Input
            id="workflow_name"
            placeholder="e.g. Enterprise Market & Architecture Audit"
            disabled={isSubmitting}
            aria-invalid={!!errors.workflow_name}
            {...register("workflow_name")}
          />
          {errors.workflow_name && (
            <p className="text-xs text-destructive">{errors.workflow_name.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="category">Category</Label>
          <select
            id="category"
            disabled={isSubmitting}
            className="flex h-9 w-full rounded-md border border-input bg-card px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            {...register("category")}
          >
            <option value="engineering">Engineering</option>
            <option value="strategy">Strategy</option>
            <option value="compliance">Compliance</option>
            <option value="custom">Custom</option>
          </select>
        </div>
      </div>

      {/* Section 3: Objective Prompt */}
      <div className="space-y-2">
        <Label htmlFor="user_request">Objective & Prompt *</Label>
        <textarea
          id="user_request"
          rows={4}
          placeholder="Describe your goal in detail (e.g., 'Design a microservices architecture for a hospital management system with security verification...')"
          className="flex w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 font-sans"
          disabled={isSubmitting}
          aria-invalid={!!errors.user_request}
          {...register("user_request")}
        />
        {errors.user_request && (
          <p className="text-xs text-destructive">{errors.user_request.message}</p>
        )}
      </div>

      {/* Section 4: Execution Architecture & DAG Mode */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <Label className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
            Multi-Agent Architecture Mode
          </Label>
          <div className="flex items-center gap-1 p-0.5 rounded-lg border border-border bg-muted/40 text-xs">
            <button
              type="button"
              onClick={() => setIsDynamicDAG(true)}
              className={cn(
                "px-2.5 py-1 rounded-md transition-all flex items-center gap-1.5 font-medium",
                isDynamicDAG ? "bg-background text-foreground shadow-xs" : "text-muted-foreground hover:text-foreground"
              )}
            >
              <Sparkles className="h-3.5 w-3.5 text-primary" />
              Dynamic DAG Flow
            </button>
            <button
              type="button"
              onClick={() => setIsDynamicDAG(false)}
              className={cn(
                "px-2.5 py-1 rounded-md transition-all flex items-center gap-1.5 font-medium",
                !isDynamicDAG ? "bg-background text-foreground shadow-xs" : "text-muted-foreground hover:text-foreground"
              )}
            >
              <Layers className="h-3.5 w-3.5" />
              Fixed Pipeline
            </button>
          </div>
        </div>

        {isDynamicDAG ? (
          <DynamicDAGBuilder
            initialGoal={watchedValues.user_request}
            onPlanChange={(plan) => setDagPlan(plan)}
          />
        ) : (
          <PipelinePreview />
        )}
      </div>

      {/* Section 5: Execution Control Options */}
      <ExecutionOptions
        startImmediately={watchedValues.start_immediately}
        onToggleStartImmediately={(val) => setValue("start_immediately", val)}
        requireApproval={watchedValues.require_approval}
        onToggleRequireApproval={(val) => setValue("require_approval", val)}
      />

      {/* Section 6: Live Summary */}
      <WorkflowSummary
        name={watchedValues.workflow_name}
        category={watchedValues.category || "custom"}
        templateName={selectedTemplateName}
        userRequest={watchedValues.user_request}
        startImmediately={watchedValues.start_immediately}
        requireApproval={watchedValues.require_approval}
      />

      {/* Submission Actions */}
      <div className="flex items-center justify-end gap-3 pt-4 border-t border-border">
        <Button
          type="button"
          variant="outline"
          onClick={() => router.back()}
          disabled={isSubmitting}
        >
          Cancel
        </Button>

        <Button type="submit" disabled={isSubmitting} className="min-w-[160px]">
          {isSubmitting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Initializing...
            </>
          ) : watchedValues.start_immediately ? (
            <>
              <Play className="mr-2 h-4 w-4" /> Start Workflow
            </>
          ) : (
            <>
              <FileCheck className="mr-2 h-4 w-4" /> Save Workflow
            </>
          )}
        </Button>
      </div>
    </form>
  );
}
