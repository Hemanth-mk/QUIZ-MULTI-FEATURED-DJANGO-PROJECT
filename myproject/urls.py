# myproject/urls.py
from django.contrib import admin
from django.urls import path
from quiz.views import initialize_quiz, quiz_arena_view, evaluate_and_close_quiz
from django.shortcuts import render

# Tiny, quick template router for your name ingestion gate
def entry_portal_view(request):
    # Renders your name ingestion portal layout frame natively
    return render(request, 'quiz1/name.html')

# Quick template router for your locked course video verification gate
def course_gate_view(request):
    # Simulates passing chosen topic details to the media template player
    return render(request, 'quiz1/course_player.html', {'topic_name': 'Technology'})

urlpatterns = [
    path('admin/', admin.site.get_admin_urls() if hasattr(admin.site, 'get_admin_urls') else admin.site.urls),
    
    # 1. The Entrance Ingestion Portal Gate
    path('', entry_portal_view, name='entry_portal'),
    
    # 2. The Unlocked Course Player Progress Gate
    path('course-orientation/', course_gate_view, name='course_orientation'),
    
    # 3. Dynamic Network Initialization Bridge 
    # Receives mode arguments ('major' for 30 online Qs or 'easy_moderate' for 20 Qs)
    path('start-quiz/<str:mode>/', initialize_quiz, name='start_quiz'),
    
    # 4. The Luminous Online Exam Arena Core
    path('arena/', quiz_arena_view, name='quiz_arena'),
    
    # 5. The Grand Cinema Reward Analytics Ledger
    path('results-ledger/', evaluate_and_close_quiz, name='evaluate_and_close_quiz'),
]