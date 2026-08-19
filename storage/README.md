# Storage

## Purpose

File storage abstraction supporting multiple backends (S3, GCS, Azure Blob, local) for documents, artifacts, and generated assets.

## Responsibilities

- Storage provider abstraction
- Upload/download operations
- Presigned URL generation
- Multipart uploads
- Lifecycle policies
- CDN integration
- Access control

## What Belongs Here

- Storage interface
- Provider implementations (S3, GCS, Local)
- Upload service
- File metadata management

## What Must NEVER Belong Here

- Business logic
- Database operations
- File processing (use services/)

## Dependencies

- `boto3` / `google-cloud-storage` / `azure-storage-blob`
- `backend.config` - Storage credentials

## Future Phases

- Phase 8: Storage for workflow artifacts
- Phase 9: Frontend uploads