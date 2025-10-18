







    
        
        
    
        
            
        
        
        
        
        
        
    
        
            
        
        
        
        
        
    
        
            
        
        
        
            
        
        
        
        
        
    
        
        
        
        
        
        
        from src.pipelines.indexing.db_schema import DBSchema
        from src.providers.google_genai import GoogleGenAIEmbedderProvider
        from src.providers.qdrant import QdrantDocumentStoreProvider
        
        embedder_provider = GoogleGenAIEmbedderProvider(
            api_key="your-google-api-key",
            model="models/embedding-001"
        )
        
        document_store_provider = QdrantDocumentStoreProvider(
            url="http://localhost:6333",
            collection_name="db_schema"
        )
        
        db_schema_pipeline = DBSchema(
            embedder_provider=embedder_provider,
            document_store_provider=document_store_provider
        )
        
        mdl_json = json.dumps(mdl)
        result = await db_schema_pipeline.run(
            mdl_str=mdl_json,
            project_id=project_id
        )
        
        print(f"Indexing complete: {result}")
        """)
        
        logger.info("\n✓ MDL is ready for indexing")
        logger.info(f"✓ Use the MDL file at: {self.output_dir / 'enriched_mdl.json'}")
    
    async def run_complete_workflow(
        self,
        tables=None,
        project_id: str = "athena_demo_project",
        skip_enrichment: bool = False
    ):
        """
        Run the complete end-to-end workflow
        
        Args:
            tables: Optional list of specific tables
            project_id: Project ID for indexing
            skip_enrichment: Skip enrichment step
        """
        logger.info("\n" + "=" * 80)
        logger.info("FinX Engine - End-to-End Workflow")
        logger.info("=" * 80)
        
        try:
            schema_metadata = self.step1_introspect_schema(tables)
            
            mdl = self.step2_generate_mdl(schema_metadata)
            
            if not skip_enrichment:
                mdl = self.step3_enrich_mdl(mdl)
            
            await self.step4_index_to_finx_ai(mdl, project_id)
            
            logger.info("\n" + "=" * 80)
            logger.info("✓ Workflow Complete!")
            logger.info("=" * 80)
            logger.info(f"\nOutput files saved to: {self.output_dir}")
            logger.info(f"  - generated_mdl.json")
            if not skip_enrichment:
                logger.info(f"  - enriched_mdl.json")
            
        except Exception as e:
            logger.error(f"\n✗ Workflow failed: {str(e)}")
            raise


async def main():
    
    demo = EndToEndDemo(
        aws_region="us-east-1",
        athena_database="my_database",
        s3_output="s3://my-bucket/athena-results/",
        finx_ai_service_path="../finx-ai-service"
    )
    
    
    
    
    logger.info("\n" + "=" * 80)
    logger.info("To run this example:")
    logger.info("  1. Update AWS configuration in the code")
    logger.info("  2. Ensure AWS credentials are configured")
    logger.info("  3. Uncomment one of the workflow options above")
    logger.info("  4. Run: python end_to_end_example.py")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
