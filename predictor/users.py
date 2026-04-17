from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


def create_user(username: str, email: str, password: str):
    """Create a new user. Returns (user, None) or (None, error_message)."""
    username = username.strip()
    email = email.strip()

    if not username or not password:
        return None, "Username and password are required."

    if User.objects.filter(username=username).exists():
        return None, "A user with that username already exists."

    try:
        user = User.objects.create_user(username=username, email=email, password=password)
        user.full_clean()
        user.save()
        return user, None
    except ValidationError as e:
        return None, "; ".join([str(v) for v in e.messages])
    except Exception as e:
        return None, str(e)


def authenticate_user(request, username: str, password: str):
    """Authenticate and log in user. Returns (user, None) or (None, error_message)."""
    username = username.strip()

    if not username or not password:
        return None, "Please enter both username and password."

    user = authenticate(request, username=username, password=password)
    if user is None:
        return None, "Invalid username/password combination."

    login(request, user)
    return user, None


def logout_user(request):
    """Log out the current user."""
    logout(request)
