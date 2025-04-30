# inventory/decorators.py
from django.http import HttpResponseForbidden
from functools import wraps

def grade_required(allowed_grades):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not hasattr(request.user, 'profile') or request.user.profile.grade not in allowed_grades:
                return HttpResponseForbidden("권한이 없습니다.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
