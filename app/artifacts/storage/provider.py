import os
from pathlib import Path

from app.artifacts.storage.local import (
    LocalArtifactStore,
)
from app.artifacts.storage.router import (
    RoutingArtifactStore,
)
from app.artifacts.storage.vercel_blob import (
    VercelBlobArtifactStore,
)


local_store = LocalArtifactStore(
    Path("/app/output")
)

vercel_blob_store = (
    VercelBlobArtifactStore()
)

provider = os.getenv(
    "ARTIFACT_STORE_PROVIDER",
    "local",
)

if provider == "local":
    write_store = local_store

elif provider == "vercel":
    write_store = vercel_blob_store

else:
    raise RuntimeError(
        "Unsupported artifact storage "
        f"provider: {provider}"
    )


artifact_store = RoutingArtifactStore(
    write_store=write_store,
    local_store=local_store,
    vercel_blob_store=vercel_blob_store,
)
