from app.models.enums import Confidence
from app.models.network_discovery import DeviceTypeGuess, DiscoveryMethod


def classify_device_type(*, is_gateway: bool, source_methods: list[DiscoveryMethod]) -> DeviceTypeGuess:
    if is_gateway:
        return DeviceTypeGuess.ROUTER
    return DeviceTypeGuess.UNKNOWN


def classify_device_confidence(*, is_gateway: bool, source_methods: list[DiscoveryMethod]) -> Confidence:
    if is_gateway and source_methods:
        return Confidence.HIGH
    if DiscoveryMethod.PRIVATE_PING in source_methods and DiscoveryMethod.PASSIVE_CACHE in source_methods:
        return Confidence.HIGH
    if DiscoveryMethod.PRIVATE_PING in source_methods:
        return Confidence.MEDIUM
    if DiscoveryMethod.PASSIVE_CACHE in source_methods:
        return Confidence.MEDIUM
    return Confidence.UNKNOWN


def device_needs_review(*, is_gateway: bool, device_type: DeviceTypeGuess) -> bool:
    if is_gateway:
        return False
    return device_type == DeviceTypeGuess.UNKNOWN
