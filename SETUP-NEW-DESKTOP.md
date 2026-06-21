# Setting Up on a New Desktop

Do this once on any new machine. Takes about 2 minutes.

## 1. Clone the project
```powershell
git clone https://github.com/enzolim/lim-ai.git C:\Users\enzolim\lim-ai
```

## 2. Open Claude Code
Open the Claude Code desktop app and sign in with your account (hpjm.pt@gmail.com).

## 3. Set the working directory
Open this project folder in Claude Code: `C:\Users\enzolim\lim-ai`

## 4. Set up the daily schedule
Send this message to Claude:
> "Set up the daily AI news brief schedule to run at 9 AM — follow reference/ai-news-sop.md"

Claude will recreate the scheduled task on this machine in seconds.

## 5. Done
The brief will now run on this desktop at 9 AM whenever Claude Code is open.
Files automatically sync via GitHub — you won't miss any days from other desktops.

---

## How sync works
- Before each run: `git pull` fetches any briefs written on other desktops
- After each run: `git push` sends today's brief to GitHub
- You always have the full archive on every machine
