from github import Github, Auth
from github.Repository import Repository

from configs.github import GitHubConfig


class GithubClient:
    def __init__(self):
        self.__config = GitHubConfig()  # type: ignore
        self.__client = Github(auth=Auth.Token(self.__config.GITHUB_TOKEN))

    def get_repo(self, owner: str, repo_name: str) -> Repository:
        return self.__client.get_repo(f"{owner}/{repo_name}")
