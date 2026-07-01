from pydantic import BaseModel, Field

from app.models.enums import Category, D3FENDGuidanceCategory, Difficulty, Platform
from app.models.guidance import D3FENDGuidance

CATALOG_VERSION = "v0.1.0-guidance-catalog"
CATALOG_SOURCE_NOTE = (
    "Local curated D3FEND-informed educational catalog bundled with AI HomeGuard. "
    "No live MITRE or external data fetch is performed at runtime."
)
CATALOG_DISCLAIMER = (
    "This catalog is D3FEND-informed educational guidance, not official certification, "
    "not full D3FEND coverage, and not a guarantee of security."
)


class D3FENDCatalogEntry(BaseModel):
    guidance_id: str = Field(..., min_length=1)
    category: D3FENDGuidanceCategory
    defensive_concept: str = Field(..., min_length=1)
    home_action: str = Field(..., min_length=1)
    technical_action: str | None = None
    rationale: str = Field(..., min_length=1)
    difficulty: Difficulty
    estimated_time_minutes: int = Field(..., ge=1)
    applies_to_categories: list[Category] = Field(default_factory=list)
    applies_to_platforms: list[Platform] = Field(default_factory=list)
    requires_admin: bool = False
    educational_only: bool = True

    def to_guidance(self) -> D3FENDGuidance:
        return D3FENDGuidance(
            guidance_id=self.guidance_id,
            category=self.category,
            defensive_concept=self.defensive_concept,
            home_action=self.home_action,
            technical_action=self.technical_action,
            rationale=self.rationale,
            difficulty=self.difficulty,
            estimated_time_minutes=self.estimated_time_minutes,
            requires_admin=self.requires_admin,
            educational_only=self.educational_only,
        )


