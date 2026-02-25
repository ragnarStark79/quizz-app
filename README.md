<p align="center">
  <h1 align="center">🧠 QuizOasis</h1>
  <p align="center">
    <strong>The Modern Interactive Quiz Platform</strong>
  </p>
  <p align="center">
    Create, share, and take quizzes with a beautiful modern interface.<br/>
    Track your progress and compete on the leaderboard.
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
    <img src="https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask"/>
    <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
    <img src="https://img.shields.io/badge/SQLAlchemy-3.1-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy"/>
    <img src="https://img.shields.io/badge/Firebase-Auth-FFCA28?style=for-the-badge&logo=firebase&logoColor=black" alt="Firebase"/>
    <img src="https://img.shields.io/badge/Chart.js-4.4-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white" alt="Chart.js"/>
    <img src="https://img.shields.io/badge/Google%20Gemini-AI-8E75B2?style=for-the-badge&logo=google&logoColor=white" alt="Google Gemini API"/>
  </p>
</p>

---

## ✨ Features

### 🎮 For Users
- **Create Quizzes** — Build quizzes with multiple-choice questions, set time limits, categories, and difficulty levels
- **✨ AI Quiz Generator** — Auto-generate structured quizzes in seconds using the **Google Gemini API** with multi-model fallback and smart rotation!
- **Take Quizzes** — Attempt quizzes from the explore page with a clean, distraction-free quiz interface
- **Dashboard** — Personal dashboard with animated stat cards, score history charts, and accuracy breakdowns
- **Leaderboard** — Global leaderboard to compete with other users and track rankings
- **Support Tickets** — Built-in support system to raise and track issues

### 👤 Profile Management
- **Profile Page** — Dedicated profile page with glassmorphism design and two-column responsive layout
- **Personal Info** — Update full name, email, and bio with server-side validation
- **Avatar Upload** — Upload custom profile pictures (JPG, PNG, WebP) with live preview. **Avatars display globally** across dashboards, leaderboards, quiz explore pages, and admin tables.
- **Password Change** — Secure password change with current password verification and complexity policy
- **Profile Completion** — Visual progress bar showing how complete your profile is
- **Navbar Dropdown** — Profile picture in the navbar with a sleek dropdown menu for quick navigation

### 🔐 Authentication
- **Email/Password Login** — Traditional registration and login with secure password hashing
- **Google Sign-In** — One-click Google authentication via Firebase with server-side token verification
- **Account Linking** — Existing email users can link their Google account seamlessly
- **OAuth Protection** — Google users are prevented from changing passwords (no password set)
- **Suspended User Blocking** — Suspended accounts are blocked at login for both auth methods

### 🛡️ For Admins
- **Admin Dashboard** — Overview of platform stats, user activity, and system health
- **User Management** — View, activate, suspend, or manage all registered users
- **Quiz Management** — Monitor, review, and moderate quizzes across the platform
- **Ticket Management** — Respond to and resolve user support tickets
- **Activity Logs** — Track all important actions and events across the platform
- **AI Usage Dashboard** — Monitor Gemini model calls, failures, fallback activity, and per-model success rates
- **Admin Stats on Profile** — Admins see platform-wide stats (users, quizzes, activities, tickets) on their profile page

---

## 🏗️ Tech Stack

