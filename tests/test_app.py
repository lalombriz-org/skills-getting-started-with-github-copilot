from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_root_redirects_to_static_index():
    """Test that GET / redirects to the static index page"""
    # Arrange - no special setup needed
    
    # Act
    response = client.get("/", follow_redirects=False)
    
    # Assert
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities_returns_all_activities():
    """Test that GET /activities returns the activities data"""
    # Arrange - no special setup needed
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    
    # Verify structure of activity data
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)

def test_signup_success_adds_participant():
    """Test successful signup adds participant to activity"""
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "Signed up" in result["message"]
    
    # Verify participant was added
    response = client.get("/activities")
    data = response.json()
    assert email in data[activity]["participants"]

def test_signup_duplicate_fails():
    """Test that signing up twice for same activity fails"""
    # Arrange
    email = "duplicatestudent@mergington.edu"
    activity = "Programming Class"
    
    # First signup (should succeed)
    client.post(f"/activities/{activity}/signup?email={email}")
    
    # Act - second signup
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "already signed up" in result["detail"].lower()

def test_signup_invalid_activity_fails():
    """Test signup for non-existent activity fails"""
    # Arrange
    email = "test@mergington.edu"
    invalid_activity = "NonExistent Club"
    
    # Act
    response = client.post(f"/activities/{invalid_activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "not found" in result["detail"].lower()

def test_delete_success_removes_participant():
    """Test successful deletion removes participant from activity"""
    # Arrange
    email = "deletetest@mergington.edu"
    activity = "Gym Class"
    
    # First signup
    client.post(f"/activities/{activity}/signup?email={email}")
    
    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "Unregistered" in result["message"]
    
    # Verify participant was removed
    response = client.get("/activities")
    data = response.json()
    assert email not in data[activity]["participants"]

def test_delete_not_signed_up_fails():
    """Test deletion of non-participant fails"""
    # Arrange
    email = "notsignedup@mergington.edu"
    activity = "Chess Club"
    
    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "not signed up" in result["detail"].lower()

def test_delete_invalid_activity_fails():
    """Test deletion from non-existent activity fails"""
    # Arrange
    email = "test@mergington.edu"
    invalid_activity = "Invalid Activity"
    
    # Act
    response = client.delete(f"/activities/{invalid_activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "not found" in result["detail"].lower()