from typing import Iterator
from urllib.parse import urlparse

from app.artifacts.storage.base import (
    ArtifactStore,
)


class RoutingArtifactStore:

    def __init__(
        self,
        *,
        write_store: ArtifactStore,
        local_store: ArtifactStore,
        vercel_blob_store: ArtifactStore,
    ):
        self.write_store = write_store
        self.local_store = local_store
        self.vercel_blob_store = (
            vercel_blob_store
        )

    def put_bytes(
        self,
        *,
        filename: str,
        data: bytes,
    ) -> str:
        return self.write_store.put_bytes(
            filename=filename,
            data=data,
        )

    def exists(
        self,
        storage_uri: str,
    ) -> bool:
        store = self._store_for_uri(
            storage_uri
        )

        return store.exists(
            storage_uri
        )

    def iter_bytes(
        self,
        storage_uri: str,
        *,
        chunk_size: int = 64 * 1024,
    ) -> Iterator[bytes]:
        store = self._store_for_uri(
            storage_uri
        )

        return store.iter_bytes(
            storage_uri,
            chunk_size=chunk_size,
        )

    def _store_for_uri(
        self,
        storage_uri: str,
    ) -> ArtifactStore:
        scheme = urlparse(
            storage_uri
        ).scheme

        if scheme == "file":
            return self.local_store

        if scheme == "vercel-blob":
            return self.vercel_blob_store

        raise ValueError(
            "Unsupported artifact "
            f"storage URI: {storage_uri}"
        )