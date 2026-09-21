from app.rag.retriever import RetrievedChunk


class RAGContextBuilder:
    """Builds grounded context from retrieved knowledge chunks."""

    def build(
        self,
        chunks: list[RetrievedChunk],
    ) -> str:
        """
        Convert retrieved chunks into structured context
        for the LLM.
        """

        if not chunks:
            return ""

        context_parts: list[str] = []

        for index, chunk in enumerate(chunks, start=1):
            source = chunk.metadata.get("source", "Unknown source")
            title = chunk.metadata.get("title", "Untitled")
            source_url = chunk.metadata.get("source_url", "")

            section = (
                f"[Source {index}]\n"
                f"Title: {title}\n"
                f"Source: {source}\n"
                f"Source URL: {source_url}\n"
                f"Content:\n{chunk.text}"
            )

            context_parts.append(section)

        return "\n\n".join(context_parts)