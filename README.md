# AI-Powered Adaptive Learning Platform

A Django-based adaptive learning platform that generates personalized courses with AI, tracks learner progress, and adapts module progression based on performance.

## What This Project Does

- Authenticates users (register, login with email, logout).
- Generates one AI course per `(user, topic)` through a gatekeeper workflow.
- Builds module-wise learning paths with warm-up lessons and assessments.
- Supports two assessment modes:
  - MCQ quizzes
  - Project/code submission with AI grading
- Applies adaptive progression:
  - `< 60%`: fail and retry
  - `60-74%`: soft pass + micro-lesson reinforcement
  - `>= 75%`: strong pass and continue
- Tracks streak and module/course progress on a dashboard.
- Stores sensitive sentiment text using encrypted model fields.

## Tech Stack

- Python
- Django
- SQLite (default local DB)
- Gemini API (`google-generativeai`)
- Tavily API (`tavily-python`)
- Markdown rendering (`Markdown` + `codehilite`)
- Field-level encryption (`django-encrypted-model-fields`)

## Project Structure

```text
ai_learning_platform/
  settings.py
  urls.py
courses/
  curator.py
  models.py
  services/course_generator.py
  views.py
  templates/courses/
guardian/
  models.py
users/
  forms.py
  models.py
  views.py
manage.py
requirements.txt
```

## Prerequisites

- Python 3.12+ (recommended for current Django version in this project)
- `pip`
- Internet access for AI calls (Gemini + Tavily)

## Installation

1. Clone the repository.
2. Create and activate a virtual environment.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

3. Install dependencies.

```powershell
pip install -r requirements.txt
```

4. Configure environment variables in `.env` (project root).

5. Run migrations and start server.

```powershell
python manage.py migrate
python manage.py runserver
```

6. Open: `http://127.0.0.1:8000/`

## Environment Variables

Create `.env` in the project root with:

```env
SECRET_KEY=your_django_secret
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key

FERNET_KEY=your_fernet_key
```

Notes:
- `FERNET_KEY` is required by `FIELD_ENCRYPTION_KEY` in `settings.py`.
- Keep all secrets private and out of version control.

## URL Map

- `/` -> redirects to dashboard
- `/users/register/` -> registration
- `/users/login/` -> login (email-based)
- `/users/logout/` -> logout
- `/courses/create/` -> create a new AI course
- `/courses/dashboard/` -> learner dashboard
- `/courses/<course_id>/` -> course detail
- `/courses/<course_id>/module/<module_id>/quiz/` -> quiz/project assessment
- `/admin/` -> Django admin

## Adaptive Learning Workflow

1. User submits topic + goal.
2. `courses.services.course_generator.get_or_create_course()`:
   - Normalizes topic
   - Returns existing course if already generated
   - Calls AI only once per `(user, topic)`
3. Modules are created and ordered.
4. Learner attempts module quiz/project.
5. Grading logic in `courses.views.handle_grading()`:
   - Fail (`<60`): retry required
   - Soft pass (`60-74`): next module unlocked + micro-lesson attached
   - Pass (`>=75`): next module unlocked
6. Dashboard computes:
   - completed modules
   - per-course progress %
   - streak by day

## Development Commands

```powershell
# Run development server
python manage.py runserver

# Make migrations after model changes
python manage.py makemigrations
python manage.py migrate

# Run tests
python manage.py test
```

## Data Model (High Level)

- `Course`: owner user, topic, generated title, creation time
- `Module`: ordered unit, warm-up content, unlock/completion flags, optional remedial text
- `Question`: MCQ options and answer for quiz-based modules
- `QuizAttempt`: stores user score and attempt count per module
- `StudentProfile`: learner goal/background metadata
- `FocusSession`: attention tracking record
- `SentimentLog`: encrypted learner text + response strategy

## Security Notes

- Never commit real API keys or encryption keys.
- Rotate keys immediately if exposed.
- Set `DEBUG=False` and configure `ALLOWED_HOSTS` in production.
- Use a production-grade DB and server stack before deployment.

## Troubleshooting

- Missing encryption key:
  - Symptom: warning about `FIELD_ENCRYPTION_KEY` in startup logs
  - Fix: set `FERNET_KEY` in `.env`
- AI generation fails:
  - Check `GEMINI_API_KEY` and internet connectivity
- Search/resource curation issues:
  - Check `TAVILY_API_KEY`
- Login fails:
  - This project authenticates via email lookup + username auth internally; ensure email exists for the user.

## License

Add your preferred license (MIT/Apache-2.0/etc.) in a `LICENSE` file.
