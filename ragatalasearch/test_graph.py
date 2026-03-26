#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ragatalasearch.settings')
django.setup()

from ragas.graph_builder import get_graph_data_for_visualization
import json

try:
    data = get_graph_data_for_visualization()
    print(f"✓ Graph data loaded successfully!")
    print(f"  Nodes: {data['total_nodes']}")
    print(f"  Links: {data['total_links']}")
    print(f"\n✓ Sample node:")
    if data['nodes']:
        print(f"    {json.dumps(data['nodes'][0], indent=4)}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
