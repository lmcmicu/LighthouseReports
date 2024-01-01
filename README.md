Example crontab entries:
-

    27 */2 * * * find /home/mike/LighthouseReports -mindepth 1 -mtime +3 -name "lighthouse_*.json" -delete
    19 10 * * * nice -n 19 /home/mike/LighthouseReports/lighthouse_aeddan.py

For an overview of lighthouse see https://developer.chrome.com/docs/lighthouse/overview
