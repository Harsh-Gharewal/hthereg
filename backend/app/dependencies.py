"""FastAPI dependency injection providers."""

from backend.app.services.data_store import DataStore, data_store


def get_data_store() -> DataStore:
    """Return the global DataStore singleton instance."""
    return data_store
