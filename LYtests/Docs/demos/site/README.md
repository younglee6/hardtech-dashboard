# Hardtech Dashboard (GitHub Pages)

This folder is deployed to GitHub Pages by workflow.

## What is deployed
- `index.html`: dashboard page
- `hardtech-live-data.json`: live data consumed by page

## Auto update schedule
- Workflow: `Update Hardtech Live Data`
- Runs daily at **09:00 Asia/Shanghai** (cron `0 1 * * *` UTC)

## One-time repo settings
1. Go to `Settings -> Pages`
2. Under **Build and deployment**, choose **Source: GitHub Actions**
3. Go to `Settings -> Actions -> General`
   - Workflow permissions: **Read and write permissions**

## Manual run
- Actions -> `Update Hardtech Live Data` -> `Run workflow`
- Actions -> `Deploy Hardtech Dashboard to GitHub Pages` -> `Run workflow`

## URL
After first successful deploy:
`https://<your-github-username>.github.io/<repo-name>/`
