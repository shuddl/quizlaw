#!/usr/bin/env python3
"""
Script to update the bar relevance flag for legal sections.

Usage:
    python update_bar_relevance.py <division> <file_path>
    
Example:
    python update_bar_relevance.py "Federal Rules" bar_relevant_sections.txt
"""

import sys
import asyncio
import logging
from pathlib import Path
from typing import List, Set

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path so we can import from app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.crud import legal_section as legal_section_crud


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def read_section_numbers(file_path: str) -> Set[str]:
    """
    Read a file containing section numbers.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Set of section numbers
    """
    section_numbers = set()
    
    try:
        with open(file_path, "r") as f:
            for line in f:
                # Remove whitespace and comments
                line = line.strip()
                if line and not line.startswith("#"):
                    section_numbers.add(line)
        
        logger.info(f"Read {len(section_numbers)} section numbers from {file_path}")
        return section_numbers
    
    except Exception as e:
        logger.error(f"Error reading section numbers from {file_path}: {str(e)}")
        raise


async def update_bar_relevance(division: str, section_numbers: List[str]) -> None:
    """
    Update the bar relevance flag for sections in a division.
    
    Args:
        division: Legal division
        section_numbers: List of bar-relevant section numbers
    """
    # Create async database connection
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Update bar relevance
        result = await legal_section_crud.update_bar_relevance(
            session, division, section_numbers
        )
        
        logger.info(
            f"Updated bar relevance for division '{division}': "
            f"{result['marked_relevant']} sections marked as relevant, "
            f"{result['marked_irrelevant']} sections marked as not relevant"
        )


async def main() -> None:
    """Main entry point."""
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <division> <file_path>")
        sys.exit(1)
    
    division = sys.argv[1]
    file_path = sys.argv[2]
    
    try:
        # Read section numbers
        section_numbers = await read_section_numbers(file_path)
        
        # Update bar relevance
        await update_bar_relevance(division, list(section_numbers))
        
        logger.info("Bar relevance update completed successfully")
    
    except Exception as e:
        logger.error(f"Error updating bar relevance: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())