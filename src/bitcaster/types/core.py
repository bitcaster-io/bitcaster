from typing import TypedDict


class DispatcherConfig(TypedDict):
    sender: str


#
# Payload = TypedDict(
#     "Payload",
#     {
#         "message": str,
#         "subject": NotRequired[str],
#         "html_message": NotRequired[str],
#     },
# )
