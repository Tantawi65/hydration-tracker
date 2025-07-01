from django.contrib import admin
from .models import UserProfile, WaterLog, DailySummary, Challenge, ChallengeParticipant, WaterTip

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'weight', 'age', 'activity_level', 'weather_condition', 'glass_volume', 'is_public_profile']
    list_filter = ['activity_level', 'weather_condition', 'is_public_profile']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['user']

@admin.register(WaterLog)
class WaterLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['user__username']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']

@admin.register(DailySummary)
class DailySummaryAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'total_consumed', 'goal_amount', 'progress_percentage', 'is_goal_reached']
    list_filter = ['date']
    search_fields = ['user__username']
    date_hierarchy = 'date'
    ordering = ['-date']
    readonly_fields = ['progress_percentage', 'is_goal_reached']

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ['name', 'challenge_type', 'start_date', 'end_date', 'goal_per_day', 'is_public', 'participant_count', 'created_by']
    list_filter = ['challenge_type', 'is_public', 'start_date', 'end_date']
    search_fields = ['name', 'description', 'created_by__username']
    date_hierarchy = 'start_date'
    ordering = ['-created_at']
    readonly_fields = ['participant_count', 'created_at']

@admin.register(ChallengeParticipant)
class ChallengeParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'challenge', 'total_days_completed', 'current_streak', 'best_streak', 'total_water_logged', 'joined_at']
    list_filter = ['challenge', 'joined_at']
    search_fields = ['user__username', 'challenge__name']
    ordering = ['-total_days_completed', '-total_water_logged']
    readonly_fields = ['joined_at', 'completion_percentage', 'rank']

@admin.register(WaterTip)
class WaterTipAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['title', 'content']
    ordering = ['category', 'title']
