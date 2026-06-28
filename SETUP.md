# Покрокова інструкція запуску бота

---

## Крок 1 — Gemini API Key (5 хв)

1. Відкрий [aistudio.google.com](https://aistudio.google.com) з університетської пошти
2. Натисни **Get API key → Create API key**
3. Збережи ключ — він виглядає як `AIzaSy...`

---

## Крок 2 — Google Sheets (15 хв)

Створи нову Google таблицю або використай існуючу.

### Лист `roster`

Додай дві колонки:

| `github_username` | `identifier` |
|---|---|
| твій-github-логін | Твоє ПІБ (для smoke test) |
| student-login | Іваненко Іван Іванович |

### Лист `prompts`

Додай дві колонки:

| `lab_name` | `Prompt` |
|---|---|
| `lab-1` | Evaluate DynamoDB module quality, remote-state readiness, and correctness of get-all-authors/get-courses/save-course lambdas.;;Score from 0 to 10 for Lab 1 only using this rubric: 0-3 architecture and IaC quality, 0-3 lambda correctness, 0-2 IAM least privilege, 0-2 evidence/tests/docs. |
| `lab-2` | Evaluate API Gateway + full CRUD implementation for courses and authors, request validation, and CORS correctness.;;Score from 0 to 10 for Lab 2 only using this rubric: 0-4 endpoint completeness, 0-3 integration/CORS correctness, 0-2 validation/error handling, 0-1 tests evidence. |
| `lab-3` | Evaluate frontend hosting pipeline on S3 + CloudFront, correct origin/access config, and environment API URL wiring.;;Score from 0 to 10 for Lab 3 only using this rubric: 0-4 end-to-end deployment, 0-3 Terraform design, 0-2 security/access setup, 0-1 evidence/report. |
| `lab-4` | Evaluate CloudWatch metrics and alarms, billing alarm, SNS notifications (email mandatory; slack optional), and demonstrable alert triggering.;;Score from 0 to 10 for Lab 4 only using this rubric: 0-4 alarm correctness+trigger proof, 0-3 notification pipeline, 0-2 runbook/operations, 0-1 cost monitoring completeness. |

> `;;` — роздільник між кількома промптами в одній клітинці. Бот об'єднає їх перед відправкою в AI.

Листи `lab-1`, `lab-2`, `lab-3`, `lab-4` з результатами бот створить сам при першій перевірці.

---

## Крок 3 — Google Service Account (10 хв)

Потрібен для того, щоб бот міг читати і писати в твою таблицю.

1. Відкрий [console.cloud.google.com](https://console.cloud.google.com)
2. Створи проект або обери існуючий
3. **APIs & Services → Enable APIs** → знайди і увімкни **Google Sheets API**
4. **APIs & Services → Credentials → Create Credentials → Service Account**
5. Назви акаунт (наприклад `pr-agent-bot`) → натисни **Done**
6. Клікни на щойно створений service account → вкладка **Keys → Add Key → Create new key → JSON**
7. Завантажиться файл — відкрий його і скопіюй **весь вміст** (це і є значення для секрету `GOOGLE_CREDENTIALS_CONTENT`)
8. У тому ж JSON файлі знайди поле `"client_email"` — скопіюй адресу (виглядає як `pr-agent-bot@project-id.iam.gserviceaccount.com`)
9. Відкрий свою Google таблицю → **Share** → встав цей email → встанови права **Editor** → **Send**

---

## Крок 4 — Секрети GitHub Organization (5 хв)

Відкрий:
```
github.com/organizations/<назва-організації>/settings/secrets/actions
```

Натисни **New organization secret** і додай три секрети:

| Назва секрету | Звідки брати |
|---|---|
| `GEMINI_API_KEY` | Ключ з Кроку 1 (`AIzaSy...`) |
| `GOOGLE_CREDENTIALS_CONTENT` | Весь JSON файл з Кроку 3 |
| `GOOGLE_SPREADSHEET_URL` | URL твоєї Google таблиці з браузера |

> Секрети на рівні організації автоматично доступні у всіх репозиторіях студентів.

---

## Крок 5 — Шаблон GitHub Classroom (10 хв)

У шаблонному репозиторії завдання:

1. Створи папку `.github/workflows/`
2. Створи файл `.github/workflows/review.yml` з таким вмістом:

```yaml
name: PR Agent for NULP

on:
  pull_request:
    types: [opened, edited, synchronize, reopened]

jobs:
  pr_agent_job:
    runs-on: ubuntu-latest
    name: Run PR Agent on every pull request
    steps:
      - name: pr-agent-nulp
        uses: shakhanton/Pr-Agent-NULP@main
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GIT_REPOSITORY: ${{ github.repository }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          GOOGLE_CREDENTIALS_CONTENT: ${{ secrets.GOOGLE_CREDENTIALS_CONTENT }}
          GOOGLE_SPREADSHEET_URL: ${{ secrets.GOOGLE_SPREADSHEET_URL }}
          LAB_PATH_RULES: >-
            {
              "lab-1": ["terraform/modules/dynamodb/", "terraform/main.tf", "terraform/context.tf"],
              "lab-2": ["terraform/modules/lambda/", "terraform/api.tf", "terraform/apigw.tf"],
              "lab-3": ["terraform/frontend.tf", "terraform/s3.tf", "terraform/cloudfront.tf", "react-app-frontend/"],
              "lab-4": ["terraform/alarm.tf", "terraform/notify_slack.tf", "terraform/cloudwatch.tf"]
            }
          MAX_ATTEMPTS: "3"
```

> Якщо структура папок у твоєму проекті інша — відредагуй `LAB_PATH_RULES`.

---

## Крок 6 — Smoke test (10 хв)

1. Прийми GitHub Classroom завдання своїм тестовим акаунтом — отримаєш особистий репозиторій
2. Переконайся що твій тестовий логін є в листі `roster`
3. Зроби будь-яку зміну у файлі з папки що відповідає Lab 1 (наприклад `terraform/main.tf`)
4. Відкрий Pull Request
5. Зачекай 1–2 хвилини
6. Перевір що бот залишив коментар у форматі:

```
## Lab 1 Review — Attempt 1/3

**Score: X/10**

**What works:**
...

**What needs improvement:**
...

**Hint:**
...

---
*2 attempt(s) remaining.*
```

7. Перевір що у Google Sheets з'явився лист `lab-1` з рядком результату

**Якщо щось пішло не так** — відкрий вкладку **Actions** у репозиторії → клікни на запуск → подивись логи.

---

## Чеклист перед семестром

- [ ] Gemini API key отримано і додано в секрети
- [ ] Google Sheets створено з листами `roster` і `prompts`
- [ ] Рубрики для всіх 4 лаб заповнені у листі `prompts`
- [ ] Service account має права Editor на таблицю
- [ ] Три секрети додано в GitHub Organization
- [ ] `review.yml` є в шаблонному репозиторії Classroom
- [ ] Smoke test пройшов — коментар з'явився, результат записався в Sheets
- [ ] Всі студенти додані в `roster` до початку семестру

---

## Troubleshooting

**Бот не коментує PR**
→ Перевір вкладку Actions у репозиторії студента. Найчастіша причина — відсутній секрет.

**`Student not found in roster`**
→ GitHub логін студента у листі `roster` написаний неправильно. Логін чутливий до регістру.

**`No rubric found for lab-X`**
→ У листі `prompts` відсутній рядок з `lab_name = lab-X`, або назва колонки написана неправильно.

**`Could not detect which lab`**
→ Студент змінив файли що не входять у жоден `LAB_PATH_RULES` префікс. Перевір структуру папок.

**`This PR contains changes for multiple labs`**
→ Студент правильно отримав помилку — він має розділити зміни на окремі PR.

**Помилка `GOOGLE_CREDENTIALS_CONTENT`**
→ JSON скопійовано некоректно. Спробуй через `cat credentials.json` і скопіюй вивід цілком.
