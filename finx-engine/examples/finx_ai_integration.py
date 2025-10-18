






    
    
    
    
    
    
    
    
    
        
        
        


    
    
    
    
    
    


    
    
    
    
    
    
    


    
    
    
        
        
        
        
        
        


    
    
    from src.pipelines.indexing.db_schema import DBSchema
    from src.providers.google_genai import GoogleGenAIEmbedderProvider
    from src.providers.qdrant import QdrantDocumentStoreProvider
    
    embedder_provider = GoogleGenAIEmbedderProvider(
        api_key="your-api-key",
        model="models/embedding-001"
    )
    
    document_store_provider = QdrantDocumentStoreProvider(
        url="http://localhost:6333",
        collection_name="db_schema"
    )
    
    db_schema_pipeline = DBSchema(
        embedder_provider=embedder_provider,
        document_store_provider=document_store_provider,
        column_batch_size=50
    )
    
    result = await integration.index_schema_async(
        mdl=mdl,
        db_schema_pipeline=db_schema_pipeline,
        project_id="my_project"
    )
    """
    
    logger.info("Sample pipeline configuration:")
    print(sample_config)


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("FinX Engine - FinX AI Service Integration Examples")
    print("=" * 80)
    print("\nNOTE: These examples require:")
    print("  1. Valid AWS credentials")
    print("  2. An existing Athena database")
    print("  3. finx-ai-service properly configured")
    print("  4. Configured EmbedderProvider and DocumentStoreProvider")
    print("=" * 80 + "\n")
    
    
    create_sample_pipeline_config()
    
    logger.info("\nExamples complete!")
