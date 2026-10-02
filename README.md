# IG — AI Image Generator

**Version 2.1.0**

A cloud-ready AI image generation control plane.

Want to use your OpenAI API credits for generating images? Deploy IG and go.

IG provides a web interface and API for submitting image-generation requests, tracking their execution, storing generation metadata, managing generated artifacts, and serving generated images.

The project began as a small self-hosted image-generation application, but is intentionally evolving into a foundation for a more general **AI control-plane framework**.

---

## Overview

IG currently provides:

* Browser-based image generation
* Persistent generation history
* Asynchronous job execution
* Job and execution tracking
* Generated artifact storage
* REST API access
* User authentication
* Multi-user capability
* Configurable self-registration
* Database migrations
* Pluggable job queue architecture
* Pluggable artifact storage
* Cloud-ready deployment

The current cloud deployment uses:

```text
Frontend        Vercel
Backend         Vercel FastAPI
Database        Neon PostgreSQL
Artifacts       Vercel Blob
Job Queue       Vercel Queue
Image Provider  OpenAI
```

IG also supports Redis/RQ as an alternative job queue implementation.

---

## Current Architecture

```text
                         Browser
                            │
                            ▼
                    ┌──────────────┐
                    │    Vercel    │
                    │ React / Vite │
                    └──────┬───────┘
                           │
                           │ /v1/*
                           │ /v2/*
                           │ /health
                           ▼
                    ┌──────────────┐
                    │   FastAPI    │
                    │     API      │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        ┌──────────┐ ┌───────────┐ ┌─────────────┐
        │   Neon   │ │  Vercel   │ │   OpenAI    │
        │PostgreSQL│ │   Queue   │ │  Image API  │
        └──────────┘ └─────┬─────┘ └─────────────┘
                           │
                           ▼
                     Job Execution
                           │
                           ▼
                    ┌──────────────┐
                    │ Vercel Blob  │
                    │  Artifacts   │
                    └──────────────┘
```

The browser does not perform long-running image generation itself.

The API creates a persistent job, submits it to the configured queue provider, and execution continues independently of the browser session.

---

## Components

### Backend

* Python
* FastAPI
* SQLAlchemy
* Alembic

### Frontend

* TypeScript
* React
* Vite

### Database

Primary cloud deployment:

* Neon PostgreSQL

Legacy/local development:

* MariaDB 11
* MySQL-compatible database support

### Artifact Storage

Supported implementations:

* Vercel Blob
* Local filesystem

Artifact access is routed according to storage URI.

Examples:

```text
vercel-blob:///artifacts/...
file:///app/output/...
```

### Job Queues

Supported implementations:

* Vercel Queue
* Redis + RQ

The queue implementation is selected through configuration.

## Redis / RQ

IG also contains a Redis/RQ implementation of the job queue abstraction.

This is an **optional alternative** to Vercel Queue.

If the application is deployed using:

```text
JOB_QUEUE_PROVIDER=vercel
```

then neither Redis nor RQ infrastructure is required.

The default IG 2.1 Vercel architecture can therefore run without provisioning any Redis service or separate worker host.

---

### Redis/RQ Architecture

When:

```text
JOB_QUEUE_PROVIDER=rq
```

the execution path becomes:

```text
Vercel FastAPI
      │
      ▼
External Redis
      │
      ▼
External RQ Worker
      │
      ├── OpenAI
      ├── Database
      └── Artifact Store
```

Both the Redis service and the RQ worker runtime must exist outside the normal Vercel serverless deployment.

Vercel can host the FastAPI producer, but a Redis/RQ configuration requires:

```text
Redis
    persistent Redis-compatible service

RQ worker
    persistent Python process
```

These do not need to be provided by the same vendor.

---

### Example Redis Providers

Examples of managed Redis or Redis-compatible services include:

* **Upstash Redis**
* **Redis Cloud**
* Other managed Redis-compatible providers
* Self-hosted Redis

Upstash has been tested with IG's Redis/RQ implementation.

