# ♟️ CyberChess: Server-Side AI (Project A)

> A full-stack chess application featuring custom heuristic algorithms, server-side state management, and Optimistic UI rendering.

## 🚀 Live Demo
**[Click here to Play CyberChess](https://cyberchess-portfolio.onrender.com)**
*(Replace this link with your actual Render URL)*

## 💡 Overview
CyberChess is an engineering exploration into **game state persistence** and **latency management**. Unlike standard chess apps that rely on client-side libraries, this project implements the game logic entirely on the server using **Python**.

This architecture ensures move validation security and allows for complex custom AI heuristics that would be too heavy for a browser to calculate.

## 🛠️ Tech Stack
*   **Backend:** Python 3, Flask (REST API)
*   **Logic:** `python-chess` library + Custom Heuristic Algorithms
*   **Frontend:** HTML5, JavaScript (Fetch API), CSS3 (Responsive)
*   **Deployment:** Render (Gunicorn WSGI)

## 🧠 Engineering Highlights

### 1. Custom Heuristic AI
Instead of using a pre-compiled engine binary, I engineered a custom Python evaluation function that:
*   Prioritizes **Material Advantage** (capturing pieces).
*   Evaluates **Center Control** (controlling e4/d4 squares).
*   Executes **Randomized Fallback** strategies to prevent decision paralysis.

### 2. Optimistic UI Pattern
To combat server latency (RTT), the frontend utilizes **Optimistic UI updates**.
*   **Action:** The user moves a piece.
*   **Instant Feedback:** The UI updates immediately (0ms latency).
*   **Validation:** The move is sent to the backend asynchronously. If the server rejects it (illegal move), the UI rolls back the state automatically.

### 3. Stateless Session Management
The application uses a RESTful architecture where the client and server exchange Board FEN (Forsyth–Edwards Notation) strings, maintaining a lightweight, stateless connection ideal for cloud deployment.

## 📦 Installation (Local)
```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/CyberChess-Portfolio.git

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
python app.py
