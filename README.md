# PR Agent для НУЛП — DevOps Course

Автоматична перевірка лабораторних робіт з DevOps курсу НУЛП через GitHub Actions + Google Gemini AI.

## Як це працює

Студент відкриває Pull Request → GitHub Action запускає цей бот → бот аналізує код і залишає коментар з оцінкою та фідбеком.

**Приклад коментаря бота:**
```
## Lab 2 Review — Attempt 2/3

**Score: 7/10**

**What works:**
- API Gateway routes are correctly defined for /courses and /authors
- CORS headers are present on all endpoints

**What needs improvement:**
- Request validation is missing on POST /courses
- Error responses don't follow a consistent format

**Hint:**
Look into AWS API Gateway request validators and how to define models for request body validation.

---
*1 attempt(s) remaining.*
```

---

## Архітектура

```
Student PR
    │
    ▼
GitHub Actions (review.yml in student repo)
    │
    ▼
shakhanton/Pr-Agent-NULP (цей репозиторій)
    ├── Визначає лабу по змінених файлах (LAB_PATH_RULES)
    ├── Читає рубрики з LAB_PROMPTS_JSON.json (студенти не бачать)
    ├── Перевіряє студента в roster (Google Sheets)
    ├── Перевіряє кількість спроб (макс. 3)
    ├── Викликає Google Gemini Flash API
    └── Залишає коментар + зберігає результат у Google Sheets
```

---

## Порівняння з оригінальним підходом (НУВГП)

| | Оригінал (НУВГП) | Цей бот (НУЛП) |
|---|---|---|
| **Репозиторій** | Окремий репо на кожну лабу | Один репо на весь курс |
| **Авторизація GitHub** | GitHub App (APP_ID + PRIVATE_KEY) | `GITHUB_TOKEN` (автоматичний) |
| **LLM** | OpenAI GPT (платно) | Google Gemini Flash (безкоштовно) |
| **Визначення студента** | З назви репозиторію | GitHub логін автора PR |
| **Визначення лаби** | З назви репозиторію | По змінених файлах (LAB_PATH_RULES) |
| **Мішані PR** | Не перевіряється | Бот відмовляє, просить розділити |
| **Шкала оцінок** | 1–5 | 0–10 (4 лаби × 10 = 40 балів) |
| **Кількість спроб** | Необмежено | Максимум 3, журналюється найвища оцінка |
| **Рубрики** | Google Sheets (видно всім) | Google Sheets (приватна таблиця викладача) |
| **Варіанти завдань** | Так | Ні (всі роблять одне завдання) |
| **Google Sheets** | Варіанти + промпти + результати | Тільки roster + результати |
| **Мова фідбеку** | Українська | Англійська |
| **Docker image** | ~1GB (opencv) | ~200MB |

---

## Налаштування для викладача

### 1. Секрети організації GitHub

`Settings → Secrets and variables → Actions` у вашій GitHub організації:

| Секрет | Опис |
|---|---|
| `GEMINI_API_KEY` | Ключ Google Gemini API (безкоштовно на aistudio.google.com) |
| `GOOGLE_CREDENTIALS_CONTENT` | JSON сервісного акаунта Google (для доступу до Sheets) |
| `GOOGLE_SPREADSHEET_URL` | URL Google таблиці з roster та результатами |

### 2. Google Sheets структура

**Лист `roster`** — хто з якого GitHub-акаунта:

| github_username | identifier |
|---|---|
| student-login | Іваненко Іван Іванович |

**Листи результатів** — створюються автоматично при першій перевірці (`lab-1`, `lab-2`, `lab-3`, `lab-4`):

| GitHub Login | Student Name | Lab | Best Score | Attempts | Last PR Link | Last Date |
|---|---|---|---|---|---|---|
| student-login | Іваненко Іван | lab-1 | 8 | 2 | https://... | 2026-03-01 |

### 3. Рубрики оцінювання (Google Sheets — приватна таблиця)

Файл `LAB_PROMPTS_JSON.json` у корені цього репо. Студенти не мають доступу до нього.

