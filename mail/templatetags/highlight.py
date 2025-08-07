from django import template
import re
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def highlight(text, word):
    if not word:
        return text
    pattern = re.compile(re.escape(word), re.IGNORECASE)
    highlighted = pattern.sub(lambda match: f'<span class="highlight">{match.group(0)}</span>', text)
    return mark_safe(highlighted)
