from typing import NotRequired, TypedDict

Payload = TypedDict("Payload", {"message": str, "subject": NotRequired[str]})
