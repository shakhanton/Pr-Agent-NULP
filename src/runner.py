"""
Main runner — executed by the GitHub Action on every PR event.
"""
import json
from pathlib import Path

from loguru import logger

from configs.github import GitHubConfig
from models.llm.tools import ReviewCodeTool
from services.ai.service import AiRequest
from services.git.service import GitHub
from services.google.service import GoogleSheet
from services.prompt.service import PromptGenerator

RUBRICS_PATH = Path(__file__).parent.parent / "LAB_PROMPTS_JSON.json"


def load_rubric(lab_name: str) -> str:
    try:
        with open(RUBRICS_PATH) as f:
            prompts: dict = json.load(f)
        lab_prompts = prompts.get(lab_name, [])
        return "\n\n".join(lab_prompts)
    except Exception as e:
        logger.error(f"Could not load rubric for {lab_name}: {e}")
        return ""


def run(owner: str, repository: str) -> bool:
    try:
        config = GitHubConfig()  # type: ignore
        git_client = GitHub(owner=owner, repo=repository)

        # Detect which lab this PR belongs to
        lab_name, error = git_client.detect_lab(config.LAB_PATH_RULES)
        if error:
            git_client.comment_pr(f":x: **Lab detection failed**\n\n{error}")
            return False

        logger.info(f"Detected lab: {lab_name}")

        # Identify the student
        pr_author = git_client.get_pr_author()
        google_client = GoogleSheet()

        if pr_author not in google_client.get_all_nicknames():
            logger.error(f"Student {pr_author} not found in roster")
            git_client.comment_pr(
                ":x: **Not registered**\n\n"
                "Your GitHub username is not in the course roster. "
                "Please contact your instructor."
            )
            return False

        student_name = google_client.get_student_name(pr_author)

        # Check attempt limit
        attempts_used = google_client.get_attempts(pr_author, lab_name)
        if attempts_used >= config.MAX_ATTEMPTS:
            best_score = google_client.get_best_score(pr_author, lab_name)
            git_client.comment_pr(
                f":no_entry: **No attempts remaining for {lab_name}**\n\n"
                f"You have used all {config.MAX_ATTEMPTS} attempts. "
                f"Your best score is **{best_score}/10**.\n\n"
                "Contact your instructor if you have questions."
            )
            return False

        attempt_number = attempts_used + 1
        remaining_after = config.MAX_ATTEMPTS - attempt_number

        # Load rubric and files
        rubric = load_rubric(lab_name)
        lab_prefixes = config.LAB_PATH_RULES.get(lab_name, [])
        files = git_client.get_pr_files_content(path_prefixes=lab_prefixes if lab_prefixes else None)
        files.pop("README.md", None)

        # Build prompt and call AI
        prompt_service = PromptGenerator(rubric=rubric, context_prompt=files)
        context = prompt_service.get_prompt()

        ai_client = AiRequest()
        response: ReviewCodeTool = ai_client.send_message(context=context)

        # Build PR comment
        lab_title = lab_name.replace("-", " ").title()
        header = f"## {lab_title} Review — Attempt {attempt_number}/{config.MAX_ATTEMPTS}\n\n"
        if remaining_after > 0:
            footer = f"\n\n---\n*{remaining_after} attempt(s) remaining.*"
        else:
            footer = "\n\n---\n*This was your last attempt. Contact your instructor if you have questions.*"

        git_client.comment_pr(header + response.message + footer)

        # Save result to Google Sheets
        google_client.save_result(
            github_login=pr_author,
            student_name=student_name,
            lab_name=lab_name,
            score=response.score,
            attempt_number=attempt_number,
            pr_link=git_client.get_last_pr_link(),
        )

        return True

    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        return False


if __name__ == "__main__":
    _owner, _repo = GitHubConfig().REPOSITORY.split("/")  # type: ignore
    success = run(owner=_owner, repository=_repo)
    if success:
        logger.info("Process completed successfully.")
    else:
        logger.error("Process failed.")
