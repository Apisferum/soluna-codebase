from contextlib import closing
import hmac
import secrets
import time

from fastapi import APIRouter, HTTPException, status

from app.core.config import settings
from app.core.security import (
    create_access_token,
    hash_password,
    hash_reset_code,
    is_legacy_sha256_hash,
    normalize_email,
    public_user,
    verify_password,
)
from app.db.database import connect_db
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordCodeRequest,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
)
from app.services.password_reset_service import (
    RESET_REQUEST_MESSAGE,
    send_password_reset_email,
)


router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthResponse,
)
def register_user(
    data: RegisterRequest,
) -> AuthResponse:
    full_name = data.fullName.strip()
    email = normalize_email(data.email)
    age = data.age.strip()
    gender = data.gender.strip()
    password = data.password

    if (
        not full_name
        or not email
        or not age
        or not gender
        or not password.strip()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All fields are required",
        )

    if len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Password must be at least "
                "6 characters long"
            ),
        )

    with closing(connect_db()) as connection:
        cursor = connection.cursor()

        existing_user = cursor.execute(
            """
            SELECT *
            FROM users
            WHERE LOWER(email) = ?
            """,
            (email,),
        ).fetchone()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        cursor.execute(
            """
            INSERT INTO users (
                full_name,
                email,
                age,
                gender,
                password_hash,
                role,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, 'user', ?)
            """,
            (
                full_name,
                email,
                age,
                gender,
                hash_password(password),
                int(time.time()),
            ),
        )

        user_id = cursor.lastrowid
        connection.commit()

        user = cursor.execute(
            """
            SELECT *
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

    access_token = create_access_token(
        email=user["email"],
        token_version=int(
            user["token_version"]
        ),
        role=user["role"],
        token_kind="user",
    )

    return AuthResponse(
        message="Registration successful",
        access_token=access_token,
        token_type="bearer",
        session_type="user",
        user=public_user(user),
    )


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=AuthResponse,
)
def login_user(
    data: LoginRequest,
) -> AuthResponse:
    email = normalize_email(data.email)
    password = data.password

    if not email or not password.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Email and password are required"
            ),
        )

    with closing(connect_db()) as connection:
        cursor = connection.cursor()

        user = cursor.execute(
            """
            SELECT *
            FROM users
            WHERE LOWER(email) = ?
            """,
            (email,),
        ).fetchone()

        if (
            not user
            or not verify_password(
                password,
                user["password_hash"],
            )
        ):
            raise HTTPException(
                status_code=(
                    status.HTTP_401_UNAUTHORIZED
                ),
                detail="Invalid email or password",
            )

        if is_legacy_sha256_hash(
            user["password_hash"]
        ):
            cursor.execute(
                """
                UPDATE users
                SET password_hash = ?
                WHERE id = ?
                """,
                (
                    hash_password(password),
                    user["id"],
                ),
            )
            connection.commit()

    access_token = create_access_token(
        email=user["email"],
        token_version=int(
            user["token_version"]
        ),
        role=user["role"],
        token_kind="user",
    )

    return AuthResponse(
        message="Login successful",
        access_token=access_token,
        token_type="bearer",
        session_type="user",
        user=public_user(user),
    )


@router.post(
    "/admin/login",
    status_code=status.HTTP_200_OK,
    response_model=AuthResponse,
)
def admin_login(
    data: LoginRequest,
) -> AuthResponse:
    email = normalize_email(data.email)
    password = data.password

    if not email or not password.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Email and password are required"
            ),
        )

    with closing(connect_db()) as connection:
        cursor = connection.cursor()

        user = cursor.execute(
            """
            SELECT *
            FROM users
            WHERE LOWER(email) = ?
            """,
            (email,),
        ).fetchone()

        if (
            not user
            or not verify_password(
                password,
                user["password_hash"],
            )
        ):
            raise HTTPException(
                status_code=(
                    status.HTTP_401_UNAUTHORIZED
                ),
                detail="Invalid email or password",
            )

        if (
            str(user["role"]).strip().lower()
            != "admin"
        ):
            raise HTTPException(
                status_code=(
                    status.HTTP_403_FORBIDDEN
                ),
                detail=(
                    "Administrator access required"
                ),
            )

        if is_legacy_sha256_hash(
            user["password_hash"]
        ):
            cursor.execute(
                """
                UPDATE users
                SET password_hash = ?
                WHERE id = ?
                """,
                (
                    hash_password(password),
                    user["id"],
                ),
            )
            connection.commit()

    access_token = create_access_token(
        email=user["email"],
        token_version=int(
            user["token_version"]
        ),
        role=user["role"],
        token_kind="admin",
    )

    return AuthResponse(
        message="Admin login successful",
        access_token=access_token,
        token_type="bearer",
        session_type="admin",
        user=public_user(user),
    )


@router.post(
    "/forgot-password/request",
    status_code=status.HTTP_200_OK,
    response_model=MessageResponse,
)
def request_password_reset(
    data: ForgotPasswordCodeRequest,
) -> MessageResponse:
    email = normalize_email(data.email)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is required",
        )

    with closing(connect_db()) as connection:
        cursor = connection.cursor()
        now = int(time.time())

        user = cursor.execute(
            """
            SELECT *
            FROM users
            WHERE LOWER(email) = ?
            """,
            (email,),
        ).fetchone()

        if not user:
            return MessageResponse(
                message=RESET_REQUEST_MESSAGE
            )

        latest_request = cursor.execute(
            """
            SELECT created_at
            FROM password_reset_codes
            WHERE email = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (email,),
        ).fetchone()

        if (
            latest_request
            and now
            - int(latest_request["created_at"])
            < settings.reset_code_cooldown_seconds
        ):
            return MessageResponse(
                message=RESET_REQUEST_MESSAGE
            )

        cursor.execute(
            """
            UPDATE password_reset_codes
            SET used = 1
            WHERE email = ?
              AND used = 0
            """,
            (email,),
        )

        code = (
            f"{secrets.randbelow(1_000_000):06d}"
        )

        code_hash = hash_reset_code(
            email,
            code,
        )

        expires_at = now + (
            settings.reset_code_expire_minutes
            * 60
        )

        cursor.execute(
            """
            INSERT INTO password_reset_codes (
                user_id,
                email,
                code_hash,
                expires_at,
                attempts,
                used,
                created_at
            )
            VALUES (?, ?, ?, ?, 0, 0, ?)
            """,
            (
                user["id"],
                email,
                code_hash,
                expires_at,
                now,
            ),
        )

        reset_record_id = cursor.lastrowid
        connection.commit()

    try:
        if settings.password_reset_debug:
            print(
                "[PASSWORD RESET DEBUG] "
                f"Code for {email}: {code} "
                f"(expires in "
                f"{settings.reset_code_expire_minutes} "
                "minutes)"
            )
        else:
            send_password_reset_email(
                email,
                code,
            )

    except Exception as error:
        with closing(
            connect_db()
        ) as failed_connection:
            failed_connection.execute(
                """
                UPDATE password_reset_codes
                SET used = 1
                WHERE id = ?
                """,
                (reset_record_id,),
            )
            failed_connection.commit()

        print(
            "Password reset email error "
            f"for {email}: {error}"
        )

    return MessageResponse(
        message=RESET_REQUEST_MESSAGE
    )


