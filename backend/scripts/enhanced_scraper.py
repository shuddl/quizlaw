#!/usr/bin/env python
"""
Enhanced Legal Code Scraper Script

This script uses the enhanced scraper service to scrape legal code divisions from specified URLs.
It supports single division scraping, multi-division scraping, and concurrent request options.

Example usage:
    # Scrape a single division
    python -m scripts.enhanced_scraper --url https://example.com/laws/division1

    # Scrape multiple divisions
    python -m scripts.enhanced_scraper --urls https://example.com/laws/division1 https://example.com/laws/division2

    # Adjust concurrency
    python -m scripts.enhanced_scraper --url https://example.com/laws/division1 --concurrency 5
"""

import argparse
import asyncio
import logging
import sys
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import session_scope
from app.services.scraper_service import scrape_division, scrape_multiple_divisions


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('scraper.log')
    ]
)

logger = logging.getLogger(__name__)


async def run_scraper(
    division_urls: List[str],
    concurrent_requests: int = 3
) -> None:
    """
    Run the scraper for given division URLs.
    
    Args:
        division_urls: List of division URLs to scrape
        concurrent_requests: Number of concurrent requests per division
    """
    logger.info(f"Starting enhanced scraper for {len(division_urls)} division(s)")
    logger.info(f"Concurrent requests per division: {concurrent_requests}")
    
    async with session_scope() as session:
        session: AsyncSession = session
        
        if len(division_urls) == 1:
            # Single division mode
            stats = await scrape_division(
                session, 
                division_urls[0], 
                concurrent_requests=concurrent_requests
            )
            
            # Print stats
            logger.info("Scraping completed!")
            logger.info(f"Sections found: {stats['sections_found']}")
            logger.info(f"Sections scraped: {stats['sections_scraped']}")
            logger.info(f"New sections: {stats['sections_created']}")
            logger.info(f"Updated sections: {stats['sections_updated']}")
            logger.info(f"Errors: {stats['errors']}")
            
        else:
            # Multiple divisions mode
            stats = await scrape_multiple_divisions(session, division_urls)
            
            # Print stats
            logger.info("Scraping completed!")
            logger.info(f"Divisions attempted: {stats['divisions_attempted']}")
            logger.info(f"Divisions completed: {stats['divisions_completed']}")
            logger.info(f"Sections found: {stats['sections_found']}")
            logger.info(f"Sections scraped: {stats['sections_scraped']}")
            logger.info(f"New sections: {stats['sections_created']}")
            logger.info(f"Updated sections: {stats['sections_updated']}")
            logger.info(f"Errors: {stats['errors']}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Enhanced scraper for legal code divisions"
    )
    
    # Create a mutually exclusive group for URL arguments
    url_group = parser.add_mutually_exclusive_group(required=True)
    url_group.add_argument(
        "--url", 
        help="URL of a single division page to scrape"
    )
    url_group.add_argument(
        "--urls", 
        nargs="+", 
        help="List of division URLs to scrape"
    )
    
    # Add options
    parser.add_argument(
        "--concurrency", 
        type=int, 
        default=3,
        help="Number of concurrent requests per division (default: 3)"
    )
    
    args = parser.parse_args()
    
    # Prepare URLs list
    if args.url:
        division_urls = [args.url]
    else:
        division_urls = args.urls
    
    # Run the scraper
    asyncio.run(run_scraper(division_urls, args.concurrency))


if __name__ == "__main__":
    main()