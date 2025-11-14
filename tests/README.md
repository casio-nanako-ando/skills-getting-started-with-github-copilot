# Testing Documentation

## Overview
This directory contains comprehensive tests for the High School Management System API using pytest and FastAPI's TestClient.

## Test Structure

### Test Files
- `conftest.py` - Test configuration and fixtures
- `test_api.py` - Main API endpoint tests

### Test Coverage
The tests provide 100% code coverage and include:

#### Basic Endpoint Tests (`TestBasicEndpoints`)
- Root redirect functionality
- Activities retrieval

#### Signup Functionality Tests (`TestSignupEndpoint`)
- Successful student signup
- Non-existent activity handling
- Duplicate registration prevention
- Activity capacity management
- URL encoding/special characters

#### Participant Removal Tests (`TestRemoveParticipantEndpoint`)
- Successful participant removal
- Non-existent activity handling
- Non-existent participant handling
- URL encoding/special characters

#### Integration Tests (`TestIntegrationScenarios`)
- Complete signup and removal workflows
- Multiple activity signups for same student
- Activity capacity management edge cases

## Running Tests

### Basic Test Run
```bash
/workspaces/skills-getting-started-with-github-copilot/.venv/bin/python -m pytest tests/ -v
```

### With Coverage Report
```bash
/workspaces/skills-getting-started-with-github-copilot/.venv/bin/python -m pytest tests/ --cov=src --cov-report=term-missing -v
```

### Using the Test Runner Script
```bash
./run_tests.sh
```

### Install Test Dependencies
```bash
pip install -r requirements.txt
```

## Test Features

### Fixtures
- `client` - FastAPI TestClient instance
- `reset_activities` - Resets activity data before each test to ensure test isolation

### Test Categories
1. **Unit Tests** - Test individual endpoint functionality
2. **Integration Tests** - Test complete user workflows
3. **Edge Case Tests** - Test boundary conditions and error scenarios
4. **Data Validation Tests** - Test input validation and error handling

### Coverage Goals
- 100% statement coverage
- All API endpoints tested
- All error conditions tested
- All success scenarios tested

## Test Data Management
Tests use a fixture that resets the in-memory activities database before each test to ensure:
- Test isolation
- Consistent starting state
- No test interdependencies
- Predictable test results

## Future Enhancements
- Performance tests
- Load testing
- API documentation tests
- Frontend integration tests