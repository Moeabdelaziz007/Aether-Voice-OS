import nacl.signing
import base64
import json
from core.utils.security import verify_signature

sk = nacl.signing.SigningKey.generate()
vk = sk.verify_key
client_id = base64.b64encode(vk.encode()).decode('utf-8')

challenge_token = '0'*64
challenge_bytes = challenge_token.encode()

# Test what test_gateway_e2e is doing:
signature_obj = sk.sign(challenge_bytes)
signature_str = base64.b64encode(signature_obj.signature).decode('utf-8')

# Try the decode:
decoded_client_id = base64.b64decode(client_id, validate=True)
decoded_sig = base64.b64decode(signature_str, validate=True)
print(verify_signature(decoded_client_id, decoded_sig, challenge_bytes))
print(verify_signature(decoded_client_id.hex(), decoded_sig.hex(), challenge_bytes))
