from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Course, Module, Question
from courses.services.course_generator import get_or_create_course
from .curator import generate_quiz_questions, grade_code_submission, generate_micro_lesson
from courses.models import QuizAttempt, Course
from django.utils.timezone import now
from datetime import timedelta
from django.urls import reverse
import markdown

# ==========================
# 1. COURSE CREATION
# ==========================
# courses/views.py
@login_required
def create_course_view(request):
    """
    This view ONLY handles user input and delegates
    course creation to the gatekeeper.

    AI generation is NOT allowed here.
    """

    if request.method == "POST":
        # 1. Capture user input
        topic = request.POST.get('topic')
        goal = request.POST.get('goal')
        level = request.POST.get('level', 'Beginner')
        duration = request.POST.get('duration')  # optional, not enforced yet

        # Basic validation
        if not topic or not goal:
            return render(request, 'create_course.html', {
                "error": "Topic and goal are required."
            })

        # 2. GATEKEEPER CALL (single source of truth)
        try:
            course = get_or_create_course(
                user=request.user,
                topic=topic,
                goal=goal,
                level=level
            )
        except Exception as e:
            return render(request, 'create_course.html', {
                "error": f"Course generation failed: {str(e)}"
            })

        # 3. Redirect to dashboard (NO AI logic here)
        return redirect(reverse('dashboard'))


    # GET request → show form
    return render(request, 'courses/create_course.html')

# ==========================
# 2. DASHBOARD
# ==========================
@login_required
def dashboard_view(request):
    courses = Course.objects.filter(user=request.user)

    # 🔴 If no course exists → force course creation
    if not courses.exists():
        return redirect('create_course')

    dashboard_courses = []
    total_completed_modules = 0

    for course in courses:
        modules = Module.objects.filter(course=course)

        completed_modules = QuizAttempt.objects.filter(
            user=request.user,
            module__course=course,
            score__gte=60  # passed
        ).values('module').distinct().count()

        total_modules = modules.count()

        progress = int((completed_modules / total_modules) * 100) if total_modules else 0

        total_completed_modules += completed_modules

        dashboard_courses.append({
            "course": course,
            "progress": progress,
            "completed_modules": completed_modules,
            "total_modules": total_modules,
        })

    print("USER:", request.user.id)
    print("COURSES:", Course.objects.filter(user=request.user))


    # 🔥 STREAK LOGIC (REAL)
    today = now().date()

    streak = 0
    day_cursor = today

    while QuizAttempt.objects.filter(
        user=request.user,
        created_at__date=day_cursor,
        score__gte=60
    ).exists():
        streak += 1
        day_cursor -= timedelta(days=1)

    return render(request, "courses/dashboard.html", {
    "dashboard_courses": dashboard_courses,
    "courses": courses, 
    "completed_modules": total_completed_modules,
    "streak": streak,
    })



# ==========================
# 3. COURSE DETAIL 
# ==========================
@login_required
def course_detail_view(request, course_id, module_id=None):
    course = get_object_or_404(Course, id=course_id, user=request.user)

    modules = Module.objects.filter(course=course).order_by("order")

    # If no module unlocked → unlock first
    if modules.exists() and not modules.filter(is_unlocked=True).exists():
        first_module = modules.first()
        first_module.is_unlocked = True
        first_module.save()

    completed_ids = list(
        QuizAttempt.objects.filter(
            user=request.user,
            module__course=course,
            score__gte=60
        ).values_list("module_id", flat=True).distinct()
    )

    unlocked_modules = list(modules.filter(is_unlocked=True).values_list("id", flat=True))
    first_module = modules.first()
    if first_module and first_module.id not in unlocked_modules:
        unlocked_modules.append(first_module.id)

    requested_module_id = module_id or request.GET.get("module")
    selected_module = None
    if requested_module_id:
        selected_module = get_object_or_404(Module, id=requested_module_id, course=course)

    if selected_module and selected_module.id not in unlocked_modules:
        return redirect(f"/courses/{course.id}/")
    if not selected_module:
        selected_module = modules.filter(id__in=unlocked_modules).first()

    total_modules = modules.count()
    completed_modules = len(completed_ids)
    progress = int((completed_modules / total_modules) * 100) if total_modules else 0
    next_module = None
    next_module_unlocked = False
    if selected_module:
        next_module = modules.filter(order__gt=selected_module.order).order_by("order").first()
        next_module_unlocked = bool(next_module and next_module.id in unlocked_modules)

    # Convert Markdown to HTML safely
    formatted_content = ""
    if selected_module and selected_module.warmup_text:
        formatted_content = markdown.markdown(
            selected_module.warmup_text,
            extensions=["fenced_code", "codehilite"]
        )


    context = {
        "course": course,
        "modules": modules,
        "selected_module": selected_module,
        "current_module": selected_module,
        "formatted_content": formatted_content,
        "unlocked_modules": unlocked_modules,
        "completed_ids": completed_ids,
        "next_module": next_module,
        "next_module_unlocked": next_module_unlocked,
        "progress": progress,
    }

    return render(request, "courses/course_detail.html", context)


