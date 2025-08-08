from app.dependencies.dep_context import get_client_ip
from fastapi import Depends, HTTPException

ALLOWED_IPS: list[str] = ["192.168.1.100", "10.0.0.5"]


def verify_ip(client_ip: str = Depends(get_client_ip)) -> str:
    """Verify the client's IP address against a list of allowed IPs.

    This function checks if the provided client IP address is in the list of allowed IPs.
    If the IP is not allowed, an HTTPException is raised.

    Args:
        client_ip (str, optional): The client's IP address. Defaults to Depends(get_client_ip).

    Raises:
        HTTPException: If the client IP is not in the allowed list, a 403 Forbidden error is raised.

    Returns:
        str: The client's IP address if it is allowed.
    """
    if client_ip not in ALLOWED_IPS:
        raise HTTPException(status_code=403, detail="Access denied: Invalid IP address")
    return client_ip
