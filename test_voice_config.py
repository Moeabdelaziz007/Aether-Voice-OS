from google.genai import types

def test_config():
    try:
        vc = types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
        )
        sc = types.SpeechConfig(voice_config=vc)
        lc = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            speech_config=sc
        )
        print("Success!", lc)
    except Exception as e:
        print("Error:", e)

test_config()
