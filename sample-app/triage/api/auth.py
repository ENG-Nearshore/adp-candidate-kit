"""API token check applied to every request."""

import hmac

TOKEN_HEADER = "X-Api-Token"
PUBLIC_PATHS = frozenset({"/health"})


def is_authorized(path: str, headers, expected_token: str) -> bool:
    if path in PUBLIC_PATHS:
        return True
    supplied = headers.get(TOKEN_HEADER, "")
    return hmac.compare_digest(supplied, expected_token)
