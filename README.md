# Psychology Bot

A Telegram bot built with Aiogram for managing psychology consultations, tests, topics, and activities. Administrators
can create and manage sessions, tests, topics, and users; regular users can view available topics, take tests, schedule
consultations, and browse recommended activities.

---

## 🔑 Features

- **User-facing functionality**  
  - `/start` command to begin interacting with the bot.  
  - Browse actual activity (take a test or read a topic)
  - **Schedule** one-on-one consultations at available time slots.

- **Admin interface**  
  - Add, update, and delete **Topics**, **Topic Items**, **Tests**, and **Test Items**.  
  - Manage the **Schedule**: add available slots, remove past or booked slots, and view all appointments.  
  - Oversee **Users**: list registered users and manage them.  
  - Return to the main admin menu at any time with “Back” commands.

- **Background tasks**  
  - Automatically clears outdated appointments daily at midnight.  
  - Creates the database schema on startup if it does not exist.

---

## 🛠️ Technologies

* Python 3.10+
* Aiogram 3
* SQLAlchemy 2
* Asyncio, schedule, loguru
* SQLite or PostgreSQL

---

## 🚀 Installation

1. **Clone the repository**
   ```bash
    git clone https://github.com/AN1CER784/psychology_bot.git
    cd psychology_bot
    ```
2. **Prepare a virtual environment**
   ```bash
    python -m venv venv
    source venv/bin/activate   # Linux/macOS
    venv\Scripts\activate      # Windows
    ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
    ```

4. **Set up environment variables**  
   Create a .env file in the project root with:
    ```bash
    TOKEN= # valid telegram bot token
    ADMIN_ID= # valid id of telegram user
    GROUP_ID=  # valid id of telegram group (you should add that bot there firstly and give it all corresponding previliges
    DB_URL= # url for project db; the simplest way: define it as sqlite+aiosqlite:///test.db
    ```

5. **Then run the bot:**
    ```bash
    python main.py
    ```

## 📁 Project Structure

```
.
├── common/                  # Bot command definitions
├── config.py                # Environment config
├── database/                # DB models and queries
│   ├── engine.py            # DB engine setup
│   ├── models.py            # SQLAlchemy models
│   └── orm_queries/         # ORM query helpers
├── filters/                 # Custom filters
├── handlers/               
│   ├── admin/               # Admin bot logic
│   └── user/                # User bot logic
├── middlewares/            # DB session middleware
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
```

## ✨ Core Functionality

The bot operates through a modular handler system using Aiogram 3.0, providing the following core functionalities:

- **Start Command (`/start`)**: Initializes the bot, registers the user if not present in the database, and displays the main menu with options.

- **Topics & Topic Items**: Users can browse categorized psychology topic chosen by admin. Each topic contains detailed items that the user can read through with inline navigation.

- **Tests**: Structured as multiple-choice quizzes. Users answer a series of questions, and their total score determines the final result level (e.g. high, medium, low). Feedback is provided based on the score.

- **Schedule Management**: Users can book consultations from a list of available time slots. Booked slots are hidden from future users. Admins can manage available slots and see all scheduled users.

- **Admin Panel**: A separate interface accessible only to admins allows content and user management:
  - Add/edit/delete topics, topic items, tests, and test items.
  - Manage the schedule by adding or removing available times.
  - View all users and their bookings.

- **Data Persistence**: All user actions, content, and schedule data are stored in a relational database using async SQLAlchemy.

- **Background Tasks**: Scheduled task runs daily at midnight to clear outdated schedule slots, ensuring database cleanliness.

