import os
from dataclasses import dataclass
from time import monotonic


@dataclass(frozen=True)
class QRScanResult:
    success: bool
    data: str
    error: str = ""


class QRScannerService:
    def __init__(
        self,
        camera_index: int = 0,
        timeout_seconds: float = 2.0,
        image_path: str = "",
    ) -> None:
        self.camera_index = camera_index
        self.timeout_seconds = max(1.0, timeout_seconds)
        self.image_path = (image_path or "").strip()

    def scan(self) -> QRScanResult:
        try:
            import cv2
        except ImportError:
            return QRScanResult(
                success=False,
                data="",
                error="OpenCV no esta instalado. Ejecuta: python3 -m pip install opencv-python",
            )

        if self.image_path:
            return self._scan_from_image(cv2)

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

    def _scan_from_image(self, cv2) -> QRScanResult:
        if not os.path.exists(self.image_path):
            return QRScanResult(
                success=False,
                data="",
                error=f"No se encontro la imagen QR_IMAGE_PATH: {self.image_path}",
            )

        frame = cv2.imread(self.image_path)
        if frame is None:
            return QRScanResult(
                success=False,
                data="",
                error=f"No se pudo abrir la imagen para escanear: {self.image_path}",
            )

        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(frame)
        if data:
            return QRScanResult(success=True, data=data.strip())

        return QRScanResult(
            success=False,
            data="",
            error=f"No se detecto ningun QR en la imagen: {self.image_path}",
        )
