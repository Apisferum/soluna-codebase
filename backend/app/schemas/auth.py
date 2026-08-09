from pydantic import BaseModel


class RegisterRequest(BaseModel):
    fullName: str
    email: str
    age: str
    gender: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class ForgotPasswordCodeRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    email: str
    code: str
    newPassword: str


class PublicUserResponse(BaseModel):
    name: str
    email: str
    age: str
    gender: str
    role: str


class AuthResponse(BaseModel):
    message: str
    access_token: str
    token_type: str
    session_type: str
    user: PublicUserResponse


class ProfileResponse(BaseModel):
    user: PublicUserResponse


class MessageResponse(BaseModel):
    message: str