The application connects using the standard:

```text
REDIS_URL
```

configuration value.

Example:

```text
rediss://default:password@host:6379
```

---

### Example RQ Worker Hosts

RQ itself is a Python job-processing framework rather than a hosted service.

The worker therefore needs somewhere capable of running a long-lived Python process.

Possible worker environments include:

* **Render Background Workers**
* Container hosting platforms
* Virtual machines
* Kubernetes
* VPS providers
* Self-hosted servers or development machines

The worker command is simply:

```bash
rq worker --url "$REDIS_URL" ig
```

A Redis provider and worker host may be combined on one infrastructure provider or supplied independently.

For example:

```text
Vercel
    FastAPI

Upstash
    Redis

Render
    RQ worker
```

or:

```text
Vercel
    FastAPI

Redis Cloud
    Redis

VM / container host
    RQ worker
```

---

### Which Queue Should I Use?

For the standard IG 2.1 deployment on Vercel:

```text
JOB_QUEUE_PROVIDER=vercel
```

is recommended.

This keeps the asynchronous execution path within the Vercel deployment architecture and avoids provisioning an additional Redis service and worker runtime.

Use:

```text
JOB_QUEUE_PROVIDER=rq
```

when an independent Redis-backed worker architecture is desirable or when deploying outside the normal Vercel execution model.

Both implementations use the same IG job abstraction, allowing the queue backend to be selected through configuration rather than application code changes.

### Image Provider

Current provider:

```text
OpenAI
```

Current image model:

```text
gpt-image-2
```

---

## Features

### Image Generation

Submit an image prompt through the web UI or REST API.

The backend creates persistent request and job records before asynchronous execution begins.

---

### Persistent History

Generation records include information such as:

* Request ID
* Creation time
* Prompt
* Model
* Status
* Generated artifacts
* MIME type
* File size
* Generation time
* Job execution state
* Error information

---

### Asynchronous Jobs

Image generation is performed through a job queue.

Once a request has been accepted, the browser does not need to remain connected while generation continues.

This is an important architectural principle:

> The control plane owns the lifecycle of the request, rather than the browser.

The configured queue provider is selected using:

```text
JOB_QUEUE_PROVIDER
```

Supported values currently include:

```text
vercel
rq
```

---

## Vercel Queue

Vercel Queue is the primary queue implementation for the current cloud deployment.

The execution path is:

```text
Browser
   │
   ▼
Vercel FastAPI
   │
   ▼
Vercel Queue
   │
   ▼
Worker / Subscriber
   │
   ├── OpenAI
   ├── Neon
   └── Vercel Blob
```

This architecture has been tested both locally using the Vercel Queue development server and in an actual Vercel deployment.

---

## Redis / RQ

IG also contains a Redis/RQ implementation of the job queue abstraction.

The alternative execution path is:

```text
Vercel FastAPI
      │
      ▼
External Redis
      │
      ▼
RQ Worker
      │
      ├── OpenAI
      ├── Neon
      └── Vercel Blob
```

Redis/RQ was tested successfully using an external Redis service and an RQ worker running on the development machine.

The RQ worker can therefore be moved to any suitable long-running cloud worker environment without changing the application architecture.

For now, Vercel Queue is the preferred development and deployment path because it removes the requirement for a separately hosted worker.

Redis/RQ remains available as an alternative execution backend.

---

## Artifact Storage

Generated images are no longer required to live on the application server filesystem.

The current cloud deployment uses:

```text
ARTIFACT_STORE_PROVIDER=vercel
```

which stores generated images in Vercel Blob.

Local development may instead use:

```text
ARTIFACT_STORE_PROVIDER=local
```

The application uses storage-independent artifact references so execution logic does not need to know where the artifact physically resides.

---

## Authentication

V2 introduces application authentication and multi-user capability.

Public self-registration is controlled using:

```text
ALLOW_SELF_REGISTRATION
```

Recommended production setting:

