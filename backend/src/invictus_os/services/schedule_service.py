from datetime import UTC, datetime
import json
from pathlib import Path
from uuid import uuid4

from pydantic import ValidationError

from invictus_os.config.settings import get_runtime_storage_dir
from invictus_os.schemas.schedule import (
    SchedulePostRequest,
    ScheduledPost,
    ScheduledPostStatus,
)


class ScheduleServiceError(Exception):
    message = "InvictusOS could not schedule the post."


class ScheduleStorageError(ScheduleServiceError):
    message = "InvictusOS could not read or write the local schedule history."


class LocalScheduleRepository:
    def __init__(self, storage_path: Path | None = None) -> None:
        self._storage_path = storage_path or get_runtime_storage_dir() / "scheduled_posts.json"

    def list_posts(self) -> list[ScheduledPost]:
        if not self._storage_path.exists():
            return []

        try:
            payload = json.loads(self._storage_path.read_text(encoding="utf-8"))
            if not isinstance(payload, list):
                raise ScheduleStorageError
            posts = [ScheduledPost.model_validate(item) for item in payload]
        except (OSError, json.JSONDecodeError, ValidationError) as exc:
            raise ScheduleStorageError from exc

        return sorted(posts, key=lambda post: post.created_at, reverse=True)

    def save_post(self, post: ScheduledPost) -> ScheduledPost:
        posts = self.list_posts()
        posts.insert(0, post)
        self._write_posts(posts)
        return post

    def _write_posts(self, posts: list[ScheduledPost]) -> None:
        try:
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            serialized = [json.loads(post.model_dump_json()) for post in posts]
            self._storage_path.write_text(
                json.dumps(serialized, indent=2) + "\n",
                encoding="utf-8",
            )
        except OSError as exc:
            raise ScheduleStorageError from exc


class ScheduleService:
    def __init__(self, repository: LocalScheduleRepository | None = None) -> None:
        self._repository = repository or LocalScheduleRepository()

    def list_posts(self) -> list[ScheduledPost]:
        return self._repository.list_posts()

    def schedule_post(self, request: SchedulePostRequest) -> ScheduledPost:
        now = datetime.now(UTC)
        post = ScheduledPost(
            id=str(uuid4()),
            platform=request.platform,
            content_type=request.content_type,
            status=resolve_status(request),
            scheduled_for=None if request.publish_now or request.draft_only else request.scheduled_for,
            created_at=now,
            updated_at=now,
            caption=request.content.caption,
            hashtags=request.content.hashtags,
            post_preview=build_post_preview(request),
            content=request.content,
            design=request.design,
            reel=request.reel,
        )
        return self._repository.save_post(post)


def resolve_status(request: SchedulePostRequest) -> ScheduledPostStatus:
    if request.draft_only:
        return "draft"
    if request.publish_now:
        return "ready_to_publish"
    return "scheduled"


def build_post_preview(request: SchedulePostRequest) -> str:
    if request.content_type == "reel" and request.reel:
        return request.reel.hook

    if request.design:
        slide_count = len(request.design.slides)
        asset_label = "carousel" if slide_count > 1 else "image"
        return f"{asset_label.title()} post with {slide_count} generated slide{'s' if slide_count != 1 else ''}."

    return request.content.post
