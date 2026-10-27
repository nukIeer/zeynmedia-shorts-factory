@echo off
rem Saves the GitHub token the hourly Cloudflare cron uses to start the video workflows.
cd /d "%~dp0.."
echo GitHub token'ini yapistir (ekranda gorunmeyebilir) ve Enter'a bas:
call npx --prefix ..\zeynmedia-studio wrangler secret put GH_DISPATCH_TOKEN --config cron\wrangler.jsonc
echo.
pause
