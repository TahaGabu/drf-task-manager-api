from django.urls import path
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import MeView, RegisterView

TokenObtainPairView = extend_schema_view(
    post=extend_schema(
        tags=["Auth"],
        summary="Obtain JWT token pair (login)",
        description="Exchange a username/password for an access + refresh JWT token pair.",
    )
)(TokenObtainPairView)

TokenRefreshView = extend_schema_view(
    post=extend_schema(
        tags=["Auth"],
        summary="Refresh access token",
        description="Exchange a valid refresh token for a new access token.",
    )
)(TokenRefreshView)

TokenVerifyView = extend_schema_view(
    post=extend_schema(
        tags=["Auth"],
        summary="Verify a token",
        description="Checks whether a given access/refresh token is still valid.",
    )
)(TokenVerifyView)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("token/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    path("me/", MeView.as_view(), name="auth-me"),
]
