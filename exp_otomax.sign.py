import base64
import hashlib


def generate_otomax_sign(purpose: str, params: list[str]) -> str:
    """Generate OtomaX signature.

    Args:
        purpose: 'transaction', 'deposit', or 'checkbalance'
        params: list of parameters sesuai urutan format

    Returns:
        str: generated signature string
    """
    # Map purpose ke base string
    if purpose == "transaction":
        raw_str = f"OtomaX|{params[0]}|{params[1]}|{params[2]}|{params[3]}|{params[4]}|{params[5]}"
    elif purpose == "deposit":
        raw_str = f"OtomaX|ticket|{params[0]}|{params[1]}|{params[2]}|{params[3]}"
    elif purpose == "checkbalance":
        raw_str = f"OtomaX|CheckBalance|{params[0]}|{params[1]}|{params[2]}"
    else:
        raise ValueError("Unknown purpose")

    # Hash dan encode base64 dengan format OtomaX
    sha1_hash = hashlib.sha1(raw_str.encode()).digest()
    base64_encoded = base64.b64encode(sha1_hash).decode().rstrip("=")
    sign = base64_encoded.replace("+", "-").replace("/", "_")

    return sign

# memberid=vps809|pin=777999|password=vps777999

def main():
    sign = generate_otomax_sign(
        "transaction", ["YUSUF", "X10", "08123456789", "2140669", "1144", "abcd"]
    )

    print(sign)


if __name__ == "__main__":
    main()
