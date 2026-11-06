
import json
import requests

from collections import Counter
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError
)


BASE_URL = "https://api.github.com"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "Generative-AI-Learning-App"
}


def debug(title, value):
    print(f"\n--- {title} ---")
    print(value)
    print("Python type:", type(value))


# ====================================
# 1. PYDANTIC MODELS
# ====================================

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


# ====================================
# 2. GITHUB API CLIENT
# ====================================

class GitHubClient:

    def __init__(self):

        print("\n[1] GitHubClient constructor called")

        print("self is:", self)
        print("self type:", type(self))

        self.session = requests.Session()

        self.session.headers.update(HEADERS)

        print("Session created successfully")


    def get(
        self,
        endpoint: str,
        params: dict | None = None
    ):

        print("\n[2] Inside GitHubClient.get()")

        print("self:", self)
        print("endpoint:", endpoint)
        print("params:", params)

        url = f"{BASE_URL}{endpoint}"

        print("Final URL:", url)

        response = self.session.get(
            url,
            params=params,
            timeout=15
        )

        print("HTTP Status:", response.status_code)

        response.raise_for_status()

        print("Response object type:", type(response))

        # Raw JSON response as text
        print("\nRaw response text (first 300 chars):")
        print(response.text[:300])

        # Convert JSON response to Python data
        data = response.json()

        print("\nAfter response.json():")
        print("Data type:", type(data))

        if isinstance(data, dict):
            print("Dictionary keys:", list(data.keys())[:10])

        elif isinstance(data, list):
            print("Total items:", len(data))

        return data


    def get_user(self, username: str) -> GitHubUser:

        print("\n[3] Inside get_user()")

        print("self:", self)
        print("username:", username)

        data = self.get(f"/users/{username}")

        debug(
            "Data received from self.get()",
            type(data)
        )

        print("Login from dictionary:", data["login"])

        user = GitHubUser.model_validate(data)

        print("\nAfter Pydantic validation:")
        print("Object:", user)
        print("Object type:", type(user))
        print("Login using attribute:", user.login)

        return user


    def get_repositories(
        self,
        username: str
    ) -> list[GitHubRepository]:

        print("\n[4] Inside get_repositories()")

        data = self.get(
            f"/users/{username}/repos",
            params={
                "sort": "updated",
                "direction": "desc",
                "per_page": 5,
                "type": "owner"
            }
        )

        print("\nRepositories raw data type:", type(data))
        print("Number of repositories:", len(data))

        validated_repos = []

        for index, repo in enumerate(data, start=1):

            print(f"\nProcessing repository {index}")

            print("Raw repo type:", type(repo))
            print("Repository name:", repo["name"])

            validated = GitHubRepository.model_validate(repo)

            print("Validated type:", type(validated))
            print("Validated name:", validated.name)

            validated_repos.append(validated)

        return validated_repos


    def close(self):

        print("\nClosing GitHub API session...")
        self.session.close()


# ====================================
# 3. GITHUB ANALYZER
# ====================================

class GitHubAnalyzer:

    def __init__(
        self,
        user: GitHubUser,
        repositories: list[GitHubRepository]
    ):

        print("\n[5] GitHubAnalyzer constructor called")

        self.user = user
        self.repositories = repositories

        print("User object type:", type(self.user))
        print("Username:", self.user.login)
        print("Repositories count:", len(self.repositories))


    def get_languages(self) -> dict:

        print("\n[6] Inside get_languages()")

        languages = []

        for repo in self.repositories:

            print(
                f"Repository: {repo.name}, "
                f"Language: {repo.language}"
            )

            if repo.language is not None:
                languages.append(repo.language)

        print("Languages list:", languages)

        language_counts = dict(Counter(languages))

        print("Language counts:", language_counts)

        return language_counts


    def generate_report(self) -> dict:

        print("\n[7] Inside generate_report()")

        report = {
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

        print("Report Python type:", type(report))
        print("Report keys:", list(report.keys()))

        return report


# ====================================
# 4. MAIN APPLICATION
# ====================================

def main():

    print("=== LESSON 05 DEBUG MODE ===")

    username = input(
        "\nEnter GitHub username: "
    ).strip()

    if not username:
        print("Username cannot be empty.")
        return

    client = GitHubClient()

    try:

        print("\nCalling client.get_user()")

        user = client.get_user(username)

        print("\nReturned user:", user)
        print("Returned user type:", type(user))

        print("\nCalling client.get_repositories()")

        repositories = client.get_repositories(username)

        print("Returned repositories type:", type(repositories))

        analyzer = GitHubAnalyzer(
            user,
            repositories
        )

        report = analyzer.generate_report()

        print("\n[8] Final report generated")

        json_output = json.dumps(
            report,
            indent=4,
            ensure_ascii=False
        )

        print("\nFinal JSON Output:")
        print(json_output)

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

        print("\nReport saved successfully!")

    except requests.exceptions.RequestException as error:
        print("API Error:", error)

    except (ValidationError, ValueError) as error:
        print("Validation Error:", error)

    finally:
        client.close()


if __name__ == "__main__":
    main()
