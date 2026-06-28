from pydantic import BaseModel, Field


class ReviewModel(BaseModel):
    github_login: str = Field()
    student_name: str = Field()
    lab: str = Field()
    best_score: int = Field(default=0)
    attempts: int = Field(default=0)
    last_pr_link: str | None = Field(default=None)
    last_date: str | None = Field(default=None)

    def to_pd_dict(self) -> dict:
        return {
            "GitHub Login": [self.github_login],
            "Student Name": [self.student_name],
            "Lab": [self.lab],
            "Best Score": [self.best_score],
            "Attempts": [self.attempts],
            "Last PR Link": [self.last_pr_link],
            "Last Date": [self.last_date],
        }
