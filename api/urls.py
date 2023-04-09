from django.urls import path, include
from api.views import CheckConnection

urlpatterns = [
    path('is_up/', CheckConnection.as_view()),
    path('accounts/', include('accounts.api.urls'))
]
