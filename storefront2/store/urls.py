from django.urls import path
from rest_framework import routers, urlpatterns, viewsets

from django.conf.urls import include
from . import views
from rest_framework.routers import SimpleRouter, DefaultRouter
from rest_framework_nested import routers

router = DefaultRouter()
router.register('products', views.ProductViewSet,basename='products')
router.register('collections', views.CollectionViewSet)
router.register('carts', views.CartViewSet)
router.register('customers', views.CustomerViewSet )
router.register('orders', views.OrderViewSet, basename='orders')

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews',views.ReviewViewSet, basename='product-reviews')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = router.urls + products_router.urls + carts_router.urls
# URLConf
#urlpatterns = [
#    path('products/', views.ProductList.as_view()),
#    path('products/<int:pk>/', views.ProductDetail.as_view()),
#    path('collection/', views.CollectionList.as_view()),
#    path('collection/<int:pk>/', views.CollectionDetail.as_view()),
#]
