from pydantic import BaseModel, Field

class Question(BaseModel):
    student_id: str
    text: str

class Answer(BaseModel):
    text: str

class Quiz(BaseModel):
    quiz_id: str
    questions: list[str] # Simplified for now

class QuizSubmission(BaseModel):
    student_id: str
    quiz_id: str
    answers: list[str] # Simplified for now

class PerformanceData(BaseModel):
    student_id: str
    quiz_id: str
    score: float # e.g., percentage
    feedback: str = ""

class AmbiguousQuestion(BaseModel):
    original_question: str
    reason: str = "Needs clarification"

class EscalationInfo(BaseModel):
    summary: str
    original_question: str
    student_id: str | None = None # Add if available 