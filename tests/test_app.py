"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


client = TestClient(app)


class TestActivities:
    """Test cases for fetching activities"""

    def test_get_activities(self):
        """Test fetching all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        
        # Check that activities exist
        assert isinstance(activities, dict)
        assert len(activities) > 0
        
        # Check that expected activities are present
        assert "Basketball Team" in activities
        assert "Tennis Club" in activities
        assert "Art Studio" in activities

    def test_activity_structure(self):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        activities = response.json()
        
        activity = activities["Basketball Team"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignup:
    """Test cases for signing up for activities"""

    def test_signup_success(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "student@mergington.edu" in data["message"]

    def test_signup_duplicate_email(self):
        """Test that duplicate signups are rejected"""
        # First signup
        client.post(
            "/activities/Chess%20Club/signup?email=duplicate@mergington.edu"
        )
        
        # Try to signup again with same email
        response = client.post(
            "/activities/Chess%20Club/signup?email=duplicate@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity(self):
        """Test signup for a non-existent activity"""
        response = client.post(
            "/activities/NonExistent%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]


class TestUnregister:
    """Test cases for unregistering from activities"""

    def test_unregister_success(self):
        """Test successful unregistration from an activity"""
        # First signup
        client.post(
            "/activities/Debate%20Team/signup?email=debate@mergington.edu"
        )
        
        # Then unregister
        response = client.delete(
            "/activities/Debate%20Team/unregister?email=debate@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_not_registered(self):
        """Test unregistration for a student not in the activity"""
        response = client.delete(
            "/activities/Programming%20Class/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_nonexistent_activity(self):
        """Test unregistration from a non-existent activity"""
        response = client.delete(
            "/activities/NonExistent%20Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]


class TestIntegration:
    """Integration tests for signup and unregister workflows"""

    def test_signup_and_unregister_flow(self):
        """Test complete flow: signup, verify, unregister, verify"""
        activity_name = "Gym%20Class"
        email = "gym@mergington.edu"
        
        # Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()["Gym Class"]["participants"])
        
        # Signup
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        after_signup_count = len(response.json()["Gym Class"]["participants"])
        assert after_signup_count == initial_count + 1
        
        # Unregister
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        after_unregister_count = len(response.json()["Gym Class"]["participants"])
        assert after_unregister_count == initial_count
