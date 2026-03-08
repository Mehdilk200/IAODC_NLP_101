from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma

from helpers.config import settings , get_settings 
from models.chunkModel import chunkModel

class RAGController:
    def __init__(self, db_client):
        self.db_client = db_client
        self.settings = get_settings()
        print("GEMINI KEY =", self.settings.KEY_GEMINI)

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001",
            google_api_key=self.settings.KEY_GEMINI
        )

        self.vector_store = Chroma(
            collection_name="rag_docs",
            embedding_function=self.embeddings,
            persist_directory="/app/data/chroma"
        )

        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite",google_api_key=self.settings.KEY_GEMINI,temperature=0.2)
       

        system_prompt = ("""
                You are an AI assistant for project RAGISO.

                CONTEXT USAGE:
                - If the answer is found in the provided context, use it and cite sources.
                - If the answer is NOT in the context, answer from your general knowledge
                and mention: "(This answer is from general knowledge, not from project documents.)"

                MULTI-LANGUAGE RULE:
                - Detect the language of the user's question.
                - Answer in the same language (Arabic, French, or English).
                - Preserve technical keywords exactly as they appear in the context.

                TECHNICAL FOCUS:
                - Prioritize technical keywords found in the context.
                - Highlight important technical terms using **bold** formatting.
                - For architecture, DevOps, security or bug questions: provide structured answers.

                ADMIN MODE:
                If the question is analytical ("list all projects", "main risks", "common issues"):
                - Summarize patterns from the retrieved context.
                - Group similar issues.
                - Provide structured bullet points.

                ANSWER FORMAT:
                1) Direct Answer
                2) Key Technical Points (bullet list if needed)
                3) Source Evidence (only if found in context)

                Context:
                ========================
                {context}
                ========================
            """)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])

        self.combine_docs_chain = create_stuff_documents_chain(self.llm, self.prompt)

    

    async def ask_question(self, query: str, project_id: str ,role: str):

        def allowed_roles(role: str) -> list[str]:
            if role == "admin":
                return ["admin", "manager", "user"]
            if role == "manager":
                return ["manager", "user"]
            return ["user"]
        
        roles_list = allowed_roles(role)

        chunk_model = await chunkModel.instance(db_client=self.db_client)
        
        for r in roles_list:
            await chunk_model.upsert_project_chunks_to_chroma(
                vector_store=self.vector_store,
                project_id=str(project_id),
                role=r  
            )


        roles_list = allowed_roles(role)

        if len(roles_list) == 1:
            where = {"allowed_roles": roles_list[0]}
        else:
            where = {"$or": [{"allowed_roles": r} for r in roles_list]}

    

        retriever = self.vector_store.as_retriever(
                    search_kwargs={
                            "k": 5,
                            "filter": where
                        }
                )

        rag_chain = create_retrieval_chain(retriever, self.combine_docs_chain)

        response = await rag_chain.ainvoke({
                    "input": query,
                    "project_id": project_id,
                    "allowed_roles": role
                })

        return response["answer"]