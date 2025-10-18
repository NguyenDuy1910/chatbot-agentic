"""
Test script for Question Recommendation pipeline with Gemini Flash 2.5

This script tests the prompt agent with Google's Gemini Flash 2.5 model.
"""

import asyncio
import logging
import os
import sys
from typing import Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in parent directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from haystack_integrations.components.generators.google_ai import GoogleAIGeminiGenerator
from haystack.utils import Secret
from src.core.provider import LLMProvider
from src.pipelines.generation.question_recommendation import QuestionRecommendation

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """Gemini LLM Provider implementation"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash-exp",
        generation_kwargs: dict = None
    ):
        self._api_key = api_key
        self._model = model
        self._model_kwargs = generation_kwargs or {}
        self._context_window_size = 1000000  # Gemini 2.0 Flash has 1M token context
    
    def get_generator(self, system_prompt: str = None, generation_kwargs: dict = None):
        """Get Gemini generator"""
        # Filter out unsupported kwargs for Gemini
        all_kwargs = {**self._model_kwargs, **(generation_kwargs or {})}
        
        # Remove response_format as it's not supported by Gemini
        gemini_kwargs = {k: v for k, v in all_kwargs.items() if k != 'response_format'}
        
        # Add JSON mode instruction to system prompt instead
        use_json_mode = 'response_format' in all_kwargs
        
        async def generator_wrapper(prompt: str) -> dict:
            """Async wrapper for Gemini generator"""
            generator = GoogleAIGeminiGenerator(
                api_key=Secret.from_token(self._api_key),
                model=self._model,
                generation_config=gemini_kwargs
            )
            
            # Combine system prompt with user prompt if system prompt exists
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Add JSON instruction if needed
            if use_json_mode:
                full_prompt = f"{full_prompt}\n\nIMPORTANT: You MUST respond with valid JSON only. Do not include any explanatory text before or after the JSON."
            
            result = generator.run(parts=[full_prompt])
            
            # Extract text from response
            replies = []
            for reply in result.get("replies", []):
                if hasattr(reply, 'text'):
                    replies.append(reply.text)
                elif isinstance(reply, str):
                    replies.append(reply)
            
            return {"replies": replies}
        
        return generator_wrapper


async def test_question_recommendation():
    """Test the question recommendation pipeline with Gemini Flash 2.5"""
    
    print("=" * 80)
    print("Testing Question Recommendation with Gemini Flash 2.5")
    print("=" * 80)
    
    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n❌ Error: GOOGLE_API_KEY environment variable not set")
        print("Please set it with: export GOOGLE_API_KEY='your-api-key'")
        return
    
    print(f"\n✓ API Key found: {api_key[:10]}...")
    
    # Initialize Gemini provider
    print("\n📦 Initializing Gemini Provider...")
    provider = GeminiProvider(
        api_key=api_key,
        model="gemini-2.0-flash-exp"
    )
    print(f"✓ Model: {provider.get_model()}")
    print(f"✓ Context Window: {provider.get_context_window_size():,} tokens")
    
    # Create pipeline
    print("\n🔧 Creating Question Recommendation Pipeline...")
    pipeline = QuestionRecommendation(llm_provider=provider)
    print("✓ Pipeline created successfully")
    
    # Sample data model context
    print("\n📊 Preparing sample data model...")
    contexts = [
        """
        Database Schema: E-commerce Platform
        
        Table: customers
        - customer_id: INTEGER (Primary Key)
        - name: VARCHAR(255)
        - email: VARCHAR(255)
        - registration_date: DATE
        - country: VARCHAR(100)
        - lifetime_value: DECIMAL(10,2)
        
        Table: orders
        - order_id: INTEGER (Primary Key)
        - customer_id: INTEGER (Foreign Key -> customers.customer_id)
        - order_date: TIMESTAMP
        - total_amount: DECIMAL(10,2)
        - status: VARCHAR(50) (pending, completed, cancelled)
        - shipping_address: TEXT
        
        Table: products
        - product_id: INTEGER (Primary Key)
        - product_name: VARCHAR(255)
        - category: VARCHAR(100)
        - price: DECIMAL(10,2)
        - stock_quantity: INTEGER
        - supplier: VARCHAR(255)
        
        Table: order_items
        - order_item_id: INTEGER (Primary Key)
        - order_id: INTEGER (Foreign Key -> orders.order_id)
        - product_id: INTEGER (Foreign Key -> products.product_id)
        - quantity: INTEGER
        - unit_price: DECIMAL(10,2)
        """
    ]
    
    print("✓ Sample schema loaded (E-commerce Platform)")
    
    # Test parameters
    categories = [
        "Descriptive Questions",
        "Segmentation Questions",
        "Comparative Questions",
        "Data Quality/Accuracy Questions"
    ]
    
    print(f"\n🎯 Test Parameters:")
    print(f"  - Max Questions: 5")
    print(f"  - Max Categories: 3")
    print(f"  - Language: English")
    print(f"  - Categories: {len(categories)}")
    
    # Run pipeline
    print("\n🚀 Running Question Recommendation Pipeline...")
    print("   (This may take 10-30 seconds depending on model response time)")
    
    try:
        result = await pipeline.run(
            contexts=contexts,
            previous_questions=[],
            categories=categories,
            language="en",
            max_questions=5,
            max_categories=3
        )
        
        print("\n✅ Pipeline execution completed successfully!")
        
        # Display results
        print("\n" + "=" * 80)
        print("GENERATED QUESTIONS")
        print("=" * 80)
        
        questions = result.get("normalized", {})
        
        if isinstance(questions, dict) and "questions" in questions:
            question_list = questions["questions"]
            print(f"\n📋 Total Questions Generated: {len(question_list)}")
            print()
            
            for idx, q in enumerate(question_list, 1):
                print(f"{idx}. Question: {q.get('question', 'N/A')}")
                print(f"   Category: {q.get('category', 'N/A')}")
                print()
        else:
            print("\n⚠️ Unexpected response format:")
            print(questions)
        
        # Test with previous questions
        print("\n" + "=" * 80)
        print("Testing with Previous Questions (Follow-up)")
        print("=" * 80)
        
        previous_questions = [
            "What was the total revenue last quarter?",
            "Which products had the highest sales?"
        ]
        
        print(f"\n📝 Previous Questions:")
        for pq in previous_questions:
            print(f"  - {pq}")
        
        print("\n🚀 Generating follow-up questions...")
        
        result2 = await pipeline.run(
            contexts=contexts,
            previous_questions=previous_questions,
            categories=categories,
            language="en",
            max_questions=3,
            max_categories=2
        )
        
        print("\n✅ Follow-up questions generated!")
        
        questions2 = result2.get("normalized", {})
        
        if isinstance(questions2, dict) and "questions" in questions2:
            question_list2 = questions2["questions"]
            print(f"\n📋 Follow-up Questions Generated: {len(question_list2)}")
            print()
            
            for idx, q in enumerate(question_list2, 1):
                print(f"{idx}. Question: {q.get('question', 'N/A')}")
                print(f"   Category: {q.get('category', 'N/A')}")
                print()
        
        print("\n" + "=" * 80)
        print("✨ Test completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during pipeline execution:")
        print(f"   {type(e).__name__}: {str(e)}")
        logger.exception("Pipeline execution failed")
        raise


async def test_gemini_direct():
    """Direct test of Gemini API connection"""
    
    print("\n" + "=" * 80)
    print("Direct Gemini API Test")
    print("=" * 80)
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n❌ Error: GOOGLE_API_KEY environment variable not set")
        return
    
    print("\n🔧 Testing direct Gemini API connection...")
    
    try:
        generator = GoogleAIGeminiGenerator(
            api_key=Secret.from_token(api_key),
            model="gemini-2.0-flash-exp"
        )
        
        result = generator.run(
            parts=["Generate a simple greeting in JSON format with a 'message' field."]
        )
        
        print("\n✅ Direct API test successful!")
        print(f"\n📄 Response:")
        for reply in result.get("replies", []):
            if hasattr(reply, 'text'):
                print(reply.text)
            else:
                print(reply)
        
    except Exception as e:
        print(f"\n❌ Direct API test failed:")
        print(f"   {type(e).__name__}: {str(e)}")
        logger.exception("Direct API test failed")


async def main():
    """Main test function"""
    
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 18 + "Gemini Flash 2.5 Prompt Agent Test" + " " * 26 + "║")
    print("╚" + "=" * 78 + "╝\n")
    
    # Check dependencies
    print("📦 Checking dependencies...")
    try:
        import haystack_integrations
        print("✓ haystack-integrations installed")
    except ImportError:
        print("❌ haystack-integrations not installed")
        print("   Install with: pip install google-ai-haystack")
        return
    
    # Run tests
    try:
        # Direct API test first
        await test_gemini_direct()
        
        # Main pipeline test
        await test_question_recommendation()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        logger.exception("Test execution failed")
    
    print("\n" + "=" * 80)
    print("Test suite completed")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n⚠️  WARNING: GOOGLE_API_KEY environment variable not set!")
        print("\nTo set it, run:")
        print("  export GOOGLE_API_KEY='your-api-key-here'")
        print("\nGet your API key from: https://makersuite.google.com/app/apikey")
        print()
    
    asyncio.run(main())
