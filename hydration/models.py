from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date

class UserProfile(models.Model):
    ACTIVITY_CHOICES = [
        (1.2, 'Sedentary'),
        (1.375, 'Light exercise'),
        (1.55, 'Moderate exercise'),
        (1.725, 'Heavy exercise'),
        (1.9, 'Very heavy exercise'),
    ]
    
    WEATHER_CHOICES = [
        ('hot', 'Hot'),
        ('mild', 'Mild'),
        ('cold', 'Cold'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    weight = models.FloatField(help_text="Weight in kg")
    activity_level = models.FloatField(choices=ACTIVITY_CHOICES, default=1.2)
    age = models.IntegerField()
    weather_condition = models.CharField(max_length=10, choices=WEATHER_CHOICES, default='mild')
    custom_daily_goal = models.FloatField(null=True, blank=True, help_text="Custom daily water goal in ml")
    glass_volume = models.IntegerField(default=250, help_text="Default glass volume in ml")
    is_public_profile = models.BooleanField(default=True, help_text="Show profile in public leaderboards")
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def calculate_daily_goal(self):
        """Calculate recommended daily water intake"""
        if self.custom_daily_goal:
            return self.custom_daily_goal
        
        # Basic formula: weight * 35ml with adjustments
        base_amount = self.weight * 35
        
        # Adjust for activity level
        if self.activity_level > 1.5:
            base_amount *= 1.2
        elif self.activity_level > 1.3:
            base_amount *= 1.1
        
        # Adjust for weather
        if self.weather_condition == 'hot':
            base_amount *= 1.2
        elif self.weather_condition == 'cold':
            base_amount *= 0.9
        
        # Adjust for age
        if self.age > 65:
            base_amount *= 1.1
        elif self.age < 18:
            base_amount *= 0.8
        
        return round(base_amount)

class WaterLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField(help_text="Amount in ml")
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.amount}ml at {self.timestamp}"

class DailySummary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    total_consumed = models.IntegerField(default=0, help_text="Total consumed in ml")
    goal_amount = models.IntegerField(default=0, help_text="Goal amount for this day in ml")
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date} ({self.total_consumed}ml/{self.goal_amount}ml)"
    
    @property
    def progress_percentage(self):
        if self.goal_amount > 0:
            return min(100, round((self.total_consumed / self.goal_amount) * 100))
        return 0
    
    @property
    def is_goal_reached(self):
        return self.total_consumed >= self.goal_amount

class Challenge(models.Model):
    CHALLENGE_TYPES = [
        ('daily', 'Daily Challenge'),
        ('weekly', 'Weekly Challenge'),
        ('custom', 'Custom Challenge'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    challenge_type = models.CharField(max_length=10, choices=CHALLENGE_TYPES, default='daily')
    start_date = models.DateField()
    end_date = models.DateField()
    goal_per_day = models.IntegerField(help_text="Daily water goal in ml for this challenge")
    is_public = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"
    
    @property
    def is_active(self):
        today = date.today()
        return self.start_date <= today <= self.end_date
    
    @property
    def is_upcoming(self):
        return self.start_date > date.today()
    
    @property
    def is_finished(self):
        return self.end_date < date.today()
    
    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days + 1
    
    @property
    def participant_count(self):
        return self.challengeparticipant_set.count()

class ChallengeParticipant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    total_days_completed = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    best_streak = models.IntegerField(default=0)
    total_water_logged = models.IntegerField(default=0)
    last_completion_date = models.DateField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'challenge']
        ordering = ['-total_days_completed', '-total_water_logged', '-best_streak']
    
    def __str__(self):
        return f"{self.user.username} in {self.challenge.name}"
    
    def update_progress(self, water_amount, log_date):
        """Update participant's progress when they log water"""
        # Add to total water logged
        self.total_water_logged += water_amount
        
        # Check if they met the daily goal
        daily_total = WaterLog.objects.filter(
            user=self.user,
            timestamp__date=log_date
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        if daily_total >= self.challenge.goal_per_day:
            # They completed today's goal
            if not self.last_completion_date or self.last_completion_date < log_date:
                self.total_days_completed += 1
                
                # Update streak
                yesterday = log_date - timezone.timedelta(days=1)
                if self.last_completion_date == yesterday:
                    self.current_streak += 1
                else:
                    self.current_streak = 1
                
                # Update best streak
                if self.current_streak > self.best_streak:
                    self.best_streak = self.current_streak
                
                self.last_completion_date = log_date
        
        self.save()
    
    @property
    def completion_percentage(self):
        if self.challenge.duration_days > 0:
            return min(100, round((self.total_days_completed / self.challenge.duration_days) * 100))
        return 0
    
    @property
    def rank(self):
        """Get participant's rank in the challenge"""
        participants = ChallengeParticipant.objects.filter(
            challenge=self.challenge,
            user__userprofile__is_public_profile=True
        ).order_by('-total_days_completed', '-total_water_logged', '-best_streak')
        
        for i, participant in enumerate(participants, 1):
            if participant.id == self.id:
                return i
        return None

class WaterTip(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('morning', 'Morning'),
        ('exercise', 'Exercise'),
        ('weather', 'Weather'),
        ('health', 'Health'),
        ('motivation', 'Motivation'),
    ]
    
    title = models.CharField(max_length=100)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    icon = models.CharField(max_length=50, default='fas fa-lightbulb', help_text="FontAwesome icon class")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.category})"
