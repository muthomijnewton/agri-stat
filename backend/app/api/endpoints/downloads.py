from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from app.models.models import User
from app.core.security import get_current_user

router = APIRouter(prefix="/api/downloads", tags=["downloads"])

# Path to the Flutter APK built by `flutter build apk --release`
APK_PATH = (
    Path(__file__).resolve().parents[4]
    / "mobile"
    / "build"
    / "app"
    / "outputs"
    / "flutter-apk"
    / "app-release.apk"
)


@router.get("/apk", summary="Download the Android APK")
def download_apk(_: User = Depends(get_current_user)):
    """Serve the pre-built Android APK for download."""
    if not APK_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="APK not yet built. Run 'flutter build apk --release' first.",
        )
    return FileResponse(
        APK_PATH,
        media_type="application/vnd.android.package-archive",
        filename="AgriStat.apk",
    )
