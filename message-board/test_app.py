import app


def test_remove_html():
    assert app.remove_html("<html>Hello") == "Hello"
