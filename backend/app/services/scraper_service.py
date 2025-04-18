import asyncio
import logging
import re
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
    
    try:
        # Primary selector strategy - handles most common cases
        links = soup.select("div.section-list a.section-link")
        
        # Fallback selector strategy if primary fails
        if not links:
            links = soup.select("table.sections-table td a")
        
        # Try common code section patterns
        if not links:
            links = soup.select("ul.sections li a")
            
        # Try code browser patterns
        if not links:
            links = soup.select("div.code-browser a.section")
        
        # Another fallback - look for any links containing "section"
        if not links:
            links = soup.find_all("a", href=lambda href: href and "section" in href.lower())
            
        # Last resort - any links with numeric patterns that might be section IDs
        if not links:
            links = soup.find_all("a", href=lambda href: href and re.search(r'\d+[.-]\d+', href))
        
        # Process found links
        for link in links:
            href = link.get("href")
            if href:
                # Construct absolute URL
                section_url = urljoin(base_url, href)
                section_links.append(section_url)
                
        # If we found too many links (possible false positives), filter them
        if len(section_links) > 200:
            logger.warning(f"Found unusually large number of links ({len(section_links)}), filtering...")
            # Keep only those that match common section patterns
            section_links = [url for url in section_links if re.search(r'(section|§|code)', url, re.IGNORECASE)]
    
    except Exception as e:
        logger.error(f"Error parsing division page: {str(e)}")
        raise ParseError(f"Failed to parse division page: {str(e)}") from e
    
    return section_links


