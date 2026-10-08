# FaceTune

FaceTune is a desktop-based face recognition and attendance management application built with Python.

It combines real-time face recognition, user management, attendance tracking, database storage, and a graphical interface into one application.

## Features

- Real-time face recognition
- Face dataset training
- User registration and management
- Attendance tracking
- SQLite database integration
- Camera management
- Audio support
- Recognition logs
- Application settings
- Graphical user interface

## Tech Stack

- **Python**
- **OpenCV**
- **Tkinter**
- **SQLite**
- **NumPy**
- **Pillow**
- Face recognition / computer vision libraries

## Project Structure

```text
FaceTune/
├── config/
│   └── Application configuration
├── core/
│   ├── audio_manager.py
│   ├── camera_manager.py
│   ├── recognition_engine.py
│   └── training_engine.py
├── database/
│   └── db_manager.py
├── gui/
│   ├── base_frame.py
│   ├── logs_page.py
│   ├── recognition_page.py
│   ├── settings_page.py
│   ├── sidebar.py
│   ├── training_page.py
│   └── user_management_page.py
├── models/
├── utils/
├── main.py
├── requirements.txt
└── README.md
```

## Installation

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd FaceTune
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run FaceTune

```bash
python main.py
```

## Usage

1. Launch the application.
2. Add/register a user.
3. Capture or provide face images for training.
4. Train the recognition model.
5. Start face recognition.
6. View attendance and recognition logs.

## Important Notes

This project is intended for educational and personal use.

Face recognition is sensitive biometric technology. Do not use the application to collect or process people's facial data without appropriate permission and safeguards.

Generated datasets, databases, logs, and trained models are intentionally excluded from the Git repository.

## Limitations

- Recognition accuracy depends on the quality of the training images and environment.
- Lighting, camera quality, pose, and occlusion can affect recognition.
- The current implementation does not provide advanced anti-spoofing protection.
- This project is not intended to be production-grade biometric security software.

## Future Improvements

- Anti-spoofing / liveness detection
- Improved recognition accuracy
- Better dataset validation
- Multi-face recognition improvements
- Attendance reports and analytics
- Export to CSV/PDF
- Authentication and role management
- Automated testing
- Improved UI/UX

## License

This project is licensed under the MIT License.