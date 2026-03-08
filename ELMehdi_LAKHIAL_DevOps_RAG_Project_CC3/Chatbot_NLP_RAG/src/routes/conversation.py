from fastapi import APIRouter, Request, HTTPException, Depends
from database.deps import get_db
from countroller.RetrievalController import RAGController 
from middlewares.auth_guard import get_current_user
from models.ConvesationModel import ConversationModel
from models.MessageModel import MessageModel
from .convesations.schema import CreateConversationRequest, AddMessageRequest
from models.UserModel import UserModel
from models.ProjectModel import ProjectModel

router_conversations = APIRouter(prefix="/conversations", tags=["conversations"])


@router_conversations.post("")
async def create_conversation(
    payload: CreateConversationRequest,
    request: Request,
    current=Depends(get_current_user)
):
    db = get_db(request)
    conv_model = ConversationModel(db)

    conv_id = await conv_model.create(user_id=current["user_id"], title=payload.title)
    return {"id": conv_id, "title": payload.title}


@router_conversations.get("")
async def list_conversations(
    request: Request,
    current=Depends(get_current_user)
):
    db = get_db(request)
    conv_model = ConversationModel(db)

    items = await conv_model.list_by_user(current["user_id"], limit=50)

    # normalize _id
    out = []
    for c in items:
        out.append({
            "id": str(c["_id"]),
            "title": c.get("title", "New conversation"),
            "updated_at": c.get("updated_at"),
            "created_at": c.get("created_at"),
        })
    return {"items": out}


@router_conversations.get("/{conversation_id}/messages")
async def list_messages(
    conversation_id: str,
    request: Request,
    current=Depends(get_current_user)
):
    db = get_db(request)

    conv_model = ConversationModel(db)
    msg_model = MessageModel(db)

    conv = await conv_model.get_by_id(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conv["user_id"] != current["user_id"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    msgs = await msg_model.list_by_conversation(conversation_id, limit=200)

    out = []
    for m in msgs:
        out.append({
            "id": str(m["_id"]),
            "role": m["role"],
            "content": m["content"],
            "sources": m.get("sources")
        })

    return {"items": out}


@router_conversations.post("/{conversation_id}/messages/")
async def add_user_message(
    conversation_id: str,
    payload: AddMessageRequest,
    request: Request,
    current=Depends(get_current_user)
):
    db = get_db(request)

    conv_model = ConversationModel(db)
    msg_model = MessageModel(db)
    user_model = UserModel(db)

    conv = await conv_model.get_by_id(conversation_id)
    user = await user_model.get_by_id(conv["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role_u = user["role"]
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conv["user_id"] != current["user_id"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    # 1 save user message
    await msg_model.add(conversation_id, role=role_u, content=payload.content)
    await conv_model.touch(conversation_id)
    print(role_u)
    project_model = await ProjectModel.instance( db_client=request.app.mongodb_client ) 
    project = await project_model.get_project_by_id(str(role_u))
    # 2 call RAG
    
    rag_ask = RAGController(db_client=db)
    answer = await rag_ask.ask_question(
        query=payload.content,
        project_id=project.id,
        role= role_u
    )

    # 3 save assistant message
    await msg_model.add(
        conversation_id,
        role="assent",
        content=answer
    )

    return {
        "answer": answer
    }

@router_conversations.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    request: Request,
    current=Depends(get_current_user)
):
    db = get_db(request)
    conv_model = ConversationModel(db)
    msg_model  = MessageModel(db)

    # check exists + ownership
    conv = await conv_model.get_by_id(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conv["user_id"] != current["user_id"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    # delete messages first, then conversation
    await msg_model.delete_by_conversation(conversation_id)
    await conv_model.delete_conv(conversation_id)

    return {"deleted": True, "id": conversation_id}