```text
ALLOW_SELF_REGISTRATION=false
```

When disabled, attempts to create an account through the public registration API are rejected.

Self-registration is intentionally **fail-closed**: if the configuration variable is absent, registration remains disabled.

Local or controlled deployments may explicitly enable registration:

```text
ALLOW_SELF_REGISTRATION=true
```

In the future this setting will become part of the multi-tenant authentication policy.

A platform-level registration control will remain available as a global safety switch.

---

## API

Current APIs include image-generation, authentication, job, execution, and health endpoints.

Core image-generation endpoints include:

```text
POST /v1/images/generations
GET  /v1/images
GET  /v1/images/{request_id}
GET  /v1/images/{request_id}/content
GET  /health
```

Additional V2 APIs provide authentication, jobs, executions, and other control-plane functionality.

FastAPI also exposes OpenAPI documentation.

---

## Deployment

### Recommended Cloud Deployment

The current primary deployment target is Vercel.

The application is structured as a multi-service deployment:

```text
Vercel Project
├── frontend
│   └── React / Vite
│
└── backend
    └── FastAPI
```

Routing is handled by Vercel.

Typical routing:

```text
/health   → backend
/v1/*     → backend
/v2/*     → backend
/*        → frontend
```

Nginx is not required for the Vercel deployment.

---

## Cloud Services

A typical deployment uses:

```text
Vercel
    Frontend
    FastAPI
    Queue
    Blob storage

Neon
    PostgreSQL database

OpenAI
    Image generation
```

This removes the requirement for a permanently running local machine.

---

## Vercel Deployment

After configuring the project and environment variables:

```bash
vercel --prod
```

Database migrations should be applied against the configured database before or as part of the release process.

Example:

```bash
alembic upgrade head
alembic current
```

Verify the deployed API:

```text
/health
```

A healthy deployment returns information similar to:

```json
{
  "status": "ok",
  "queue_provider": "vercel"
}
```

---

## Deploying IG to Vercel from Scratch

The standard IG 2.1 deployment uses:

```text
Vercel
    Frontend
    FastAPI
    Vercel Queue
    Vercel Blob

Neon
    PostgreSQL

OpenAI
    Image generation
```

Redis and RQ are **not required** for the standard Vercel deployment.

### 1. Create the Required Accounts

You will need:

* A GitHub account
* A Vercel account
* An OpenAI API account

A separate Neon account is optional. Neon can be provisioned through the Vercel Marketplace, including when starting without an existing Neon account.

---

### 2. Fork IG on GitHub

Fork:

```text
github.com/ywptr/ig
```

into your own GitHub account or organization.

This allows Vercel to deploy from your own copy of the repository and enables automatic deployments from future Git changes.

---

### 3. Import the Repository into Vercel

From the Vercel dashboard:

```text
Add New
    ↓
Project
    ↓
Import Git Repository
    ↓
Select your IG fork
```

Allow Vercel access to the GitHub repository when prompted.

IG already contains its Vercel project configuration, including frontend/backend routing.

Do not deploy yet if the required services and environment variables have not been configured.

---

### 4. Create a PostgreSQL Database

The recommended database is Neon PostgreSQL.

Neon can be provisioned directly through the Vercel Marketplace and connected to the IG project.

Alternatively, an existing PostgreSQL or compatible database may be used.

IG requires a SQLAlchemy-compatible:

```text
DATABASE_URL
```

Example:

```text
postgresql+psycopg://user:password@host/database?sslmode=require
```

MariaDB/MySQL may also be used with an appropriate SQLAlchemy connection string.

---

### 5. Create a Vercel Blob Store

Create or connect a Vercel Blob store to the project.

The standard IG cloud deployment uses:

```text
ARTIFACT_STORE_PROVIDER=vercel
```

Vercel Blob provides the persistent storage used for generated image artifacts.

Modern Vercel Blob projects may use Vercel OIDC authentication automatically. Existing/token-based configurations may instead expose a Blob access token as an environment variable.

