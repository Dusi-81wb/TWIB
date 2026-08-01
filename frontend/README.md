# Frontend

## Purpose

The Next.js React application providing the user interface for TWIB. This is the presentation layer in Clean Architecture.

## Responsibilities

- Render workflow builder interface
- Display real-time workflow execution status
- Provide agent interaction UI
- Handle user authentication flows
- Communicate with backend via REST and WebSocket

## What Belongs Here

- Next.js App Router pages and layouts
- React components (UI primitives, feature components)
- Client-side state management (Zustand stores)
- API client (TanStack Query hooks)
- TypeScript types shared with backend schemas
- Tailwind CSS configuration
- Static assets

## What Must NEVER Belong Here

- Business logic
- Database queries
- Direct LLM provider calls
- Authentication implementation (use auth provider SDK only)
- File system access
- Background job processing

## Dependencies

- Backend API (REST + WebSocket)
- Authentication provider (Auth0/Clerk)
- Shared TypeScript types (from backend schemas)

## Future Phases

- Phase 9: Initial dashboard implementation
- Phase 10: Real-time collaboration features
- Phase 12: Analytics dashboard