from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter(prefix="/downloads", tags=["downloads"])

APK_PATH = Path(__file__).resolve().parents[4] / "mobile" / "build" / "app" / "outputs" / "flutter-apk" / "app-release.apk"

@router.get("/apk")
def download_apk():
    if not APK_PATH.exists():
        raise HTTPException(status_code=404, detail="APK not found")
    return FileResponse(APK_PATH, media_type="application/vnd.android.package-archive", filename="AgriStat.apk")
