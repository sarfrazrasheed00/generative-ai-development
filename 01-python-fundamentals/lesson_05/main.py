
import json
import requests

from collections import Counter
from pydantic import BaseModel, ConfigDict, Field, ValidationError


# ---------------------------------------
# 1. API Configuration
# ---------------------------------------

BASE_URL = "https://api.github.com"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "Generative-AI-Learning-App"
}


# ---------------------------------------
# 2. Pydantic Data Models
# ---------------------------------------

class GitHubUser(BaseModel):
    model_config = ConfigDict(extra="ignore")

    login: str
    name: str | None = None
    bio: str | None = None
    public_repos: int = Field(ge=0)
    followers: int = Field(ge=0)
    html_url: str


class GitHubRepository(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    description: str | None = None
    language: str | None = None
    stargazers_count: int = Field(ge=0)
    html_url: str


# ---------------------------------------
# 3. API Client
# ---------------------------------------

class GitHubClient:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def get(self, endpoint: str, params: dict | None = None):

        url = f"{BASE_URL}{endpoint}"

        response = self.session.get(
            url,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        return response.json()

    def get_user(self, username: str) -> GitHubUser:

        data = self.get(f"/users/{username}")

        return GitHubUser.model_validate(data)

    def get_repositories(
        self,
        username: str
    ) -> list[GitHubRepository]:

        data = self.get(
            f"/users/{username}/repos",
            params={
                "sort": "updated",
                "direction": "desc",
                "per_page": 5,
                "type": "owner"
            }
        )

        return [
            GitHubRepository.model_validate(repo)
            for repo in data
        ]

    def close(self):
        self.session.close()


# ---------------------------------------
# 4. Profile Analyzer
# ---------------------------------------

class GitHubAnalyzer:

    def __init__(
        self,
        user: GitHubUser,
        repositories: list[GitHubRepository]
    ):
        self.user = user
        self.repositories = repositories

    def get_languages(self) -> dict:

        languages = [
            repo.language
            for repo in self.repositories
            if repo.language is not None
        ]

        return dict(Counter(languages))

    def generate_report(self) -> dict:

        return {
            "username": self.user.login,
            "full_name": self.user.name,
            "bio": self.user.bio,
            "profile_url": self.user.html_url,
            "public_repositories": self.user.public_repos,
            "followers": self.user.followers,
            "analyzed_repositories": len(self.repositories),
            "languages": self.get_languages(),
            "repositories": [
                repo.model_dump()
                for repo in self.repositories
            ]
        }


# ---------------------------------------
# 5. Main Application
# ---------------------------------------

def main():

    print("\n=== GITHUB PROFILE ANALYZER ===")

    username = input(
        "\nEnter GitHub username: "
    ).strip()

    if not username:
        print("Username cannot be empty.")
        return

    client = GitHubClient()

    try:

        print("\nFetching GitHub data...")

        user = client.get_user(username)

        repositories = client.get_repositories(username)

        analyzer = GitHubAnalyzer(
            user,
            repositories
        )

        report = analyzer.generate_report()

        print("\n=== ANALYSIS REPORT ===")

        print(
            json.dumps(
                report,
                indent=4,
                ensure_ascii=False
            )
        )

        # Save report to JSON file
        with open(
            "github_report.json",
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False
            )

        print("\nReport saved to github_report.json")

    except requests.exceptions.HTTPError as error:

        status = error.response.status_code

        if status == 404:
            print("GitHub user not found.")
        elif status == 403:
            print("Access denied or API rate limit reached.")
        else:
            print(f"HTTP error: {status}")

    except requests.exceptions.RequestException as error:

        print(f"Network/API error: {error}")

    except (ValidationError, ValueError) as error:

        print(f"Invalid API data: {error}")

    finally:

        client.close()


if __name__ == "__main__":
    main()
