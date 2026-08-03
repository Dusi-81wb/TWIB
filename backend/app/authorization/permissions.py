"""System permissions constants.

Centralizes string constants for every permission in the TWIB platform.
Permissions follow the ``resource.action`` naming convention.
"""

from __future__ import annotations

# Organization permissions
ORGANIZATION_READ: str = "organization.read"
ORGANIZATION_UPDATE: str = "organization.update"
ORGANIZATION_DELETE: str = "organization.delete"
ORGANIZATION_MANAGE_MEMBERS: str = "organization.manage_members"

# Workspace permissions
WORKSPACE_READ: str = "workspace.read"
WORKSPACE_CREATE: str = "workspace.create"
WORKSPACE_UPDATE: str = "workspace.update"
WORKSPACE_DELETE: str = "workspace.delete"
WORKSPACE_MANAGE_MEMBERS: str = "workspace.manage_members"

# Workflow permissions
WORKFLOW_READ: str = "workflow.read"
WORKFLOW_CREATE: str = "workflow.create"
WORKFLOW_UPDATE: str = "workflow.update"
WORKFLOW_EXECUTE: str = "workflow.execute"
WORKFLOW_DELETE: str = "workflow.delete"

# Agent permissions
AGENT_READ: str = "agent.read"
AGENT_CREATE: str = "agent.create"
AGENT_UPDATE: str = "agent.update"
AGENT_EXECUTE: str = "agent.execute"
AGENT_DELETE: str = "agent.delete"

# Knowledge Base permissions
KNOWLEDGE_READ: str = "knowledge.read"
KNOWLEDGE_WRITE: str = "knowledge.write"
KNOWLEDGE_DELETE: str = "knowledge.delete"

# API Key permissions
API_KEY_READ: str = "api_key.read"
API_KEY_CREATE: str = "api_key.create"
API_KEY_DELETE: str = "api_key.delete"

ALL_PERMISSIONS: set[str] = {
    ORGANIZATION_READ,
    ORGANIZATION_UPDATE,
    ORGANIZATION_DELETE,
    ORGANIZATION_MANAGE_MEMBERS,
    WORKSPACE_READ,
    WORKSPACE_CREATE,
    WORKSPACE_UPDATE,
    WORKSPACE_DELETE,
    WORKSPACE_MANAGE_MEMBERS,
    WORKFLOW_READ,
    WORKFLOW_CREATE,
    WORKFLOW_UPDATE,
    WORKFLOW_EXECUTE,
    WORKFLOW_DELETE,
    AGENT_READ,
    AGENT_CREATE,
    AGENT_UPDATE,
    AGENT_EXECUTE,
    AGENT_DELETE,
    KNOWLEDGE_READ,
    KNOWLEDGE_WRITE,
    KNOWLEDGE_DELETE,
    API_KEY_READ,
    API_KEY_CREATE,
    API_KEY_DELETE,
}
