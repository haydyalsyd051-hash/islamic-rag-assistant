import sys
from pathlib import Path

# يضيف مجلد backend/ إلى sys.path حتى يعمل `import app...` من داخل tests/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture(scope="module")
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c
