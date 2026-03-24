"""
Tests for the Mergington High School Activities API.
Uses the AAA (Arrange, Act, Assert) pattern.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities data before each test to ensure test isolation."""
    original_participants = {
        name: list(details["participants"])
        for name, details in activities.items()
    }
    yield
    for name, participants in original_participants.items():
        activities[name]["participants"] = participants


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestGetActivities:
    def test_get_activities_returns_200(self, client):
        # Arrange & Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        # Arrange & Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        assert isinstance(data, dict)

    def test_get_activities_contains_expected_fields(self, client):
        # Arrange & Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        for name, details in data.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details


class TestSignup:
    def test_signup_for_valid_activity(self, client):
        # Arrange
        email = "test@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert email in activities[activity]["participants"]

    def test_signup_returns_confirmation_message(self, client):
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Programming Class"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_signup_for_nonexistent_activity_returns_404(self, client):
        # Arrange
        email = "test@mergington.edu"
        activity = "Nonexistent Activity"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404

    def test_signup_duplicate_returns_400(self, client):
        # Arrange
        email = "duplicate@mergington.edu"
        activity = "Chess Club"
        client.post(f"/activities/{activity}/signup?email={email}")

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_when_activity_full_returns_400(self, client):
        # Arrange
        activity = "Math Team"
        max_participants = activities[activity]["max_participants"]
        for i in range(max_participants):
            client.post(f"/activities/{activity}/signup?email=student{i}@mergington.edu")

        # Act
        response = client.post(f"/activities/{activity}/signup?email=overflow@mergington.edu")

        # Assert
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()


class TestUnregister:
    def test_unregister_existing_participant(self, client):
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert email not in activities[activity]["participants"]

    def test_unregister_returns_confirmation_message(self, client):
        # Arrange
        email = "daniel@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_unregister_from_nonexistent_activity_returns_404(self, client):
        # Arrange
        email = "test@mergington.edu"
        activity = "Nonexistent Activity"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404

    def test_unregister_not_registered_student_returns_400(self, client):
        # Arrange
        email = "notregistered@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()
