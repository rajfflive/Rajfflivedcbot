# 🤖 RAJFFLIVE BOT DC — Render Deployment

## 📁 File Structure
```
discord-bot/
├── main.py              # Entry point
├── config.py            # Reads env vars
├── database.py          # SQLite setup
├── render.yaml          # Render config
├── build.sh             # Installs ffmpeg
├── requirements.txt
├── .gitignore
└── cogs/
    ├── moderation.py
    ├── music.py
    ├── fun.py
    ├── custom_commands.py
    └── ai.py
```

## 🚀 Deploy Steps

### 1. Push to GitHub
1. Go to github.com/new → create a private repo
2. Extract this zip, open terminal in folder:
```bash
git init
git add .
git commit -m "Initial bot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 2. Create Render Service
1. Go to render.com → sign up
2. Click New → Background Worker
3. Connect GitHub → select your repo
4. Render auto-detects render.yaml

### 3. Add Environment Variables
In Render dashboard → Environment tab:

| Key | Value |
|-----|-------|
| DISCORD_TOKEN | your bot token |
| ANTHROPIC_API_KEY | your Anthropic key |
| COMMAND_PREFIX | ! |

### 4. Deploy!
Hit Deploy — done!

## ⚠️ Notes
- Free tier may sleep — use UptimeRobot to keep alive
- SQLite resets on redeploy on free tier
