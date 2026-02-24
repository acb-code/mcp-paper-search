This is a template and example for an mcp server with filesystem access.

It's set up to search through a local folder of pdf files - papers - and provide back info.

We're designing this to be able to host it locally and then connect via chatgpt developer mode.

To do this we're using ngrok. You need to go to ngrok.com and set up a free account. In the menu dropdown there we will be using the auth token.

For WSL/linux - `sudo snap install ngrok`, `ngrok config add-authtoken YOUR_TOKEN`



We're running the mcp server via docker:

The settings are configured in the docker compose yml

The Dockerfile defines the commands run

simple to run as `docker compose up --build` in the base directory `mcp-paper-search`

Actual mcp tools and fastmcp setup is in `app/server.py`

Once this is running in one terminal, open another to set up the http/s to expose:

`ngrok http 8000 --host-header=rewrite`
You'll get a free forwarding url: e.g., something like `https://nonsanguine-greetingly-hayden.ngrok-free.dev`and 

Then in chatgpt, need to go in the browser to settings, apps, advanced settings, and toggle on developer mode.

Then add an app, use the ngrok url with add `/mcp` at the end, and select no auth for this simple test.


