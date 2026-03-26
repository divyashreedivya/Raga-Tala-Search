"""
Management command to generate embeddings for all ragas using the ML model.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from ragas.models import Raga
from ragas.embedding_model import get_embedding_model
import json
import time

class Command(BaseCommand):
    help = 'Generate ML embeddings for all ragas in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Number of ragas to process in each batch'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Regenerate embeddings even if they already exist'
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        force = options['force']

        # Get all ragas
        if force:
            ragas = Raga.objects.all()
            self.stdout.write(f'Processing all {ragas.count()} ragas (forced regeneration)')
        else:
            ragas = Raga.objects.filter(embedding__isnull=True)
            self.stdout.write(f'Processing {ragas.count()} ragas without embeddings')

        if not ragas.exists():
            self.stdout.write(self.style.SUCCESS('All ragas already have embeddings!'))
            return

        # Initialize the embedding model
        self.stdout.write('Loading embedding model...')
        model = get_embedding_model()
        model.load_model()
        self.stdout.write(self.style.SUCCESS('Model loaded successfully'))

        # Process ragas in batches
        total_processed = 0
        start_time = time.time()

        for i in range(0, ragas.count(), batch_size):
            batch = ragas[i:i + batch_size]
            batch_data = []

            self.stdout.write(f'Processing batch {i//batch_size + 1} ({len(batch)} ragas)...')

            # Extract features for this batch
            raga_features = []
            raga_objects = []

            for raga in batch:
                features = model.extract_features(raga.arohanam, raga.avarohanam)
                raga_features.append(features)
                raga_objects.append(raga)

            # Generate embeddings for the batch
            try:
                embeddings = model.generate_embeddings_batch(raga_features)

                # Update database with embeddings
                with transaction.atomic():
                    for raga, embedding in zip(raga_objects, embeddings):
                        raga.set_embedding(embedding)
                        raga.save(update_fields=['embedding'])

                total_processed += len(batch)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Batch completed: {len(batch)} ragas processed'
                    )
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error processing batch: {str(e)}'
                    )
                )
                continue

        elapsed_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f'Embedding generation completed! '
                f'Total processed: {total_processed} ragas '
                f'Time: {elapsed_time:.2f}s '
                f'Average: {total_processed/elapsed_time:.2f} ragas/sec'
            )
        )