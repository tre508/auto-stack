# Freqtrade Installation Guide

**Status:** ✅ Rewritten for WSL Dev Container Workflow - 2025-05-23

---

## ⚠️ Important: Installation Method

This project provides a pre-configured and managed Freqtrade environment that runs inside a **VS Code Dev Container**.

**You must not install Freqtrade manually or using the scripts described in the official Freqtrade documentation.** Doing so will create an unsupported environment that will not integrate with the `automation-stack` and will conflict with the project's established workflow.

The **only supported method** for setting up and running Freqtrade for this project is through the provided Dev Container.

## Supported Setup Procedure

The setup for Freqtrade is handled almost entirely by Docker and the VS Code Dev Containers extension. The correct procedure is detailed in the primary project setup documents.

1.  **Prerequisites:** Ensure you have met all the prerequisites outlined in `docs/triage/00_MasterSetup.md`, including setting up WSL 2, Docker Desktop, and VS Code.

2.  **Follow the "Focused Workflow":** The Freqtrade environment must be launched correctly:
    *   Open a **WSL terminal**.
    *   Navigate to your `freqtrade` project directory (e.g., `cd ~/projects/freqtrade`).
    *   Run `code .` from within that directory.
    *   Once VS Code launches, use the Command Palette (`Ctrl+Shift+P`) to run the **"Dev Containers: Reopen in Container"** command.

3.  **Automatic Setup:** VS Code will now build the Docker image and start the dev container. This process automatically:
    *   Installs all necessary system dependencies (like TA-Lib).
    *   Sets up the correct Python environment.
    *   Installs all required Python packages.
    *   Mounts your local `user_data` directory into the container.

For more detailed context, please refer to:
*   **`docs/triage/00_MasterSetup.md`**
*   **`docs/triage/02_Trading.md`**

---

## Freqtrade Repository Branches

While the setup is automated, it's useful to know which branch of Freqtrade you are using.

When you first clone the repository, you are on the `develop` branch by default.

```bash
# Enter the project directory in WSL
cd ~/projects/freqtrade

# To switch to the stable branch (less frequent updates)
git checkout stable

# To switch back to the development branch (latest features)
git checkout develop
```

*   **`develop` branch:** Contains the latest features and is generally stable due to automated testing. This is recommended for most users of this project.
*   **`stable` branch:** Contains the code from the last official release. It is updated less frequently.

You can switch between branches at any time from your WSL terminal before starting the dev container. The container will use whichever branch is currently checked out.
