import os
from dataclasses import dataclass
from time import monotonic


@dataclass(frozen=True)
class QRScanResult:
    success: bool
    data: str
    error: str = ""


class QRScannerService:
    def __init__(self, camera_index: int = 0, timeout_seconds: float = 2.0) -> None:
        self.camera_index = camera_index
        self.timeout_seconds = max(1.0, timeout_seconds)

    def scan(self) -> QRScanResult:
        try:
            import cv2
        except ImportError:
            return QRScanResult(
                success=False,
                data="",
                error="OpenCV no esta instalado. Ejecuta: python3 -m pip install opencv-python",
            )

        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            return QRScanResult(
                success=False,
                data="",
                error=f"No se pudo abrir la camara (index={self.camera_index}).",
            )

        detector = cv2.QRCodeDetector()
        start = monotonic()

        try:
            while monotonic() - start < self.timeout_seconds:
                ok, frame = cap.read()
                if not ok:
                    continue

                data, _, _ = detector.detectAndDecode(frame)
                if data:
                    return QRScanResult(success=True, data=data.strip())
        finally:
            cap.release()
            if os.getenv("DISPLAY"):
                try:
                    cv2.destroyAllWindows()
                except Exception:
                    pass

        return QRScanResult(
            success=False,
            data="",
            error="No se detecto ningun QR dentro del tiempo limite.",
        )
