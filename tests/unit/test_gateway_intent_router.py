from core.infra.transport.intent_router import predict_next_goal


def test_predict_next_goal_keywords():
    assert predict_next_goal("please fix this") == "apply autonomous repair"
