from courses.models import Course, Module
from courses.curator import generate_course_plan
from django.db import transaction


def get_or_create_course(*, user, topic, goal, level="Beginner"):
    """
    GATEKEEPER FUNCTION

    Rule enforced here:
    - A course is generated EXACTLY ONCE per (user, topic)
    - AI is never called again for the same user & topic
    """

    # 1. Always check DB first
    # Normalize topic to prevent duplicates
    normalized_topic = topic.strip().lower()

    existing_course = Course.objects.filter(
        user=user,
        topic=normalized_topic
        ).first()


    if existing_course:
        return existing_course

    # 2. Generate course plan using AI (ONE TIME ONLY)
    course_plan = generate_course_plan(
        topic=topic,
        goal=goal,
        level=level
    )

    if not course_plan:
        raise ValueError("AI failed to generate course plan")

    # 3. Persist atomically (all or nothing)
    with transaction.atomic():
        course = Course.objects.create(
            user=user,
            topic=normalized_topic,
            title=course_plan["course_title"]
            )


        for module_data in course_plan["modules"]:
            Module.objects.create(
                course=course,
                title=module_data["title"],
                order=module_data["order"],
                warmup_text=module_data["content"],
                is_project_based=module_data.get("is_project", False),
                is_unlocked=(module_data['order'] == 1)
            )

    return course
