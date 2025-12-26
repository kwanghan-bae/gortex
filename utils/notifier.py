import json
import logging
import os
import urllib.request

logger = logging.getLogger("GortexNotifier")

class Notifier:
    """
    Webhook을 사용하여 Slack 또는 Discord로 알림을 보내는 시스템.
    """
    def __init__(self):
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
        self.discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")

    def send_notification(self, message: str, title: str = "🚀 Gortex Notification"):
        """모든 설정된 채널로 알림 전송"""
        if self.slack_webhook:
            self._send_to_slack(message, title)
        if self.discord_webhook:
            self._send_to_discord(message, title)
        
        if not self.slack_webhook and not self.discord_webhook:
            logger.info("Notification skipped: No webhooks configured.")

    def _send_to_slack(self, message: str, title: str):
        payload = {
            "text": f"*{title}*\n{message}"
        }
        self._post_webhook(self.slack_webhook, payload)

    def _send_to_discord(self, message: str, title: str):
        payload = {
            "content": f"**{title}**\n{message}"
        }
        self._post_webhook(self.discord_webhook, payload)

    def _post_webhook(self, url: str, payload: dict):
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                url, data=data, 
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req):
                pass
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

if __name__ == "__main__":
    n = Notifier()
    n.send_notification("Test")
