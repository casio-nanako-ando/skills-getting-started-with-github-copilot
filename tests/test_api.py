"""
Tests for the High School Management System API endpoints.
"""

import pytest
import urllib.parse
from fastapi.testclient import TestClient


class TestBasicEndpoints:
    """Test basic API endpoints."""

    def test_root_redirect(self, client: TestClient):
        """Test that root endpoint redirects to static index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_get_activities(self, client: TestClient, reset_activities):
        """Test retrieving all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # We have 9 activities in the initial data
        
        # Check if Chess Club exists and has correct structure
        assert "Chess Club" in data
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert chess_club["max_participants"] == 12
        assert len(chess_club["participants"]) == 2


class TestSignupEndpoint:
    """Test activity signup functionality."""

    def test_successful_signup(self, client: TestClient, reset_activities):
        """Test successful signup for an activity."""
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_nonexistent_activity(self, client: TestClient, reset_activities):
        """Test signup for non-existent activity."""
        response = client.post("/activities/Nonexistent Club/signup?email=test@mergington.edu")
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_already_registered(self, client: TestClient, reset_activities):
        """Test signup when student is already registered."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_activity_full(self, client: TestClient, reset_activities):
        """Test signup when activity is full."""
        # First, fill up the Chess Club (max 12 participants)
        activity_name = "Chess Club"
        # Chess Club already has 2 participants, so add 10 more to fill it
        for i in range(10):
            email = f"student{i}@mergington.edu"
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # Now try to add one more (should fail)
        email = "overflow@mergington.edu"
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 400
        assert response.json()["detail"] == "Activity is full"

    def test_signup_with_special_characters(self, client: TestClient, reset_activities):
        """Test signup with URL-encoded special characters."""
        activity_name = "Chess Club"
        email = "test+user@mergington.edu"
        
        # URL encode the email
        encoded_email = urllib.parse.quote(email)
        
        response = client.post(f"/activities/{urllib.parse.quote(activity_name)}/signup?email={encoded_email}")
        assert response.status_code == 200
        
        # Verify the participant was added with correct email
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]


class TestRemoveParticipantEndpoint:
    """Test participant removal functionality."""

    def test_successful_removal(self, client: TestClient, reset_activities):
        """Test successful removal of a participant."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Existing participant
        
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == f"Removed {email} from {activity_name}"
        
        # Verify the participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]

    def test_remove_from_nonexistent_activity(self, client: TestClient, reset_activities):
        """Test removal from non-existent activity."""
        response = client.delete("/activities/Nonexistent Club/participants/test@mergington.edu")
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_remove_nonexistent_participant(self, client: TestClient, reset_activities):
        """Test removal of non-existent participant."""
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"
        
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found in this activity"

    def test_remove_with_special_characters(self, client: TestClient, reset_activities):
        """Test removal with URL-encoded special characters."""
        activity_name = "Chess Club"
        email = "test+user@mergington.edu"
        
        # First add the participant
        client.post(f"/activities/{activity_name}/signup?email={urllib.parse.quote(email)}")
        
        # Then remove them
        response = client.delete(f"/activities/{urllib.parse.quote(activity_name)}/participants/{urllib.parse.quote(email)}")
        assert response.status_code == 200
        
        # Verify removal
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]


class TestIntegrationScenarios:
    """Test complete user scenarios."""

    def test_complete_signup_and_removal_flow(self, client: TestClient, reset_activities):
        """Test a complete flow of signup and removal."""
        activity_name = "Programming Class"
        email = "newcoder@mergington.edu"
        
        # Check initial state
        activities_response = client.get("/activities")
        initial_activities = activities_response.json()
        initial_count = len(initial_activities[activity_name]["participants"])
        
        # Sign up
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1
        
        # Remove participant
        remove_response = client.delete(f"/activities/{activity_name}/participants/{email}")
        assert remove_response.status_code == 200
        
        # Verify removal
        activities_response = client.get("/activities")
        final_activities = activities_response.json()
        assert email not in final_activities[activity_name]["participants"]
        assert len(final_activities[activity_name]["participants"]) == initial_count

    def test_multiple_signups_different_activities(self, client: TestClient, reset_activities):
        """Test signing up the same student for multiple activities."""
        email = "multi@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Art Club"]
        
        for activity_name in activities_to_join:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify student is in all activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        for activity_name in activities_to_join:
            assert email in activities[activity_name]["participants"]

    def test_activity_capacity_management(self, client: TestClient, reset_activities):
        """Test that activity capacity is properly managed."""
        activity_name = "Debate Team"  # Max 16, currently has 2
        
        # Get current state
        activities_response = client.get("/activities")
        activity = activities_response.json()[activity_name]
        max_participants = activity["max_participants"]
        current_participants = len(activity["participants"])
        spots_available = max_participants - current_participants
        
        # Fill up the remaining spots
        for i in range(spots_available):
            email = f"debater{i}@mergington.edu"
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # Try to add one more (should fail)
        overflow_email = "overflow@mergington.edu"
        response = client.post(f"/activities/{activity_name}/signup?email={overflow_email}")
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()
        
        # Remove one participant and try again (should succeed)
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        participant_to_remove = participants[0]
        
        remove_response = client.delete(f"/activities/{activity_name}/participants/{participant_to_remove}")
        assert remove_response.status_code == 200
        
        # Now adding the overflow student should work
        response = client.post(f"/activities/{activity_name}/signup?email={overflow_email}")
        assert response.status_code == 200