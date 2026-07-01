from fastapi import APIRouter
from pydantic import BaseModel

from app.demo.device_inventory import get_demo_device_inventory_submission
from app.inventory.analyzer import analyze_device_inventory, build_device_inventory_report
from app.models.device_inventory import DeviceInventoryResult, DeviceInventorySubmission
from app.models.report import HomeGuardReport

router = APIRouter(prefix="/inventory", tags=["device inventory"])


class DeviceInventoryDemoResponse(BaseModel):
    submission: DeviceInventorySubmission
    result: DeviceInventoryResult
    report: HomeGuardReport


@router.get("/demo", response_model=DeviceInventoryDemoResponse)
def read_demo_device_inventory() -> DeviceInventoryDemoResponse:
    submission = get_demo_device_inventory_submission()
    return DeviceInventoryDemoResponse(
        submission=submission,
        result=analyze_device_inventory(submission),
        report=build_device_inventory_report(submission),
    )


@router.post("/analyze", response_model=DeviceInventoryResult)
def analyze_inventory(submission: DeviceInventorySubmission) -> DeviceInventoryResult:
    return analyze_device_inventory(submission)
