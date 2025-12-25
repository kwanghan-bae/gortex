import os
import unittest
from unittest.mock import patch

from gortex.utils.notifier import Notifier

class TestNotifier(unittest.TestCase):
    @patch("gortex.utils.notifier.Notifier._post_webhook")
    def test_send_notification_targets_configured_webhooks(self, mock_post):
        env = {
            "SLACK_WEBHOOK_URL": "http://slack.test",
            "DISCORD_WEBHOOK_URL": "http://discord.test"
        }
        with patch.dict(os.environ, env, clear=True):
            notifier = Notifier()
            notifier.send_notification("body", "Title")

        self.assertEqual(mock_post.call_count, 2)
        mock_post.assert_any_call("http://slack.test", {"text": "*Title*\nbody"})
        mock_post.assert_any_call("http://discord.test", {"content": "**Title**\nbody"})

    def test_send_notification_skips_when_no_webhooks(self):
        with patch.dict(os.environ, {}, clear=True):
            notifier = Notifier()
            with self.assertLogs("GortexNotifier", level="INFO") as logs:
                notifier.send_notification("body")

        self.assertTrue(any("Notification skipped" in line for line in logs.output))

    @patch("gortex.utils.notifier.urllib.request.urlopen", side_effect=Exception("boom"))
    def test_post_webhook_logs_failure(self, mock_urlopen):
        notifier = Notifier()
        with self.assertLogs("GortexNotifier", level="ERROR") as logs:
            notifier._post_webhook("http://fail", {"foo": "bar"})

        self.assertTrue(any("Failed to send notification" in line for line in logs.output))
