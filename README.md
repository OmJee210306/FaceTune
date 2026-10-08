# FaceTune 🎵

### Facial Recognition • Personalized Music • Desktop Application

FaceTune is a Python-based desktop application that combines **real-time facial recognition with personalized music playback**.

The application uses a webcam to detect and recognize registered users. When a registered user is recognized consistently for a configured period, FaceTune can automatically play that user's assigned song.

It also provides user management, face dataset training, recognition logs, application settings, and SQLite-based local data storage through a modern desktop interface.

---

## ✨ Features

- 🎥 **Real-time webcam face recognition**
- 🧠 **Face encoding and recognition using `face_recognition` / dlib**
- 👤 **User registration and management**
- 📸 **Face dataset management**
- 🏋️ **Face recognition model training**
- 🎵 **Personalized music playback**
- ⏱️ **Recognition stability tracking** to reduce accidental triggers
- 📋 **Recognition and activity logs**
- 🗄️ **SQLite local database**
- ⚙️ **Configurable recognition settings**
- 🖥️ **Modern CustomTkinter desktop interface**
- 📷 **Threaded camera capture**
- 📝 **Application logging**
- 🔊 **MP3/WAV audio playback**

---

## 🖥️ Application Workflow

```text
                ┌──────────────────┐
                │   Add User       │
                │ + Face Images    │
                │ + Personal Song  │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │   Train Model    │
                │ Generate Face    │
                │    Embeddings    │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Start Recognition│
                │     Webcam       │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Detect & Identify│
                │      Face        │
                └────────┬─────────┘
                         │
                   Stable match
                         │
                         ▼
                ┌──────────────────┐
                │ Play User's Song │
                │ + Record Log     │
                └──────────────────┘
```

---

## 🛠️ Tech Stack

| Technology           | Purpose                                      |
| -------------------- | -------------------------------------------- |
| **Python**           | Core application language                    |
| **OpenCV**           | Webcam and image processing                  |
| **face_recognition** | Face detection and face encoding             |
| **dlib**             | Underlying face recognition models           |
| **CustomTkinter**    | Desktop GUI                                  |
| **SQLite**           | Local database                               |
| **Pygame**           | Audio playback                               |
| **NumPy**            | Numerical operations                         |
| **Pillow**           | Image processing                             |
| **Logging**          | Application diagnostics and activity logging |

---

## 📁 Project Structure

```text
FaceTune/
│
├── main.py                         # Application entry point
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── LICENSE                         # MIT License
├── .gitignore                      # Git exclusions
│
├── config/
│   ├── __init__.py
│   └── settings.py                 # Application configuration
│
├── core/
│   ├── __init__.py
│   ├── audio_manager.py            # Music playback
│   ├── camera_manager.py           # Threaded camera capture
│   ├── recognition_engine.py       # Face recognition logic
│   └── training_engine.py          # Face embedding generation
│
├── database/
│   ├── __init__.py
│   └── db_manager.py               # SQLite database operations
│
├── gui/
│   ├── __init__.py
│   ├── base_frame.py               # Shared GUI functionality
│   ├── logs_page.py                # Recognition/activity logs
│   ├── recognition_page.py        # Live recognition interface
│   ├── settings_page.py            # Application settings
│   ├── sidebar.py                  # Navigation sidebar
│   ├── training_page.py            # Model training interface
│   └── user_management_page.py     # User management
│
├── models/
│   └── embeddings.pkl              # Generated locally after training
│
├── dataset/
│   └── <user>/                     # Local face images
│
├── songs/
│   └── <audio files>                # Local user songs
│
└── logs/
    └── facetune.log                # Runtime application logs
```

> **Note:** `dataset/`, `songs/`, `logs/`, the SQLite database, and generated model files contain local/generated data and should not be committed to the repository.

---

# 🚀 Installation

## Prerequisites

Before installing FaceTune, make sure you have:

- Python **3.9–3.11**
- A working webcam
- Git
- CMake
- A C/C++ build environment required by `dlib`

### Windows

You may need:

