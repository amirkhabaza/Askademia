from uagents import Model

class StudentQuery(Model):
    query: str

class TAResponse(Model):
    answer: str

class ErrorResponse(Model):
    error: str
