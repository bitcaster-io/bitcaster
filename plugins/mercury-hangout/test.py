import hangups


async def send_message(client, args):
    request = hangups.hangouts_pb2.SendChatMessageRequest(
        request_header=client.get_request_header(),
        event_request_header=hangups.hangouts_pb2.EventRequestHeader(
            conversation_id=hangups.hangouts_pb2.ConversationId(
                id=args.conversation_id
            ),
            client_generated_id=client.get_client_generated_id(),
        ),
        message_content=hangups.hangouts_pb2.MessageContent(
            segment=[
                hangups.ChatMessageSegment(args.message_text).serialize()
            ],
        ),
    )
    await client.send_chat_message(request)


cookies = hangups.auth.get_auth_stdin('.')
client = hangups.Client(cookies)
