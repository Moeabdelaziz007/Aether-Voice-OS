import base64
import os
import sys


def main():
    """
    Reads a service account JSON file and converts it to a Base64 string
    suitable for the FIREBASE_CREDENTIALS_BASE64 environment variable.
    """
    filename = "service-account.json"
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        print("Usage: python generate_creds.py [path_to_service_account.json]")
        return

    with open(filename, "rb") as f:
        content = f.read()
        encoded = base64.b64encode(content).decode("utf-8")

    print("\n✅ Generated Base64 Credentials:")
    print("-" * 60)
    print(f'FIREBASE_CREDENTIALS_BASE64="{encoded}"')
    print("-" * 60)
    print("\nCopy the line above into your .env file.")


if __name__ == "__main__":
    main()
