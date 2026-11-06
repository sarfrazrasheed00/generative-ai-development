
import asyncio
import json
import time

import httpx

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError
)


# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_URL = "https://api.github.com"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "Generative-AI-Learning-App"
}


# ==========================================
# 2. PYDANTIC MODELS
# ==========================================

class GitHubUser(BaseModel):

    model_config = ConfigDict(extra="ignore")

    login: str
    name: str | None = None
    followers: int = Field(ge=0)
    public_repos: int = Field(ge=0)


class GitHubRepository(BaseModel):

    model_config = ConfigDict(extra="ignore")

    name: str
    language: str | None = None
    stargazers_count: int = Field(ge=0)


# ==========================================
# 3. ASYNC GITHUB CLIENT
# ==========================================

class AsyncGitHubClient:

    def __init__(self):

        print("\n[DEBUG 1] Client constructor called")

        self.client = httpx.AsyncClient(
            base_url=BASE_URL,
            headers=HEADERS,
            timeout=15.0
        )

        print("[DEBUG 2] Async HTTP client created")


    async def get(
        self,
        endpoint: str,
        params: dict | None = None
    ):

        print(f"\n[DEBUG 3] Starting GET: {endpoint}")

        start = time.perf_counter()

        response = await self.client.get(
            endpoint,
            params=params
        )

        elapsed = time.perf_counter() - start

        print(f"[DEBUG 4] Finished GET: {endpoint}")
        print(f"[DEBUG] HTTP status: {response.status_code}")
        print(f"[DEBUG] Request time: {elapsed:.2f}s")

        response.raise_for_status()

        data = response.json()

        print(f"[DEBUG] Parsed data type: {type(data)}")

        return data


    async def get_user(
        self,
        username: str
    ) -> GitHubUser:

        print("\n[DEBUG 5] Inside get_user()")

        print("[DEBUG] self:", self)
        print("[DEBUG] username:", username)

        data = await self.get(
            f"/users/{username}"
        )

        print("[DEBUG] Returned from self.get()")
        print("[DEBUG] Raw data type:", type(data))

        user = GitHubUser.model_validate(data)

        print("[DEBUG] Validated object:", type(user))
        print("[DEBUG] Login:", user.login)

        return user


    async def get_repositories(
        self,
        username: str
    ) -> list[GitHubRepository]:

        print("\n[DEBUG 6] Inside get_repositories()")

        data = await self.get(
            f"/users/{username}/repos",
            params={
                "sort": "updated",
                "direction": "desc",
                "per_page": 5,
                "type": "owner"
            }
        )

        print("[DEBUG] Raw repositories:", len(data))

        repositories = []

        for repo_data in data:

            repo = GitHubRepository.model_validate(
                repo_data
            )

            print("[DEBUG] Validated repo:", repo.name)

            repositories.append(repo)

        return repositories


    async def close(self):

        print("\n[DEBUG] Closing HTTP client")

        await self.client.aclose()


# ==========================================
# 4. SEQUENTIAL API EXECUTION
# ==========================================

async def fetch_sequential(
    client: AsyncGitHubClient,
    username: str
):

    print("\n========== SEQUENTIAL MODE ==========")

    start = time.perf_counter()

    print("[DEBUG] Fetching user first...")

    user = await client.get_user(username)

    print("[DEBUG] User completed.")
    print("[DEBUG] Now fetching repositories...")

    repositories = await client.get_repositories(
        username
    )

    print("[DEBUG] Repositories completed.")

    elapsed = time.perf_counter() - start

    print(f"\nSequential time: {elapsed:.2f}s")

    return user, repositories, elapsed


# ==========================================
# 5. CONCURRENT API EXECUTION
# ==========================================

async def fetch_concurrent(
    client: AsyncGitHubClient,
    username: str
):

    print("\n========== CONCURRENT MODE ==========")

    start = time.perf_counter()

    print("[DEBUG] Scheduling user task")

    user_task = asyncio.create_task(
        client.get_user(username)
    )

    print("[DEBUG] Scheduling repository task")

    repo_task = asyncio.create_task(
        client.get_repositories(username)
    )

    print("[DEBUG] Both tasks have been scheduled")
    print("[DEBUG] Waiting for both results...")

    user, repositories = await asyncio.gather(
        user_task,
        repo_task
    )

    elapsed = time.perf_counter() - start

    print("[DEBUG] Both tasks completed")
    print(f"Concurrent time: {elapsed:.2f}s")

    return user, repositories, elapsed


# ==========================================
# 6. MAIN APPLICATION
# ==========================================

async def main():

    print("=== ASYNC GITHUB API ANALYZER ===")

    username = input(
        "\nEnter GitHub username: "
    ).strip()

    if not username:
        print("Username cannot be empty.")
        return

    client = AsyncGitHubClient()

    try:

        # Test sequential execution
        seq_user, seq_repos, seq_time = (
            await fetch_sequential(client, username)
        )

        # Test concurrent execution
        con_user, con_repos, con_time = (
            await fetch_concurrent(client, username)
        )

        print("\n========== PERFORMANCE ==========")

        print(f"Sequential: {seq_time:.2f}s")
        print(f"Concurrent: {con_time:.2f}s")

        if con_time > 0:
            print(
                f"Time ratio: {seq_time / con_time:.2f}x"
            )

        # Create report using concurrent result
        report = {
            "username": con_user.login,
            "name": con_user.name,
            "followers": con_user.followers,
            "public_repos": con_user.public_repos,
            "repositories": [
                repo.model_dump()
                for repo in con_repos
            ]
        }

        print("\n========== FINAL REPORT ==========")

        print(json.dumps(report, indent=4))

        with open(
            "async_github_report.json",
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(report, file, indent=4)

        print("\nReport saved successfully.")

    except httpx.HTTPStatusError as error:

        print(
            f"HTTP Error: "
            f"{error.response.status_code}"
        )

    except httpx.RequestError as error:

        print(f"Network Error: {error}")

    except (ValidationError, ValueError) as error:

        print(f"Validation Error: {error}")

    finally:

        await client.close()


# ==========================================
# 7. ENTRY POINT
# ==========================================

if __name__ == "__main__":
    asyncio.run(main())
