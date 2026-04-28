import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

INITIAL_ACTIVITIES = copy.deepcopy(activities)

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def test_get_activities_returns_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_student():
    new_email = "test.student@mergington.edu"
    response = client.post("/activities/Chess%20Club/signup", params={"email": new_email})

    assert response.status_code == 200
    assert new_email in activities["Chess Club"]["participants"]
    assert response.json()["message"] == f"Signed up {new_email} for Chess Club"


def test_signup_for_activity_duplicate_returns_400():
    email = "michael@mergington.edu"
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_nonexistent_activity_returns_404():
    response = client.post("/activities/Nonexistent/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_student():
    email = "michael@mergington.edu"
    response = client.delete("/activities/Chess%20Club/participants", params={"email": email})

    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"


def test_unregister_missing_participant_returns_404():
    response = client.delete("/activities/Chess%20Club/participants", params={"email": "missing@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
