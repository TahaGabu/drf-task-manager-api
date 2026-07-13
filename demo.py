"""
End-to-end demo script for the Task Manager API.

Walks through the full auth + CRUD flow against a running server:
  1. Register a new user
  2. Log in to obtain a JWT access/refresh token pair
  3. Call /me/ with the access token
  4. Create a task
  5. List tasks (with filtering)
  6. Retrieve a single task
  7. Update a task (PATCH)
  8. Refresh the access token
  9. Delete the task
  10. Confirm the task is gone

Run this while `python manage.py runserver` is active, and use it as the
script for a Loom/live recording:

    python demo.py

Each step prints the HTTP request, status code, and JSON response so it's
easy to narrate on camera.
"""

import json
import sys
import time
import uuid

import requests

BASE_URL = "http://127.0.0.1:8000/api"


def show(step: str, method: str, url: str, response: requests.Response) -> None:
    print(f"\n{'=' * 70}\nSTEP: {step}\n{method} {url}\nStatus: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except ValueError:
        print(response.text)


def main() -> None:
    session = requests.Session()
    username = f"demo_user_{uuid.uuid4().hex[:8]}"
    password = "DemoPass123!"

    # 1. Register
    url = f"{BASE_URL}/auth/register/"
    r = session.post(
        url,
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": password,
            "password_confirm": password,
        },
    )
    show("Register new user", "POST", url, r)
    r.raise_for_status()

    # 2. Login (obtain JWT pair)
    url = f"{BASE_URL}/auth/token/"
    r = session.post(url, json={"username": username, "password": password})
    show("Login (obtain JWT access/refresh tokens)", "POST", url, r)
    r.raise_for_status()
    tokens = r.json()
    access = tokens["access"]
    refresh = tokens["refresh"]
    auth_header = {"Authorization": f"Bearer {access}"}

    # 3. Who am I
    url = f"{BASE_URL}/auth/me/"
    r = session.get(url, headers=auth_header)
    show("Get current user profile", "GET", url, r)
    r.raise_for_status()

    # 4. Create a task
    url = f"{BASE_URL}/tasks/"
    r = session.post(
        url,
        headers=auth_header,
        json={
            "title": "Record Loom demo",
            "description": "Show off the CRUD API end to end",
            "priority": "high",
            "due_date": "2026-08-01",
        },
    )
    show("Create a task", "POST", url, r)
    r.raise_for_status()
    task_id = r.json()["id"]

    # 5. List tasks (filtered by priority)
    url = f"{BASE_URL}/tasks/?priority=high"
    r = session.get(url, headers=auth_header)
    show("List my tasks (filter: priority=high)", "GET", url, r)
    r.raise_for_status()

    # 6. Retrieve the task
    url = f"{BASE_URL}/tasks/{task_id}/"
    r = session.get(url, headers=auth_header)
    show("Retrieve a single task", "GET", url, r)
    r.raise_for_status()

    # 7. Update the task (PATCH)
    r = session.patch(url, headers=auth_header, json={"completed": True})
    show("Partially update the task (mark completed)", "PATCH", url, r)
    r.raise_for_status()

    # 8. Refresh the access token
    refresh_url = f"{BASE_URL}/auth/token/refresh/"
    r = session.post(refresh_url, json={"refresh": refresh})
    show("Refresh access token", "POST", refresh_url, r)
    r.raise_for_status()

    # 9. Delete the task
    r = session.delete(url, headers=auth_header)
    show("Delete the task", "DELETE", url, r)
    r.raise_for_status()

    # 10. Confirm it's gone
    r = session.get(url, headers=auth_header)
    show("Confirm task is deleted (expect 404)", "GET", url, r)

    print(f"\n{'=' * 70}\nDemo complete! All auth + CRUD steps succeeded.\n{'=' * 70}")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print(
            "Could not connect to the API. Start the server first:\n"
            "  python manage.py runserver",
            file=sys.stderr,
        )
        sys.exit(1)
    except requests.exceptions.HTTPError as exc:
        print(f"\nRequest failed: {exc}", file=sys.stderr)
        sys.exit(1)
