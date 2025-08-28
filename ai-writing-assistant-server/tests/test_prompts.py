from app.providers.openai_chat import STYLE_SYSTEM


def test_styles_exist():
    for key in ["professional", "casual", "polite", "social-media"]:
        assert key in STYLE_SYSTEM
        assert isinstance(STYLE_SYSTEM[key], str)
