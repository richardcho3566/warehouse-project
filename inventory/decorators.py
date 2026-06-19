# inventory/decorators.py
from functools import wraps

from django.http import HttpResponseForbidden

from .utils import get_user_grade


def grade_required(allowed_grades):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user_grade = get_user_grade(request.user)
            if user_grade not in allowed_grades:
                return HttpResponseForbidden("권한이 없습니다.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
