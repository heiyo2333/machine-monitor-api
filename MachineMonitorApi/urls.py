"""MachineMonitorApi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url

from django.contrib.auth.models import User
from rest_framework import routers, permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.documentation import include_docs_urls

from Equipment_Status.views import EquipmentStatusViewSet
from Method_Config.views import MethodConfigViewSet
from System_Config.views import SystemConfigViewSet

from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
    openapi.Info(
        title="精密数控机床预测性维护系统",  # 必传
        default_version="v1",  # 必传
        description="API接口文档",
        terms_of_service="西南交通大学",
        contact=openapi.Contact(email="2431461804@qq.com"),
        license=openapi.License(name="BSD LICENSE")
    ),
    public=True,
    permission_classes=(permissions.AllowAny,)  # 权限类
)

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'config', SystemConfigViewSet, basename='system-configuration-query')  # 系统配置
router.register(r'Method_config', MethodConfigViewSet, basename='method_config')  # 监测信号展示
router.register(r'Equipment_Status', EquipmentStatusViewSet, basename='equipment_status')  # 设备运行状态


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'api/', include(router.urls)),
    url(r"^docs/", include_docs_urls(title="My API title")),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),

    # path('upload/', Adaptive_Learning.views.upload_file),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