D3FEND_GUIDANCE_CATALOG: tuple[D3FENDCatalogEntry, ...] = (
    D3FENDCatalogEntry(
        guidance_id="enable_host_firewall",
        category=D3FENDGuidanceCategory.HARDEN,
        defensive_concept="Host Firewall",
        home_action="Keep the device firewall enabled.",
        technical_action="Enable the host firewall and review allowed inbound applications/services.",
        rationale="A firewall helps reduce unsolicited inbound access to local services.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=5,
        applies_to_categories=[Category.DEVICE_POSTURE, Category.NETWORK_AWARENESS],
        applies_to_platforms=[Platform.WINDOWS, Platform.MACOS, Platform.LINUX],
        requires_admin=True,
    ),
    D3FENDCatalogEntry(
        guidance_id="review_remote_access",
        category=D3FENDGuidanceCategory.HARDEN,
        defensive_concept="Remote Access Review",
        home_action="Turn off remote access services you do not use.",
        technical_action="Review RDP, SSH, VNC, WinRM, and remote administration services.",
        rationale="Remote access services are useful but increase exposure if left enabled unnecessarily.",
        difficulty=Difficulty.MEDIUM,
        estimated_time_minutes=10,
        applies_to_categories=[Category.IDENTITY_ACCESS, Category.DEVICE_POSTURE],
        applies_to_platforms=[Platform.WINDOWS, Platform.MACOS, Platform.LINUX],
        requires_admin=True,
    ),
    D3FENDCatalogEntry(
        guidance_id="strengthen_authentication",
        category=D3FENDGuidanceCategory.HARDEN,
        defensive_concept="Strong Authentication",
        home_action="Use strong unique passwords and MFA for important accounts.",
        technical_action="Enable MFA, reduce password reuse, and prefer key-based access for remote services.",
        rationale="Stronger authentication reduces the chance that stolen or guessed credentials can be reused.",
        difficulty=Difficulty.MEDIUM,
        estimated_time_minutes=15,
        applies_to_categories=[Category.IDENTITY_ACCESS],
        applies_to_platforms=[Platform.CROSS_PLATFORM, Platform.QUESTIONNAIRE, Platform.ROUTER],
    ),
    D3FENDCatalogEntry(
        guidance_id="enable_full_disk_encryption",
        category=D3FENDGuidanceCategory.HARDEN,
        defensive_concept="Full-Disk Encryption",
        home_action="Enable disk encryption and store the recovery key safely.",
        technical_action="Use BitLocker, FileVault, or appropriate Linux disk encryption where available.",
        rationale="Disk encryption helps protect files if a device is lost or stolen.",
        difficulty=Difficulty.MEDIUM,
        estimated_time_minutes=20,
        applies_to_categories=[Category.DATA_PROTECTION],
        applies_to_platforms=[Platform.WINDOWS, Platform.MACOS, Platform.LINUX],
        requires_admin=True,
    ),
    D3FENDCatalogEntry(
        guidance_id="keep_endpoint_protection_enabled",
        category=D3FENDGuidanceCategory.DETECT,
        defensive_concept="Endpoint Protection",
        home_action="Keep built-in malware protection enabled and up to date.",
        technical_action=(
            "Confirm Microsoft Defender, Gatekeeper, XProtect, or appropriate endpoint protection remains active."
        ),
        rationale="Endpoint protection can help detect or block known malicious software.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=5,
        applies_to_categories=[Category.MALWARE_PROTECTION],
        applies_to_platforms=[Platform.WINDOWS, Platform.MACOS, Platform.LINUX],
    ),
    D3FENDCatalogEntry(
        guidance_id="keep_system_updated",
        category=D3FENDGuidanceCategory.HARDEN,
        defensive_concept="Software Update Hygiene",
        home_action="Keep your operating system and apps updated.",
        technical_action="Enable automatic updates where appropriate and restart to complete installation.",
        rationale="Updates often close known security weaknesses and stability issues.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=10,
        applies_to_categories=[Category.UPDATES],
        applies_to_platforms=[Platform.WINDOWS, Platform.MACOS, Platform.LINUX, Platform.CROSS_PLATFORM],
    ),
    D3FENDCatalogEntry(
        guidance_id="identify_assets",
        category=D3FENDGuidanceCategory.DETECT,
        defensive_concept="Asset Identification",
        home_action="Know which devices are connected to your home network.",
        technical_action="Review router device lists and remove or investigate unknown devices.",
        rationale="You cannot protect devices you do not know about.",
        difficulty=Difficulty.EASY,
        estimated_time_minutes=10,
        applies_to_categories=[Category.NETWORK_AWARENESS],
        applies_to_platforms=[Platform.NETWORK, Platform.ROUTER, Platform.QUESTIONNAIRE],
        requires_admin=True,
    ),
    D3FENDCatalogEntry(
        guidance_id="isolate_untrusted_devices",
        category=D3FENDGuidanceCategory.ISOLATE,
        defensive_concept="Network Isolation",
        home_action="Put guest and smart-home devices on a guest Wi-Fi network where practical.",
        technical_action="Use guest Wi-Fi, VLANs, or router isolation features when available.",
        rationale="Separating less-trusted devices can reduce the impact if one device is compromised.",
        difficulty=Difficulty.MEDIUM,
        estimated_time_minutes=20,
        applies_to_categories=[Category.NETWORK_AWARENESS],
        applies_to_platforms=[Platform.NETWORK, Platform.ROUTER, Platform.QUESTIONNAIRE],
        requires_admin=True,
    ),
    D3FENDCatalogEntry(
        guidance_id="backup_important_data",
        category=D3FENDGuidanceCategory.RECOVER,
        defensive_concept="Data Backup",
        home_action="Back up important files and test restoring at least one file.",
        technical_action="Use a 3-2-1-style backup approach where practical.",
        rationale="Backups help recover from device failure, accidental deletion, theft, or ransomware.",
        difficulty=Difficulty.MEDIUM,
        estimated_time_minutes=30,
        applies_to_categories=[Category.BACKUP_RECOVERY],
        applies_to_platforms=[Platform.CROSS_PLATFORM, Platform.QUESTIONNAIRE],
    ),
    D3FENDCatalogEntry(
        guidance_id="reduce_admin_use",
        category=D3FENDGuidanceCategory.HARDEN,
        defensive_concept="Least Privilege",
        home_action="Avoid using an administrator account for everyday activity when practical.",
        technical_action="Review local administrator membership and use standard accounts for routine work.",
        rationale="Reducing administrator use can limit the impact of mistakes or malicious software.",
        difficulty=Difficulty.MEDIUM,
        estimated_time_minutes=15,
        applies_to_categories=[Category.IDENTITY_ACCESS, Category.DEVICE_POSTURE],
        applies_to_platforms=[Platform.WINDOWS, Platform.MACOS, Platform.LINUX],
        requires_admin=True,
    ),
    D3FENDCatalogEntry(
        guidance_id="review_router_admin",
        category=D3FENDGuidanceCategory.HARDEN,
        defensive_concept="Router Administration Hardening",
        home_action="Change default router admin credentials and disable remote administration if unused.",
        technical_action="Review router admin password, firmware, remote admin, and Wi-Fi security settings.",
        rationale="The router is the front door of many home networks.",
        difficulty=Difficulty.MEDIUM,
        estimated_time_minutes=20,
        applies_to_categories=[Category.IDENTITY_ACCESS, Category.NETWORK_AWARENESS],
        applies_to_platforms=[Platform.ROUTER, Platform.QUESTIONNAIRE],
        requires_admin=True,
    ),
    D3FENDCatalogEntry(
        guidance_id="review_local_services",
        category=D3FENDGuidanceCategory.DETECT,
        defensive_concept="Local Service Exposure Review",
        home_action="Review services listening on your device and turn off anything you do not use.",
        technical_action="Review listening ports such as RDP, SSH, SMB, VNC, WinRM, and local web services.",
        rationale="Unused listening services can increase the paths available for unwanted access.",
        difficulty=Difficulty.MEDIUM,
        estimated_time_minutes=15,
        applies_to_categories=[Category.DEVICE_POSTURE, Category.NETWORK_AWARENESS],
        applies_to_platforms=[Platform.WINDOWS, Platform.MACOS, Platform.LINUX],
        requires_admin=True,
    ),
)

CATALOG_BY_ID = {entry.guidance_id: entry for entry in D3FEND_GUIDANCE_CATALOG}
