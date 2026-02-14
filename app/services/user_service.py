"""
User Authentication - User Service

Handles user CRUD operations with JSON file persistence.
Thread-safe with atomic writes for crash safety.
"""

import json
import logging
import os
import secrets
import tempfile
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.api.errors import EmailConflictError
from app.models.user import User, UserStatus

logger = logging.getLogger("app.services.user_service")


class UserService:
    """Manages user accounts with JSON file persistence."""

    def __init__(self, data_file: str = "data/users.json") -> None:
        self._data_file = Path(data_file)
        self._lock = threading.Lock()
        self._users: dict[str, dict] = {}
        self._api_key_index: dict[str, str] = {}  # api_key -> user_id
        self._email_index: dict[str, str] = {}  # email -> user_id
        self._load()

    def _load(self) -> None:
        """Load users from JSON file. On error, start with empty store."""
        if not self._data_file.exists():
            logger.info("User data file not found at %s, starting empty", self._data_file)
            return
        try:
            raw = self._data_file.read_text(encoding="utf-8")
            data = json.loads(raw)
            self._users = data.get("users", {})
            self._rebuild_indexes()
            logger.info("Loaded %d users from %s", len(self._users), self._data_file)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to load user data from %s: %s. Starting empty.", self._data_file, exc)
            self._users = {}
            self._api_key_index = {}
            self._email_index = {}

    def _rebuild_indexes(self) -> None:
        """Rebuild lookup indexes from user data."""
        self._api_key_index = {}
        self._email_index = {}
        for user_id, user_data in self._users.items():
            api_key = user_data.get("api_key")
            email = user_data.get("email")
            if api_key:
                self._api_key_index[api_key] = user_id
            if email:
                self._email_index[email] = user_id

    def _save(self) -> None:
        """Persist users to JSON file using atomic write (temp + rename)."""
        self._data_file.parent.mkdir(parents=True, exist_ok=True)
        data = {"users": self._users}
        dir_path = str(self._data_file.parent)
        try:
            fd, tmp_path = tempfile.mkstemp(dir=dir_path, suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
            os.replace(tmp_path, str(self._data_file))
        except OSError as exc:
            logger.error("Failed to save user data: %s", exc)
            # Clean up temp file if rename failed
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    def create_user(self, name: str, email: str) -> User:
        """Register a new user. Returns User with api_key."""
        email = email.strip().lower()
        with self._lock:
            if email in self._email_index:
                raise EmailConflictError(email)

            user_id = str(uuid.uuid4())
            api_key = secrets.token_hex(16)
            now = datetime.now(timezone.utc)

            user_data = {
                "id": user_id,
                "name": name.strip(),
                "email": email,
                "api_key": api_key,
                "status": UserStatus.ACTIVE.value,
                "created_at": now.isoformat(),
                "last_active_at": now.isoformat(),
                "request_count": 0,
            }

            self._users[user_id] = user_data
            self._api_key_index[api_key] = user_id
            self._email_index[email] = user_id
            self._save()

            logger.info("User registered: id=%s email=%s", user_id, email)
            return User(**user_data)

    def get_user_by_api_key(self, api_key: str) -> User | None:
        """Look up a user by their API key. Returns None if not found."""
        with self._lock:
            user_id = self._api_key_index.get(api_key)
            if user_id is None:
                return None
            user_data = self._users.get(user_id)
            if user_data is None:
                return None
            return User(**user_data)

    def get_user_by_id(self, user_id: str) -> User | None:
        """Look up a user by their ID. Returns None if not found."""
        with self._lock:
            user_data = self._users.get(user_id)
            if user_data is None:
                return None
            return User(**user_data)

    def list_users(self) -> list[User]:
        """Return all registered users."""
        with self._lock:
            return [User(**data) for data in self._users.values()]

    def update_last_active(self, user_id: str) -> None:
        """Update the last_active_at timestamp for a user."""
        with self._lock:
            if user_id in self._users:
                self._users[user_id]["last_active_at"] = datetime.now(timezone.utc).isoformat()
                # Don't persist on every request for performance — persist periodically or on shutdown
                # For MVP simplicity, we persist here
                self._save()

    def increment_request_count(self, user_id: str) -> None:
        """Increment the lifetime request count for a user."""
        with self._lock:
            if user_id in self._users:
                self._users[user_id]["request_count"] = self._users[user_id].get("request_count", 0) + 1
                self._save()

    def disable_user(self, user_id: str) -> User | None:
        """Disable a user account. Returns updated User or None if not found."""
        with self._lock:
            if user_id not in self._users:
                return None
            self._users[user_id]["status"] = UserStatus.DISABLED.value
            self._save()
            logger.info("User disabled: id=%s", user_id)
            return User(**self._users[user_id])

    def enable_user(self, user_id: str) -> User | None:
        """Re-enable a user account. Returns updated User or None if not found."""
        with self._lock:
            if user_id not in self._users:
                return None
            self._users[user_id]["status"] = UserStatus.ACTIVE.value
            self._save()
            logger.info("User enabled: id=%s", user_id)
            return User(**self._users[user_id])

    def regenerate_api_key(self, user_id: str) -> str | None:
        """Generate a new API key for a user. Returns new key or None if user not found."""
        with self._lock:
            if user_id not in self._users:
                return None
            old_key = self._users[user_id]["api_key"]
            new_key = secrets.token_hex(16)

            # Update indexes
            del self._api_key_index[old_key]
            self._api_key_index[new_key] = user_id

            self._users[user_id]["api_key"] = new_key
            self._save()
            logger.info("API key regenerated: user_id=%s", user_id)
            return new_key
