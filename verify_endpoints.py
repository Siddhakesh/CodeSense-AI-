import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000"

def test_health():
    print(f"Testing Health Check at {BASE_URL}/health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("âœ… Health Check Passed:", response.json())
            return True
        else:
            print(f"âŒ Health Check Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"âŒ Health Check Error: {e}")
        return False

def test_analyze():
    # Note: This test requires internet access to clone a repo.
    # We will use a small public repo or a dummy one.
    # Using a small popular repo to test.
    repo_url = "https://github.com/octocat/Hello-World.git"
    print(f"\nTesting Analyze Endpoint with {repo_url}...")
    
    try:
        response = requests.post(f"{BASE_URL}/api/analyze", json={"repo_url": repo_url})
        if response.status_code == 200:
            data = response.json()
            print("âœ… Analysis Passed!")
            print(f"  Repo ID: {data.get('repo_id')}")
            print(f"  Framework: {data.get('index', {}).get('framework')}")
            print(f"  Files: {len(data.get('index', {}).get('files', {}))}")
            return True
        else:
            print(f"âŒ Analysis Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"âŒ Analysis Error: {e}")
        return False

if __name__ == "__main__":
    print("Waiting for server to be ready...")
    time.sleep(2) # Give it a moment if just started
    
    if test_health():
        # Only run analyze if health passes
        # Note: Analyze might fail if git is not in path or network issues, but we want to see it try.
        test_analyze()