async def extract_footnotes(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Extract footnotes from a section page.
    
    Args:
        soup: BeautifulSoup object of the page
        
    Returns:
        Dictionary mapping footnote numbers to footnote text
    """
    footnotes = {}
    
    # Find common footnote patterns
    footnote_elements = (
        soup.select("div.footnotes li") or
        soup.select("div.footnotes p") or
        soup.select("ol.footnotes li") or
        soup.select("div.annotations p") or
        soup.find_all("div", class_=lambda c: c and "footnote" in c.lower()) or
        soup.find_all("sup", class_=lambda c: c and "footnote" in c.lower())
    )
    
    for elem in footnote_elements:
        # Try to extract footnote number and text
        footnote_text = elem.get_text(strip=True)
        match = re.search(r'^(\d+)[.:]?\s+(.*)', footnote_text)
        
        if match:
            num, text = match.groups()
            footnotes[num] = text
    
    return footnotes


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
    
    try:
        # Extract section number - try multiple selectors
        section_number_elem = (
            soup.select_one("span.section-number") or
            soup.select_one("h1 .section-num") or
            soup.select_one("div.section-header .number") or
            soup.select_one("p.section-number") or
            soup.select_one("[id^='section-']")
        )
        
        if section_number_elem:
            section_data["section_number"] = section_number_elem.get_text().strip()
        else:
            # Fallback: try to parse from title or URL
            title = soup.title.string if soup.title else ""
            if "Section" in title and any(c.isdigit() for c in title):
                # Extract section number from title
                section_match = re.search(r'Section\s+([0-9.-]+)', title)
                if section_match:
                    section_data["section_number"] = section_match.group(1)
            else:
                # Try to extract from URL
                path = urlparse(url).path
                section_match = re.search(r'section[-_]?([0-9.-]+)', path, re.IGNORECASE) or re.search(r'([0-9]+[.-][0-9]+)', path)
                if section_match:
                    section_data["section_number"] = section_match.group(1)
                else:
                    raise ParseError(f"Could not extract section number from {url}")
        
        # Extract section title
        section_title_elem = (
            soup.select_one("h1.section-title") or
            soup.select_one("div.section-header h2") or
            soup.select_one("span.title") or
            soup.select_one("h2.title") or
            soup.select_one("div.title")
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
        
        # Extract footnotes that might be needed for full context
        footnotes = await extract_footnotes(soup)
        
        # Extract section text
        section_text_elem = (
            soup.select_one("div.section-content") or
            soup.select_one("div.section-text") or
            soup.select_one("div.content") or
            soup.select_one("div.statutory-body") or
            soup.select_one("div.code-text")
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
        
        # Handle multi-part sections and subsections
        section_parts = {}
        subsection_elements = section_text_elem.select("p.subsection") if section_text_elem else []
        
        if subsection_elements:
            for i, subsection in enumerate(subsection_elements):
                label = subsection.select_one(".label")
                text = subsection.select_one(".text")
                if label and text:
                    section_parts[label.get_text(strip=True)] = text.get_text(strip=True)
            
            if section_parts:
                section_data["structured_content"] = section_parts
        
        # If we found footnotes, include them in the data
        if footnotes:
            section_data["footnotes"] = footnotes
        
        # Extract division (assuming it can be derived from the page)
        division_elem = (
            soup.select_one("div.breadcrumb .division") or
            soup.select_one("span.division-name") or
            soup.select_one("div.breadcrumbs a") or
            soup.select_one("ol.breadcrumb li a")
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
    session: AsyncSession, target_url: str, concurrent_requests: int = 3
) -> Dict[str, Any]:
    """
    Scrape all sections within a division.
    
    Args:
        session: Database session
        target_url: URL of the division page
        concurrent_requests: Number of concurrent requests to make
        
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
            
            # Process sections in batches for controlled concurrency
            for i in range(0, len(section_urls), concurrent_requests):
                batch = section_urls[i:i + concurrent_requests]
                tasks = []
                
                for section_url in batch:
                    tasks.append(process_section(client, session, section_url, stats))
                
                await asyncio.gather(*tasks)
                
                # Add a small delay between batches
                await asyncio.sleep(1.0)
        
        except Exception as e:
            logger.error(f"Error in scrape_division: {str(e)}")
            stats["errors"] += 1
    
    return stats


async def process_section(
    client: httpx.AsyncClient, 
    session: AsyncSession, 
    section_url: str,
    stats: Dict[str, int]
) -> None:
    """
    Process a single section page.
    
    Args:
        client: HTTP client
        session: Database session
        section_url: URL of the section page
        stats: Statistics dictionary to update
    """
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
                logger.info(f"Created new section: {section_data.get('section_number', 'Unknown')}")
            elif result == "updated":
                stats["sections_updated"] += 1
                logger.info(f"Updated section: {section_data.get('section_number', 'Unknown')}")
        else:
            stats["errors"] += 1
            logger.error(f"Failed to store section {section_url}: {result}")
    
    except (NetworkError, ParseError, SectionNotFoundError) as e:
        stats["errors"] += 1
        logger.error(f"Error scraping section {section_url}: {str(e)}")


async def scrape_multiple_divisions(
    session: AsyncSession, division_urls: List[str]
) -> Dict[str, Any]:
    """
    Scrape multiple divisions in sequence.
    
    Args:
        session: Database session
        division_urls: List of division URLs to scrape
        
    Returns:
        Dictionary with combined scraping statistics
    """
    combined_stats = {
        "divisions_attempted": len(division_urls),
        "divisions_completed": 0,
        "sections_found": 0,
        "sections_scraped": 0,
        "sections_created": 0,
        "sections_updated": 0,
        "errors": 0,
    }
    
    for url in division_urls:
        try:
            logger.info(f"Starting to scrape division: {url}")
            division_stats = await scrape_division(session, url)
            
            # Update combined stats
            combined_stats["sections_found"] += division_stats["sections_found"]
            combined_stats["sections_scraped"] += division_stats["sections_scraped"]
            combined_stats["sections_created"] += division_stats["sections_created"]
            combined_stats["sections_updated"] += division_stats["sections_updated"]
            combined_stats["errors"] += division_stats["errors"]
            
            combined_stats["divisions_completed"] += 1
            logger.info(f"Completed scraping division: {url}")
            
        except Exception as e:
            combined_stats["errors"] += 1
            logger.error(f"Failed to scrape division {url}: {str(e)}")
    
    return combined_stats