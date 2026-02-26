import google.genai.types as types

print(types.LiveConnectConfig.schema_json(indent=2))
if hasattr(types, "SpeechConfig"):
    print(types.SpeechConfig.schema_json(indent=2))
