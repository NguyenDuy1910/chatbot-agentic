






    
    
    
    
    
    
    
    
    


    
    
    
    
    
    
    
    


    
    
    
    
    
                    SELECT 
                        c.customer_id,
                        c.name,
                        COUNT(o.order_id) as total_orders,
                        SUM(o.total_amount) as total_spent
                    FROM customers c
                    LEFT JOIN orders o ON c.customer_id = o.customer_id
                    GROUP BY c.customer_id, c.name
                """
            }
        ],
        "metrics": [
            {
                "name": "revenue_by_customer",
                "baseObject": "orders",
                "dimension": [
                    {"name": "customer_id", "type": "INTEGER"}
                ],
                "measure": [
                    {
                        "name": "total_revenue",
                        "type": "DECIMAL",
                        "expression": "SUM(total_amount)"
                    },
                    {
                        "name": "order_count",
                        "type": "INTEGER",
                        "expression": "COUNT(order_id)"
                    }
                ]
            }
        ]
    }
    
    enriched_mdl = generator.enrich_mdl(mdl, enrichments)
    
    output_path = Path(__file__).parent / "output" / "enriched_mdl.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(enriched_mdl, f, indent=2)
    
    logger.info(f"\nEnriched MDL saved to: {output_path}")
    logger.info(f"Added {len(enrichments['views'])} views")
    logger.info(f"Added {len(enrichments['metrics'])} metrics")


def example_save_and_load():