---

### 6. Configure Environment Variables

In:

```text
Vercel
→ Project
→ Settings
→ Environment Variables
```

configure at minimum:

```text
OPENAI_API_KEY=<your-openai-api-key>

DATABASE_URL=<database-connection-string>

JOB_QUEUE_PROVIDER=vercel

ARTIFACT_STORE_PROVIDER=vercel

ALLOW_SELF_REGISTRATION=false

LOG_LEVEL=INFO

IG_TRACE_JOBS=false
```

Any Blob-related credentials required by the connected Vercel Blob configuration should also be present.

Environment-variable changes only affect new deployments, so redeploy after changing them.

Redis configuration is not required when:

```text
JOB_QUEUE_PROVIDER=vercel
```

Therefore these are optional for the standard deployment:

```text
REDIS_URL
RQ worker host
```

---

### 7. Prepare a Local Development Environment

A local development environment is recommended for managing database migrations, performing command-line deployments, testing changes, and troubleshooting the application.

IG's development workflow is primarily Linux-oriented.

Suitable development environments include:

* **Windows Subsystem for Linux (WSL)** — Ubuntu or Debian-based WSL distributions work well on Windows
* **Linux workstation** — for example Debian or Ubuntu
* **Linux virtual machine** — Debian/Ubuntu running under Hyper-V, VMware, VirtualBox, Proxmox, or another hypervisor
* **Bare-metal Linux machine** — a physical Debian/Ubuntu development system
* **Remote Linux development VM/server** — provided it is treated as a development environment and has the required tools installed

A typical development environment might therefore look like:

```text id="x18gxv"
Windows PC
    └── WSL2
        └── Ubuntu
            ├── Git
            ├── Python
            ├── Node.js / npm
            ├── Vercel CLI
            └── IG repository
```

or:

```text id="sg3tgi"
Debian / Ubuntu
    ├── bare metal
    │
    └── or virtual machine

        ├── Git
        ├── Python
        ├── Node.js / npm
        ├── Vercel CLI
        └── IG repository
```

Docker is useful for exercising the legacy/self-hosted architecture, but it is **not required** for the standard IG 2.1 Vercel development and deployment workflow.

At minimum, install:

```text id="019jke"
Git
Python
Node.js / npm
Vercel CLI
```

Clone your fork:

```bash id="qopmlb"
git clone https://github.com/<your-account>/ig.git
cd ig
```

Create and activate a Python virtual environment:

```bash id="g6a3hh"
python -m venv venv
source venv/bin/activate
```

Install the backend dependencies:

```bash id="2mo2zm"
pip install -e .
```

Install the frontend dependencies:

```bash id="ombb0s"
cd frontend
npm install
cd ..
```

Install the Vercel CLI if it is not already available:

```bash id="9es8ps"
npm install -g vercel
```

Authenticate and link the repository to your Vercel project:

```bash id="92qmcb"
vercel login
vercel link
```

This local environment is particularly important for:

```text id="v90jox"
Alembic database migrations
manual Vercel deployments
local development
queue-backend testing
diagnostics and troubleshooting
```

The application itself does not need to remain running on this development machine after it has been deployed to Vercel.

---

### 8. Apply Database Migrations

Before using the application, apply the current Alembic migrations to the configured database.

Ensure that:

```text
DATABASE_URL
```

points to the intended deployment database.

Then run:

```bash
venv/bin/alembic upgrade head
```

Verify the active revision:

```bash
venv/bin/alembic current
```

The database must be migrated before application features that depend on the schema are used.

---

---

### 9. Deploy

From the locally linked repository:

```bash
vercel --prod
```

Vercel will build:

```text
React / Vite frontend
        +
FastAPI backend
```

and apply the routing defined by the project.

Alternatively, deployments may be triggered automatically through the connected Git repository.

A local environment is still useful for:

```text
database migrations
manual production deployments
local development
queue testing
troubleshooting
```

---

### 10. Verify the Deployment

