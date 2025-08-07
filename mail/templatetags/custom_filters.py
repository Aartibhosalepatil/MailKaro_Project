from django import template

register = template.Library()

@register.filter(name='add_css')
def add_css(field, css):
    return field.as_widget(attrs={"style": css})

@register.filter(name='add_class') # Useful for adding CSS classes
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})