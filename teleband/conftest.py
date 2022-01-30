import pytest

from teleband.users.models import User
from teleband.users.tests.factories import UserFactory

from teleband.musics.models import Piece
from teleband.musics.tests.factories import PieceFactory


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def piece() -> Piece:
    return PieceFactory()
