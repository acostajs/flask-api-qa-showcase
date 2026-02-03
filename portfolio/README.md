# 📁 Portfolio Folder

## Purpose

This folder contains curated project metadata and assets used by my personal portfolio website. The data is fetched dynamically via GitHub's Contents API to showcase detailed project information and screenshots.

## Structure

portfolio/
├── portfolio.json # Project details (title, description, tech stack)
├── portfolio-img-1.avif # Screenshot 1 (optimized AVIF format)
├── portfolio-img-2.avif # Screenshot 2 (optional)
└── README.md # This file

## portfolio.json Format

{
“title”: “Project Name”,
“description”: “Full project description in HTML…”,
“technologies”: “React”, “Django”, “TypeScript”
}

## Why on main branch?

- **Dynamic updates**: Portfolio reflects latest project state without manual sync
- **GitHub Pages compatible**: Works with `?ref=main` API calls
- **Single source of truth**: Project info lives with the code
- **Version controlled**: All assets tracked with git history

## How it works

My portfolio site makes **one API call** to:

GET /repos/{userName}/{repoName}/contents/portfolio?ref=main

- Discovers all files in folder
- Fetches `portfolio.json` for project details
- Uses `portfolio-img-*.avif` for screenshots

**No backend needed** - pure GitHub API + static hosting.
