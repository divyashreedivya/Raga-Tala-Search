#!/usr/bin/env python
"""
Test the semantic similarity API endpoint.
"""

import requests
import json

def test_api():
    url = 'http://127.0.0.1:8000/ragas/api/similarity/search/'

    # Test data
    data = {
        'raga_id': 1,
        'top_k': 3
    }

    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("API Response:")
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == '__main__':
    test_api()