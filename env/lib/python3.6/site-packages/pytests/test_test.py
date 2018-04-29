import pytest

from telegram import User, Chat, Video, Audio, Message


@pytest.fixture(scope="function", params=[{'video': Video("my_id", 12, 12, 12)}, {'audio':Audio("audio_id",12)}], ids=['video', 'audio'])
def tester(request):
    return Message(1,User(1, "aa"), None, Chat(2, 'private'), **request.param)

def test_something(tester, request):
    print (request.param)
    test = "try it"
    assert -0