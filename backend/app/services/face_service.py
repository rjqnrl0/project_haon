import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import NotFoundError, ValidationError
from app.models.user import User
from app.services.file_manager import FileManagerService

logger = logging.getLogger("v-suitcase.face_service")


class FaceVerificationService:
    def __init__(self):
        self.file_manager = FileManagerService()
        self.settings = get_settings()
        self.similarity_threshold = 90

    async def register_face(
        self, user: User, image_bytes: bytes, content_type: str, db: AsyncSession
    ) -> dict:
        self.file_manager.validate_file(content_type, len(image_bytes))

        s3_key = self.file_manager.upload_file(
            user_id=str(user.id),
            task_id="face-registration",
            file_bytes=image_bytes,
            content_type=content_type,
            category="reference",
        )

        if user.face_s3_key:
            self.file_manager.delete_file(user.face_s3_key)

        user.face_s3_key = s3_key
        user.face_registered = True
        await db.flush()

        logger.info("Face registered for user %s", user.id)
        return {"registered": True, "message": "얼굴 등록이 완료되었습니다"}

    async def verify_face(
        self, user: User, image_bytes: bytes, content_type: str
    ) -> dict:
        if not user.face_registered or not user.face_s3_key:
            raise ValidationError("Face ID가 등록되지 않았습니다. 먼저 얼굴을 등록해주세요.")

        # Phase 1: Mock — always return verified
        # Phase 2: AWS Rekognition compareFaces
        similarity = 95.0
        verified = similarity >= self.similarity_threshold

        logger.info(
            "Face verification for user %s: similarity=%.1f, verified=%s",
            user.id, similarity, verified
        )

        return {
            "verified": verified,
            "similarity": similarity,
            "threshold": self.similarity_threshold,
        }
