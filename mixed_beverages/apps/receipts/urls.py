from django.conf.urls import url
from django.views.generic import TemplateView


app_name = "receipts"
urlpatterns = [
    url(r"^$", TemplateView.as_view(template_name="home.html"), name="home"),
    url(r"^about/$", TemplateView.as_view(template_name="about.html"), name="about"),
]
