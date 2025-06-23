from django.template.loader import render_to_string

def render_html(template_name, context):
    return render_to_string(template_name, context)