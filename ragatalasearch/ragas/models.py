from django.db import models
from django.core.files.storage import default_storage
import json

class Melakarta(models.Model):
    name = models.CharField(max_length= 128)
    num = models.IntegerField(default =0)
    def __str__(self):
        return self.name

class Raga(models.Model):
    name = models.CharField(max_length= 128)
    arohanam = models.CharField(max_length = 256)
    avarohanam = models.CharField(max_length = 256)
    mela_true = models.BooleanField(default= False)
    mela = models.ForeignKey(Melakarta , on_delete= models.CASCADE)
    embedding = models.TextField(
        null=True,
        blank=True,
        help_text="ML-generated embedding vector stored as JSON"
    )

    def __str__(self):
        return self.name

    def get_embedding(self):
        """Get embedding as list of floats"""
        if self.embedding:
            return json.loads(self.embedding)
        return None

    def set_embedding(self, embedding_list):
        """Set embedding from list of floats"""
        self.embedding = json.dumps(embedding_list)

class RagaEdge(models.Model):
    """
    Represents an edge in the Raga Similarity Graph.
    Stores similarity relationships between ragas based on shared arohanam/avarohanam notes.
    """
    source_raga = models.ForeignKey(Raga, on_delete=models.CASCADE, related_name='outgoing_edges')
    target_raga = models.ForeignKey(Raga, on_delete=models.CASCADE, related_name='incoming_edges')
    similarity_score = models.FloatField(default=0.0, help_text="Jaccard similarity between 0 and 1")
    shared_notes = models.IntegerField(default=0, help_text="Number of shared notes")
    total_notes = models.IntegerField(default=0, help_text="Total unique notes in union")
    
    class Meta:
        unique_together = ('source_raga', 'target_raga')
        ordering = ['-similarity_score']
    
    def __str__(self):
        return f"{self.source_raga.name} -> {self.target_raga.name} ({self.similarity_score:.2f})"
