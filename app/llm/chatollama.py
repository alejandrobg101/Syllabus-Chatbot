from app.dao.syllabus import SyllabusDAO
from sentence_transformers import SentenceTransformer
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

embedder = SentenceTransformer("all-mpnet-base-v2")


class ChatOllamaBot:
    def __init__(self):
        self.dao = SyllabusDAO()

    def ask(self, question: str) -> str:
        courseid = None

        import re

        match = re.search(r"([A-Z]{2,4})[-\s]?(\d{3,4})", question)
        if match:
            cname, ccode = match.group(1), match.group(2)
            courseid = self.dao.find_course(cname=cname, ccode=ccode)
        else:
            match_desc = re.search(r"(?:course|class)\s+([\w\s]+)", question, re.IGNORECASE)
            if match_desc:
                cdesc = match_desc.group(1).strip()
                courseid = self.dao.find_course(cdesc=cdesc)

        emb = embedder.encode(question).tolist()

        chunks = self.dao.get_relevant_chunks(emb, courseid=courseid, limit=20)
        if not chunks:
            return "I couldn't find that information in the syllabus."

        context_texts = [chunk[0] for chunk in chunks]
        documents = "\n".join(context_texts)

        prompt = PromptTemplate(
            template="""You are an assistant for question-answering tasks at UPR-Mayagüez.
Use the following syllabus excerpts to answer the question.
If you don't know the answer, just say: "I couldn't find that information in the syllabus."
Keep the answer concise and professional.

Syllabus excerpts:
{documents}

Question: {question}

Answer:""",
            input_variables=["documents", "question"],
        )

        llm = ChatOllama(model="llama3.2", temperature=0)
        chain = prompt | llm | StrOutputParser()

        answer = chain.invoke({"documents": documents, "question": question})
        return answer.strip()
