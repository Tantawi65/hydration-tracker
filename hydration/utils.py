from datetime import datetime, date, timedelta
from django.db.models import Sum
from django.utils import timezone
from .models import WaterLog, DailySummary, Challenge, ChallengeParticipant
import random

def get_coachbot_message(user):
    """
    Generate a personalized CoachBot message based on user's hydration behavior
    """
    try:
        profile = user.userprofile
        today = date.today()
        current_time = datetime.now().time()
        daily_goal = profile.calculate_daily_goal()
        
        # Calculate today's consumption
        today_consumption = WaterLog.objects.filter(
            user=user,
            timestamp__date=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate progress percentage
        progress_percentage = min(100, round((today_consumption / daily_goal) * 100)) if daily_goal > 0 else 0
        
        # Check for active challenges
        active_challenges = Challenge.objects.filter(
            start_date__lte=today,
            end_date__gte=today,
            challengeparticipant__user=user
        )
        
        # Calculate streak
        current_streak = calculate_streak(user)
        
        # Determine time of day
        if current_time.hour < 11:
            time_period = "morning"
        elif current_time.hour < 17:
            time_period = "afternoon"
        else:
            time_period = "evening"
        
        # Generate message based on conditions
        message = generate_message_by_conditions(
            progress_percentage, 
            time_period, 
            active_challenges, 
            current_streak,
            today_consumption,
            daily_goal
        )
        
        return {
            'message': message,
            'progress_percentage': progress_percentage,
            'streak': current_streak,
            'time_period': time_period,
            'has_active_challenge': active_challenges.exists()
        }
        
    except Exception as e:
        # Fallback message
        return {
            'message': "Hi there! Remember to stay hydrated throughout the day! 💧",
            'progress_percentage': 0,
            'streak': 0,
            'time_period': 'day',
            'has_active_challenge': False
        }

def generate_message_by_conditions(progress_percentage, time_period, active_challenges, streak, consumption, goal):
    """
    Generate specific message based on user conditions
    """
    has_challenge = active_challenges.exists()
    
    # Goal completed (100%+)
    if progress_percentage >= 100:
        messages = [
            "Fantastic! You've crushed your hydration goal today! 🎉",
            "Amazing work! You're properly hydrated and feeling great! 🌟",
            "Goal achieved! Your body is thanking you for staying hydrated! 💪",
            "Perfect! You've reached your daily goal. Keep up the excellent work! 🏆"
        ]
        if streak >= 3:
            messages.append(f"Incredible! You've hit your goal AND you're on a {streak}-day streak! 🔥")
        return random.choice(messages)
    
    # Very close to goal (70-99%)
    elif progress_percentage >= 70:
        messages = [
            f"Almost there! Just {goal - consumption}ml more to crush your daily goal! 🎯",
            "You're in the home stretch! A few more sips and you'll reach your goal! 🚀",
            f"So close! Only {goal - consumption}ml away from victory! 💧",
            "Great progress! You're almost at your hydration finish line! 🏁"
        ]
        return random.choice(messages)
    
    # Good progress (30-69%)
    elif progress_percentage >= 30:
        messages = [
            f"Steady progress! You're at {progress_percentage}% - keep the momentum going! 🚶‍♂️💧",
            "Nice work! You're making solid progress toward your goal! 👍",
            f"Keep it up! You're {progress_percentage}% there and doing great! ⭐",
            "Good job staying consistent! Your hydration journey is on track! 🛤️"
        ]
        if has_challenge:
            messages.append("Don't forget - today counts toward your challenge! Stay focused! 🏆")
        return random.choice(messages)
    
    # Low progress (1-29%)
    elif progress_percentage > 0:
        if time_period == "evening":
            messages = [
                f"It's {time_period} and you're only at {progress_percentage}%. Time to catch up! ⏰",
                "Evening reminder: Your body still needs more hydration today! 🌙💧",
                "Don't let today slip away! You can still make good progress! 💪"
            ]
        else:
            messages = [
                f"You're at {progress_percentage}% - time to step up your hydration game! 💪",
                "Great start! Now let's build on that momentum! 🚀",
                f"You've begun your hydration journey. Keep adding to that {progress_percentage}%! 📈"
            ]
        
        if has_challenge:
            messages.append("Remember: today counts toward your challenge! Don't miss out! 🏆")
        return random.choice(messages)
    
    # No progress yet (0%)
    else:
        if time_period == "morning":
            messages = [
                "Good morning! It's a perfect day to start fresh - log your first glass! ☀️💧",
                "Rise and hydrate! Your body is ready for some refreshing water! 🌅",
                "Morning sunshine! Let's kickstart your hydration journey today! ✨"
            ]
        elif time_period == "afternoon":
            messages = [
                "Afternoon check-in: You haven't logged any water yet. Time to start! 🕐💧",
                "It's afternoon and your hydration meter is empty. Let's change that! 📊",
                "Midday reminder: Your body is waiting for some hydration love! 💝"
            ]
        else:
            messages = [
                "Evening alert: You haven't logged any water today. It's not too late! 🌆",
                "End-of-day reminder: Even a little hydration is better than none! 🌙",
                "Don't let today end without any water logged. Start now! ⭐"
            ]
        
        if streak > 0:
            messages.append(f"You have a {streak}-day streak to protect! Don't break it now! 🔥")
        if has_challenge:
            messages.append("You're in a challenge but haven't started today. Jump in! 🏆")
        
        return random.choice(messages)

def calculate_streak(user):
    """
    Calculate current hydration streak for user
    """
    try:
        today = date.today()
        streak = 0
        check_date = today - timedelta(days=1)  # Start from yesterday
        
        # Go backwards day by day and check if goal was met
        for _ in range(30):  # Check last 30 days max
            try:
                summary = DailySummary.objects.get(user=user, date=check_date)
                if summary.is_goal_reached:
                    streak += 1
                else:
                    # Streak broken
                    break
            except DailySummary.DoesNotExist:
                # No data for this day, streak broken
                break
            
            check_date -= timedelta(days=1)
        
        return streak
        
    except Exception:
        return 0