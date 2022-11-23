import sys
import os

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src import bot


@pytest.mark.parametrize(
    'boxes, screen_name, expected_text',
    [
        (
            [['cat', 1.0, 0, 10, 0, 10],
             ['cat', 0.9, 0, 9, 0, 9],
             ['dog', 0.9, 0, 9, 0, 9]],
            'username',
            '@username This image contains:\n2 cats\n1 dog'
        ),
        (
            [['dog', 1.0, 0, 10, 0, 10],
             ['cat', 0.9, 0, 9, 0, 9],
             ['dog', 0.9, 0, 9, 0, 9]],
            'username',
            '@username This image contains:\n1 cat\n2 dogs'
        ),
        (
            [['skis', 1.0, 0, 10, 0, 10],
             ['scissors', 0.9, 0, 9, 0, 9],
             ['dog', 0.9, 0, 9, 0, 9]],
            'username',
            '@username This image contains:\n1 dog\n1 scissors\n1 skis'
        ),
        (
            [],
            'username',
            'Sorry @username, I have found nothing. Try with other image.'
        )
    ]
)
def test_generate_text(boxes, screen_name, expected_text):

    text = bot.generate_text(boxes, screen_name)

    assert text == expected_text


@pytest.mark.parametrize(
    'label, count, expected_text',
    [
        ('cat', 2, '\n2 cats'),
        ('cat', 1, '\n1 cat'),
        ('skis', 2, '\n2 skis'),
        ('bus', 1, '\n1 bus'),
        ('bus', 5, '\n5 buses')
    ]
)
def test_get_label_text(label, count, expected_text):

    text = bot.get_label_text(label, count)

    assert text == expected_text
    