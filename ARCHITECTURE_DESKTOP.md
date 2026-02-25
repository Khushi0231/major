# DRAVIS Desktop - Technical Architecture

This document describes the architecture of the native desktop version of DRAVIS, designed for offline-first usage with zero technical setup requirements for the end-user.

## 1. System Components

### 1.1 Native Wrapper (Tauri v2)
- **Role**: Provides the desktop window, OS integration (file system, menus), and manages the lifecycle of the backend.
- **Frontend**: React 19 + Vite (built to static files).
- **Backend Wrapper**: Rust (manages process spawning and IPC).

### 1.2 Unified Backend (Sidecar)
- **DRAVIS Bridge**: A single compiled Python binary (`dravis-bridge.exe`) that manages all microservices.
- **Microservices**: Auth, Chat, Document, Quiz, and Speech services running as sub-processes.
- **Internal Gateway**: A local FastAPI proxy on port 8080 that routes requests from the frontend to the correct microservice.

### 1.3 Local Storage
- **Relational DB**: SQLite (replacing MySQL for zero-dependency portability).
- **Vector DB**: ChromaDB (running in Persistent Client mode).
- **File Storage**: `./uploads/` directory relative to the app data folder.

## 2. Process Lifecycle

1. **App Launch**: The user clicks `DRAVIS.exe`.
2. **Tauri Init**: The Rust process starts and immediately spawns `dravis-bridge.exe` as a sidecar.
3. **Bridge Init**: The bridge calls `multiprocessing.freeze_support()` and starts 6 sub-processes (5 services + 1 gateway).
4. **Data Verification**: The logic ensures SQLite databases and UPLOAD folders exist.
5. **App Ready**: The React UI connects to `localhost:8080`.

## 3. Deployment Flow

### 3.1 Build Phase
1. **Frontend Build**: `npm run build` generates `dist/`.
2. **Backend Compilation**: `PyInstaller` bundles the Python environment and microservices into a single `dravis-bridge.exe`.
3. **Rust Compilation**: `cargo tauri build` compiles the Rust wrapper and bundles the sidecar.
4. **Installer Generation**: Generates an `.exe` (Windows) or `.dmg` (Mac).

### 3.2 Installation Phase
- The user runs the installer.
- It places the binary and dependencies in the Applications folder.
- No Docker or Python installation is required on the user's system.

## 4. Key Improvements for Desktop
- **SQLite Support**: Zero configuration database.
- **Persistent Chroma**: Local semantic search indexed on disk.
- **Auto-Recovery**: If a sub-process fails, the Bridge can restart it.
- **No Internet Required**: All intelligence (Ollama excluded - must be present) happens on the local CPU/GPU.
