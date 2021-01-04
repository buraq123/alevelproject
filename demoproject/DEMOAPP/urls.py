from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.register, name=""),
    path('graph/', views.graph),
    path('logout/', views.logout),
    path('notification/', views.Notification),
    path('login/', views.mylogin),
    path('invoice/', views.invoiceCreate),
    path('invoicelist/', views.invoiceList),
    path('stocklist/', views.Stocklist),
    path('stockout/', views.Stockout),
    path('stockout2/', views.Stockout2),
    path('products/<productId>', views.productUpdate),
    path('products/', views.productCreate),
    path('productlist/', views.Productlist),
    path('saleinformation/',views.saleinformation)
]
