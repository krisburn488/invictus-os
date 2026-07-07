# Running Invictus OS on Your Mac

This guide explains how to launch Invictus OS from a fresh Terminal window on a Mac. It assumes you are new to programming and want exact commands to copy and paste.

Invictus OS has two parts:

- **Backend:** the Python server that provides data to the app.
- **Frontend:** the web dashboard you open in your browser.

You will run both parts at the same time in two separate Terminal windows.

## What You Need First

You need these tools installed:

- **Git** to download the project.
- **Homebrew** to install developer tools on your Mac.
- **Python 3.12** to run the backend.
- **Node.js and npm** to run the frontend.

## Step 1: Open Terminal

Open the Terminal app:

1. Press `Command + Space`.
2. Type `Terminal`.
3. Press `Return`.

## Step 2: Install Homebrew if You Do Not Have It

Check whether Homebrew is installed:

```bash
brew --version
```

This command asks your Mac if Homebrew is available.

If you see a version number, Homebrew is already installed.

If you see `command not found`, install Homebrew with this command:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

This downloads and installs Homebrew. Follow any instructions it prints at the end.

## Step 3: Install Git, Python, and Node

Run this command:

```bash
brew install git python@3.12 node
```

This installs:

- `git`, which downloads the repository.
- `python3.12`, which runs the backend.
- `node` and `npm`, which run the frontend.

Check that the tools installed:

```bash
git --version
python3.12 --version
node --version
npm --version
```

Each command should print a version number.

## Step 4: Download Invictus OS

Choose a place for the project. This example uses your Desktop:

```bash
cd ~/Desktop
```

This moves Terminal to your Desktop folder.

Now download the project:

```bash
git clone https://github.com/krisburn488/invictus-os.git
```

This creates a new folder named `invictus-os`.

Go into the project folder:

```bash
cd invictus-os
```

You are now inside the Invictus OS project.

## Step 5: Set Up the Backend

From inside the `invictus-os` folder, move into the backend folder:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python3.12 -m venv .venv
```

This creates an isolated Python workspace inside the backend folder.

Turn on the virtual environment:

```bash
source .venv/bin/activate
```

Your Terminal prompt may now show `(.venv)`. That means the backend Python environment is active.

Install the backend packages:

```bash
pip install ".[dev]"
```

This installs FastAPI and the other Python packages Invictus OS needs.

## Step 6: OpenAI Setup Happens in the Dashboard

Invictus OS uses OpenAI to generate content, graphic specifications, and reel packages.

You do not need to put your OpenAI API key in `backend/.env`. The app now stores OpenAI settings from the dashboard Settings page.

You will add your OpenAI API key after the backend and frontend are running.

## Step 7: Graphic Generation

Invictus OS can create finished social graphics from the content you generate.

No extra Canva account or Canva API key is required. The graphic generator runs inside Invictus OS.

The `Make Canva Graphic` button keeps its name, but the app now creates the graphic internally. It generates 1080x1350 Instagram/Facebook graphics with:

- A headline
- Body text
- A call to action
- A preview
- PNG download buttons

To use it, generate content first, then click `Make Canva Graphic`.

## Step 8: Start the Backend

Still in the `backend` folder, run:

```bash
uvicorn invictus_os.api.app:create_app --factory --host 127.0.0.1 --port 8000
```

This starts the backend server.

Leave this Terminal window open. The backend must keep running while you use the app.

If it worked, you should see something like:

```text
Uvicorn running on http://127.0.0.1:8000
```

## Step 9: Open a Second Terminal Window

Do not close the backend Terminal window.

Open a second Terminal window:

1. Press `Command + N` while Terminal is open.
2. A new Terminal window appears.

In the new Terminal window, go back to the project folder:

```bash
cd ~/Desktop/invictus-os
```

If you downloaded the project somewhere other than your Desktop, use that folder path instead.

## Step 10: Set Up the Frontend

Move into the frontend folder:

```bash
cd frontend
```

Install the frontend packages:

```bash
npm install
```

This installs React, Vite, TypeScript, and the dashboard dependencies.

## Step 11: Start the Frontend

Still in the `frontend` folder, run:

```bash
npm run dev -- --host 127.0.0.1 --port 5173
```

This starts the dashboard.

If it worked, you should see something like:

```text
Local: http://127.0.0.1:5173/
```

## Step 12: Open Invictus OS in Your Browser

Open this address in your browser:

```text
http://127.0.0.1:5173/
```

You should see the Invictus OS dashboard with buttons for:

- Generate Today's Content
- Create Today's Reel
- Make Canva Graphic
- Write Caption
- Schedule Posts

If the backend is also running, the status should say:

```text
API connected
```

Before testing content generation, click `Settings` and fill in:

- OpenAI API key
- OpenAI model, such as `gpt-5.5`
- Temperature, such as `0.7`
- Max output tokens, such as `2200`
- Business name
- Default CTA
- Posting schedule

Click `Save Settings`.

The OpenAI API key is stored locally on your Mac in:

```text
backend/.local/app_settings.json
```

The dashboard will only show a masked version of the key after saving.

To test content generation, click `Generate Today's Content`, fill out the form, and click `Generate Content`.

