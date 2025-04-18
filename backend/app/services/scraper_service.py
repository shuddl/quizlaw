import asyncio
import logging
from typing import Dict, List, Any, Tuple, Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup, Tag
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from app.core.config import settings
from app.crud import legal_section as legal_section_crud


# Set up logger
logger = logging.getLogger(__name__)


class ScraperError(Exception):
    """Base exception for scraper errors."""
    pass


class NetworkError(ScraperError):
    """Exception for network-related errors."""
    pass


class ParseError(ScraperError):
    """Exception for content parsing errors."""
    pass


class SectionNotFoundError(ScraperError):
    """Exception for when a section cannot be found."""
    pass


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(NetworkError),
    before_sleep=before_sleep_log(logger, logging.WARNING),
)
async def fetch_page(client: httpx.AsyncClient, url: str) -> str:
    """Fetch a page with retry logic for network errors."""
    try:
        response = await client.get(url)
        response.raise_for_status()
        return response.text
    except httpx.HTTPError as e:
        logger.error(f"Error fetching {url}: {str(e)}")
        raise NetworkError(f"Failed to fetch {url}: {str(e)}") from e


async def parse_division_page(html: str, base_url: str) -> List[str]:
    """
    Parse the division page to extract links to section pages.
    
    Args:
        html: HTML content of the division page
        base_url: Base URL for constructing absolute URLs
        
    Returns:
        List of URLs to individual section pages
    """
    soup = BeautifulSoup(html, "lxml")
    section_links = []
    
    # This is a placeholder - actual selectors would depend on the target website structure
    try:
        # Primary selector strategy
        links = soup.select("div.section-list a.section-link")
        
        # Fallback selector strategy if primary fails
        if not links:
            links = soup.select("table.sections-table td a")
        
        # Another fallback
        if not links:
            links = soup.find_all("a", href=lambda href: href and "section" in href.lower())
        
        for link in links:
            href = link.get("href")
            if href:
                # Construct absolute URL
                section_url = urljoin(base_url, href)
                section_links.append(section_url)
    
    except Exception as e:
        logger.error(f"Error parsing division page: {str(e)}")
        raise ParseError(f"Failed to parse division page: {str(e)}") from e
    
    return section_links


async def parse_section_page(html: str, url: str) -> Dict[str, Any]:
    """
    Parse an individual section page to extract section details.
    
    Args:
        html: HTML content of the section page
        url: URL of the section page
        
    Returns:
        Dictionary with section data
    """
    soup = BeautifulSoup(html, "lxml")
    section_data = {
        "source_url": url,
    }
    
    # This is a placeholder - actual selectors would depend on the target website structure
    try:
        # Extract section number - try multiple selectors
        section_number_elem = (
            soup.select_one("span.section-number") or
            soup.select_one("h1 .section-num") or
            soup.select_one("div.section-header .number")
        )
        
        if section_number_elem:
            section_data["section_number"] = section_number_elem.get_text().strip()
        else:
            # Fallback: try to parse from title or URL
            title = soup.title.string if soup.title else ""
            if "Section" in title and any(c.isdigit() for c in title):
                # Extract section number from title
                import re
                section_match = re.search(r'Section\s+([0-9.-]+)', title)
                if section_match:
                    section_data["section_number"] = section_match.group(1)
            else:
                # Try to extract from URL
                path = urlparse(url).path
                section_match = re.search(r'section[-_]?([0-9.-]+)', path, re.IGNORECASE)
                if section_match:
                    section_data["section_number"] = section_match.group(1)
                else:
                    raise ParseError(f"Could not extract section number from {url}")
        
        # Extract section title
        section_title_elem = (
            soup.select_one("h1.section-title") or
            soup.select_one("div.section-header h2") or
            soup.select_one("span.title")
        )
        
        if section_title_elem:
            section_data["section_title"] = section_title_elem.get_text().strip()
        else:
            # Fallback to any heading that might contain the title
            headings = soup.find_all(["h1", "h2", "h3"])
            for heading in headings:
                if heading.get_text().strip() and "section" not in heading.get_text().lower():
                    section_data["section_title"] = heading.get_text().strip()
                    break
            else:
                section_data["section_title"] = "Unknown Title"
        
        # Extract section text
        section_text_elem = (
            soup.select_one("div.section-content") or
            soup.select_one("div.section-text") or
            soup.select_one("div.content")
        )
        
        if section_text_elem:
            # Preserve structure by maintaining line breaks
            section_data["section_text"] = section_text_elem.get_text("\n", strip=True)
        else:
            # Fallback: try to get main content area
            main_content = soup.select_one("main") or soup.select_one("article") or soup.body
            if main_content:
                # Remove navigation, headers, footers, etc.
                for elem in main_content.select("nav, header, footer, script, style"):
                    elem.decompose()
                section_data["section_text"] = main_content.get_text("\n", strip=True)
            else:
                raise ParseError(f"Could not extract section text from {url}")
        
        # Extract division (assuming it can be derived from the page)
        division_elem = (
            soup.select_one("div.breadcrumb .division") or
            soup.select_one("span.division-name")
        )
        
        if division_elem:
            section_data["division"] = division_elem.get_text().strip()
        else:
            # Default division if not found
            section_data["division"] = "Main Code"
        
        # Extract part and chapter if available
        part_elem = soup.select_one("span.part-name")
        if part_elem:
            section_data["part"] = part_elem.get_text().strip()
        
        chapter_elem = soup.select_one("span.chapter-name")
        if chapter_elem:
            section_data["chapter"] = chapter_elem.get_text().strip()
        
    except Exception as e:
        logger.error(f"Error parsing section page {url}: {str(e)}")
        raise ParseError(f"Failed to parse section page {url}: {str(e)}") from e
    
    return section_data


