from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.network import NetworkAuthorization
from app.models.report import HomeGuardReport
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


@router.post("/reports/network-awareness", response_model=HomeGuardReport)
def read_network_awareness_report(authorization: NetworkAuthorization) -> HomeGuardReport:
    try:
        return run_network_awareness(authorization)
    except ValueError as error:
        detail = str(error)
        if detail not in {NETWORK_AUTHORIZATION_ERROR, NETWORK_SCOPE_ERROR}:
            detail = "Network awareness could not be started safely."
        raise HTTPException(status_code=400, detail=detail) from error