Open:

```text
https://<your-production-domain>/health
```

A healthy standard deployment should return something similar to:

```json
{
  "status": "ok",
  "queue_provider": "vercel"
}
```

Then open the main application in a browser and verify login and image generation.

The expected execution path is:

```text
Browser
   ↓
Vercel frontend
   ↓
Vercel FastAPI
   ↓
Vercel Queue
   ↓
OpenAI
   ↓
Vercel Blob
   ↓
Neon PostgreSQL
```

---

### Optional — Redis/RQ Instead of Vercel Queue

Redis/RQ is an alternative queue backend and is not required for a normal Vercel deployment.

To use it:

```text
JOB_QUEUE_PROVIDER=rq
```

you must additionally provide:

```text
external Redis-compatible service
            +
external long-running RQ worker
```

The Vercel application can remain the producer, but Redis and the worker runtime must be hosted separately.

---

## Configuration

Configuration is environment-driven.

Do not commit `.env`, `.env.local`, provider credentials, database credentials, or API keys to the repository.

The repository includes `.env.example` documenting available settings.

Typical cloud configuration includes:

```text
OPENAI_API_KEY=<secret>

DATABASE_URL=<postgresql-connection-string>

JOB_QUEUE_PROVIDER=vercel

ARTIFACT_STORE_PROVIDER=vercel

BLOB_READ_WRITE_TOKEN=<secret>

ALLOW_SELF_REGISTRATION=false

LOG_LEVEL=INFO
IG_TRACE_JOBS=false
```

For Redis/RQ:

```text
JOB_QUEUE_PROVIDER=rq
REDIS_URL=<redis-connection-string>
```

---

## Environment Precedence

Local development commonly uses:

```text
.env
.env.local
```

The base environment is loaded first:

```text
.env
```

and cloud/local overrides are then loaded from:

```text
.env.local
```

Therefore `.env.local` takes precedence.

---

## Database

The current cloud deployment uses Neon PostgreSQL.

SQLAlchemy provides the application database abstraction and Alembic manages schema migrations.

Database records include entities such as:

```text
users
user_sessions
image_requests
jobs
executions
artifacts
```

Generated image binaries are stored separately from application metadata.

---

## Local Development

### Frontend

Install dependencies:

```bash
cd frontend
npm install
```

Run the frontend:

```bash
npm run dev
```

Build:

```bash
npm run build
```

---

### Full Vercel-Compatible Development

The project can be run locally using:

```bash
vercel dev
```

This more closely matches the deployed Vercel routing model than the original Docker/Nginx setup.

---

### Vercel Queue Development

The repository includes development support for running the Vercel Queue implementation locally.

This allows the same queue abstraction used by the cloud deployment to be exercised during development.

---

### Redis / RQ Development

Redis/RQ remains available as an alternate job execution path.

A worker may be started with:

```bash
rq worker --url "$REDIS_URL" ig
```

A helper script is provided for starting only the RQ worker against external cloud services:

```text
scripts/dev-cloud-redis-rq-worker-only.sh
```

This is useful when testing:

```text
Vercel API
    ↓
External Redis
    ↓
Local RQ worker
```

---

## Development Helper Scripts (for running locally hosted )

The repository includes helper scripts for exercising the supported cloud-oriented queue configurations during local development.

These scripts are **development conveniences only**. They are not required by the production Vercel deployment.

### `scripts/dev-cloud-vercel-queue.sh`

Runs the application locally using the Vercel-oriented development stack.

Typical responsibilities include:

```text id="z8aozg"
Vercel dev
    frontend + FastAPI routing

Local Vercel Queue development server

Local Vercel Queue subscriber / worker
```

This is the preferred local development path when testing the same queue architecture used by the standard IG 2.1 Vercel deployment.

Use this script when:

```text id="26k99x"
JOB_QUEUE_PROVIDER=vercel
```

It allows the Vercel Queue execution path to be tested locally before deployment.

---