@router.post(
    "/forgot-password/reset",
    status_code=status.HTTP_200_OK,
    response_model=MessageResponse,
)
def reset_password(
    data: ResetPasswordRequest,
) -> MessageResponse:
    email = normalize_email(data.email)
    code = data.code.strip()
    new_password = data.newPassword

    if (
        not email
        or not code
        or not new_password.strip()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Email, reset code, and "
                "new password are required"
            ),
        )

    if (
        not code.isdigit()
        or len(code) != 6
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Reset code must contain "
                "exactly 6 digits"
            ),
        )

    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Password must be at least "
                "6 characters long"
            ),
        )

    invalid_code_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=(
            "The reset code is invalid "
            "or has expired"
        ),
    )

    with closing(connect_db()) as connection:
        cursor = connection.cursor()
        now = int(time.time())

        user = cursor.execute(
            """
            SELECT *
            FROM users
            WHERE LOWER(email) = ?
            """,
            (email,),
        ).fetchone()

        reset_record = cursor.execute(
            """
            SELECT *
            FROM password_reset_codes
            WHERE email = ?
              AND used = 0
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (email,),
        ).fetchone()

        if not user or not reset_record:
            raise invalid_code_error

        if int(reset_record["expires_at"]) < now:
            cursor.execute(
                """
                UPDATE password_reset_codes
                SET used = 1
                WHERE id = ?
                """,
                (reset_record["id"],),
            )
            connection.commit()
            raise invalid_code_error

        current_attempts = int(
            reset_record["attempts"]
        )

        if (
            current_attempts
            >= settings.reset_code_max_attempts
        ):
            cursor.execute(
                """
                UPDATE password_reset_codes
                SET used = 1
                WHERE id = ?
                """,
                (reset_record["id"],),
            )
            connection.commit()
            raise invalid_code_error

        submitted_code_hash = hash_reset_code(
            email,
            code,
        )

        code_matches = hmac.compare_digest(
            submitted_code_hash,
            reset_record["code_hash"],
        )

        if not code_matches:
            new_attempt_count = (
                current_attempts + 1
            )

            mark_used = (
                1
                if new_attempt_count
                >= settings.reset_code_max_attempts
                else 0
            )

            cursor.execute(
                """
                UPDATE password_reset_codes
                SET attempts = ?,
                    used = ?
                WHERE id = ?
                """,
                (
                    new_attempt_count,
                    mark_used,
                    reset_record["id"],
                ),
            )

            connection.commit()
            raise invalid_code_error

        cursor.execute(
            """
            UPDATE users
            SET password_hash = ?,
                token_version =
                    token_version + 1
            WHERE id = ?
            """,
            (
                hash_password(new_password),
                user["id"],
            ),
        )

        cursor.execute(
            """
            UPDATE password_reset_codes
            SET used = 1
            WHERE email = ?
            """,
            (email,),
        )

        connection.commit()

    return MessageResponse(
        message=(
            "Password reset successful. "
            "All previous sessions have been "
            "invalidated. Please log in with "
            "your new password."
        )
    )