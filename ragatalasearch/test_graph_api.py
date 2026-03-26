#!/usr/bin/env python
import requests

# Test graph data API
response = requests.get('http://127.0.0.1:8000/ragas/api/graph/data/')
print(f'Graph API Status: {response.status_code}')

if response.status_code == 200:
    data = response.json()
    nodes = data.get('nodes', [])
    print(f'Nodes loaded: {len(nodes)}')
    if nodes:
        print(f'First node: {nodes[0]}')
else:
    print(f'Error: {response.text}')