| Layer          | Technology                                                                 |
|----------------|---------------------------------------------------------------------------|
| **Backend**    | [Flask 3.0](https://flask.palletsprojects.com/) — Lightweight Python web framework |
| **Database**   | [PostgreSQL](https://www.postgresql.org/) via [SQLAlchemy](https://www.sqlalchemy.org/) ORM |
| **Migrations** | [Flask-Migrate](https://flask-migrate.readthedocs.io/) (Alembic)          |
| **Auth**       | [Flask-Login](https://flask-login.readthedocs.io/) — Session-based authentication |
| **Google Auth**| [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup) — Server-side token verification |
| **AI Engine**  | [Google Gemini API](https://ai.google.dev/) (`google-genai`) — Multi-model fallback with round-robin rotation |
| **Charts**     | [Chart.js 4.4](https://www.chartjs.org/) — Interactive dashboard charts    |
| **Frontend**   | HTML5 + Vanilla CSS + JavaScript — Custom glassmorphism design system      |

---

## 📁 Project Structure

```
QuizOasis/
├── app/
│   ├── __init__.py            # App factory & extension init
│   ├── config.py              # Configuration settings
│   ├── models/                # Database models
│   │   ├── user.py            #   User accounts (email & Google auth)
│   │   ├── quiz.py            #   Quizzes
│   │   ├── question.py        #   Quiz questions
│   │   ├── attempt.py         #   Quiz attempts & scores
│   │   ├── category.py        #   Quiz categories
│   │   ├── support.py         #   Support tickets & replies
│   │   └── activity.py        #   Activity logs
│   ├── routes/                # Route blueprints
│   │   ├── auth_routes.py     #   Login, register, logout, Google login
│   │   ├── dashboard_routes.py#   User dashboard
│   │   ├── quiz_routes.py     #   CRUD for quizzes
│   │   ├── attempt_routes.py  #   Taking & submitting quizzes
│   │   ├── leaderboard_routes.py # Global leaderboard
│   │   ├── support_routes.py  #   Support tickets
│   │   ├── admin_routes.py    #   Admin panel
│   │   ├── profile_routes.py  #   Profile management
│   │   └── main_routes.py     #   Landing page
│   ├── services/              # Business logic layer
│   │   ├── auth_service.py    #   User registration
│   │   ├── quiz_service.py    #   Quiz CRUD operations
│   │   ├── ai_quiz_service.py #   Google Gemini AI integrations
│   │   ├── attempt_service.py #   Quiz attempt processing
│   │   ├── activity_service.py#   Activity logging
│   │   ├── support_service.py #   Support ticket management
│   │   └── profile_service.py #   Profile updates, avatar, password
│   ├── templates/             # Jinja2 HTML templates
│   │   ├── base.html          #   Base layout with navbar dropdown
│   │   ├── index.html         #   Landing page
│   │   ├── auth/              #   Login & register (with Google button)
│   │   ├── dashboard/         #   User dashboard
│   │   ├── quiz/              #   Quiz CRUD, explore, & AI Generate template
│   │   ├── attempt/           #   Quiz attempt interface
│   │   ├── leaderboard/       #   Leaderboard page
│   │   ├── support/           #   Support ticket pages
│   │   ├── admin/             #   Admin panel pages
│   │   └── profile/           #   Profile management page
│   ├── static/                # CSS, uploads
│   │   ├── css/style.css      #   Design system & all styles
│   │   └── uploads/           #   User-uploaded profile pictures
│   └── utils/                 # Helper utilities
│       ├── decorators.py      #   Auth & role decorators
│       └── firebase.py        #   Firebase token verification
├── migrations/                # Alembic database migrations
├── run.py                     # Application entry point
├── requirements.txt           # Python dependencies
├── seedadmin.py               # Admin user seeder script
└── .env                       # Environment variables (not committed)
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** installed on your system
- **PostgreSQL** database server
- **pip** (Python package manager)
- **Git**
- **Firebase project** (for Google authentication)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ragnarStark79/quizz-app.git
   cd quizz-app
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate        # macOS / Linux
   # venv\Scripts\activate         # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Create a `.env` file in the root directory:
   ```env
   # Database
   SQLALCHEMY_DATABASE_URI=postgresql+psycopg://localhost/quizz_db

   # Flask
   SECRET_KEY=your-secret-key-here
   FLASK_APP=run.py
   FLASK_ENV=development

   # Firebase
   FIREBASE_CREDENTIALS=path/to/serviceAccountKey.json
   FIREBASE_API_KEY=your-firebase-api-key
   FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   FIREBASE_PROJECT_ID=your-project-id

   # Google Gemini AI
   GEMINI_API_KEY=your_gemini_api_key
   ```

5. **Set up Firebase** *(for Google authentication)*
   - Create a project at [Firebase Console](https://console.firebase.google.com/)
   - Enable **Google** sign-in under Authentication → Sign-in method
   - Download your **Service Account Key** JSON and place it at the path specified in `.env`
   - Copy your **Web app config** values into the `.env` file

6. **Initialize the database**
   ```bash
   flask db upgrade
   ```

7. **Seed the admin user** *(optional)*
   ```bash
   python seedadmin.py
   ```

8. **Run the application**
   ```bash
   python run.py
   ```

9. **Open in browser**
   ```
   http://127.0.0.1:5000
   ```

---

## 📸 Application Overview

| Page              | Description                                                  |
|-------------------|--------------------------------------------------------------|
| **Landing Page**  | Modern hero section with feature cards and CTA buttons       |
| **Login/Register**| Email/password + Google sign-in with Firebase                 |
| **Dashboard**     | Animated stats, score history bar chart, accuracy doughnut   |
| **Explore**       | Browse and search available quizzes with filters             |
| **Quiz Builder**  | Create quizzes with questions, options, and settings          |
| **Quiz Attempt**  | Clean interface for taking quizzes with progress bar         |
| **Leaderboard**   | Global user rankings by score with medal icons               |
| **Profile**       | Personal info, avatar upload, password change, account details|
| **Admin Panel**   | Full admin dashboard with user, quiz, and ticket management  |
| **Support**       | Submit and track support tickets with chat-style threads     |

---

## 🔐 Authentication Flow

```
┌─────────────────────────────────────────────────┐
│                   Login Page                     │
│                                                  │
│   ┌──────────────────────────────────────────┐   │
│   │       Email / Password Form              │   │
│   │       ─────────────────────              │   │
│   │       Flask-Login session auth           │   │
│   └──────────────────────────────────────────┘   │
│                                                  │
│          ── or continue with ──                  │
│                                                  │
│   ┌──────────────────────────────────────────┐   │
│   │       🔵 Sign in with Google             │   │
│   │       ─────────────────────              │   │
│   │   Firebase SDK → ID Token → Flask API    │   │
│   │   → Server-side verification → Session   │   │
│   └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

---

## � User Roles

| Role       | Capabilities                                                                 |
|------------|-----------------------------------------------------------------------------|
| **User**   | Register, login (email or Google), create quizzes, take quizzes, manage profile, view dashboard & leaderboard |
| **Admin**  | All user capabilities + manage users, quizzes, tickets, view activity logs, admin stats on profile   |

---

## 🧪 Database Models

```mermaid
erDiagram
    User ||--o{ Quiz : creates
    User ||--o{ Attempt : takes
    User ||--o{ SupportTicket : submits
    User ||--o{ Activity : logs
    Quiz ||--|{ Question : contains
    Quiz ||--o{ Attempt : "attempted via"
    Category ||--o{ Quiz : categorizes
    SupportTicket ||--o{ SupportReply : "has replies"
```

---

## 🎨 Design System

The application uses a custom **glassmorphism design system** built with vanilla CSS:

- **Color Palette** — Creamy gradient background (`#fdfcfb → #e2d1c3`), soft indigo accent (`#6366f1`)
- **25+ CSS Variables** — Design tokens for colors, spacing, shadows, and border radii
- **Glassmorphism Cards** — `backdrop-filter: blur(20px)` with soft borders and hover lift effects
- **Floating Blobs** — Radial gradient pseudo-elements for premium visual depth
- **Animations** — `fadeIn`, `fadeSlideUp`, `scaleIn` with stagger support
- **Responsive** — Mobile-first with hamburger nav and adaptive layouts
- **Premium Tables** — Glass tables that transform into stacked cards on mobile

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  Made by Ragnar Stark using Flask
</p>
