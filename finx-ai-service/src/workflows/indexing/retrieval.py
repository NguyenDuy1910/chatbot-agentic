import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import google.generativeai as gemini_client
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Filter, 
    FieldCondition, 
    MatchValue, 
    MatchText,
    SearchRequest,
    ScoredPoint
)

logger = logging.getLogger(__name__)


class SearchMode(Enum):
    """Search mode options."""
    VECTOR = "vector"           # Pure semantic search
    HYBRID = "hybrid"           # Vector + keyword matching
    METADATA = "metadata"       # Pure metadata filtering


@dataclass
class SearchResult:
    """Enhanced search result with structured data."""
    
    # Qdrant result data
    id: str
    score: float
    
    # Table info
    table_name: str
    database: str
    table_type: str
    table_description: str
    
    # Column info
    column_count: int
    column_names: List[str]
    columns_metadata: List[Dict[str, Any]]
    
    # Keys
    primary_keys: List[str]
    foreign_keys: List[str]
    
    # Full content and metadata
    content: str
    metadata: Dict[str, Any]
    
    # Additional scores (for hybrid search)
    vector_score: Optional[float] = None
    keyword_score: Optional[float] = None
    
    @classmethod
    def from_scored_point(cls, point: ScoredPoint) -> 'SearchResult':
        """Create SearchResult from Qdrant ScoredPoint."""
        payload = point.payload
        
        return cls(
            id=str(point.id),
            score=point.score,
            table_name=payload.get('table_name', ''),
            database=payload.get('database', ''),
            table_type=payload.get('table_type', ''),
            table_description=payload.get('table_description', ''),
            column_count=payload.get('column_count', 0),
            column_names=payload.get('column_names', []),
            columns_metadata=payload.get('columns_metadata', []),
            primary_keys=payload.get('primary_keys', []),
            foreign_keys=payload.get('foreign_keys', []),
            content=payload.get('content', ''),
            metadata=payload
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'score': self.score,
            'table_name': self.table_name,
            'database': self.database,
            'table_type': self.table_type,
            'table_description': self.table_description,
            'column_count': self.column_count,
            'column_names': self.column_names,
            'columns_metadata': self.columns_metadata,
            'primary_keys': self.primary_keys,
            'foreign_keys': self.foreign_keys,
            'vector_score': self.vector_score,
            'keyword_score': self.keyword_score,
        }
    
    def get_column_by_name(self, column_name: str) -> Optional[Dict[str, Any]]:
        """Get column metadata by name."""
        for col in self.columns_metadata:
            if col.get('name', '').lower() == column_name.lower():
                return col
        return None
    
    def find_columns_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Find columns matching keyword in name or description."""
        keyword_lower = keyword.lower()
        matching_columns = []
        
        for col in self.columns_metadata:
            col_name = col.get('name', '').lower()
            col_desc = col.get('description', '').lower()
            
            if keyword_lower in col_name or keyword_lower in col_desc:
                matching_columns.append(col)
        
        return matching_columns


class DBSchemaRetriever:
    """
    Retriever for querying indexed database schemas from vector store.
    
    Supports:
    - Semantic search using embeddings
    - Metadata filtering (database, table type, etc.)
    - Hybrid search (vector + keyword)
    - Result ranking and filtering
    """
    
    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "db_schema",
        gemini_api_key: Optional[str] = None,
        gemini_model: str = "models/text-embedding-004",
    ):
        """
        Initialize DB Schema Retriever.
        
        Args:
            qdrant_url: URL of Qdrant server
            collection_name: Name of the collection with indexed schemas
            gemini_api_key: Google Gemini API key (if None, uses env var)
            gemini_model: Gemini embedding model name
        """
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        self.gemini_model = gemini_model
        
        # Initialize Qdrant client
        self.qdrant_client = QdrantClient(url=qdrant_url)
        
        # Configure Gemini
        if gemini_api_key:
            gemini_client.configure(api_key=gemini_api_key)
        
        logger.info(
            f"DBSchemaRetriever initialized: "
            f"collection={collection_name}, model={gemini_model}"
        )
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for search query.
        
        Args:
            query: Search query text
            
        Returns:
            Embedding vector
        """
        try:
            result = gemini_client.embed_content(
                model=self.gemini_model,
                content=query,
                task_type="retrieval_query"  # Important: use query task type
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise
    
    async def search(
        self,
        query: str,
        limit: int = 10,
        mode: SearchMode = SearchMode.VECTOR,
        filters: Optional[Dict[str, Any]] = None,
        min_score: Optional[float] = None
    ) -> List[SearchResult]:
        """
        Search for database schemas matching the query.
        
        Args:
            query: Natural language search query
            limit: Maximum number of results to return
            mode: Search mode (vector, hybrid, metadata)
            filters: Optional metadata filters
                - database: Filter by database name
                - table_type: Filter by table type
                - has_primary_key: Filter by presence of primary key
                - project_id: Filter by project ID
            min_score: Minimum similarity score threshold
            
        Returns:
            List of SearchResult objects
        """
        logger.info(f"Searching: '{query}' (mode={mode.value}, limit={limit})")
        
        # Generate query embedding
        query_embedding = await self.generate_query_embedding(query)
        
        # Build Qdrant filter
        qdrant_filter = self._build_filter(filters) if filters else None
        
        # Execute search based on mode
        if mode == SearchMode.VECTOR:
            results = self._vector_search(
                query_embedding=query_embedding,
                limit=limit,
                qdrant_filter=qdrant_filter
            )
            logger.info(f"Search with mode=VECTOR returned {len(results)} results")
        elif mode == SearchMode.HYBRID:
            results = await self._hybrid_search(
                query=query,
                query_embedding=query_embedding,
                limit=limit,
                qdrant_filter=qdrant_filter
            )
        else:  # METADATA
            results = self._metadata_search(
                query_embedding=query_embedding,
                limit=limit,
                qdrant_filter=qdrant_filter
            )
        
        # Apply score threshold
        if min_score is not None:
            results = [r for r in results if r.score >= min_score]
        
        logger.info(f"Found {len(results)} results")
        return results
    
    def _vector_search(
        self,
        query_embedding: List[float],
        limit: int,
        qdrant_filter: Optional[Filter]
    ) -> List[SearchResult]:
        """Pure vector similarity search."""
        
        search_results = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=qdrant_filter,
            limit=limit
        )
        
        return [SearchResult.from_scored_point(r) for r in search_results]
    
    async def _hybrid_search(
        self,
        query: str,
        query_embedding: List[float],
        limit: int,
        qdrant_filter: Optional[Filter]
    ) -> List[SearchResult]:
        """
        Hybrid search combining vector similarity and keyword matching.
        
        Strategy:
        1. Get initial results from vector search (2x limit)
        2. Calculate keyword matching scores
        3. Combine scores with weighting
        4. Re-rank and return top results
        """
        
        # Get more results for re-ranking
        initial_limit = min(limit * 2, 100)
        
        vector_results = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=qdrant_filter,
            limit=initial_limit
        )
        
        # Calculate keyword scores
        query_terms = set(query.lower().split())
        
        hybrid_results = []
        for result in vector_results:
            # Get keyword matching score
            keyword_score = self._calculate_keyword_score(
                query_terms=query_terms,
                payload=result.payload
            )
            
            # Combine scores (70% vector, 30% keyword)
            vector_score = result.score
            hybrid_score = (0.7 * vector_score) + (0.3 * keyword_score)
            
            # Create SearchResult with hybrid scoring
            search_result = SearchResult.from_scored_point(result)
            search_result.score = hybrid_score
            search_result.vector_score = vector_score
            search_result.keyword_score = keyword_score
            
            hybrid_results.append(search_result)
        
        # Sort by hybrid score
        hybrid_results.sort(key=lambda x: x.score, reverse=True)
        
        return hybrid_results[:limit]
    
    def _metadata_search(
        self,
        query_embedding: List[float],
        limit: int,
        qdrant_filter: Filter
    ) -> List[SearchResult]:
        """Search primarily based on metadata filters."""
        
        if qdrant_filter is None:
            raise ValueError("Metadata search requires filters")
        
        # Still use vector for ranking, but filter is primary
        search_results = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=qdrant_filter,
            limit=limit
        )
        
        return [SearchResult.from_scored_point(r) for r in search_results]
    
    def _calculate_keyword_score(
        self,
        query_terms: set,
        payload: Dict[str, Any]
    ) -> float:
        """
        Calculate keyword matching score for a result.
        
        Args:
            query_terms: Set of query terms
            payload: Result payload from Qdrant
            
        Returns:
            Keyword matching score (0.0 to 1.0)
        """
        # Extract searchable text from payload
        searchable_parts = [
            payload.get('table_name', ''),
            payload.get('database', ''),
            payload.get('table_description', ''),
            ' '.join(payload.get('column_names', [])),
            payload.get('column_descriptions', ''),  # If available
        ]
        
        searchable_text = ' '.join(searchable_parts).lower()
        text_terms = set(searchable_text.split())
        
        # Calculate term overlap
        overlap = len(query_terms & text_terms)
        score = overlap / len(query_terms) if query_terms else 0.0
        
        # Boost for exact matches in important fields
        table_name = payload.get('table_name', '').lower()
        if any(term in table_name for term in query_terms):
            score += 0.2
        
        # Boost for primary/foreign keys (important tables)
        if payload.get('has_primary_key'):
            score += 0.05
        if payload.get('has_foreign_key'):
            score += 0.05
        
        return min(score, 1.0)
    
    def _build_filter(self, filters: Dict[str, Any]) -> Filter:
        """
        Build Qdrant filter from filter dict.
        
        Args:
            filters: Dictionary of filter conditions
                - database: str
                - table_type: str
                - has_primary_key: bool
                - has_foreign_key: bool
                - project_id: str
                
        Returns:
            Qdrant Filter object
        """
        conditions = []
        
        if 'database' in filters:
            conditions.append(
                FieldCondition(
                    key='database',
                    match=MatchValue(value=filters['database'])
                )
            )
        
        if 'table_type' in filters:
            conditions.append(
                FieldCondition(
                    key='table_type',
                    match=MatchValue(value=filters['table_type'])
                )
            )
        
        if 'has_primary_key' in filters:
            conditions.append(
                FieldCondition(
                    key='has_primary_key',
                    match=MatchValue(value=filters['has_primary_key'])
                )
            )
        
        if 'has_foreign_key' in filters:
            conditions.append(
                FieldCondition(
                    key='has_foreign_key',
                    match=MatchValue(value=filters['has_foreign_key'])
                )
            )
        
        if 'project_id' in filters:
            conditions.append(
                FieldCondition(
                    key='project_id',
                    match=MatchValue(value=filters['project_id'])
                )
            )
        
        return Filter(must=conditions) if conditions else None
    
    async def search_by_table_name(
        self,
        table_name: str,
        database: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Search for specific table by name.
        
        Args:
            table_name: Table name to search for
            database: Optional database name filter
            
        Returns:
            List of matching tables
        """
        filters = {'database': database} if database else {}
        
        # Use the table name as query
        results = await self.search(
            query=f"table {table_name}",
            limit=10,
            mode=SearchMode.HYBRID,
            filters=filters
        )
        
        # Filter to exact or partial matches
        filtered_results = [
            r for r in results
            if table_name.lower() in r.table_name.lower()
        ]
        
        return filtered_results
    
    async def search_by_column_keyword(
        self,
        keyword: str,
        limit: int = 10,
        database: Optional[str] = None
    ) -> List[Tuple[SearchResult, List[Dict[str, Any]]]]:
        """
        Search for tables containing columns matching keyword.
        
        Args:
            keyword: Keyword to search in column names/descriptions
            limit: Maximum number of results
            database: Optional database filter
            
        Returns:
            List of tuples (SearchResult, matching_columns)
        """
        filters = {'database': database} if database else {}
        
        # Search with column keyword
        results = await self.search(
            query=f"column field {keyword}",
            limit=limit * 2,  # Get more for filtering
            mode=SearchMode.HYBRID,
            filters=filters
        )
        
        # Find tables with matching columns
        tables_with_columns = []
        for result in results:
            matching_cols = result.find_columns_by_keyword(keyword)
            if matching_cols:
                tables_with_columns.append((result, matching_cols))
        
        return tables_with_columns[:limit]
    
    async def get_related_tables(
        self,
        table_name: str,
        database: str,
        limit: int = 5
    ) -> List[SearchResult]:
        """
        Find tables related to the given table.
        
        Uses foreign key relationships and semantic similarity.
        
        Args:
            table_name: Source table name
            database: Database name
            limit: Maximum number of related tables
            
        Returns:
            List of related tables
        """
        # First get the source table
        source_tables = await self.search_by_table_name(table_name, database)
        
        if not source_tables:
            logger.warning(f"Table {database}.{table_name} not found")
            return []
        
        source_table = source_tables[0]
        
        # Search for related tables using table description
        query = f"related to {table_name} {source_table.table_description}"
        
        results = await self.search(
            query=query,
            limit=limit + 1,  # +1 because source table will be in results
            filters={'database': database}
        )
        
        # Remove source table from results
        related_tables = [
            r for r in results
            if r.table_name != table_name
        ]
        
        return related_tables[:limit]
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the indexed collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            collection_info = self.qdrant_client.get_collection(
                self.collection_name
            )
            
            return {
                'collection_name': self.collection_name,
                'total_points': collection_info.points_count,
                'vector_size': collection_info.config.params.vectors.size,
                'distance_metric': collection_info.config.params.vectors.distance,
                'status': collection_info.status
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}


# Convenience functions for quick usage

async def search_schemas(
    query: str,
    collection_name: str = "db_schema",
    limit: int = 10,
    qdrant_url: str = "http://localhost:6333",
    gemini_api_key: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None
) -> List[SearchResult]:
    """
    Quick search for database schemas.
    
    Args:
        query: Search query
        collection_name: Qdrant collection name
        limit: Maximum results
        qdrant_url: Qdrant URL
        gemini_api_key: Gemini API key
        filters: Optional filters
        
    Returns:
        List of search results
    """
    retriever = DBSchemaRetriever(
        qdrant_url=qdrant_url,
        collection_name=collection_name,
        gemini_api_key=gemini_api_key
    )
    
    return await retriever.search(
        query=query,
        limit=limit,
        mode=SearchMode.HYBRID,
        filters=filters
    )


async def find_table(
    table_name: str,
    database: Optional[str] = None,
    collection_name: str = "db_schema",
    qdrant_url: str = "http://localhost:6333",
    gemini_api_key: Optional[str] = None
) -> Optional[SearchResult]:
    """
    Find a specific table by name.
    
    Args:
        table_name: Table name
        database: Optional database name
        collection_name: Qdrant collection
        qdrant_url: Qdrant URL
        gemini_api_key: Gemini API key
        
    Returns:
        SearchResult if found, None otherwise
    """
    retriever = DBSchemaRetriever(
        qdrant_url=qdrant_url,
        collection_name=collection_name,
        gemini_api_key=gemini_api_key
    )
    
    results = await retriever.search_by_table_name(table_name, database)
    return results[0] if results else None