async def store_scraped_section(session: AsyncSession, section_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Store or update a scraped section in the database.
    
    Args:
        session: Database session
        section_data: Section data to store
        
    Returns:
        Tuple of (success, message)
    """
    try:
        # Check if section already exists
        existing_section = await legal_section_crud.get_by_source_url(
            session, section_data["source_url"]
        )
        
        if existing_section:
            # Update existing section
            await legal_section_crud.update_section(
                session, existing_section.id, section_data
            )
            return True, "updated"
        else:
            # Create new section
            await legal_section_crud.create_legal_section(session, section_data)
            return True, "created"
    
    except Exception as e:
        logger.error(f"Error storing section: {str(e)}")
        return False, str(e)


async def scrape_division(
    session: AsyncSession, target_url: str
) -> Dict[str, Any]:
    """
    Scrape all sections within a division.
    
    Args:
        session: Database session
        target_url: URL of the division page
        
    Returns:
        Dictionary with scraping statistics
    """
    stats = {
        "sections_found": 0,
        "sections_scraped": 0,
        "sections_created": 0,
        "sections_updated": 0,
        "errors": 0,
    }
    
    # Configure HTTP client with appropriate headers and timeouts
    async with httpx.AsyncClient(
        headers={"User-Agent": settings.SCRAPER_USER_AGENT},
        timeout=settings.SCRAPER_REQUEST_TIMEOUT,
    ) as client:
        try:
            # Fetch and parse division page
            logger.info(f"Fetching division page: {target_url}")
            division_html = await fetch_page(client, target_url)
            section_urls = await parse_division_page(division_html, target_url)
            
            stats["sections_found"] = len(section_urls)
            logger.info(f"Found {len(section_urls)} section pages to scrape")
            
            # Scrape each section
            for section_url in section_urls:
                try:
                    logger.debug(f"Fetching section page: {section_url}")
                    section_html = await fetch_page(client, section_url)
                    section_data = await parse_section_page(section_html, section_url)
                    
                    # Store section in database
                    success, result = await store_scraped_section(session, section_data)
                    
                    if success:
                        stats["sections_scraped"] += 1
                        if result == "created":
                            stats["sections_created"] += 1
                        elif result == "updated":
                            stats["sections_updated"] += 1
                    else:
                        stats["errors"] += 1
                        logger.error(f"Failed to store section {section_url}: {result}")
                
                except (NetworkError, ParseError, SectionNotFoundError) as e:
                    stats["errors"] += 1
                    logger.error(f"Error scraping section {section_url}: {str(e)}")
                
                # Add a small delay to avoid overloading the server
                await asyncio.sleep(0.5)
        
        except Exception as e:
            logger.error(f"Error in scrape_division: {str(e)}")
            stats["errors"] += 1
    
    return stats