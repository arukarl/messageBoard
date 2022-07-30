import app


def test_remove_html():
    assert app.remove_html("<html>Hello") == "Hello"
    assert app.remove_html("Hello<script>") == "Hello"
    assert app.remove_html("Te</p>st") == "Test"
    assert app.remove_html("Te<>st") == "Te<>st"


def test_set_images_url():
    message = {'img': 'image.name'}
    cdn_url = 'https://test.io/'
    new_message = app.set_images_url(message, cdn_url)
    assert new_message['img_url'] == 'https://test.io/images/image.name'
    assert new_message['thumbnail_url'] == 'https://test.io/thumbnails/image.name'
