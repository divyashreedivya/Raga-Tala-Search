from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from ragas.models import Raga, Melakarta, RagaEdge
from django.views.generic import DetailView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
import json
from ragas.embedding_model import get_embedding_model
from ragas.graph_builder import calculate_combined_similarity, generate_raga_similarity_graph, get_raga_neighbors
from django.db.models import Q

class SearchRaga(View):
    def get(self,request):
        return render(request, 'ragas/raga_search.html')

class RagaListView(View):
    template_name = 'ragas/raga_list.html'

    def get(self,request):
        strval = request.GET.get("search", False)
        raga_exact = None
        if strval:
            raga_list = Raga.objects.all().filter(name__contains = strval).select_related()
        else:
            #raga_list = Raga.objects.all()[:5]
            raga_list = None
            
        ctx ={'raga_list':raga_list , 'search':strval}
        return render(request, self.template_name, ctx)

class RagaArListView(View):
    template_name = 'ragas/raga_ar_list.html'

    def get(self, request):
        strval = request.GET.get("search", False)
        if strval:
            raga_list = Raga.objects.all().filter(arohanam__contains = strval.rstrip()).select_related()
        else:
            raga_list = None
        ctx = {'raga_list':raga_list, 'search':strval}       
        return render(request, self.template_name, ctx)       

class RagaAvListView(View):
    template_name = 'ragas/raga_av_list.html'

    def get(self, request):
        strval = request.GET.get("search", False)
        if strval:
            raga_list = Raga.objects.all().filter(avarohanam__contains = strval.rstrip()).select_related()
        else:
            raga_list = None
        ctx = {'raga_list':raga_list, 'search':strval}       
        return render(request, self.template_name, ctx)   

class RagaTableView(View):
    template_name='ragas/raga_table.html'
    def get(self, request):
        mela_list = Raga.objects.all().filter(mela_true=True) 
        return render(request, self.template_name, {'mela_list':mela_list})       


class RagaDetailView(DetailView):
    model =Raga
    template_name = 'ragas/raga_detail.html'
    def get(self, request, pk):
        x = Raga.objects.all().get(id= pk)
        ctx = {'raga': x}
        return render(request, self.template_name, ctx)

class RagaMelaDetailView(DetailView):
    model = Raga
    template_name = 'ragas/raga_mela_detail.html'
    def get(self, request, pk):
        x = Raga.objects.all().get(id=pk)
        y = Raga.objects.all().filter(mela_id = x.mela_id)[1:]
        ctx = {'raga':x,'janyas':y} 
        return render(request, self.template_name, ctx)


# ===== Raga Similarity Graph Views =====