- [CMake](https://cmake.org/download/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

Make sure CMake and the required compiler tools are available in your system PATH.

### Ubuntu / Debian

```bash
sudo apt-get update
sudo apt-get install -y cmake build-essential libportaudio2 libgl1
```

### macOS

```bash
brew install cmake
```

---

# 📥 Clone the Repository

```bash
git clone https://github.com/OmJee210306/FaceTune.git
cd FaceTune
```

---

# 🐍 Create a Virtual Environment

Creating a virtual environment is recommended so that FaceTune's dependencies remain isolated from other Python projects.

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

# 📦 Install Dependencies

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install project dependencies:

```bash
pip install -r requirements.txt
```

> **Note:** `dlib` and `face_recognition` may require additional build tools depending on your operating system and Python version.

---

# ▶️ Run FaceTune

Once the dependencies are installed:

```bash
python main.py
```

The FaceTune desktop application should open.

---

# 🎯 How to Use

## 1. Add a User

Open the **Users** section.

Create a new user and provide:

- User name
- Face images
- Personal MP3/WAV song

For better recognition results, use multiple images with variations in:

- Face angle
- Lighting
- Expression
- Distance from the camera

Around **20–40 images per user** can provide a useful starting dataset.

---

## 2. Train the Recognition Model

Open the **Training** section and start model training.

FaceTune:

1. Scans the user dataset.
2. Detects faces.
3. Generates face encodings.
4. Associates encodings with user names.
5. Saves the generated model locally.

The generated model is stored as:

```text
models/embeddings.pkl
```

You should retrain the model after adding new users or significantly changing the training dataset.

---

## 3. Start Recognition

Open the **Recognition** section and start the webcam.

FaceTune will:

1. Capture frames from the webcam.
2. Detect faces.
3. Generate face encodings.
4. Compare them with registered users.
5. Determine whether the face matches a known user.
6. Wait for a stable recognition.
7. Trigger the associated song.
8. Record the recognition event.

---

# 🎵 Personalized Music

Each registered user can have an associated audio file.

Supported formats include:

```text
.mp3
.wav
```

When a user is successfully recognized, FaceTune can automatically play their assigned song.

---

# ⚙️ Configuration

Application settings are centralized in:

```text
config/settings.py
```

Important configuration options include:

| Setting                      | Default | Description                         |
| ---------------------------- | ------: | ----------------------------------- |
| `DEFAULT_THRESHOLD`          |  `0.50` | Face-distance recognition threshold |
| `RECOGNITION_STABLE_SECONDS` |   `1.0` | Required stable recognition time    |
| `DEFAULT_CAMERA_INDEX`       |     `0` | Default webcam index                |
| `FRAME_WIDTH`                |   `640` | Camera frame width                  |
| `FRAME_HEIGHT`               |   `480` | Camera frame height                 |

Some settings can also be changed through the application's **Settings** page.

### Recognition Threshold

A lower threshold makes recognition more strict.

For example:

```text
0.50 → default
0.45 → stricter
0.42 → even stricter
```

The appropriate value depends on the quality of the dataset, camera, lighting, and environment.

---

# 🗄️ Database

FaceTune uses **SQLite** for local application data.

The database stores information such as:

- Registered users
- Assigned songs
- User creation timestamps
- Recognition logs
- Recognition status
- Recognition timestamps

The database is created automatically when the application starts.

---

# 🧠 Recognition Architecture

FaceTune uses facial embeddings rather than directly comparing raw images.

The general pipeline is:

```text
Webcam Frame
     ↓
Face Detection
     ↓
Face Encoding
     ↓
Compare Against Stored Encodings
     ↓
Distance Calculation
     ↓
Threshold Check
     ↓
Stable Recognition
     ↓
Personalized Music
```

The recognition engine also uses a **stability mechanism** so that a face must remain consistently recognized for a configured period before a recognition event is confirmed.

This helps reduce accidental triggers caused by a single unstable frame.

---

# 🔒 Privacy & Security

FaceTune processes facial data locally as part of its recognition workflow.

However, this project is **not intended to be production-grade biometric security software**.

Important considerations:

- Do not collect facial data without appropriate permission.
- Do not commit personal face datasets to GitHub.
- Do not commit generated embeddings containing personal biometric information.
- Do not commit personal databases or logs.
- Use the application responsibly and in accordance with applicable privacy laws and policies.

Generated biometric data is intentionally excluded from the Git repository.

---

# ⚠️ Current Limitations

FaceTune is primarily an educational/personal project and has several limitations.

### Recognition

Recognition performance can vary depending on:

- Lighting
- Camera quality
- Face angle
- Occlusion
- Training dataset quality
- Recognition threshold

### Anti-Spoofing

The current implementation does **not provide advanced liveness detection or anti-spoofing protection**.

A production biometric system would require additional safeguards.

### Training

The current training pipeline generates an encoding from the first detected face in each image.

Images without a detectable face are skipped.

### Local Storage

Face embeddings, user data, logs, and application state are stored locally.

---

# 🔮 Future Improvements

Potential future improvements include:

- [ ] Advanced anti-spoofing / liveness detection
- [ ] Improved face-recognition accuracy
- [ ] Better dataset validation
- [ ] Multi-face recognition improvements
- [ ] Attendance analytics and reports
- [ ] CSV/PDF export
- [ ] User authentication and role management
- [ ] Improved model/data security
- [ ] Automated testing
- [ ] Better error recovery
- [ ] Improved UI/UX
- [ ] Cross-platform packaging
- [ ] Standalone executable releases

---

# 🧪 Development

To contribute or experiment with FaceTune:

```bash
git clone https://github.com/OmJee210306/FaceTune.git
cd FaceTune
python -m venv venv
```

Activate the environment and install dependencies:

```bash
pip install -r requirements.txt
```

Then run:

```bash
python main.py
```

---

# 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

A typical workflow:

```bash
# Create a branch
git checkout -b feature/your-feature

# Make your changes

# Stage changes
git add .

# Commit
git commit -m "Add your feature"

# Push branch
git push origin feature/your-feature
```

Then open a Pull Request on GitHub.

---

# 📄 License

FaceTune is released under the **MIT License**.

See [`LICENSE`](LICENSE) for the complete license text.

---

# 👨‍💻 Author

**OmJee210306**

GitHub:
[https://github.com/OmJee210306](https://github.com/OmJee210306)

---

## ⭐ If you find this project useful

Consider giving the repository a ⭐ on GitHub.

Feedback, suggestions, and contributions are welcome.

---

> **FaceTune — Recognize the face. Play the vibe. 🎵**
