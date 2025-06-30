import re
from typing import Dict

def parse_proposal_sections(text: str) -> Dict[str, str]:
    """
    Attempts to extract common proposal sections from text.
    Returns a dictionary with section names as keys and content as values.
    If sections can't be identified, returns the full text under 'full_content'.
    """
    # Define common section headers (case-insensitive)
    section_patterns = [
        ("executive_summary", r"executive summary"),
        ("scope_of_work", r"scope of work|project scope"),
        ("pricing", r"pricing|budget"),
        ("timeline", r"timeline|schedule")
    ]
    # Find all section headers and their positions
    matches = []
    for key, pattern in section_patterns:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            matches.append((m.start(), key, m.group(0)))
    if not matches:
        return {"full_content": text.strip()}
    # Sort by position
    matches.sort()
    # Extract sections
    sections = {}
    for i, (start, key, header) in enumerate(matches):
        end = matches[i+1][0] if i+1 < len(matches) else len(text)
        content = text[start:end].strip()
        sections[key] = content
    return sections

def extract_metadata_from_text(text: str) -> Dict[str, str]:
    """
    Attempts to extract client name, industry, and service type from text.
    Uses simple regex/string matching. Returns a dict with found metadata.
    """
    metadata = {}
    # Try to find client name (look for 'Client: ...' or 'To: ...')
    client_match = re.search(r"Client[:\-]\s*([A-Za-z0-9 &]+)", text, re.IGNORECASE)
    if not client_match:
        client_match = re.search(r"To[:\-]\s*([A-Za-z0-9 &]+)", text, re.IGNORECASE)
    if client_match:
        metadata["client_name"] = client_match.group(1).strip()
    # Try to find industry (look for 'Industry: ...')
    industry_match = re.search(r"Industry[:\-]\s*([A-Za-z0-9 &]+)", text, re.IGNORECASE)
    if industry_match:
        metadata["industry"] = industry_match.group(1).strip()
    # Try to find service type (look for 'Service Type: ...' or 'Services: ...')
    service_match = re.search(r"Service Type[:\-]\s*([A-Za-z0-9 &]+)", text, re.IGNORECASE)
    if not service_match:
        service_match = re.search(r"Services?[:\-]\s*([A-Za-z0-9 &]+)", text, re.IGNORECASE)
    if service_match:
        metadata["service_type"] = service_match.group(1).strip()
    return metadata