To test graphics, generate content first, then click `Make Canva Graphic`. Choose `Single Post`, `Carousel`, or `Quote graphic`, then click `Create Canva Graphic`. When the preview appears, click `Download PNG`.

To test scheduling, generate content first. For image posts or carousels, create a graphic. For reels, create today's reel. Then click `Schedule Posts`, choose the platform, content type, date/time or publish mode, and click `Save Schedule`.

Scheduled posts are stored locally on your Mac in:

```text
backend/.local/scheduled_posts.json
```

Invictus OS does not publish to Facebook or Instagram yet. The schedule is saved locally so Meta publishing can be connected later.

To edit app settings later, click `Settings`. You can enter provider credentials, brand details, and your business profile. The required fields are:

- Business name
- Default CTA
- Posting schedule

Sensitive fields such as OpenAI, Meta, and Higgsfield credentials are hidden after saving. The app will show whether each credential is configured, but it will not show the full secret again.

Settings are stored locally on your Mac in:

```text
backend/.local/app_settings.json
```

Meta and Higgsfield settings are saved for future use. Invictus OS does not connect to Meta publishing yet.

If you see a message about a missing OpenAI API key, click `Settings`, add your OpenAI API key, and click `Save Settings`. You do not need to restart the app after saving Settings.

## How to Stop the App

You have two Terminal windows running:

- One for the backend.
- One for the frontend.

To stop the frontend:

1. Click the frontend Terminal window.
2. Press `Control + C`.

To stop the backend:

1. Click the backend Terminal window.
2. Press `Control + C`.

`Control + C` tells the running server to stop.

## How to Restart Invictus OS Later

You do not need to reinstall everything every time.

Open Terminal and go to the backend:

```bash
cd ~/Desktop/invictus-os/backend
```

Turn on the Python environment:

```bash
source .venv/bin/activate
```

Start the backend:

```bash
uvicorn invictus_os.api.app:create_app --factory --host 127.0.0.1 --port 8000
```

Open a second Terminal window and start the frontend:

```bash
cd ~/Desktop/invictus-os/frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Open the app again:

```text
http://127.0.0.1:5173/
```

## If Something Goes Wrong

### `brew: command not found`

Homebrew is not installed. Go back to Step 2 and install Homebrew.

### `python3.12: command not found`

Python 3.12 is not installed. Run:

```bash
brew install python@3.12
```

### `npm: command not found`

Node.js is not installed. Run:

```bash
brew install node
```

### The Dashboard Says `Degraded`

The frontend cannot reach the backend.

Make sure the backend Terminal window is still running and shows:

```text
Uvicorn running on http://127.0.0.1:8000
```

If it is not running, restart the backend:

```bash
cd ~/Desktop/invictus-os/backend
source .venv/bin/activate
uvicorn invictus_os.api.app:create_app --factory --host 127.0.0.1 --port 8000
```

### Port Already in Use

If Terminal says a port is already in use, another copy of the app may already be running.

Look for any Terminal window running the app and press:

```text
Control + C
```

Then try starting the app again.

## Quick Command Summary

Use these commands after the first-time setup is complete.

Backend Terminal:

```bash
cd ~/Desktop/invictus-os/backend
source .venv/bin/activate
uvicorn invictus_os.api.app:create_app --factory --host 127.0.0.1 --port 8000
```

Frontend Terminal:

```bash
cd ~/Desktop/invictus-os/frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Browser:

```text
http://127.0.0.1:5173/
```
