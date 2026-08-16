from src.embeddings import embed_query
from src.vectorstore import search
from src.llm import generate_mcqs
from src.exam_db import add_question


def generate_exam(
    exam_id,
    subject,
    topic,
    difficulty,
    total_questions,
):

    # -------------------------------------------------
    # Search uploaded documents
    # -------------------------------------------------

    query = f"{subject} {topic}"

    vector = embed_query(query)

    results = search(
        vector,
        top_k=10
    )

    # -------------------------------------------------
    # Build document context
    # -------------------------------------------------

    context = ""

    for item in results:

        # Only use reasonably relevant chunks
        if item["score"] >= 0.40:

            context += (
                item["text"]
                + "\n\n"
            )

    # -------------------------------------------------
    # Generate Questions
    # -------------------------------------------------

    # If context exists:
    # AI uses uploaded documents.
    #
    # If context is empty:
    # AI uses general knowledge.

    questions = generate_mcqs(
        context=context,
        subject=subject,
        topic=topic,
        difficulty=difficulty,
        total_questions=total_questions,
    )

    # -------------------------------------------------
    # Save Questions to Database
    # -------------------------------------------------

    for q in questions:

        add_question(
            exam_id,
            q["question"],
            q["option_a"],
            q["option_b"],
            q["option_c"],
            q["option_d"],
            q["answer"],
        )

    return questions