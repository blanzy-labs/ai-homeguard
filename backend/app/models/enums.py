from enum import Enum


class FindingStatus(str, Enum):
    GOOD = "good"
    REVIEW = "review"
    FIX_SOON = "fix_soon"
    NEEDS_ATTENTION = "needs_attention"
    UNABLE_TO_CHECK = "unable_to_check"


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    ADVANCED = "advanced"


class Platform(str, Enum):
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    NETWORK = "network"
    ROUTER = "router"
    CROSS_PLATFORM = "cross_platform"
    QUESTIONNAIRE = "questionnaire"
    SAFETY = "safety"
    UNKNOWN = "unknown"


class Category(str, Enum):
    DEVICE_POSTURE = "device_posture"
    NETWORK_AWARENESS = "network_awareness"
    IDENTITY_ACCESS = "identity_access"
    DATA_PROTECTION = "data_protection"
    UPDATES = "updates"
    MALWARE_PROTECTION = "malware_protection"
    BACKUP_RECOVERY = "backup_recovery"
    PRIVACY = "privacy"
    QUESTIONNAIRE = "questionnaire"
    SAFETY = "safety"


class D3FENDGuidanceCategory(str, Enum):
    HARDEN = "harden"
    DETECT = "detect"
    ISOLATE = "isolate"
    RECOVER = "recover"
    EDUCATE = "educate"
    OUT_OF_SCOPE = "out_of_scope"


class ReportMode(str, Enum):
    DEMO = "demo"
    LOCAL = "local"
    COMBINED = "combined"