### `scripts/dev-cloud-redis.sh`

Runs the application locally while using an external Redis service and a local RQ worker.

Typical execution path:

```text id="5s9uzq"
Browser
   ↓
Local Vercel-compatible application
   ↓
External Redis
   ↓
Local RQ worker
   ↓
OpenAI / Database / Artifact Store
```

Use this script when:

```text id="zwl3e1"
JOB_QUEUE_PROVIDER=rq
```

This is useful for validating the alternate Redis/RQ queue backend without requiring a separately hosted worker environment.

Redis/RQ is optional and is not required for the normal Vercel Queue deployment.

---

### `scripts/dev-cloud-redis-rq-worker-only.sh`

Starts only the RQ worker.

This is useful when the API is already running somewhere else, for example:

```text id="hw66ai"
Vercel FastAPI
      ↓
External Redis
      ↓
Local RQ worker
```

The script does not start the frontend, FastAPI, or Vercel development server.

It exists primarily for testing the boundary between a remotely deployed producer and an externally hosted RQ worker.

---

### Why These Scripts Exist

The helper scripts provide repeatable development environments for both implementations of the IG job queue abstraction:

```text id="mn3b9e"
JobQueue
├── Vercel Queue
└── Redis / RQ
```

They may be used on any compatible development host with the required dependencies and environment variables.

Production deployments should rely on the process management of the hosting platform, rather than these shell scripts.

---

## Legacy Docker Deployment

The original IG implementation was designed around Docker Compose.

That deployment used:

```text
Nginx
FastAPI
MariaDB
Redis
RQ worker
Local artifact storage
```

Typical architecture:

```text
Browser
   │
   ▼
Nginx
   │
   ▼
FastAPI
   │
   ├── MariaDB
   ├── Redis / RQ
   └── /app/output
```

Docker support remains useful for development, testing, and architectural reference, but it is no longer the primary deployment model.

The cloud architecture supersedes the original requirement for an always-running local Docker host.

---

## Legacy Operational Ports

The original lab deployment exposed:

| Port | Purpose |
| --- | --- |
| **8888** | Nginx / web application |
| **8889** | Direct FastAPI backend |
| **8890** | phpMyAdmin |

These ports belong to the original Docker/lab environment and are not part of the Vercel production architecture.

---

## Error Handling

Provider, queue, and execution failures are recorded against persistent jobs and requests where possible.

Failed operations therefore remain visible rather than disappearing as transient browser errors.

Operational tracing can be enabled using:

```text
IG_TRACE_JOBS=true
```

Normal failures are logged regardless of trace configuration.

---

## Design Principle

A central design principle of IG is the separation between **application-specific functionality** and **general control-plane primitives**.

When introducing a new component, we ask:

> Is this infrastructure-specific, or is this a general control-plane primitive?

Examples:

### Application Domain

```text
Image generation
Image prompt
Image provider
Story generation
Future infrastructure actions
```

### Control-Plane Domain

```text
Provider
Model
MediaType
Capability
Workflow
WorkflowStep
Job
Execution
ExecutionTrace
Artifact
Quota
Usage
Policy
Tenant
User
```

This separation allows the control-plane framework to evolve independently from image generation.

IG is therefore both:

```text
an image-generation application
```

and:

```text
a working reference implementation
for reusable AI control-plane primitives
```

---

## V2 — Control Plane Foundation

V2 formalizes reusable control-plane primitives.

Current and planned areas include:

* Authentication
* Multi-user architecture
* Job abstraction
* Execution tracking
* Artifact abstraction
* Pluggable queues
* Pluggable storage
* Multi-provider architecture
* Provider registry
* Model abstraction
* Media-type abstraction
* Capability abstraction
* Workflow model
* Workflow-step model
* Execution tracing
* Quota and usage primitives
* Policy
* Multi-tenancy
* Provider credential management

---

## V3 — Cloud-Ready Implementation

V3 moves IG away from dependence on a local development machine and toward a cloud-hosted deployment model.

