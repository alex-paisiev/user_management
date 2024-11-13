# User List Application

This is a simple Flask-based user management application that allows users to view, add, update, and delete user entries from a list. The application also includes features such as phone number validation, CSRF protection, and AI-generated avatars.

## Features

- List users with pagination
- Add, update, and delete users
- User-friendly error messages for form validation
- Phone number validation with country code handling
- CSRF protection for all forms
- AI-generated avatars using Robohash

## Prerequisites

- Docker
- Python 3.8 or higher
- PostgreSQL (optional for **not** containerized setup)


## Installation

1. **Clone the repository**
   ```sh
   git clone <repository-url>
   cd user_list_app
   ```

2. **Create a virtual environment**
   ```sh
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory copy the variable from the .env_sample file:
   ```sh
   FLASK_ENV=development
   SECRET_KEY=your_secret_key_here
   DATABASE_URL=postgresql://username:password@localhost/dbname
   ```

## Docker Setup 

To run the application using Docker, follow these steps:

1. **Build the Docker images**
   ```sh
   docker-compose build
   ```

2. **Run the containers**
   ```sh
   docker-compose up
   ```

This will spin up two containers: one for the Flask application and one for the PostgreSQL database.

## Running the Application
**Apply database migrations**
   - **Initialize migrations**
     ```sh
     flask db init
     ```
   - **Create migration scripts**
     ```sh
     flask db migrate -m "Initial migration."
     ```
   - **Apply migrations to the database**
     ```sh
     flask db upgrade
     ```

## Project Structure

```
user_list_app/
├── app.py                # Main application file
├── forms.py              # Form definitions with validation logic
├── models.py             # Database models
├── templates/            # HTML templates
│   ├── add_user.html
│   ├── update_user.html
│   └── index.html
├── static/               # Static files (CSS, JavaScript, images)
│   └── images/
│       └── avatars/
│           └── default_avatar.png
├── migrations/           # Database migration files
├── Dockerfile            # Docker configuration for the Flask app
├── docker-compose.yml    # Docker Compose file to set up multi-container environment
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## Usage Instructions

### Adding Users
- Go to the **Add User** page.
- Fill in the **Name**, **Email**, and **Phone** fields.
- **Phone number** should contain only digits and can start with a `+`.
- Submit the form to add a user.

### Updating Users
- Click on the **Edit** button next to a user in the list.
- Modify the user details and submit the form.

### Deleting Users
- Click the **Delete** button next to a user.
- Confirm the deletion. The associated avatar file will also be deleted.

## Notes

- **AI Avatars**: Avatars are generated using Robohash and are saved locally in the `static/images/avatars` directory.
- **Phone Validation**: Both client-side and server-side validation ensure that the phone number contains only digits or an optional `+`.
- **CSRF Protection**: All forms are CSRF protected to prevent cross-site request forgery attacks.
