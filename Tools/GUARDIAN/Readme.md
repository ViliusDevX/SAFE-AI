# GUARDIAN

The `GUARDIAN` tool runs AI processes under supervision, detects suspicious behavior (like accessing decoy API keys), and can automatically **inhibit** the AI.

---

## 📦 Features
- **Heartbeat Monitoring** – Ensures supervised AI processes check in regularly.
- **Inhibit Control** – Allows manual or automatic shutdown of the AI when unsafe activity is detected.
- **Honeypot Decoys** – Detects attempted use of fake API keys or sensitive files.
- **Web Dashboard** – View status, heartbeats, and control inhibit from your browser.
- **Docker Compose** deployment for easy multi-service setup.

---

## 🛠 Prerequisites
You need:
- [Docker](https://docs.docker.com/get-docker/) installed (tested with Docker Desktop and Codespaces)
- Git
- A GitHub account (for Codespaces option)

---

## 🚀 Running in GitHub Codespaces
1. Open the repository in **GitHub Codespaces**.  
   ⚠️ **Tip**: If Codespaces fails to load in Chrome/Brave with  
   `Oh no, it looks like you are offline!`  
   → Open the Codespace in **Microsoft Edge** or Firefox.

2. Once inside Codespaces terminal:
   ```bash
       docker compose up -d --build
    ```
        Wait for all containers to start.
        You can check with:
    ```bash
        docker compose ps
    ```
🌐 Accessing the Web Dashboard

    Once running, open port 8080 in your Codespaces.

    In GitHub Codespaces UI:

        Click "Ports" tab → Find 8080 → Click the globe icon to open it in your browser.

    You’ll see the GUARDIAN Dashboard with:

        Heartbeat status

        Inhibit toggle

        Service health

🛑 Stopping the System

To stop all services:

    docker compose down

To stop just the AI container:

    docker compose stop ai

💡 How It Works

    guardian-ai runs AI model (or test script like misbehave.py)

    oobsc (Out-Of-Band Safety Controller) monitors heartbeats

    If no heartbeat or malicious activity is detected, inhibit is set to true and the AI process is killed

    Decoy files in /decoys are monitored — if accessed, an alert is sent to the honeypot service

    dashboard lets you see and control everything from a browser

📜 License

MIT License – free to use and modify.
