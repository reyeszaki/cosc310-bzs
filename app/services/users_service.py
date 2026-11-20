import hashlib
import hmac
import secrets
from app.repository.users_repo import UserRepository
from app.schema.users_schema import CreateUser, LoginRequest, LoginResponse, UpdateUser, UserPublic

def hash_password(plain:str)-> str:
    salt=secrets.token_hex(16)
    digest=hashlib.pbkdf2_hmac("sha256", plain.encode(),salt.encode(), 100_000).hex()
    return f"{salt}${digest}"

def verify_password(plain: str, stored: str) -> bool:
    salt, digest = stored.split("$")
    new_digest = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt.encode(), 100_000).hex()
    return hmac.compare_digest(new_digest, digest)

class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository
        self._sessions: dict[str, int] = {}

    def _normalize(self, email: str) -> str:
        return email.strip().lower()

    def _to_public(self, row: dict) -> UserPublic:
        public = {key: value for key, value in row.items() if key != "password_hash"}
        return UserPublic(**public)

    def get_user(self, user_id: int) -> UserPublic:
        row = self.repository.get_by_id(user_id)
        if row is None:
            raise LookupError(f"User with id {user_id} not found")
        return self._to_public(row)

    def require_active(self, user_id: int) -> UserPublic:
        user = self.get_user(user_id)
        if not user.is_active:
            raise PermissionError("Account is deactivated")
        return user

    def register(self, request: CreateUser) -> UserPublic:
        email = self._normalize(request.email)
        if self.repository.get_by_email(email) is not None:
            raise ValueError("Email already registered")
        fields = request.model_dump()
        password = fields.pop("password")
        fields["email"] = email
        fields["password_hash"] = hash_password(password)
        fields["address"] = None
        fields["role"] = "customer"
        fields["is_active"] = True
        row = self.repository.create(fields)
        return self._to_public(row)

    def login(self, request: LoginRequest) -> LoginResponse:
        row = self.repository.get_by_email(self._normalize(request.email))
        if row is None or not verify_password(request.password, row["password_hash"]):
            raise PermissionError("Invalid email or password")
        if not row["is_active"]:
            raise PermissionError("Account is deactivated")
        token = secrets.token_urlsafe(32)
        self._sessions[token] = row["id"]
        return LoginResponse(access_token=token, user=self._to_public(row))

    def logout(self, token: str) -> None:
        self._sessions.pop(token, None)

    def get_user_by_token(self, token: str) -> UserPublic:
        user_id = self._sessions.get(token)
        if user_id is None:
            raise PermissionError("Invalid or expired token")
        return self.require_active(user_id)

    def update_user(self, user_id: int, request: UpdateUser) -> UserPublic:
        self.require_active(user_id)
        fields = request.model_dump(exclude_unset=True)
        if "email" in fields:
            fields["email"] = self._normalize(fields["email"])
            other = self.repository.get_by_email(fields["email"])
            if other is not None and other["id"] != user_id:
                raise ValueError("Email already registered")
        if "password" in fields:
            fields["password_hash"] = hash_password(fields.pop("password"))
        row = self.repository.update(user_id, fields)
        return self._to_public(row)

    def deactivate_user(self, user_id: int) -> UserPublic:
        self.get_user(user_id)
        row = self.repository.update(user_id, {"is_active": False})
        self._sessions = {token: uid for token, uid in self._sessions.items() if uid != user_id}
        return self._to_public(row)


