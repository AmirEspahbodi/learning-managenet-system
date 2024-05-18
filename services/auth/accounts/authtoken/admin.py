from django.contrib import admin

from accounts.authtoken.models import AuthToken, AuthTokenExtra


class TokenInformationInline(admin.TabularInline):
    model = AuthTokenExtra


@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    inlines = [
        TokenInformationInline,
    ]
    list_display = (
        "token_key",
        "user",
        "expiry",
        "last_use",
    )
    ordering = (
        "-expiry",
        "-last_use",
    )
    fields = ()
    raw_id_fields = ("user",)
