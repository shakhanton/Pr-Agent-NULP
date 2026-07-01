import os
from typing import Dict, Optional

from loguru import logger

from clients.github import GithubClient


class GitHub:
    def __init__(
            self,
            owner: Optional[str] = None,
            repo: Optional[str] = None
    ):
        self.github_client = GithubClient()
        self.__owner = owner
        self.__repo = repo
        self.repository = self.github_client.get_repo(owner, repo)
        self.last_pr_number = self._get_last_pr_number()

    def _get_last_pr_number(self) -> int:
        env_pr = os.environ.get("PR_NUMBER", "").strip()
        if env_pr.isdigit():
            pr_number = int(env_pr)
            logger.info(f"PR number from env: {pr_number}")
            return pr_number
        pr_number = self.repository.get_pulls(sort="created", direction="desc")
        logger.info(f"Last PR number: {pr_number[0].number}")
        return pr_number[0].number

    def get_pr_author(self) -> str:
        pr = self.repository.get_pull(self.last_pr_number)
        author = pr.user.login
        logger.info(f"PR author: {author}")
        return author

    def get_changed_file_paths(self) -> list[str]:
        pr = self.repository.get_pull(self.last_pr_number)
        paths = [f.filename for f in pr.get_files()]
        logger.info(f"Changed files: {paths}")
        return paths

    def detect_lab(self, lab_path_rules: dict) -> tuple[Optional[str], Optional[str]]:
        """Returns (lab_name, error_message). One of them is always None."""
        if not lab_path_rules:
            return None, "LAB_PATH_RULES is not configured. Contact your instructor."

        changed_paths = self.get_changed_file_paths()
        matched_labs: set[str] = set()

        for path in changed_paths:
            for lab, prefixes in lab_path_rules.items():
                for prefix in prefixes:
                    if path.startswith(prefix):
                        matched_labs.add(lab)
                        break

        if len(matched_labs) == 0:
            return None, (
                "Could not detect which lab this PR belongs to. "
                "Make sure your changes are in the correct directory according to the lab path rules."
            )

        if len(matched_labs) > 1:
            labs_str = ", ".join(sorted(matched_labs))
            return None, (
                f"This PR contains changes for multiple labs ({labs_str}). "
                "Please split your changes into separate PRs, one per lab."
            )

        return matched_labs.pop(), None

    def get_pr_files_content(self, path_prefixes: Optional[list[str]] = None) -> Dict[str, str]:
        def get_files_recursively(path: str, ref: str) -> Dict[str, str]:
            files = self.repository.get_contents(path, ref=ref)
            context = dict()
            encodings = ['utf-8', 'latin-1', 'cp1252']
            for file in files:
                if file.type == "dir":
                    context.update(get_files_recursively(file.path, ref))
                else:
                    for encoding in encodings:
                        try:
                            content = file.decoded_content.decode(encoding)
                            context[file.path] = content
                            break
                        except UnicodeDecodeError:
                            continue
            return context

        last_pr = self.repository.get_pull(self.last_pr_number)
        all_files = get_files_recursively("", last_pr.head.ref)

        if path_prefixes:
            return {
                k: v for k, v in all_files.items()
                if any(k.startswith(p) for p in path_prefixes)
            }
        return all_files

    def comment_pr(self, comment: str, pull_number: Optional[int] = None) -> None:
        if not pull_number:
            pull_number = self.last_pr_number
        pr = self.repository.get_pull(pull_number)
        pr.create_issue_comment(comment)
        logger.info(f"Comment left on PR #{pull_number}")

    def get_last_pr_number(self) -> int:
        return self.last_pr_number

    def get_last_pr_link(self) -> str:
        return f"https://github.com/{self.__owner}/{self.__repo}/pull/{self.last_pr_number}"
