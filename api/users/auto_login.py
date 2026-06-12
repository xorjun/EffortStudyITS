"""
Auto-login by Prolific PID.

The SCRIPT backend traditionally required an email+password registration
via the /auth/register endpoint. With the participant pipeline redesign,
the Prolific PID is the single tying identity across all components, and
we want participants to land in the tutoring view immediately after
Prolific redirects them. This module exposes a small endpoint that:

  1. Validates the incoming Prolific PID.
  2. Looks up a SCRIPT user keyed on a deterministic email
     `prolific+<pid>@scriptorium.local`. If no user exists, creates one
     with a deterministic password (derived from the PID via a server
     secret) so the same PID always signs into the same account.
  3. Programmatically logs the user in (sets the same cookie that
     /auth/jwt/login sets) and returns a small JSON payload so the
     Angular client can transition to the tutoring view.

The deterministic password is server-side only and never leaves this
module. The client must NOT store or display it.
"""
import hashlib
import hmac
import os

from fastapi import APIRouter, HTTPException, Response
from fastapi_users.password import PasswordHelper
from pydantic import BaseModel, Field

from users.schemas import User, UserLevel
from users.handle_users import auth_backend

router = APIRouter()
_password_helper = PasswordHelper()


def _pid_email(prolific_pid: str) -> str:
    return f"prolific+{prolific_pid}@scriptorium.local"


def _pid_password(prolific_pid: str) -> str:
    """Derive a deterministic password from the Prolific PID.

    Uses a server-side HMAC secret so that a leaked PID cannot be used to
    guess the password without the secret. Output is the first 32 chars
    of the hex digest, well within fastapi-users' password length
    tolerance.
    """
    secret = (
        os.environ.get("PROLIFIC_AUTO_LOGIN_SECRET")
        or os.environ.get("JWT_SECRET")
        or "scriptorium-default-auto-login-secret"
    )
    digest = hmac.new(
        secret.encode("utf-8"),
        prolific_pid.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return digest[:32]


class AutoLoginRequest(BaseModel):
    prolific_pid: str = Field(..., min_length=1, max_length=64)


class AutoLoginResponse(BaseModel):
    participant_id: str
    email: str
    user_id: str


async def _get_or_create_user(prolific_pid: str) -> User:
    """Look up the SCRIPT user for a Prolific PID, creating one if needed.

    Mirrors the on_after_register behavior of the regular /auth/register
    flow (default role = 'student', is_active/is_verified = True) so the
    SCRIPT app accepts the user without any further steps.
    """
    email = _pid_email(prolific_pid)

    existing = await User.find_one(User.email == email)
    if existing is not None:
        return existing

    # Build a User with the same defaults the regular registration flow
    # uses, but with a server-derived password. We deliberately bypass
    # the /auth/register router so the email-domain checks and the
    # verification flow do not block the auto-login path.
    user_count = await User.count()
    role = UserLevel.admin if user_count <= 0 else UserLevel.student

    user = User(
        email=email,
        username=prolific_pid[:64],
        hashed_password=_password_helper.hash(_pid_password(prolific_pid)),
        current_course="",
        enrolled_courses=[],
        register_datetime={"utc": "", "local": ""},
        settings={},
        roles=[role],
        is_active=True,
        is_verified=True,
    )
    await user.insert()
    return user


@router.post("/auth/auto-login-by-pid", response_model=AutoLoginResponse)
async def auto_login_by_pid(body: AutoLoginRequest, response: Response):
    """Sign a participant in to SCRIPT using only their Prolific PID.

    No password is required from the client; the server derives a
    deterministic password from the PID, looks up or creates the SCRIPT
    user, and sets the same auth cookie as /auth/jwt/login.
    """
    if not body.prolific_pid or not body.prolific_pid.strip():
        raise HTTPException(status_code=400, detail="prolific_pid is required.")

    pid = body.prolific_pid.strip()
    user = await _get_or_create_user(pid)

    # Mint a JWT identical to the one /auth/jwt/login would have issued
    # and set it on the response via the existing cookie transport. This
    # is the same path the regular login flow uses, so all subsequent
    # endpoints that read `current_active_user` keep working.
    strategy = auth_backend.get_strategy()
    token = await strategy.write_token(user.id)

    # CookieTransport sets Set-Cookie on the response. The transport's
    # get_login_response returns a Response object which we use to copy
    # the cookie headers onto our own response.
    transport_response = await auth_backend.transport.get_login_response(
        strategy=strategy,
        user=user,
        token=token,
        response=None,
    )
    # Copy any cookies the transport set onto our own response.
    for header_name, header_value in transport_response.headers.items():
        if header_name.lower() == "set-cookie":
            response.headers.append(header_name, header_value)

    return AutoLoginResponse(
        participant_id=user.email,
        email=user.email,
        user_id=str(user.id),
    )
