from pydantic import BaseModel, Field


class RouterGuidanceTopic(BaseModel):
    id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1)
    steps: list[str] = Field(default_factory=list)


class RouterGuidanceResponse(BaseModel):
    source_note: str
    safety_notes: list[str] = Field(default_factory=list)
    topics: list[RouterGuidanceTopic] = Field(default_factory=list)


ROUTER_GUIDANCE_SOURCE_NOTE = (
    "Generic, vendor-neutral router guidance. Router menus vary by manufacturer and ISP."
)

ROUTER_GUIDANCE_SAFETY_NOTES = [
    "AI HomeGuard does not log in to routers.",
    "Do not enter router passwords into AI HomeGuard.",
    "No router credentials are requested or collected.",
    "No scan, packet capture, exploit, bypass, or public target instruction is included.",
    "Use your router app or admin page as the source of truth for connected devices.",
]

ROUTER_GUIDANCE_TOPICS = [
    RouterGuidanceTopic(
        id="find-router-app",
        title="Find your router app or admin page",
        summary="Start with the app from your ISP/router maker or the router admin page documented by the vendor.",
        steps=[
            "Look for a connected-devices, clients, or devices section.",
            "Use your router or ISP documentation because menu names vary.",
            "Keep router passwords in your password manager, not in AI HomeGuard.",
        ],
    ),
    RouterGuidanceTopic(
        id="review-connected-devices",
        title="Review connected devices",
        summary="Compare your router device list with a simple household inventory.",
        steps=[
            "Mark devices you recognize, such as computers, phones, tablets, TVs, printers, and smart-home devices.",
            "Use generic labels when taking notes, such as family phone or smart TV.",
            "Avoid storing serial numbers, exact room locations, or personal names in AI HomeGuard.",
        ],
    ),
    RouterGuidanceTopic(
        id="identify-unknown-devices",
        title="Identify unknown devices",
        summary="Unknown devices are a reason to review calmly, not proof of compromise.",
        steps=[
            "Compare the router list against devices currently powered on in the home.",
            "Pause and identify devices before blocking anything important.",
            "If a device cannot be identified, consider removing it from Wi-Fi and changing the Wi-Fi password.",
        ],
    ),
    RouterGuidanceTopic(
        id="use-guest-wifi",
        title="Use guest Wi-Fi where practical",
        summary="Guest Wi-Fi can help separate visitor and smart-home devices from sensitive devices.",
        steps=[
            "Put visitor devices on guest Wi-Fi when available.",
            "Consider guest Wi-Fi or isolation for smart TVs, cameras, doorbells, speakers, and printers.",
            "Keep computers and phones that hold important accounts on the main trusted network.",
        ],
    ),
    RouterGuidanceTopic(
        id="router-admin-settings",
        title="Review router administration settings",
        summary="Basic router administration hygiene can reduce avoidable exposure.",
        steps=[
            "Disable router remote administration if you do not use it.",
            "Change the router admin password from the factory setting.",
            "Keep router firmware updated using the vendor or ISP-supported update path.",
        ],
    ),
    RouterGuidanceTopic(
        id="wifi-security",
        title="Prefer modern Wi-Fi security",
        summary="Use the strongest Wi-Fi security mode your router and devices support.",
        steps=[
            "Prefer WPA2 or WPA3 where available.",
            "Avoid sharing the main Wi-Fi password with guests.",
            "Use a long, unique Wi-Fi password and update it if an unknown device cannot be identified.",
        ],
    ),
    RouterGuidanceTopic(
        id="document-important-devices",
        title="Document important devices",
        summary="A simple inventory helps you spot changes in your router app over time.",
        steps=[
            "Track broad device type, trust level, update status, and whether the device is sensitive.",
            "Use privacy-safe labels and avoid personal names.",
            "Refresh the list when you add, replace, sell, or retire devices.",
        ],
    ),
]


def get_router_guidance() -> RouterGuidanceResponse:
    return RouterGuidanceResponse(
        source_note=ROUTER_GUIDANCE_SOURCE_NOTE,
        safety_notes=ROUTER_GUIDANCE_SAFETY_NOTES,
        topics=ROUTER_GUIDANCE_TOPICS,
    )
