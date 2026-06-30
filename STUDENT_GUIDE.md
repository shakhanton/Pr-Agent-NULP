# Student Guide — DevOps Course Lab Submissions

## How it works

Every lab is submitted as a **Pull Request** in your personal GitHub Classroom repository. Once you open a PR, the bot automatically reviews your code, posts a score with feedback, and logs the result.

You have **3 attempts per lab**. Each time you push new commits to your PR branch, the bot re-reviews your work.

---

## Repository structure

Your repository must follow this exact folder structure:

```
├── terraform/
│   ├── main.tf               # Lab 1 — DynamoDB
│   ├── context.tf            # Lab 1 — DynamoDB
│   ├── modules/
│   │   ├── dynamodb/         # Lab 1 — DynamoDB module
│   │   └── lambda/           # Lab 2 — Lambda module
│   ├── api.tf                # Lab 2 — API Gateway
│   ├── apigw.tf              # Lab 2 — API Gateway
│   ├── frontend.tf           # Lab 3 — Frontend hosting
│   ├── s3.tf                 # Lab 3 — S3
│   ├── cloudfront.tf         # Lab 3 — CloudFront
│   ├── alarm.tf              # Lab 4 — CloudWatch alarms
│   ├── notify_slack.tf       # Lab 4 — Notifications
│   └── cloudwatch.tf         # Lab 4 — CloudWatch
└── react-app-frontend/       # Lab 3 — Frontend source code
```

**Do not rename or move files** — the bot detects which lab you are submitting based on file paths.

---

## Submitting a lab

1. **Work on a separate branch** — never commit directly to `main`
   ```bash
   git checkout -b lab-1
   ```

2. **Make your changes** in the correct folder for your lab

3. **Push your branch**
   ```bash
   git add .
   git commit -m "lab-1: implement DynamoDB module"
   git push origin lab-1
   ```

4. **Open a Pull Request** on GitHub — base: `main`, compare: your branch

5. **Wait 1–2 minutes** — the bot will post a review comment on your PR

---

## Example bot comment

```
## Lab 1 Review — Attempt 1/3

**Score: 7/10**

**What works:**
- DynamoDB table is correctly defined with hash key
- PAY_PER_REQUEST billing mode is set

**What needs improvement:**
- Missing get-all-authors Lambda function
- IAM role permissions are too broad

**Hint:**
Look into how to scope IAM policies to specific DynamoDB table ARNs.

---
*2 attempt(s) remaining.*
```

---

## Re-submitting after feedback

You do **not** need to open a new PR. Just push new commits to the same branch — the bot will re-review automatically:

```bash
# fix your code, then:
git add .
git commit -m "lab-1: fix IAM permissions"
git push origin lab-1
```

Each push to an open PR counts as one attempt.

---

## Rules

- **One lab per PR** — do not mix changes from different labs in a single PR
- **Maximum 3 attempts per lab** — after that, the bot will not review further
- **Your GitHub username must be registered** — contact your instructor if you get a "not registered" error
- The bot reviews all files in your PR branch, not just the changed ones

---

## Common errors

| Error | What to do |
|---|---|
| `Your GitHub username is not in the course roster` | Contact your instructor to add your GitHub login |
| `Could not detect which lab this PR belongs to` | Make sure your changes are in the correct folder |
| `This PR contains changes for multiple labs` | Split your changes into separate PRs, one per lab |
| `No attempts remaining` | You have used all 3 attempts — contact your instructor |

---

## Questions?

Contact your instructor or post in the course channel.
