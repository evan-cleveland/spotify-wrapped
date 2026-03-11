from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),  # Use landing_page for the main page
    path('login/', views.spotify_login, name='spotify_login'),  # Redirect to Spotify login
    path('callback/', views.spotify_callback, name='spotify_callback'),  # Callback after Spotify login
    path('loggedIn/', views.loggedIn, name='loggedIn'), #new loggedIN
    path('user_data/', views.user_data, name='user_data'),  # User data page
    path('store_past_data/', views.store_past_data, name='store_past_data'),
    path('saved_wrappeds/', views.saved_wrappeds, name='saved_wrappeds'),
    path('get_ai_response/', views.get_ai_response, name='get_ai_response'),

    path('saved_wrapped/<int:wrapped_id>/', views.view_saved_wrapped, name='view_saved_wrapped'),
    path('delete_all_wrappeds/', views.delete_all_wrappeds, name='delete_all_wrappeds'),
]
