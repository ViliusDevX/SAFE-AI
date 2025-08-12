# 🚀 GUARDIAN Project Roadmap

Basic roadmap of Guardian project.

## 📍 Current Stage – MVP (Minimum Viable Product)

    ✅ Multi-container architecture with oobsc, ai, dashboard, egress, and honeytoken.

    ✅ OOBSC heartbeat-based AI kill switch.

    ✅ Decoy file + honeytoken ingestion detection.

    ✅ GUI dashboard for monitoring.

    ✅ Working in GitHub Codespaces + Docker.

## 🔜 Short-Term Goals (1–2 months)

    Improve OOBSC Reliability

        Persistent heartbeat storage (avoid losing state on restart).

        Configurable heartbeat timeout via .env file.

        Better error handling for container restarts.

    Dashboard Enhancements

        Live updating heartbeat list without page refresh.

        Visual indicators for inhibit state.

        Manual override buttons with confirmation prompts.

    Better Developer Experience

        Full README with Codespaces, local, and server setup.

        One-command startup script for all platforms.

        Browser compatibility notes (Chrome/Edge).

    Safer Defaults

        Fail-closed on startup until heartbeat is detected.

        Auto-restart ai container only after manual approval.

## 📅 Mid-Term Goals (3–6 months)

    Threat Detection Expansion

        Multiple honeytoken file types (API keys, passwords, SSH).

        Network traffic pattern alerts.

        Suspicious command execution detection in AI runtime.

    Access Control

        Password-protected dashboard.

        Role-based access for viewing vs. controlling.

    Persistence & Logging

        Store incident logs in SQLite or PostgreSQL.

        Exportable incident reports (PDF/JSON).

    Better Notifications

        Email/Webhook alerts for incidents.

        Slack/Discord integration.

## 🎯 Long-Term Goals (6–12+ months)

    Cloud-Ready Deployment

        Helm chart for Kubernetes.

        AWS/GCP/Azure deployment templates.

    AI Model Guardrails

        Fine-grained policy enforcement (e.g., block specific API calls).

        Pre/post-processing pipelines for AI outputs.

    Advanced Detection

        Machine learning–based anomaly detection for AI behaviors.

        Real-time network interception & blocking.

    Compliance Features

        Logging and auditing for regulatory compliance (SOC2, GDPR).

        Data masking for sensitive outputs.

### 📌 Milestone Structure
    Milestone	Focus	ETA
    M1 – Stable MVP	Make current stack production-stable	1 month
    M2 – Usable Dashboard	Real-time UI + better UX	2 months
    M3 – Threat Expansion	More detection methods	4 months
    M4 – Cloud-Ready	Scalable deployments	8 months
    M5 – AI Guardrails	Policy-based AI controls	12+ months
