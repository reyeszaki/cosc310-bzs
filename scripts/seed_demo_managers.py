import sys
from pathlib import Path

# Allow running directly via: python scripts/seed_demo_managers.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.main import app
from app.repository.users_repo import UserRepository

DEMO_MANAGERS = [
    {
        "name": "Demo",
        "last_name": "Admin",
        "email": "admin@example.ca",
        "password": "secret123",
        "role": "admin",
    },
    {
        "name": "Demo",
        "last_name": "Owner",
        "email": "owner@example.ca",
        "password": "secret123",
        "role": "owner",
    },
]


def main() -> None:
    repo = UserRepository()
    with TestClient(app) as client:
        for account in DEMO_MANAGERS:
            existing = repo.get_by_email(account["email"])
            if existing is None:
                payload = {k: v for k, v in account.items() if k != "role"}
                response = client.post("/users", json=payload)
                if response.status_code != 201:
                    raise RuntimeError(
                        f"Failed to create {account['email']}: "
                        f"{response.status_code} {response.text}"
                    )
                user_id = response.json()["id"]
                status = "created"
            else:
                user_id = existing["id"]
                status = "updated"

            repo.update(user_id, {"role": account["role"], "is_active": True})
            print(
                f"{status.capitalize()} {account['role']} account "
                f"(ID: {user_id}): {account['email']} / {account['password']}"
            )


if __name__ == "__main__":
    main()