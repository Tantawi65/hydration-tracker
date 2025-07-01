from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Sum, Q
from datetime import date, timedelta
import json

from .models import UserProfile, WaterLog, DailySummary, Challenge, ChallengeParticipant, WaterTip
from .forms import UserProfileForm, CustomUserCreationForm, ChallengeForm
from .utils import get_coachbot_message

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'hydration/home.html')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            return redirect('profile_setup')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def profile_setup(request):
    try:
        profile = request.user.userprofile
        return redirect('dashboard')
    except UserProfile.DoesNotExist:
        if request.method == 'POST':
            form = UserProfileForm(request.POST)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                messages.success(request, 'Profile created successfully!')
                return redirect('dashboard')
        else:
            form = UserProfileForm()
        return render(request, 'hydration/profile_setup.html', {'form': form})

@login_required
def dashboard(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return redirect('profile_setup')
    
    today = date.today()
    daily_goal = profile.calculate_daily_goal()
    
    # Get or create today's summary
    summary, created = DailySummary.objects.get_or_create(
        user=request.user,
        date=today,
        defaults={'goal_amount': daily_goal}
    )
    
    # Update goal if it's different
    if summary.goal_amount != daily_goal:
        summary.goal_amount = daily_goal
        summary.save()
    
    # Calculate today's consumption
    today_consumption = WaterLog.objects.filter(
        user=request.user,
        timestamp__date=today
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Update summary
    summary.total_consumed = today_consumption
    summary.save()
    
    # Recent logs
    recent_logs = WaterLog.objects.filter(user=request.user)[:5]
    
    # Get CoachBot message
    coachbot_data = get_coachbot_message(request.user)
    
    context = {
        'profile': profile,
        'summary': summary,
        'today_consumption': today_consumption,
        'daily_goal': daily_goal,
        'progress_percentage': summary.progress_percentage,
        'recent_logs': recent_logs,
        'coachbot': coachbot_data,
    }
    
    return render(request, 'hydration/dashboard.html', context)

@login_required
@csrf_exempt
def log_water(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = int(data.get('amount', 0))
            
            if amount > 0:
                today = date.today()
                profile = request.user.userprofile
                daily_goal = profile.calculate_daily_goal()
                
                # Get consumption before logging
                previous_consumption = WaterLog.objects.filter(
                    user=request.user,
                    timestamp__date=today
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                # Create water log
                water_log = WaterLog.objects.create(
                    user=request.user,
                    amount=amount
                )
                
                # Update today's summary
                summary, created = DailySummary.objects.get_or_create(
                    user=request.user,
                    date=today,
                    defaults={'goal_amount': daily_goal}
                )
                
                # Recalculate total consumption
                today_consumption = WaterLog.objects.filter(
                    user=request.user,
                    timestamp__date=today
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                summary.total_consumed = today_consumption
                summary.save()
                
                # Check for goal completion (celebration trigger)
                goal_just_completed = (previous_consumption < daily_goal and today_consumption >= daily_goal)
                
                # Update challenge progress
                active_challenges = Challenge.objects.filter(
                    start_date__lte=today,
                    end_date__gte=today,
                    challengeparticipant__user=request.user
                )
                
                challenge_completions = []
                for challenge in active_challenges:
                    try:
                        participant = ChallengeParticipant.objects.get(
                            user=request.user,
                            challenge=challenge
                        )
                        participant.update_progress(amount, today)
                        
                        # Check if challenge goal was just completed
                        if today_consumption >= challenge.goal_per_day:
                            challenge_completions.append({
                                'name': challenge.name,
                                'goal': challenge.goal_per_day
                            })
                    except ChallengeParticipant.DoesNotExist:
                        pass
                
                response_data = {
                    'success': True,
                    'total_consumed': today_consumption,
                    'daily_goal': daily_goal,
                    'progress_percentage': summary.progress_percentage,
                    'goal_completed': goal_just_completed,
                    'challenge_completions': challenge_completions
                }
                
                return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def settings(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return redirect('profile_setup')
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully!')
            return redirect('settings')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'hydration/settings.html', {'form': form, 'profile': profile})

@login_required
def history(request):
    # Get last 30 days of summaries
    end_date = date.today()
    start_date = end_date - timedelta(days=29)
    
    summaries = DailySummary.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    ).order_by('-date')
    
    # Calculate streaks and stats
    consecutive_days = 0
    max_streak = 0
    current_streak = 0
    total_consumed = 0
    goals_met = 0
    
    for summary in summaries:
        total_consumed += summary.total_consumed
        if summary.is_goal_reached:
            goals_met += 1
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0
    
    # Prepare chart data
    chart_data = {
        'dates': [summary.date.strftime('%Y-%m-%d') for summary in reversed(summaries)],
        'consumed': [summary.total_consumed for summary in reversed(summaries)],
        'goals': [summary.goal_amount for summary in reversed(summaries)]
    }
    
    # Get today's date for template
    today = date.today()
    
    context = {
        'summaries': summaries,
        'max_streak': max_streak,
        'current_streak': current_streak,
        'total_consumed': total_consumed,
        'goals_met': goals_met,
        'total_days': summaries.count(),
        'chart_data': json.dumps(chart_data),
        'today': today,
    }
    
    return render(request, 'hydration/history.html', context)

def logout_view(request):
    """Custom logout view that handles GET requests"""
    logout(request)
    messages.success(request, 'You have been successfully logged out. Stay hydrated!')
    return redirect('home')

# Challenge Views
@login_required
def challenges_list(request):
    """Display all available challenges"""
    active_challenges = Challenge.objects.filter(
        start_date__lte=date.today(),
        end_date__gte=date.today(),
        is_public=True
    )
    
    upcoming_challenges = Challenge.objects.filter(
        start_date__gt=date.today(),
        is_public=True
    )
    
    # Get user's participations
    user_challenges = ChallengeParticipant.objects.filter(
        user=request.user
    ).select_related('challenge')
    
    # Get a random water tip
    random_tip = WaterTip.objects.filter(is_active=True).order_by('?').first()
    
    context = {
        'active_challenges': active_challenges,
        'upcoming_challenges': upcoming_challenges,
        'user_challenges': user_challenges,
        'random_tip': random_tip,
    }
    
    return render(request, 'hydration/challenges_list.html', context)

@login_required
def challenge_detail(request, challenge_id):
    """Display challenge details and allow joining"""
    challenge = get_object_or_404(Challenge, id=challenge_id)
    
    # Check if user is already participating
    try:
        participant = ChallengeParticipant.objects.get(
            user=request.user,
            challenge=challenge
        )
        is_participating = True
    except ChallengeParticipant.DoesNotExist:
        participant = None
        is_participating = False
    
    context = {
        'challenge': challenge,
        'participant': participant,
        'is_participating': is_participating,
    }
    
    return render(request, 'hydration/challenge_detail.html', context)

@login_required
def join_challenge(request, challenge_id):
    """Join a challenge"""
    challenge = get_object_or_404(Challenge, id=challenge_id)
    
    # Check if already participating
    if ChallengeParticipant.objects.filter(user=request.user, challenge=challenge).exists():
        messages.warning(request, 'You are already participating in this challenge!')
        return redirect('challenge_detail', challenge_id=challenge_id)
    
    # Create participation
    ChallengeParticipant.objects.create(
        user=request.user,
        challenge=challenge
    )
    
    messages.success(request, f'Successfully joined "{challenge.name}"! Good luck! 💪')
    return redirect('challenge_detail', challenge_id=challenge_id)

@login_required
def leaderboard(request, challenge_id):
    """Display challenge leaderboard"""
    challenge = get_object_or_404(Challenge, id=challenge_id)
    
    # Get participants (only public profiles)
    participants = ChallengeParticipant.objects.filter(
        challenge=challenge,
        user__userprofile__is_public_profile=True
    ).select_related('user', 'user__userprofile').order_by(
        '-total_days_completed',
        '-total_water_logged',
        '-best_streak'
    )
    
    # Check if current user is participating
    user_participant = None
    if request.user.is_authenticated:
        try:
            user_participant = ChallengeParticipant.objects.get(
                user=request.user,
                challenge=challenge
            )
        except ChallengeParticipant.DoesNotExist:
            pass
    
    context = {
        'challenge': challenge,
        'participants': participants,
        'user_participant': user_participant,
    }
    
    return render(request, 'hydration/leaderboard.html', context)

@login_required
def create_challenge(request):
    """Create a new challenge"""
    if request.method == 'POST':
        form = ChallengeForm(request.POST)
        if form.is_valid():
            challenge = form.save(commit=False)
            challenge.created_by = request.user
            challenge.save()
            
            # Automatically join the creator
            ChallengeParticipant.objects.create(
                user=request.user,
                challenge=challenge
            )
            
            messages.success(request, f'Challenge "{challenge.name}" created successfully!')
            return redirect('challenge_detail', challenge_id=challenge.id)
    else:
        form = ChallengeForm()
    
    context = {
        'form': form
    }
    
    return render(request, 'hydration/create_challenge.html', context)

def get_water_tips(request):
    """API endpoint to get random water tips"""
    tips = WaterTip.objects.filter(is_active=True).order_by('?')[:3]
    
    tips_data = []
    for tip in tips:
        tips_data.append({
            'title': tip.title,
            'content': tip.content,
            'icon': tip.icon,
            'category': tip.category
        })
    
    return JsonResponse({'tips': tips_data})

@login_required
def get_coachbot_message_api(request):
    """
    API endpoint to get fresh CoachBot message
    """
    coachbot_data = get_coachbot_message(request.user)
    return JsonResponse(coachbot_data)
