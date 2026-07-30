from pydantic import BaseModel


class AuditRequest(BaseModel):
    query: str