```json
{
    "lab-1": [
        "Evaluate DynamoDB module quality...",
        "Score from 0 to 10 using this rubric: 0-3 architecture, 0-3 lambda correctness, ..."
    ]
}
```

Редагуйте через git commit у цьому репозиторії.

### 4. Workflow у репозиторії студентів

Скопіюйте `.github/workflows/TEMPLATE-review.yml` як `.github/workflows/review.yml` у шаблон GitHub Classroom.

Ключові змінні у workflow:

```yaml
LAB_PATH_RULES: >-
  {
    "lab-1": ["terraform/modules/dynamodb/", "terraform/main.tf", "terraform/context.tf"],
    "lab-2": ["terraform/modules/lambda/", "terraform/api.tf", "terraform/apigw.tf"],
    "lab-3": ["terraform/frontend.tf", "terraform/s3.tf", "terraform/cloudfront.tf", "react-app-frontend/"],
    "lab-4": ["terraform/alarm.tf", "terraform/notify_slack.tf", "terraform/cloudwatch.tf"]
  }
MAX_ATTEMPTS: "3"
```

---

## Логіка роботи бота (крок за кроком)

```
1. Студент відкриває PR
2. Бот дивиться які файли змінились
3. Визначає лабу по LAB_PATH_RULES
   ├── Якщо файли з кількох лаб → помилка, просить розділити PR
   └── Якщо файли не підходять жодній лабі → помилка
4. Дістає GitHub логін автора PR
5. Перевіряє чи є студент у roster
   └── Якщо немає → просить звернутись до викладача
6. Перевіряє кількість спроб (з Google Sheets)
   └── Якщо ≥ 3 → повідомляє про вичерпання спроб + найкращий бал
7. Завантажує рубрику з LAB_PROMPTS_JSON.json
8. Зчитує файли студента (тільки з папки поточної лаби)
9. Викликає Gemini Flash з системним промптом:
   "Відповідай англійською. НЕ давай готових рішень."
10. Формує коментар: заголовок + оцінка + фідбек + залишок спроб
11. Зберігає в Google Sheets (оновлює якщо новий бал вищий)
```

---

## Правила оцінювання

- Шкала: **0–10** балів за кожну лабу
- Всього: **4 лаби × 10 = 40 балів** (60 балів — екзамен)
- У журнал іде **найвища** оцінка з усіх спроб
- Максимум **3 спроби** на кожну лабу
- AI-оцінка є попередньою — фінальне рішення на **усному захисті**

---

## Структура коду

```
src/
├── runner.py                    # Головний файл, точка входу
├── configs/
│   ├── github.py                # GITHUB_TOKEN, LAB_PATH_RULES, MAX_ATTEMPTS
│   ├── gemini.py                # GEMINI_API_KEY, GEMINI_MODEL
│   └── google.py                # GOOGLE_CREDENTIALS_CONTENT, SPREADSHEET_URL
├── clients/
│   ├── github.py                # Token-based GitHub API клієнт
│   ├── gemini.py                # Gemini через OpenAI-сумісний endpoint
│   └── google.py                # Google Sheets клієнт
├── models/
│   ├── llm/tools.py             # ReviewCodeTool: score, what_works, what_needs_improvement, hint
│   └── google/entity.py         # ReviewModel: нова схема для Google Sheets
└── services/
    ├── ai/service.py            # Виклик Gemini + системний промпт
    ├── git/service.py           # PR автор, визначення лаби, файли
    ├── google/service.py        # Roster, спроби, збереження результатів
    └── prompt/service.py        # Формування промпту для AI
# Рубрики зберігаються у приватній Google Sheets таблиці викладача (лист "prompts")
```

---

## Smoke test перед семестром

1. Додайте себе в roster з вашим GitHub логіном
2. Відкрийте тестовий PR з файлами тільки Lab 1
3. Перевірте що коментар з'явився і має формат Score/What works/Hint
4. Перевірте що результат записався в Google Sheet `lab-1`
5. Відкрийте ще 2 PR — перевірте лічильник спроб
6. Відкрийте 4-й PR — бот має відмовити з повідомленням про вичерпання спроб
7. Відкрийте PR з файлами і Lab 1 і Lab 2 — бот має попросити розділити
