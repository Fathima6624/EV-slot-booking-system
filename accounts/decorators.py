from django.core.exceptions import PermissionDenied

def operator_only(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied

        # 🔴 THIS is the correct role check for your project
        if request.user.profile.role != "operator":
            raise PermissionDenied

        return view_func(request, *args, **kwargs)
    return wrapper
