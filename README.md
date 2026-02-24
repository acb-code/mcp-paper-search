# MCP Paper Search (Local + ChatGPT Developer Mode)

This repo is a template/example MCP server with filesystem access.

It is set up to search a local paper archive (the `papers/` folder) and return content from files. The server is meant to run locally and be connected to ChatGPT in Developer Mode through `ngrok`.

## What this project does

- Runs an MCP server over HTTP on port `8000`
- Reads files from `./papers` (mounted read-only into the container as `/data`)
- Provides MCP tools implemented in [`app/server.py`](app/server.py)
- Supports `.pdf`, `.txt`, and `.md` files (PDF-focused workflow)

## Project structure

- [`docker-compose.yml`](docker-compose.yml): container config, port mapping, and `papers` volume mount
- [`Dockerfile`](Dockerfile): image build and run command
- [`app/server.py`](app/server.py): FastMCP server and tools

## Prerequisites

- Docker + Docker Compose
- An ngrok account (free tier is fine)

Install and configure ngrok (WSL/Linux example):

```bash
sudo snap install ngrok
ngrok config add-authtoken YOUR_TOKEN
```

## Run the server

From the repo root (`mcp-paper-search`):

```bash
docker compose up --build
```

The MCP server will start on `http://localhost:8000` and expose the MCP endpoint at `/mcp`.

## Expose local server with ngrok

In a second terminal:

```bash
ngrok http 8000 --host-header=rewrite
```

ngrok will give you a forwarding URL such as:

`https://example-subdomain.ngrok-free.dev`

Your MCP URL for ChatGPT will be:

`https://example-subdomain.ngrok-free.dev/mcp`

## Connect in ChatGPT Developer Mode

1. Open ChatGPT in your browser.
2. Go to `Settings` -> `Apps` -> `Advanced settings`.
3. Turn on `Developer mode`.
4. Add an app using your ngrok URL with `/mcp` appended.
5. For this simple local test setup, select `No auth`.

## Notes

- Keep your papers in the local `papers/` directory.
- The container reads that directory as `/data` via a read-only volume mount.
- This setup is intentionally simple for local development/testing.
