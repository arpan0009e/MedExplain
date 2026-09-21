from dataclasses import dataclass

from app.rag.context_builder import RAGContextBuilder
from app.rag.retriever import KnowledgeRetriever, RetrievedChunk
from app.services.llm import LLMService


@dataclass(frozen=True)
class ExplanationResult:
    """Result of a grounded medical explanation."""

    answer: str
    sources: list[RetrievedChunk]


class ExplanationService:
    """Orchestrates medical knowledge retrieval and LLM explanation."""

    SYSTEM_INSTRUCTION = """
You are MedExplain, an AI assistant that explains medical reports
and medical terminology in clear, understandable language.

Your role is educational explanation only. You are not a doctor and
must not provide diagnosis or treatment decisions.

Follow these rules strictly:

1. Explain medical terminology in simple, patient-friendly language.
2. Use the provided medical knowledge context as the primary source
   for medical information.
3. Do not invent facts or provide unsupported medical claims.
4. Do not diagnose diseases, disorders, or medical conditions.
5. Do not prescribe medicines, treatments, or dosages.
6. Do not tell the user to start, stop, or change medication.
7. Clearly distinguish between information explicitly present in the
   user's report and general medical information from the knowledge
   context.
8. Explain laboratory values cautiously because reference ranges can
   vary between laboratories and individuals.
9. Mention the provided source when using information from the
   retrieved medical knowledge.
10. If the retrieved context does not contain enough information,
    explicitly state that there is insufficient information rather
    than guessing.
11. Encourage the user to discuss concerning or unclear results with
    a qualified healthcare professional.
12. Keep explanations understandable to a non-medical user while
    maintaining medical accuracy and appropriate caution.

Never use the absence of information as evidence that a condition
is absent or present.
"""

    def __init__(
        self,
        retriever: KnowledgeRetriever | None = None,
        context_builder: RAGContextBuilder | None = None,
        llm_service: LLMService | None = None,
    ):
        self.retriever = retriever or KnowledgeRetriever()
        self.context_builder = context_builder or RAGContextBuilder()
        self.llm_service = llm_service or LLMService()

    def build_prompt(
        self,
        user_question: str,
        retrieved_chunks: list[RetrievedChunk],
    ) -> str:
        """Build a grounded prompt using retrieved medical knowledge."""

        context = self.context_builder.build(retrieved_chunks)

        if not context:
            context = (
                "No relevant medical knowledge was retrieved. "
                "Do not make unsupported medical claims. "
                "State that sufficient information is not available."
            )

        return f"""
Medical knowledge context:

{context}

User question:

{user_question}

Instructions:

- Answer the user's question using the provided medical knowledge context.
- Keep the explanation clear and understandable.
- Do not guess when the context is insufficient.
- Do not make a diagnosis.
- Do not provide treatment or medication instructions.
- If the available context is insufficient, clearly say so.
"""

    async def explain(self, user_question: str) -> ExplanationResult:
        """Retrieve relevant knowledge and generate a grounded explanation."""

        if not user_question.strip():
            raise ValueError("User question cannot be empty.")

        retrieved_chunks = await self.retriever.search(
            query=user_question,
            top_k=5,
        )

        prompt = self.build_prompt(
            user_question=user_question,
            retrieved_chunks=retrieved_chunks,
        )

        answer = await self.llm_service.generate(
            system_instruction=self.SYSTEM_INSTRUCTION,
            user_prompt=prompt,
        )

        return ExplanationResult(
            answer=answer,
            sources=retrieved_chunks,
        )