# Vercel Deployment Guide

This guide explains the production Vercel setup for Invictus OS from a clean Vercel dashboard.

Invictus OS should be deployed as two separate Vercel projects from the same GitHub repository:

- `invictus-os-backend`
- `invictus-os-frontend`

Do not deploy the repository root as a production project. The repository root is a monorepo
container, not a runnable application.

## Projects To Delete

Delete every Vercel project that is not one of the two projects below.

Delete projects that:

- Point to the repository root.
- Were created during troubleshooting.
- Return `404_NOT_FOUND` or `404 DEPLOYMENT_NOT_FOUND`.
- Duplicate the frontend project.
- Duplicate the backend project.
- Have no clear root directory set to either `frontend` or `backend`.

## Projects To Keep

Keep exactly these two Vercel projects:

| Vercel project name | GitHub repository | Root directory | Purpose |
| --- | --- | --- | --- |
| `invictus-os-backend` | `krisburn488/invictus-os` | `backend` | FastAPI API |
| `invictus-os-frontend` | `krisburn488/invictus-os` | `frontend` | Vite dashboard |

## Deployment Order

Deploy the backend first.

After the backend deploys, copy its production URL. Use that exact URL as the frontend
`VITE_API_BASE_URL`.

Then deploy the frontend.

## Backend Project Settings

In Vercel, open the `invictus-os-backend` project.

Set these values:

| Setting | Value |
| --- | --- |
| Root Directory | `backend` |
| Framework Preset | Other |
| Build Command | Leave default unless Vercel fills it automatically |
| Output Directory | Leave empty |
| Install Command | Leave default unless Vercel fills it automatically |

The backend FastAPI entrypoint is configured in `backend/pyproject.toml`:

```toml
[tool.vercel]
entrypoint = "src.invictus_os.api.app:app"
```

The backend also includes `backend/vercel.json` and `backend/api/index.py` so Vercel creates a
Python serverless function for every API route when the project root is `backend`.

## Backend Environment Variables

Add these environment variables to the `invictus-os-backend` Vercel project.

| Name | Required | Value |
| --- | --- | --- |
| `OPENAI_API_KEY` | Yes | Your OpenAI project API key |
| `INVICTUS_CORS_ORIGIN_REGEX` | No | `https://.*\.vercel\.app` |
| `INVICTUS_CORS_ORIGINS` | No | JSON list of custom frontend domains |

For the normal Vercel production URL, no custom CORS variable is required because the backend
already allows Vercel app domains by default.

If you add a custom frontend domain later, set `INVICTUS_CORS_ORIGINS` to a JSON list like this:

```text
["https://www.your-domain.com","https://invictus-os-frontend.vercel.app"]
```

## Frontend Project Settings

In Vercel, open the `invictus-os-frontend` project.

Set these values:

| Setting | Value |
| --- | --- |
| Root Directory | `frontend` |
| Framework Preset | Vite |
| Build Command | `npm run build` |
| Output Directory | `dist` |
| Install Command | `npm install` |

The frontend Vercel behavior is configured in `frontend/vercel.json`.

## Frontend Environment Variables

Add this environment variable to the `invictus-os-frontend` Vercel project.

| Name | Required | Value |
| --- | --- | --- |
| `VITE_API_BASE_URL` | Yes | The deployed backend URL |

Use the exact backend production URL from the `invictus-os-backend` Vercel project.

Example:

```text
VITE_API_BASE_URL=https://invictus-os-backend.vercel.app
```

Do not add a trailing slash.

## Click-By-Click Backend Deployment

1. Open Vercel.
2. Click `Add New`.
3. Click `Project`.
4. Choose `krisburn488/invictus-os`.
5. Set the project name to `invictus-os-backend`.
6. Set `Root Directory` to `backend`.
7. Confirm the root directory change if Vercel asks.
8. Open `Environment Variables`.
9. Add `OPENAI_API_KEY`.
10. Click `Deploy`.
11. Wait for the deployment to finish.
12. Open the deployed backend URL.
13. Add `/health` to the end of the URL.
14. Confirm the browser shows a healthy API response.

The backend URL should look like this:

```text
https://invictus-os-backend.vercel.app
```

If Vercel gives the project a generated suffix, use the actual production URL Vercel shows.

## Click-By-Click Frontend Deployment

1. Open Vercel.
2. Click `Add New`.
3. Click `Project`.
4. Choose `krisburn488/invictus-os`.
5. Set the project name to `invictus-os-frontend`.
6. Set `Root Directory` to `frontend`.
7. Confirm the root directory change if Vercel asks.
8. Set `Framework Preset` to `Vite`.
9. Confirm `Build Command` is `npm run build`.
10. Confirm `Output Directory` is `dist`.
11. Open `Environment Variables`.
12. Add `VITE_API_BASE_URL`.
13. Set `VITE_API_BASE_URL` to the backend URL from the previous section.
14. Click `Deploy`.
15. Wait for the deployment to finish.
16. Open the frontend URL.

The frontend URL should look like this:

```text
https://invictus-os-frontend.vercel.app
```

If Vercel gives the project a generated suffix, use the actual production URL Vercel shows.

## Verify Frontend To Backend Communication

1. Open the frontend deployment URL.
2. Look at the status panel on the dashboard.
3. Confirm it says `API connected`.
4. If it does not, open the frontend Vercel project settings.
5. Confirm `VITE_API_BASE_URL` exactly matches the backend deployment URL.
6. Redeploy the frontend after changing `VITE_API_BASE_URL`.

## Verify Each Dashboard Workflow

Run these checks in order.

### Generate Today's Content

1. Click `Generate Today's Content`.
2. Fill in the form.
3. Click `Generate Content`.
4. Confirm generated content appears with sections for the post, caption, hashtags, and call to action.

### Create Today's Reel

1. Generate today's content first.
2. Click `Create Today's Reel`.
3. Select a reel format.
4. Confirm the reel package appears with hook, script, storyboard, voice-over, on-screen text, and download buttons.

### Make Canva Graphic

1. Generate today's content first.
2. Click `Make Canva Graphic`.
3. Choose Single Post, Carousel, or Quote Graphic.
4. Confirm a graphic preview appears.
5. Confirm the PNG download button works.

### Write Caption

1. Generate today's content first.
2. Click `Write Caption`.
3. Confirm the generated caption section is visible.
4. Use the caption copy button to confirm the caption can be copied.

### Schedule Posts

1. Generate content first.
2. Optionally generate a graphic or reel.
3. Click `Schedule Posts`.
4. Choose Facebook, Instagram, or both.
5. Choose image post, carousel, or reel.
6. Pick a date and time, choose publish now, or choose draft-only.
7. Click the schedule button.
8. Confirm the scheduled posts/history view shows the new item.

## Expected Production Behavior

- The frontend loads from the `invictus-os-frontend` project.
- The backend API responds from the `invictus-os-backend` project.
- The dashboard status says `API connected`.
- OpenAI-backed workflows work when `OPENAI_API_KEY` is configured on the backend project.
- Graphic generation and scheduling work through the backend API.
- Duplicate or root-level Vercel projects are not needed and should be deleted.
