from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.network import NetworkAuthorization
from app.models.network_discovery import NetworkDiscoveryRequest, NetworkDiscoveryResult
from app.models.report import HomeGuardReport
from app.network.discovery import (
    DISCOVERY_ACTIVE_ERROR,
    DISCOVERY_AUTHORIZATION_ERROR,
    DISCOVERY_METHOD_ERROR,
    DISCOVERY_PRIVATE_ONLY_ERROR,
    DISCOVERY_SCOPE_ERROR,
    demo_network_discovery_result,
    run_network_discovery_report,
)
from app.network.runner import NETWORK_AUTHORIZATION_ERROR, NETWORK_SCOPE_ERROR, run_network_awareness

router = APIRouter(tags=["network awareness"])

NETWORK_AUTHORIZATION_STATEMENT = (
    "I confirm this is my own home network or a network I am authorized to assess. "
    "I understand this version uses passive local network context only."
)


class NetworkSafetyPolicy(BaseModel):
    authorization_statement: str
    allowed_scopes: list[str]
    disallowed_actions: list[str]
    private_network_only: str
    no_public_scanning: str
    no_active_scanning: str
    statement_version: str


class NetworkDiscoveryPolicy(BaseModel):
    authorization_required: bool
    authorization_statement: str
    allowed_scopes: list[str]
    allowed_methods: list[str]
    private_network_only: str
    no_public_scanning: str
    no_port_scanning: str
    no_router_login: str
    no_credentials: str
    no_packet_capture: str
    no_nmap: str
    statement_version: str


@router.get("/network/safety-policy", response_model=NetworkSafetyPolicy)
def read_network_safety_policy() -> NetworkSafetyPolicy:
    return NetworkSafetyPolicy(
        authorization_statement=NETWORK_AUTHORIZATION_STATEMENT,
        allowed_scopes=["home_network", "demo"],
        disallowed_actions=[
            "active discovery",
            "Nmap",
            "ping sweeps",
            "port scanning",
            "packet capture",
            "router login",
            "credential testing",
            "public target scanning",
        ],
        private_network_only="Future discovery features must be limited to private/local ranges.",
        no_public_scanning="AI HomeGuard does not support public target scanning.",
        no_active_scanning="This version performs passive local network awareness only.",
        statement_version="v0.1.0-network-awareness",
    )


@router.get("/network/discovery-policy", response_model=NetworkDiscoveryPolicy)
def read_network_discovery_policy() -> NetworkDiscoveryPolicy:
    return NetworkDiscoveryPolicy(
        authorization_required=True,
        authorization_statement=(
            "Only run device discovery on your own home network or one you are authorized to check."
        ),
        allowed_scopes=["home_network"],
        allowed_methods=["passive_cache", "combined"],
        private_network_only="HomeGuard checks private RFC1918 IPv4 addresses only.",
        no_public_scanning="No public targets are scanned.",
        no_port_scanning="No ports are scanned.",
        no_router_login="No router login is attempted.",
        no_credentials="No passwords or credentials are requested, collected, or tested.",
        no_packet_capture="No packet capture is performed.",
        no_nmap="Nmap is not used.",
        statement_version="v0.1.0-slice-14",
    )


@router.get("/network/discovery/demo", response_model=NetworkDiscoveryResult)
def read_network_discovery_demo() -> NetworkDiscoveryResult:
    return demo_network_discovery_result()


@router.post("/reports/network-awareness", response_model=HomeGuardReport)
def read_network_awareness_report(authorization: NetworkAuthorization) -> HomeGuardReport:
    try:
        return run_network_awareness(authorization)
    except ValueError as error:
        detail = str(error)
        if detail not in {NETWORK_AUTHORIZATION_ERROR, NETWORK_SCOPE_ERROR}:
            detail = "Network awareness could not be started safely."
        raise HTTPException(status_code=400, detail=detail) from error


@router.post("/reports/network-discovery", response_model=HomeGuardReport)
def read_network_discovery_report(request: NetworkDiscoveryRequest) -> HomeGuardReport:
    try:
        return run_network_discovery_report(request)
    except ValueError as error:
        detail = str(error)
        if detail not in {
            DISCOVERY_AUTHORIZATION_ERROR,
            DISCOVERY_SCOPE_ERROR,
            DISCOVERY_PRIVATE_ONLY_ERROR,
            DISCOVERY_ACTIVE_ERROR,
            DISCOVERY_METHOD_ERROR,
        }:
            detail = "Network discovery could not be started safely."
        raise HTTPException(status_code=400, detail=detail) from error
