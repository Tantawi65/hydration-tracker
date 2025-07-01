# Interactive Hydration Calculator

A beautiful and interactive Django web application that helps users track their daily water intake, calculate personalized hydration goals, and monitor their progress with animated visualizations.

## Features

### User Authentication
- User registration and login system
- Profile setup with personalized settings
- Secure session management

### Interactive Dashboard
- Animated water bottle visualization that fills up based on daily intake
- Real-time progress tracking with animated progress bars
- Quick water logging buttons (+1 glass, +500ml, custom amount)
- Daily statistics and recent activity log

### Personalized Settings
- Weight, age, and activity level configuration
- Weather condition adjustments
- Custom glass volume settings
- Optional manual daily goal override
- Smart goal calculation based on user parameters

### History & Analytics
- 30-day hydration history with interactive charts
- Daily consumption tracking
- Streak counting and achievement system
- Progress statistics and goal completion rates

### Gamification
- Achievement badges (3-day streak, week warrior, goal crusher)
- Streak tracking (current and best streaks)
- Visual progress indicators
- Celebration animations for goals met

## Technologies Used
- Backend: Django 5.2.3 + SQLite
- Frontend: HTML5, CSS3, JavaScript (ES6+)
- Styling: Bootstrap 5.1.3 + Custom CSS
- Charts: Chart.js
- Icons: Font Awesome 6.0
- Animations: Pure CSS + JavaScript

## Installation & Setup
### Prerequisites
- Python 3.8+ installed
- Virtual environment (recommended)

### 1. Clone/Download the Project

### 2. Activate Virtual Environment

### 3. Install Dependencies

### 4. Database Setup
python manage.py makemigrations
python manage.py migrate


### 5. Create Superuser (Admin Access)
python manage.py createsuperuser

Follow the prompts to create an admin account.

### 6. Run the Development Server
python manage.py runserver


The application will be available at: `http://127.0.0.1:8000/`

## Responsive Design

The application is fully responsive and works seamlessly on:
- Desktop computers
- Tablets
- Mobile phones

**Stay Hydrated!**

*Built with care for better health and wellness*