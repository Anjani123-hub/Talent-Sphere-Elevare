import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.2,
    api_key=os.getenv("GROQ_API_KEY"),
)


def ask_llm(
    question: str,
    context: str,
    history: list = None
) -> str:

    conversation = ""

    if history:
        for msg in history[-10:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            conversation += f"{role}: {msg['content']}\n"

    if context and context.strip() != "":
        source_instruction = f"""
The following information was retrieved from the user's uploaded documents:

{context}

Use this document information when it is relevant.
"""
    else:
        source_instruction = """
No relevant information was found in the uploaded documents.
Answer the user's question using your general knowledge.
"""

    prompt = f"""
You are TalentSphere AI, an intelligent document analysis assistant.

Your task is to answer the user's question accurately and naturally.

IMPORTANT RULES:

1. If relevant information exists in the uploaded documents:
   - Use the uploaded documents as the primary source.
   - Do not invent information that is not present in the documents.

2. If the uploaded documents do NOT contain the answer:
   - Answer using your general knowledge.
   - Do NOT say that the answer cannot be found in the document.
   - Clearly mention that the answer is based on general knowledge.

3. If the question asks for a comparison, create a clear comparison table when appropriate.

4. If the question asks for differences, explain the differences clearly.

5. If the question asks for a summary, provide a concise summary.

6. If the question asks about multiple concepts, compare or explain them in a structured way.

7. For programming questions, provide correct code examples when needed.

8. Do not repeat the user's question.

9. Keep simple answers short.

10. Give detailed answers when the user asks for detailed explanations.

Previous Conversation:
{conversation}

{source_instruction}

Current User Question:
{question}

Now answer the user.
"""

    response = llm.invoke(
        [
            HumanMessage(content=prompt)
        ]
    )

    if response is None or response.content is None:
        return "Sorry, I couldn't generate a response."

    return response.content


def summarize_document(context: str) -> str:

    if not context or not context.strip():
        return "No document content is available to summarize."

    prompt = f"""
You are TalentSphere AI.

Summarize the following uploaded document content.

Give:
1. A short overview.
2. The main topics.
3. The important points.
4. Key concepts or conclusions.

Document content:

{context}
"""

    response = llm.invoke(
        [
            HumanMessage(content=prompt)
        ]
    )

    if response is None or response.content is None:
        return "Unable to summarize the document."

    return response.content


def generate_comparison(
    topic: str,
    context: str
) -> str:

    prompt = f"""
You are TalentSphere AI.

The user wants a comparison about:

{topic}

Use the uploaded document context if it contains relevant information.

If the document contains information about both concepts:
- Use the document as the primary source.

If the document does not contain enough information:
- Use your general knowledge.
- Clearly state that general knowledge was used.

Create a clear Markdown comparison table.

Use columns such as:

| Feature | Concept 1 | Concept 2 |
|---|---|---|

Uploaded document context:

{context}
"""

    response = llm.invoke(
        [
            HumanMessage(content=prompt)
        ]
    )

    if response is None or response.content is None:
        return "Unable to generate comparison."

    return response.content

def extract_key_points(context: str) -> str:

    if not context or not context.strip():
        return "No document content is available."

    prompt = f"""
You are TalentSphere AI.

Analyze the following uploaded document content and extract the most important key points.

Give the result in a clear and easy-to-read format.

Include:
- Main topic
- Important concepts
- Important facts
- Key definitions
- Important conclusions

Use bullet points.

Uploaded document:

{context}
"""

    response = llm.invoke(
        [
            HumanMessage(content=prompt)
        ]
    )

    if response is None or response.content is None:
        return "Unable to extract key points."

    return response.content

def compare_documents(context: str) -> str:

    if not context or not context.strip():
        return "No document content is available for comparison."

    prompt = f"""
You are TalentSphere AI.

Analyze the uploaded document content below and create a comparison table
based only on the information available in the documents.

Identify the main concepts, topics, technologies, methods, or items that can
be meaningfully compared.

Return the comparison in a Markdown table.

Use this format when applicable:

| Feature | Item 1 | Item 2 |
|---|---|---|
| Feature 1 | ... | ... |
| Feature 2 | ... | ... |

If the document does not contain enough information to create a meaningful
comparison, clearly state that a comparison cannot be created from the
uploaded document.

Uploaded Document Content:

{context}
"""

    response = llm.invoke(
        [
            HumanMessage(content=prompt)
        ]
    )

    if response is None or response.content is None:
        return "Unable to compare the documents."

    return response.content


import json


import json


def generate_mcqs(
    context: str,
    subject: str,
    topic: str,
    difficulty: str,
    total_questions: int,
):

    if context and context.strip():

        source_instruction = f"""
Use the following uploaded document content as the PRIMARY source
for generating the questions.

Uploaded Document Content:

{context}

IMPORTANT:
- Questions should be based mainly on the uploaded document.
- Do not invent facts that contradict the document.
- Questions must be relevant to the requested subject and topic.
"""

    else:

        source_instruction = f"""
No relevant uploaded document content is available.

Generate the questions using your own reliable general knowledge
about the requested subject and topic.

Subject: {subject}
Topic: {topic}

Do NOT say that the document is missing.
Do NOT return an error.
Generate the exam normally using general knowledge.
"""

    prompt = f"""
You are an expert exam question generator for TalentSphere AI.

Generate exactly {total_questions} multiple-choice questions.

Subject:
{subject}

Topic:
{topic}

Difficulty:
{difficulty}

{source_instruction}

Requirements:

1. Generate EXACTLY {total_questions} questions.
2. Every question must be relevant to the subject and topic.
3. Match the requested difficulty: {difficulty}.
4. Each question must have exactly four options.
5. Only one option must be correct.
6. The correct answer must be exactly one of:
   A
   B
   C
   D
7. Do not use placeholder options such as:
   "Option A"
   "Option B"
   "Option C"
   "Option D"
8. Do not repeat questions.
9. Make the questions meaningful and suitable for an actual exam.
10. Return ONLY valid JSON.
11. Do not include Markdown.
12. Do not include ```json.
13. Do not include explanations.

Return exactly this format:

[
    {{
        "question": "Question text",
        "option_a": "First option",
        "option_b": "Second option",
        "option_c": "Third option",
        "option_d": "Fourth option",
        "answer": "A"
    }}
]
"""

    try:

        response = llm.invoke(
            [
                HumanMessage(content=prompt)
            ]
        )

        if response is None or response.content is None:
            raise Exception(
                "AI did not return a response."
            )

        content = response.content.strip()

        # Remove Markdown code fences if AI adds them
        if content.startswith("```json"):
            content = content[7:]

        elif content.startswith("```"):
            content = content[3:]

        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()

        # Convert AI JSON response into Python object
        questions = json.loads(content)

        if not isinstance(questions, list):
            raise Exception(
                "AI response is not a list."
            )

        valid_questions = []

        for q in questions:

            required_keys = [
                "question",
                "option_a",
                "option_b",
                "option_c",
                "option_d",
                "answer",
            ]

            if not all(
                key in q
                for key in required_keys
            ):
                continue

            # Check empty values
            if not all(
                str(q[key]).strip()
                for key in required_keys
            ):
                continue

            # Check correct answer
            if q["answer"] not in [
                "A",
                "B",
                "C",
                "D",
            ]:
                continue

            valid_questions.append(q)

        if len(valid_questions) < total_questions:

            raise Exception(
                f"AI generated only "
                f"{len(valid_questions)} valid questions "
                f"out of {total_questions} requested."
            )

        return valid_questions[
            :total_questions
        ]

    except json.JSONDecodeError as e:

        raise Exception(
            f"AI returned invalid JSON format: {str(e)}"
        )

    except Exception as e:

        raise Exception(
            f"Failed to generate exam questions: {str(e)}"
        )