def graph_data_api(request):
    """
    API endpoint to retrieve graph data for visualization.
    Returns nodes and links for D3.js/Canvas visualizer.
    Supports full graph or focused subgraph around a selected raga.
    Query params:
      - raga_id: int (optional) to focus on a raga and its top neighbors
      - max_neighbors: int (optional, default=30)
    """
    from ragas.models import Raga, RagaEdge
    from ragas.graph_builder import get_raga_neighbors

    def format_node(raga):
        note_count = 0
        if raga.arohanam or raga.avarohanam:
            note_count = len(set((raga.arohanam or '').split() + (raga.avarohanam or '').split()))
        return {
            'id': raga.id,
            'name': raga.name,
            'label': raga.name,
            'title': f"{raga.name}\nNotes: {note_count}",
            'arohanam': raga.arohanam,
            'avarohanam': raga.avarohanam,
            'note_count': note_count,
            'value': note_count,
        }

    try:
        raga_id = request.GET.get('raga_id')
        max_neighbors = int(request.GET.get('max_neighbors', 30))

        if raga_id:
            raga_id = int(raga_id)
            neighbors_data = get_raga_neighbors(raga_id)

            root_raga = Raga.objects.get(id=raga_id)
            neighbor_ids = [n['id'] for n in neighbors_data['similar_ragas'][:max_neighbors]]
            node_ids = [raga_id] + neighbor_ids

            nodes = [format_node(root_raga)]
            nodes.extend([format_node(r) for r in Raga.objects.filter(id__in=neighbor_ids)])

            edges = []
            root_edges = RagaEdge.objects.filter(
                (Q(source_raga_id=raga_id) & Q(target_raga_id__in=neighbor_ids)) |
                (Q(target_raga_id=raga_id) & Q(source_raga_id__in=neighbor_ids))
            ).select_related('source_raga', 'target_raga')

            for edge in root_edges:
                edges.append({
                    'source': edge.source_raga_id,
                    'target': edge.target_raga_id,
                    'weight': edge.similarity_score,
                    'value': edge.similarity_score,
                    'shared_notes': edge.shared_notes,
                    'total_notes': edge.total_notes,
                    'label': f"Similarity: {edge.similarity_score:.2%}"
                })

            return JsonResponse({
                'nodes': nodes,
                'links': edges,
                'total_nodes': len(nodes),
                'total_links': len(edges),
                'focused_raga': raga_id,
                'max_neighbors': max_neighbors
            })

        else:
            from ragas.graph_builder import get_graph_data_for_visualization
            data = get_graph_data_for_visualization()
            return JsonResponse(data)

    except Raga.DoesNotExist:
        return JsonResponse({'error': 'Raga not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['POST'])
def build_graph_api(request):
    """
    API endpoint to build/rebuild the raga similarity graph.
    Query parameter: threshold (default 0.3)
    """
    try:
        threshold = float(request.GET.get('threshold', 0.3))
        stats = generate_raga_similarity_graph(threshold)
        
        return Response({
            'success': True,
            'message': f'Graph built successfully with {stats["edges_stored"]} edges',
            'statistics': {
                'nodes_count': stats['nodes_count'],
                'edges_count': stats['edges_count'],
                'density': float(stats['density']),
                'connected_components': stats['connected_components'],
                'similarity_threshold': stats['similarity_threshold']
            }
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def raga_neighbors_api(request, raga_id):
    """
    API endpoint to get similar ragas for a specific raga.
    """
    try:
        data = get_raga_neighbors(raga_id)
        return Response(data, status=status.HTTP_200_OK)
    except Raga.DoesNotExist:
        return Response(
            {'error': 'Raga not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class RagaSimilarityGraphView(View):
    """
    View to render the interactive raga similarity graph visualization.
    """
    template_name = 'ragas/raga_similarity_graph.html'
    
    def get(self, request):
        # Get graph statistics
        edges_count = RagaEdge.objects.count()
        ragas_count = Raga.objects.count()
        
        if edges_count > 0:
            avg_similarity = RagaEdge.objects.values_list('similarity_score', flat=True)
            avg_sim = sum(avg_similarity) / len(avg_similarity)
        else:
            avg_sim = 0
        
        raga_list = Raga.objects.all().order_by('name').values('id', 'name')

        ctx = {
            'ragas_count': ragas_count,
            'edges_count': edges_count,
            'avg_similarity': avg_sim,
            'raga_list': raga_list,
        }
        return render(request, self.template_name, ctx)


class FindSimilarRagasView(View):
    """
    View to render the find similar ragas search interface.
    """
    template_name = 'ragas/find_similar_ragas.html'
    
    def get(self, request):
        return render(request, self.template_name)


# ===== Semantic Similarity API Views =====

@api_view(['POST'])
def semantic_similarity_search(request):
    """
    API endpoint for semantic similarity search using ML embeddings.
    Accepts a raga ID or custom note sequence and returns similar ragas.
    """
    try:
        # Get query parameters
        raga_id = request.data.get('raga_id')
        custom_arohanam = request.data.get('arohanam', '').strip()
        custom_avarohanam = request.data.get('avarohanam', '').strip()
        top_k = min(int(request.data.get('top_k', 10)), 50)  # Max 50 results

        if not raga_id and not (custom_arohanam or custom_avarohanam):
            return Response(
                {'error': 'Either raga_id or note sequences (arohanam/avarohanam) must be provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        model = get_embedding_model()

        # Get query embedding
        if raga_id:
            # Use existing raga
            try:
                query_raga = Raga.objects.get(id=raga_id)
                if not query_raga.embedding:
                    return Response(
                        {'error': 'Selected raga does not have an embedding. Please generate embeddings first.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                query_embedding = query_raga.get_embedding()
                query_info = {
                    'id': query_raga.id,
                    'name': query_raga.name,
                    'arohanam': query_raga.arohanam,
                    'avarohanam': query_raga.avarohanam,
                }
            except Raga.DoesNotExist:
                return Response(
                    {'error': 'Raga not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Use custom note sequence
            features = model.extract_features(custom_arohanam, custom_avarohanam)
            query_embedding = model.generate_embedding(features)
            query_info = {
                'name': 'Custom Query',
                'arohanam': custom_arohanam,
                'avarohanam': custom_avarohanam,
            }

        # Get all ragas with embeddings
        ragas_with_embeddings = Raga.objects.exclude(embedding__isnull=True).exclude(embedding='')

        if not ragas_with_embeddings.exists():
            return Response(
                {'error': 'No ragas with embeddings found. Please generate embeddings first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Build embeddings dictionary
        all_embeddings = {}
        for raga in ragas_with_embeddings:
            # Exclude the searched raga itself from candidates
            if raga_id and raga.id == int(raga_id):
                continue
            try:
                embedding = raga.get_embedding()
                if embedding:
                    all_embeddings[raga.id] = embedding
            except (json.JSONDecodeError, TypeError):
                continue  # Skip invalid embeddings

        if not all_embeddings:
            return Response(
                {'error': 'No valid embeddings found'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Find similar ragas
        similar_ragas = model.find_similar_ragas(query_embedding, all_embeddings, top_k)

        query_arohanam_notes = query_info.get('arohanam', '').split() if query_info.get('arohanam') else []
        query_avarohanam_notes = query_info.get('avarohanam', '').split() if query_info.get('avarohanam') else []
        query_notes_set = set(query_arohanam_notes + query_avarohanam_notes)

        # Add order/content note similarity boost and produce a combined ranking
        enriched_results = []
        for candidate_raga_id, semantic_score in similar_ragas:
            raga = Raga.objects.get(id=candidate_raga_id)

            candidate_arohanam_notes = raga.arohanam.split() if raga.arohanam else []
            candidate_avarohanam_notes = raga.avarohanam.split() if raga.avarohanam else []
            candidate_notes_set = set(candidate_arohanam_notes + candidate_avarohanam_notes)

            note_score, _, _ = calculate_combined_similarity(
                query_notes_set,
                candidate_notes_set,
                query_info.get('arohanam', ''),
                query_info.get('avarohanam', ''),
                raga.arohanam or '',
                raga.avarohanam or ''
            )

            combined_score = (0.6 * semantic_score) + (0.4 * note_score)

            enriched_results.append({
                'id': raga.id,
                'name': raga.name,
                'arohanam': raga.arohanam,
                'avarohanam': raga.avarohanam,
                'similarity_score': round(semantic_score, 4),
                'note_similarity': round(note_score, 4),
                'combined_score': round(combined_score, 4),
                'mela': raga.mela.name if raga.mela else None,
                'mela_num': raga.mela.num if raga.mela else None,
            })

        enriched_results.sort(key=lambda x: x['combined_score'], reverse=True)

        # Limit to top_k in case additional records are present
        results = enriched_results[:top_k]

        response_data = {
            'query': query_info,
            'results': results,
            'total_results': len(results),
            'embedding_model': model.model_name,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def generate_raga_embeddings(request):
    """
    API endpoint to trigger embedding generation for all ragas.
    This is a background task that may take some time.
    """
    try:
        from django.core.management import call_command
        from django.db import connection

        # Check if embeddings already exist
        existing_count = Raga.objects.exclude(embedding__isnull=True).exclude(embedding='').count()
        total_count = Raga.objects.count()

        if existing_count == total_count:
            return Response({
                'message': 'All ragas already have embeddings',
                'total_ragas': total_count,
                'with_embeddings': existing_count,
            }, status=status.HTTP_200_OK)

        # Run the management command
        # Note: In production, this should be run as a background task
        call_command('generate_embeddings', force=True)

        # Get updated counts
        new_count = Raga.objects.exclude(embedding__isnull=True).exclude(embedding='').count()

        return Response({
            'message': f'Embeddings generated successfully for {new_count - existing_count} ragas',
            'total_ragas': total_count,
            'with_embeddings': new_count,
            'previously_had_embeddings': existing_count,
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def embedding_status(request):
    """
    API endpoint to check the status of embeddings in the database.
    """
    try:
        total_ragas = Raga.objects.count()
        ragas_with_embeddings = Raga.objects.exclude(embedding__isnull=True).exclude(embedding='').count()

        return Response({
            'total_ragas': total_ragas,
            'ragas_with_embeddings': ragas_with_embeddings,
            'embedding_coverage': ragas_with_embeddings / total_ragas if total_ragas > 0 else 0,
            'model_name': get_embedding_model().model_name,
            'embedding_dimension': get_embedding_model().embedding_dim,
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
