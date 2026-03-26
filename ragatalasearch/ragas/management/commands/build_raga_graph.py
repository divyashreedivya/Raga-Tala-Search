"""
Management command to build the Raga Similarity Graph.

Considers both note content (Jaccard similarity) and note order (LCS).
Combined metric: 60% Jaccard + 40% Sequence order similarity.

Usage:
    python manage.py build_raga_graph [--threshold 0.3]
"""

from django.core.management.base import BaseCommand, CommandError
from ragas.graph_builder import generate_raga_similarity_graph
from ragas.models import Raga

class Command(BaseCommand):
    help = 'Build the Raga similarity graph based on shared notes and their order in arohanam/avarohanam'

    def add_arguments(self, parser):
        parser.add_argument(
            '--threshold',
            type=float,
            default=0.3,
            help='Minimum similarity threshold (0-1) for creating edges. Uses combined metric: 60 percent note content + 40 percent sequence order. Default: 0.3'
        )
        parser.add_argument(
            '--min-ragas',
            type=int,
            default=2,
            help='Minimum number of ragas required to build graph. Default: 2'
        )

    def handle(self, *args, **options):
        threshold = options['threshold']
        min_ragas = options['min_ragas']

        # Validate threshold
        if not (0 <= threshold <= 1):
            raise CommandError(f'Threshold must be between 0 and 1, got {threshold}')

        # Check if enough ragas exist
        raga_count = Raga.objects.count()
        if raga_count < min_ragas:
            raise CommandError(
                f'Not enough ragas to build graph. Found: {raga_count}, Required: {min_ragas}'
            )

        self.stdout.write(
            self.style.SUCCESS(f'Building Raga Similarity Graph with threshold={threshold}...')
        )
        self.stdout.write(f'Total ragas in database: {raga_count}')

        try:
            stats = generate_raga_similarity_graph(similarity_threshold=threshold)
            
            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.SUCCESS('✓ Graph built successfully!'))
            self.stdout.write('='*60)
            
            self.stdout.write(f'\nStatistics:')
            self.stdout.write(f'  - Nodes (Ragas): {stats["nodes_count"]}')
            self.stdout.write(f'  - Edges (Similarities): {stats["edges_count"]}')
            self.stdout.write(f'  - Graph Density: {stats["density"]:.4f}')
            self.stdout.write(f'  - Connected Components: {stats["connected_components"]}')
            self.stdout.write(f'  - Similarity Threshold: {stats["similarity_threshold"]:.2f}')
            self.stdout.write(f'  - Edges Stored in DB: {stats["edges_stored"]}')
            
            # Calculate some additional statistics
            graph = stats['graph']
            avg_degree = 2 * graph.number_of_edges() / graph.number_of_nodes() if graph.number_of_nodes() > 0 else 0
            self.stdout.write(f'  - Average Node Degree: {avg_degree:.2f}')
            
            self.stdout.write(self.style.SUCCESS('\nYou can now view the graph at: /ragas/graph/'))
            
        except ValueError as e:
            raise CommandError(f'Error: {str(e)}')
        except Exception as e:
            raise CommandError(f'Unexpected error: {str(e)}')
