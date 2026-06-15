from pydantic import BaseModel


class ResumeResponse(BaseModel):

    id: int

    filename: str

    skills: str

    class Config:

        from_attributes = True