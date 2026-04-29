import unittest

from thingspeak_client import ChannelConfig, ThingSpeakClient, chart_payload, extract_field_labels


class ThingSpeakClientTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ThingSpeakClient()
        self.config = ChannelConfig(channel_id=12397, read_api_key="READKEY", write_api_key="WRITEKEY", results=10)

    def test_build_feed_url(self) -> None:
        expected = "https://api.thingspeak.com/channels/12397/feeds.json?results=10&api_key=READKEY"
        self.assertEqual(self.client.build_feed_url(self.config), expected)

    def test_build_status_url(self) -> None:
        expected = "https://api.thingspeak.com/channels/12397/status.json?results=10&api_key=READKEY"
        self.assertEqual(self.client.build_status_url(self.config), expected)

    def test_extract_field_labels(self) -> None:
        labels = extract_field_labels(
            {
                "channel": {
                    "field1": "Temperatura",
                    "field2": "Humedad",
                }
            }
        )
        self.assertEqual(labels, [{"key": "field1", "label": "Temperatura"}, {"key": "field2", "label": "Humedad"}])

    def test_chart_payload_ignores_non_numeric_values(self) -> None:
        charts = chart_payload(
            [
                {"created_at": "2026-04-29T10:00:00Z", "field1": "20.5"},
                {"created_at": "2026-04-29T10:01:00Z", "field1": "abc"},
            ],
            [{"key": "field1", "label": "Temperatura"}],
        )
        self.assertEqual(charts[0]["data"], [20.5, None])


if __name__ == "__main__":
    unittest.main()
