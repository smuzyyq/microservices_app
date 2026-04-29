import httpx

from config import settings
from domain.exceptions import UnauthorizedError


async def verify_auth_token(authorization: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            settings.auth_verify_url,
            headers={"Authorization": authorization},
        )
    if response.status_code != 200:
        raise UnauthorizedError("Unauthorized.")
    return response.json()
