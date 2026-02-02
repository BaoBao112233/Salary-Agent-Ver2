from googlesearch import search
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def google_search(query: str) -> str:
    """Search Google for information"""
    try:
        logger.info(f"Searching Google for: {query}")
        
        results = search(query, advanced=True, num_results=5)
        formatted_results = []
        
        for r in results:
            formatted_results.append(f"{r.title} - {r.description}")
        
        return "\n".join(formatted_results)
    except Exception as e:
        logger.error(f"Error searching Google: {str(e)}", exc_info=True)
        return f"Error searching Google: {str(e)}"