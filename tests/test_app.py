from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)

INITIAL_ACTIVITIES = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))
    yield


def test_get_activities_returns_activity_list():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    json_data = response.json()
    assert expected_activity in json_data
    assert "description" in json_data[expected_activity]


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    url = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_duplicate_signup_returns_bad_request():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent2@mergington.edu"
    url = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"

    # Act
    first_response = client.post(url)
    second_response = client.post(url)

    # Assert
    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up"


def test_remove_participant_from_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    url = f"/activities/{quote(activity_name)}/participants?email={quote(email)}"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_not_found():
    # Arrange
    activity_name = "Chess Club"
    email = "notfound@mergington.edu"
    url = f"/activities/{quote(activity_name)}/participants?email={quote(email)}"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
