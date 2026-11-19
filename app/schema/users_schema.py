from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Literal


class User(BaseModel):
    id:int
    name:str=Field(min_length=1)
    last_name: str=Field(min_length=1)
    email:str
    password_hash:str
    address:str |None =None
    role: Literal["customer", "owner", "admin"]= "customer"
    is_active:bool=True

class UserPublic(BaseModel):
    id:int
    name:str=Field(min_length=1)
    last_name: str=Field(min_length=1)
    email:str
    address:str |None =None
    role: Literal["customer", "owner", "admin"]= "customer"
    is_active:bool=True


class CreateUser(BaseModel):
    model_config=ConfigDict(extra="forbid")
    name: str=Field(min_length=1)
    last_name:str=Field(min_length=1)
    email:str
    password:str=Field(min_length=8)

class LoginRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token:str
    token_type: str ="bearer"
    user: UserPublic


class UpdateUser(BaseModel):
    model_config=ConfigDict(extra="forbid")
    name: str | None =Field(default=None, min_length=1)
    last_name: str | None =Field(default=None, min_length=1)
    email:str | None = None
    password:str | None =Field(default= None, min_length=8)
    address: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def require_chnages(self) -> "UpdateUser":
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update")
        for field in self.model_fields_set:
            if getattr(self, field) is None:
                raise ValueError("Fields cannot be null")
        return self

    


