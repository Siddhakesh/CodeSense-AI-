import httpx
from typing import Dict, List, Any
from app.models.profile import ProfileAnalysis, RepositorySummary
from app.llm.profile_summary import generate_profile_summary

class GithubClient:
    BASE_URL = "https://api.github.com"

    async def get_profile(self, username: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/users/{username}")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()

    async def get_repos(self, username: str) -> List[Dict[str, Any]]:
        repos = []
        page = 1
        async with httpx.AsyncClient() as client:
            while True:
                # Fetch up to 100 repos per page (max allowed)
                response = await client.get(
                    f"{self.BASE_URL}/users/{username}/repos",
                    params={"per_page": 100, "page": page, "sort": "pushed"}
                )
                response.raise_for_status()
                data = response.json()
                if not data:
                    break
                repos.extend(data)
                page += 1
                # Limit to first 2 pages (200 repos) to avoid rate limits
                if page > 2:
                    break
        return repos

    async def analyze_profile(self, username: str) -> ProfileAnalysis:
        user_data = await self.get_profile(username)
        if not user_data:
            raise ValueError(f"User {username} not found")

        repos_data = await self.get_repos(username)

        # Aggregate languages
        languages = {}
        top_repos_list = []

        for repo in repos_data:
            # Language stats
            lang = repo.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
            
            # Prepare repo summary
            summary = RepositorySummary(
                name=repo["name"],
                description=repo.get("description"),
                language=lang,
                stars=repo["stargazers_count"],
                forks=repo["forks_count"],
                url=repo["html_url"]
            )
            top_repos_list.append(summary)

        # Sort repos by stars
        top_repos_list.sort(key=lambda x: x.stars, reverse=True)
        top_repos_list = top_repos_list[:6] # Top 6

        # Generate Deep Summary
        profile_summary = await generate_profile_summary(
            username=user_data["login"],
            bio=user_data.get("bio", ""),
            repos_count=user_data["public_repos"],
            followers=user_data["followers"],
            languages=languages,
            top_repos=top_repos_list
        )

        return ProfileAnalysis(
            username=user_data["login"],
            name=user_data.get("name"),
            bio=user_data.get("bio"),
            avatar_url=user_data["avatar_url"],
            public_repos=user_data["public_repos"],
            followers=user_data["followers"],
            following=user_data["following"],
            languages=languages,
            top_repos=top_repos_list,
            summary=profile_summary
        )
