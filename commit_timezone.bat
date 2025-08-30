@echo off
echo Committing timezone changes...
git add .
git commit -m "Fix timezone: Change from UTC to EST for better readability and local timezone alignment"
echo Pushing to GitHub...
git push origin main
echo Done!
pause
