# models.py
from django.db import models

class QuestionBank(models.Model):
    """
    Central repository for multi-domain dynamic quiz queries.
    Supports native categorizations and structural difficulty scaling tiers.
    """
    CATEGORY_CHOICES = [
        ('GK', 'General Knowledge'),
        ('SCIENCE', 'Science'),
        ('SOCIAL_SCIENCE', 'Social Science'),
        ('MATH', 'Mathematics'),
        ('CS', 'Computer Science'),
        ('TECHNOLOGY', 'Technology'),
        ('MOVIES', 'Movies'),
        ('SPORTS', 'Sports'),
    ]
    DIFFICULTY_CHOICES = [
        ('EASY', 'Easy'),
        ('MODERATE', 'Moderate'),
        ('HARD', 'Hard'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    question_text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])

    def __str__(self):
        return f"[{self.category} - {self.difficulty}] {self.question_text[:50]}"


class QuizResult(models.Model):
    """
    Advanced Gamified Telemetry Ledger.
    Logs multi-tier medal metadata, certificate tracking, and anti-cheat parameters.
    """
    name = models.CharField(max_length=100)
    quiz_mode = models.CharField(max_length=50, default="Standard Adaptive")
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=30)
    time_taken_seconds = models.FloatField(default=0.0)
    achievement_tier = models.CharField(max_length=50, default="Fail")
    anti_cheat_infractions = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - Tier: {self.achievement_tier} ({self.score}/{self.total_questions})"