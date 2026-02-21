from django import template
import markdown

register = template.Library()

@register.filter
def render_markdown(text):
    if not text:
        return ""
    return markdown.markdown(
        text,
        extensions=["extra", "nl2br"]
    )
