# Smiota Common Model (`smiota-common-model`)

A shared Java library containing common models, DTOs, database entities, and request/response payloads used across the Smiota platform.

> [!NOTE]
> This library does **not** run a web server or handle HTTP requests. It provides the shared Java classes and data models that other Smiota projects import and use.

---

## 🎯 Why This Library?

Different Smiota applications—the main server, AI agents, mobile apps, and web portals—need to exchange the same information (like packages, lockers, and users).

Instead of recreating the same models in every project, this library keeps them all in one place:

- **Single Source of Truth**: Changes to a package, locker, or user model happen in one place so all services stay in sync.
- **Tailored for Each App**: Different clients get models suited to their needs:
  - **AI / MCP Agents**: Short, token-efficient context.
  - **Mobile Apps**: Quick status checks, PINs, and QR codes.
  - **Web Admin**: Full logs, hardware telemetry, and diagnostics.
  - **Public Tracking**: Clean, safe details with personal info removed.
- **Lightweight**: Only includes essential annotations (`jakarta.persistence` and Jackson), without pulling in heavy frameworks like Spring Web or Hibernate.
- **Modern & Robust**: Built with **Java 17** and standard **Maven** for reliable, predictable builds.

---

## 📂 Project Structure

```
smiota-common-model/
│
├── .gitignore
├── pom.xml
├── build.bat       # Quick build & install script for Windows CMD
├── build.ps1       # Quick build & install script for PowerShell
├── README.md
│
└── src/
    └── main/
        └── java/
            └── com/
                └── smiota/
                    └── common/
                        ├── constants/      # Shared constants (date formats, error codes, regex)
                        ├── entities/       # Shared JPA entity models & mappings
                        ├── enums/          # Status codes, delivery types, roles
                        ├── dto/            # Data Transfer Objects organized by domain
                        │   ├── package/    # Package models across AI, mobile, web, and public
                        │   ├── locker/     # Locker unit, telemetry, and availability models
                        │   └── user/       # User profile and recipient contact models
                        ├── request/        # Command / action payloads (e.g. open door, reserve)
                        └── response/       # Standardized API response envelopes & pagination
```

---

## 🛠 Tech Stack & Dependencies

| Tool / Dependency | Version | Purpose |
| :--- | :--- | :--- |
| **Java** | 17 | Modern LTS runtime & bytecode target |
| **Maven** | 3.9+ | Build and dependency management |
| **Jakarta Persistence API** | `3.1.0` | JPA annotations (`@Entity`, `@Table`, `@Id`, etc.) |
| **Jackson Annotations & Databind** | `2.15.2` | JSON serialization/deserialization control |

---

## 🚀 Build & Local Publishing

### Quick Script (One-Click)

- **Command Prompt (CMD)**: Double-click or run:
  ```cmd
  build.bat
  ```
- **PowerShell**:
  ```powershell
  .\build.ps1
  ```

### Or using Maven CLI directly:

- **Compile & Package JAR**:
  ```bash
  mvn clean package
  ```
- **Install into Local Maven Cache (`~/.m2/repository`)**:
  ```bash
  mvn clean install
  ```
