# Applyra Version 1.0.0: Resume and Cover Letter Builder

> A web-based application that enables users to create, manage, and generate professional resumes and cover letters tailored to specific job advertisements using AI-assisted analysis.

Developed as an **NCEA Level 3 Software Development** project to demonstrate full-stack web development, responsive web design, and AI integration.

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,flask,sqlite,js,html,css,git,github,vscode,neovim,htmx" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white">
</p>

---

## Overview
The purpose of this project is to develop a web-based job application platform that helps users create professional, job-specific CVs and cover letters more efficiently. Users can securely store their personal information, education, work experience, and skills in a central profile, allowing the system to generate tailored application documents and analyse job advertisements using AI. The platform is designed for students and job seekers, reducing the time and effort required to prepare applications while improving the quality of their job applications.

---

## Features

- **User Authentication** – Secure user registration, login, and account management.
- **User Profile Management** – Store and manage personal details, education, work experience, skills, and certificates.
- **AI Job Analysis** – Analyse job advertisements to identify required skills and job suitability.
- **AI Resume Generation** – Generate a professional, job-specific resume based on the user's profile and the selected job.
- **AI Cover Letter Generation** – Create customised cover letters tailored to individual job applications.
- **Document Management** – Save, view, edit, and organise generated resumes and cover letters.
- **Rich Text Document Editor** – Edit generated documents before downloading or submitting them.
- **Responsive Web Interface** – Accessible across desktop, tablet, and mobile devices.
- **Persistent Database Storage** – Store user information and generated documents securely using a relational database.
- **Form Validation & Error Handling** – Validate user input and provide clear feedback to improve usability.

---
## Architecture

| Component | Technology |
|-----------|------------|
| Backend | Flask |
| Frontend | HTMX + Jinja2 |
| Database | SQLite + SQLAlchemy |
| AI | Gemini API |
| Architecture | Server-side rendered, SPA-like navigation using HTMX |

---

## Demo

<p align="center">
  <img src="docs/demo.gif" alt="Applyra Demo" width="900">
</p>

---

## Tech Stack

### Backend

- Python
- Flask
- SQLAlchemy
- Flask-WTF
- Flask-Migrate
- Flask-Login


### Frontend

- HTML5
- CSS3
- JavaScript
- Jinja2
- HTMX

### Database

- SQLite

### AI

- Gemini API

---

## Project Structure

```
project/
│
├── app/
│   ├── ai/
│   ├── routes/
│   ├── templates/
│   ├── static/
│   ├── utilities/
|   ├── __init__.py
|   ├── extensions.py
|   ├── forms.py
|   └── models.py
│  
│
├── migrations/
├── instance/
├── docs/
├── config.py
├── .env
├── requirements.txt
├── main.py
└── README.md
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/AlgorithmicPV/Applyra-v1.git
```

Go into the project

```bash
cd applyra-v1
```

Create virtual environment

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file.

Example:

```env
SECRET_KEY=
MAIL_SERVER=
MAIL_USERNAME=
MAIL_PASSWORD=
OTP_SECRET=
FERNET_KEY=
GEMINI_API_KEY=
```

### TOTP Setup Tutorial

If you are unfamiliar with setting up TOTP, this tutorial may help:

[▶ TOTP Setup Tutorial by NeuralNine](https://youtu.be/o0XZZkI69E8)

**Credit:** [NeuralNine](https://www.youtube.com/@NeuralNine) — external tutorial used for reference only.

### Gemini API Key

This application uses the Gemini API for AI-powered features.

1. Go to [Google AI Studio](https://aistudio.google.com/api-keys).
2. Sign in with your Google account.
3. Create a Gemini API key.
4. Add the API key to your `.env` file:

### Email Setup Tutorial

If you need help setting up the email system for this application, you can follow this external tutorial:

[▶ Watch Email Setup Tutorial by Arpan Neupane](https://youtu.be/L7Cslucyyyo)

**Credit:** Arpan Neupane — external tutorial provided for setup reference only.

#### Generate a Fernet Key

This application uses a Fernet key to encrypt sensitive data such as TOTP secrets.

Generate a key by running:

```python
from cryptography.fernet import Fernet

print(Fernet.generate_key().decode())
```

#### Generate a Secret Key

The application requires a `SECRET_KEY` for Flask security features such as sessions and CSRF protection.

You can generate a random key using UUID4:

```python
import uuid

print(uuid.uuid4().hex)
```

---

## Database Setup

Initialize migrations

```bash
flask db init
```

Create migration

```bash
flask db migrate -m "Initial migration"
```

Apply migration

```bash
flask db upgrade
```

---

## Running the Project

```bash
flask run
```

or

```bash
python main.py
```
or
```bash
python3 main.py
```

Application will be available at

```
http://127.0.0.1:5000
```
---


## Usage

1. Register an account.
2. Verify your email address.
3. Complete your profile.
4. Add your education, skills, and work experience.
5. Analyse a job advertisement.
6. Generate an AI-tailored resume.
7. Generate an AI-tailored cover letter.
8. Edit the generated documents.
9. Save or download the final documents.

---

## Author

**G.A.P Vidunitha**

GitHub: https://github.com/AlgorithmicPV

LinkedIn: https://www.linkedin.com/in/pasindu-vidunitha-7b3a573a5/


---

## Acknowledgements

- Flask
- SQLAlchemy
- HTMX
- Google Gemini
- Bootstrap
- TinyMCE


---

## Support

If you found this project useful, please consider giving it a ⭐ on GitHub.

## Copyright

© 2026 G.A.P Vidunitha. All rights reserved.

