from pydantic import BaseModel, Field

class OrderCreate(BaseModel):
    id: str
    quantity: int = Field(gt=0)