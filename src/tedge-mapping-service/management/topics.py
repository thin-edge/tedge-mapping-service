"""MQTT Topics"""


def health_topic(root_topic: str = "te", topic_id: str = "device/main//") -> str:
    """Health topic for the child device"""
    return "/".join(
        [
            root_topic,
            topic_id,
            "status",
            "health",
        ]
    )