A substantial part of this transition is already operational.

Implemented or validated areas include:

* Vercel frontend deployment
* Vercel FastAPI deployment
* Neon PostgreSQL
* Vercel Blob artifact storage
* Vercel Queue
* Redis/RQ queue alternative
* Environment-driven queue selection
* Environment-driven artifact storage selection
* Simple authentication
* Multi-user support
* Configurable self-registration

Remaining V3 areas include:

* Google OIDC as the default authentication method
* Administrative account provisioning
* Improved authorization
* Multi-tenancy
* Tenant-aware configuration
* Production observability
* Cloud execution hardening

For public deployments, self-service registration is disabled by default.

Future tenant configuration may allow individual tenants to choose whether self-registration is permitted.

The effective policy will follow a hierarchy similar to:

```text
Platform policy
    ↓
Tenant policy
    ↓
User action
```

Tenant configuration will never override a platform-level security restriction.

---

## Multi-Tenancy Direction

Multi-tenancy should be introduced early enough that later application layers do not assume a single global organization.

Future tenant-scoped configuration may include:

```text
branding
authentication policy
self-registration
identity providers
provider credentials
usage limits
models
workflows
policies
artifact configuration
```

This will also allow higher-level applications built on IG to customize presentation and behavior according to the domain or tenant from which they are accessed.

---

## V4 — Creative Application Framework

Build higher-level creative applications on top of the control plane.

Planned creative primitives include:

```text
Story
 ├── Canon
 ├── Characters
 │    └── Outfits
 ├── Locations
 ├── Assets
 └── Storyboards
```

The objective is to maintain continuity across generations rather than treating each generation request as an isolated operation.

This architecture is expected to become the foundation for applications such as Sandcastle.

---

## Future — BYO Models

Support multiple forms of Bring Your Own Model:

* External provider APIs
* Tenant-provided API endpoints
* Self-hosted inference endpoints
* Locally hosted models
* Containerized model runtimes
* Tenant-managed inference infrastructure

The control plane should treat these as different execution targets behind common provider and model abstractions.

---

## Future — Billing & Publishing

Billing will be introduced only after the multi-tenant and provider abstractions are sufficiently mature.

The eventual architecture is intended to support tenant-specific commercial rules such as:

* Platform fees
* Model and inference costs
* Usage-based charging
* Tenant-defined user pricing
* Regional billing mechanisms
* Publishing and deployment options

---

## Security

IG is still under active development.

Current security controls include application authentication and the ability to disable public account creation.

Recommended public deployment configuration:

```text
ALLOW_SELF_REGISTRATION=false
```

Future work includes:

* Google OIDC
* Administrative account provisioning
* Tenant-level authentication policy
* Improved authorization
* Provider credential isolation
* Tenant isolation
* Rate limiting
* Auditability
* Policy enforcement

Do not expose credentials through source code, committed environment files, logs, or client-side code.

---

## License / Copyright

Licensed under the **Apache License 2.0**.

Copyright © 2026 Yogi Wiputra

Repository:

`github.com/ywptr/ig`

See `LICENSE` for the complete license text.

---

## User Content

User-provided prompts and generated content remain the property of their respective users, subject to the applicable terms, licenses, and policies of the underlying model/provider.

IG does not claim ownership of user-generated content.

Users are responsible for ensuring that their prompts, inputs, and generated content comply with applicable laws, provider terms, and third-party rights.

---

## Status

**V2 — Cloud-ready control-plane foundation**

IG has moved beyond the original single-machine Docker architecture.

The current implementation has validated:

```text
Vercel
    frontend
    FastAPI
    Queue
    Blob

Neon
    PostgreSQL

OpenAI
    image generation
```

Redis/RQ has also been validated as an alternative queue backend.

The local development machine is no longer required as part of the primary IG runtime.

Development now focuses on strengthening the reusable control-plane architecture, authentication, multi-tenancy, provider abstraction, observability, and higher-level applications built on top of these primitives.