# ==========================
# 5. MODULE QUIZ
# ==========================
@login_required
def take_quiz_view(request, course_id, module_id):
    module = get_object_or_404(Module, id=module_id, course_id=course_id)

    # Prevent retake if already passed
    already_passed = QuizAttempt.objects.filter(
        user=request.user,
        module=module,
        score__gte=60
    ).exists()

    if already_passed:
        return redirect(f"/courses/{course_id}/?module={module.id}")
    
    # === PATH A: PROJECT SUBMISSION (If module is project-based) ===
    if module.is_project_based:
        if request.method == "POST":
            user_code = request.POST.get('user_code')
            # 1. Ask AI to grade the code
            result = grade_code_submission(module.title, user_code)
            score = result.get('score', 0)
            return handle_grading(request, module, score, feedback=result.get('feedback'))
        
        return render(request, 'courses/project_submit.html', {'module': module})

    # === PATH B: QUIZ SUBMISSION (Standard) ===
    # 1. Generate Questions if missing
    if not module.question_set.exists():
        q_data = generate_quiz_questions(module.title, module.warmup_text)
        for q in q_data:
            Question.objects.create(
                module=module, 
                question_text=q['question'], 
                option_a=q['a'], 
                option_b=q['b'], 
                option_c=q['c'], 
                correct_option=q['answer'])

    questions = module.question_set.all()

    if request.method == "POST":
        score_count = 0
        total = questions.count()

        for q in questions:
            user_answer = request.POST.get(f"question_{q.id}", "").strip().upper()
            correct_answer = q.correct_option.strip().upper()

            if user_answer == correct_answer:
                score_count += 1

        
        final_score = (score_count / total) * 100 if total > 0 else 0
        return handle_grading(request, module, final_score)

    return render(request, 'courses/quiz.html', 
                  {'module': module, 
                   'questions': questions})


# === SHARED GRADING LOGIC (The 3-Tier System) ===
def handle_grading(request, module, score, feedback=""):

    # Determine attempt number    
    previous_attempts = QuizAttempt.objects.filter(
        user=request.user,
        module=module
    ).count()

    QuizAttempt.objects.create(
        user=request.user,
        module=module,
        score=score,
        attempt_number=previous_attempts + 1
    )

    
    # TIER 1: FAIL (< 60%)
    if score < 60:
        return render(request, 'courses/quiz_result.html', {
            'passed': False, 'score': int(score), 'module': module, 'feedback': feedback
        })
    
    # Mark current as complete
    # NOTE: Module completion is tracked via QuizAttempt for per-user accuracy
    

    
    # If this module had a micro-lesson earlier → mark it consumed
    if module.remedial_text:
        module.remedial_consumed = True
        module.save()
    
    # Find next module
    next_module = Module.objects.filter(
                                        course=module.course,
                                        order__gt=module.order
                                    ).order_by("order").first()

    if next_module:
        next_module.is_unlocked = True

        # Soft pass: unlock next module but attach reinforcement micro-lesson.
        if 60 <= score < 75:
            remedial = generate_micro_lesson(module.title, "key concepts")
            next_module.remedial_text = f"Review from last module: {remedial}"

        next_module.save()

    return render(request, 'courses/quiz_result.html', {
        'passed': True,
        'soft_pass': 60 <= score < 75,
        'score': int(score),
        'module': module,
        'feedback': feedback,
        'next_module': next_module,
    })


