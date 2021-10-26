from django.urls import path
from . import views

app_name = 'tweet'

urlpatterns = [
    #path('', views.index, name='index'),
    path('', views.sentiment_result, name='sentiment_result'),
    path('sentiment_result/', views.sentiment_result, name='sentiment_result'),
    path('input_portfolio/', views.input_portfolio, name='input_portfolio'),   
    path('result_portfolio/', views.result_portfolio, name='result_portfolio'),    
]
