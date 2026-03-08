async def ensure_chat_collections(db):
    existing = await db.list_collection_names()

    if "conversations" not in existing:
        await db.create_collection("conversations")
    if "messages" not in existing:
        await db.create_collection("messages")

    conv = db["conversations"]
    msg = db["messages"]

    # indexes
    await conv.create_index("user_id", name="conversation_user_id_index")
    await conv.create_index("updated_at", name="conversation_updated_at_index")

    await msg.create_index(
        [("conversation_id", 1), ("created_at", 1)],
        name="messages_conversation_time_index"
    )