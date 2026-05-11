import time
import structlog
from typing import Optional, Tuple
from app.services.ai.fal_client import FalClient
from app.services.ai.replicate_client import ReplicateClient

logger = structlog.get_logger()


class AIRouter:
    """
    AI Service Router with circuit breaker pattern.

    Strategy:
    1. Primary: fal.ai (IDM-VTON / CatVTON)
    2. Fallback: Replicate (Kolors VTON)
    3. Circuit breaker: if fal fails 5x in 1min, bypass for 5min
    """

    def __init__(self):
        self.fal = FalClient()
        self.replicate = ReplicateClient()
        self._failure_count = 0
        self._last_failure_time = 0
        self._circuit_open = False
        self._circuit_open_time = 0
        self._failure_threshold = 5
        self._circuit_reset_seconds = 300  # 5 minutes
        self._failure_window_seconds = 60

    async def generate_tryon(
        self,
        model_photo: str,
        garment_image: str,
        category: str = "upper_body",
        steps: int = 30,
        seed: Optional[int] = None,
    ) -> Tuple[Optional[str], str]:
        """
        Generate a try-on, routing to appropriate service.
        Returns (result_url, provider_name).
        """
        # Check circuit breaker
        if self._is_circuit_open():
            logger.info("ai_router.circuit_open", reason="fal_failures")

            # Try fallback directly
            result = await self.replicate.generate_tryon(model_photo, garment_image, category)
            if result:
                return result, "replicate"
            return None, "none"

        # Try primary (fal.ai)
        result = await self.fal.generate_tryon(
            model_photo_url=model_photo,
            garment_image_url=garment_image,
            category=category,
            steps=steps,
            seed=seed,
        )

        if result:
            self._record_success()
            return result, "fal"

        # fal.ai failed — record failure
        self._record_failure()

        # Try fallback (Replicate)
        logger.info("ai_router.fallback", provider="replicate")
        result = await self.replicate.generate_tryon(model_photo, garment_image, category)
        if result:
            return result, "replicate"

        return None, "none"

    def _record_failure(self):
        now = time.time()
        if now - self._last_failure_time > self._failure_window_seconds:
            self._failure_count = 0
        self._failure_count += 1
        self._last_failure_time = now

        if self._failure_count >= self._failure_threshold:
            self._circuit_open = True
            self._circuit_open_time = now
            logger.warning("ai_router.circuit_breaker_open", failures=self._failure_count)

    def _record_success(self):
        self._failure_count = 0
        self._circuit_open = False

    def _is_circuit_open(self) -> bool:
        if not self._circuit_open:
            return False
        if time.time() - self._circuit_open_time > self._circuit_reset_seconds:
            self._circuit_open = False
            self._failure_count = 0
            return False
        return True
