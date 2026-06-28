import gspread
import pandas as pd
from loguru import logger

from clients.google import GoogleSheetsClient

ROSTER_SHEET = "roster"
RESULTS_COLUMNS = ["GitHub Login", "Student Name", "Lab", "Best Score", "Attempts", "Last PR Link", "Last Date"]


class GoogleSheet:
    def __init__(self):
        self.__client = GoogleSheetsClient()

    def get_all_nicknames(self) -> list[str]:
        try:
            data = self.__client.get_sheet_data(ROSTER_SHEET)
            return data["github_username"].dropna().tolist()
        except Exception as e:
            logger.error(f"Error getting nicknames: {e}")
            return []

    def get_student_name(self, github_login: str) -> str:
        try:
            data = self.__client.get_sheet_data(ROSTER_SHEET)
            row = data.loc[data["github_username"] == github_login]
            if row.empty:
                return github_login
            return str(row["identifier"].values[0]).strip()
        except Exception as e:
            logger.error(f"Error getting student name: {e}")
            return github_login

    def get_attempts(self, github_login: str, lab_name: str) -> int:
        try:
            data = self.__client.get_sheet_data(lab_name)
            if data.empty or "GitHub Login" not in data.columns:
                return 0
            row = data.loc[data["GitHub Login"] == github_login]
            if row.empty:
                return 0
            val = row["Attempts"].values[0]
            return int(val) if val else 0
        except Exception as e:
            logger.error(f"Error getting attempts: {e}")
            return 0

    def get_best_score(self, github_login: str, lab_name: str) -> int:
        try:
            data = self.__client.get_sheet_data(lab_name)
            if data.empty or "GitHub Login" not in data.columns:
                return 0
            row = data.loc[data["GitHub Login"] == github_login]
            if row.empty:
                return 0
            val = row["Best Score"].values[0]
            return int(val) if val else 0
        except Exception as e:
            logger.error(f"Error getting best score: {e}")
            return 0

    def save_result(
            self,
            github_login: str,
            student_name: str,
            lab_name: str,
            score: int,
            attempt_number: int,
            pr_link: str,
    ) -> bool:
        try:
            try:
                sheet = self.__client.spreadsheet.worksheet(lab_name)
                data = pd.DataFrame(sheet.get_all_records())
            except gspread.exceptions.WorksheetNotFound:
                sheet = self.__client.spreadsheet.add_worksheet(
                    title=lab_name, rows=200, cols=len(RESULTS_COLUMNS)
                )
                data = pd.DataFrame(columns=RESULTS_COLUMNS)

            date = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

            if not data.empty and "GitHub Login" in data.columns:
                idx_list = data.index[data["GitHub Login"] == github_login].tolist()
            else:
                idx_list = []

            if idx_list:
                idx = idx_list[0]
                current_best = data.at[idx, "Best Score"]
                data.at[idx, "Best Score"] = max(int(current_best) if current_best else 0, score)
                data.at[idx, "Attempts"] = attempt_number
                data.at[idx, "Last PR Link"] = pr_link
                data.at[idx, "Last Date"] = date
            else:
                new_row = pd.DataFrame([{
                    "GitHub Login": github_login,
                    "Student Name": student_name,
                    "Lab": lab_name,
                    "Best Score": score,
                    "Attempts": attempt_number,
                    "Last PR Link": pr_link,
                    "Last Date": date,
                }])
                data = pd.concat([data, new_row], ignore_index=True)

            self.__client.write_dataframe_to_sheet(lab_name, data)
            logger.info(f"Saved result for {github_login} on {lab_name}: score={score}, attempt={attempt_number}")
            return True

        except Exception as e:
            logger.error(f"Error saving result: {e}")
            return False
