# quiz/views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import QuizResult
import requests
import html  # Decodes raw HTML entities sent over the network stream
import random
import time

def initialize_quiz(request, mode="major"):
    """
    Session initializer that pulls live data feeds over the network.
    Requires no local database storage or paid API keys.
    """
    # Grab user name or handle default fallback
    request.session['name'] = request.POST.get('name', request.session.get('name', 'Anonymous Candidate'))
    request.session['quiz_mode'] = mode
    request.session['score'] = 0
    request.session['current_step'] = 1
    request.session['infractions'] = 0
    request.session['start_timestamp'] = time.time()
    
    # 1. Map configurations dynamically based on user mode choices
    if mode == "easy_moderate":
        total_questions = 20
        request.session['max_time_allowed'] = 20 * 60  # 20 Minutes
        api_url = "https://opentdb.com/api.php?amount=20&type=multiple&difficulty=easy"
    else:
        total_questions = 30
        request.session['max_time_allowed'] = 30 * 60  # 30 Minutes
        # Pulls across mixed premium categories globally
        api_url = "https://opentdb.com/api.php?amount=30&type=multiple"

    try:
        # 2. Live HTTP GET Network Request to Online Base
        response = requests.get(api_url, timeout=5)
        data = response.json()
        
        if data.get('response_code') == 0:
            network_questions = []
            for idx, item in enumerate(data['results']):
                # Clean up dirty strings and symbols coming from the internet
                raw_q = html.unescape(item['question'])
                correct_ans = html.unescape(item['correct_answer'])
                incorrect_answers = [html.unescape(ans) for ans in item['incorrect_answers']]
                
                # Natively shuffle choices so the correct answer isn't always in the same slot
                all_choices = incorrect_answers + [correct_ans]
                random.shuffle(all_choices)
                
                # Structure the live packet into a clean data dictionary
                network_questions.append({
                    'id': idx + 1,
                    'category': item['category'],
                    'difficulty': item['difficulty'],
                    'question_text': raw_q,
                    'choices': all_choices,
                    'correct_answer': correct_ans
                })
            
            # Save the entire live question bank directly inside the secure session cache
            request.session['online_quiz_pool'] = network_questions
            request.session['total_questions'] = len(network_questions)
            return redirect('quiz_arena')
        else:
            return render(request, 'quiz1/error.html', {'msg': 'API stream traffic limit hit. Please reload.'})
            
    except Exception as network_err:
        return render(request, 'quiz1/error.html', {'msg': f'Connection dropped: {str(network_err)}'})


def quiz_arena_view(request):
    """
    Core Execution Arena.
    Tracks active countdowns and evaluates answers against the cached network pool.
    """
    if 'online_quiz_pool' not in request.session:
        return redirect('entry_portal')

    # Native Time Expiry Safety Checker
    elapsed_time = time.time() - request.session['start_timestamp']
    if elapsed_time > request.session['max_time_allowed']:
        return redirect('evaluate_and_close_quiz')

    current_step = request.session.get('current_step', 1)
    quiz_pool = request.session.get('online_quiz_pool', [])
    total_qs = request.session.get('total_questions', 30)
    
    # Extract the current active question frame from session memory
    active_question = quiz_pool[current_step - 1]

    if request.method == 'POST':
        user_answer = request.POST.get('answer_choice')
        if user_answer == active_question['correct_answer']:
            request.session['score'] = request.session.get('score', 0) + 1
        
        # Track anti-cheat tab switches passed from client forms
        request.session['infractions'] += int(request.POST.get('infractions_delta', 0))

        if current_step < total_qs:
            request.session['current_step'] = current_step + 1
            return redirect('quiz_arena')
        else:
            return redirect('evaluate_and_close_quiz')

    seconds_remaining = int(request.session['max_time_allowed'] - elapsed_time)
    
    return render(request, 'quiz1/arena.html', {
        'question': active_question,
        'current_step': current_step,
        'total_questions': total_qs,
        'seconds_remaining': seconds_remaining,
        'category': active_question['category'],
        'difficulty': active_question['difficulty'],
        'name': request.session.get('name', 'Candidate')
    })


def evaluate_and_close_quiz(request):
    """
    The Grand Reward Compute Engine.
    Maps precision percentages to custom enterprise certificates and diamond price actions.
    """
    score = request.session.get('score', 0)
    total_qs = request.session.get('total_questions', 30)
    percentage = (score / total_qs) * 100 if total_qs > 0 else 0
    duration = round(time.time() - request.session.get('start_timestamp', time.time()), 1)
    
    tier = "Fail"
    prize_action = "None"
    certificate_unlocked = False

    if percentage >= 50 and percentage < 65:
        tier = "Pass Banner"
    elif percentage >= 65 and percentage < 75:
        tier = "Bronze Medal"
    elif percentage >= 75 and percentage < 85:
        tier = "Silver Medal"
    elif percentage >= 85 and percentage < 95:
        tier = "Gold Medal"
    elif percentage >= 95 and percentage < 100:
        tier = "Diamond Badge"
        certificate_unlocked = True
    elif percentage == 100:
        tier = "Absolute Mastery: Diamond Crown"
        prize_action = "BIG_BAZAAR_MEGA_DASHBOARD_EXPLOSION"
        certificate_unlocked = True

    # Safely write metrics into your database model structure
    try:
        QuizResult.objects.create(
            name=request.session.get('name', 'Candidate'),
            quiz_mode=request.session.get('quiz_mode', 'Major'),
            score=score,
            total_questions=total_qs,
            time_taken_seconds=duration,
            achievement_tier=tier,
            anti_cheat_infractions=request.session.get('infractions', 0)
        )
    except Exception:
        # Safeguard if you haven't run your migrations yet
        pass

    response = render(request, 'quiz1/grand_ledger.html', {
        'name': request.session.get('name', 'Candidate'),
        'score': score,
        'total_questions': total_qs,
        'percentage': round(percentage, 1),
        'duration': duration,
        'tier': tier,
        'prize_action': prize_action,
        'certificate_unlocked': certificate_unlocked,
        'infractions': request.session.get('infractions', 0)
    })

    # Clear out transactional session tokens smoothly
    request.session.pop('online_quiz_pool', None)
    request.session.pop('total_questions', None)
    request.session.pop('current_step', None)
    request.session.pop('score', None)
    request.session.pop('infractions', None)
    request.session.pop('start_timestamp', None)
    return response