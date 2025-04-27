# scripts/download_canvas_files.py

import sys
import os
import requests
import argparse
from urllib.parse import unquote, urljoin, urlparse # To handle URL-encoded filenames and join URLs
from bs4 import BeautifulSoup # For HTML parsing

# Add project root to sys.path to allow sibling imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

try:
    import config # Load configuration
except ImportError:
    print("Error: config.py not found or cannot be imported.")
    sys.exit(1)

# --- Constants ---
# Directory to save downloaded files, relative to project root
DOWNLOAD_DIR = "embeddings" 
# Create the directory if it doesn't exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True) 

# Keywords to identify potential lecture pages/slides
# Adjust this list based on your course naming conventions
LECTURE_KEYWORDS = ['lecture', 'slides', 'week', 'module', 'topic', 'session', 'ppt', 'present']

# --- Helper Functions ---
def download_file(url, save_path, headers):
    """Downloads a file from a URL to a specified path."""
    try:
        print(f"  Downloading {os.path.basename(save_path)} from {url[:50]}...")
        with requests.get(url, headers=headers, stream=True, timeout=60) as r: # Added timeout
            r.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
        print(f"  Successfully downloaded {os.path.basename(save_path)}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"  Error downloading {os.path.basename(save_path)}: {e}")
        # Clean up potentially incomplete file
        if os.path.exists(save_path):
            os.remove(save_path)
        return False
    except Exception as e:
        print(f"  An unexpected error occurred during download: {e}")
        if os.path.exists(save_path):
            os.remove(save_path)
        return False

def fetch_course_pages_and_download_pdfs(base_url, token, course_id, target_dir):
    """
    Fetches course pages, parses their content for PDF links, and downloads them.
    Focuses on pages likely related to lectures/slides.
    """
    if not base_url or not token:
        print(f"Error: Canvas Base URL or API Token is missing in config/.env for course {course_id}.")
        return

    pages_api_url = f"{base_url.rstrip('/')}/api/v1/courses/{course_id}/pages"
    headers = {'Authorization': f'Bearer {token}'}
    params = {'per_page': 50}
    
    print(f"\nFetching page list for course ID: {course_id} from {pages_api_url}")
    
    page_num = 1
    processed_urls = set() # Keep track of pages already processed

    while pages_api_url:
        print(f"  Fetching page list - Page {page_num}...")
        try:
            response = requests.get(pages_api_url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            pages_data = response.json()
            
            if not pages_data:
                print("  No pages found on this list page.")
                break

            print(f"  Processing {len(pages_data)} page entries...")

            for page_info in pages_data:
                page_url = page_info.get('url') # This is the page identifier used in the page content API
                page_title = page_info.get('title', '').lower()
                html_url = page_info.get('html_url', '') # The URL you see in browser

                if not page_url:
                    continue
                
                # Check if page title or URL suggests it contains lecture material
                is_lecture_page = any(keyword in page_title for keyword in LECTURE_KEYWORDS)
                
                if is_lecture_page and html_url not in processed_urls:
                    processed_urls.add(html_url)
                    print(f"  Found potential lecture page: '{page_info.get('title')}'. Fetching content...")
                    
                    # --- Fetch the actual page content --- 
                    page_content_url = f"{base_url.rstrip('/')}/api/v1/courses/{course_id}/pages/{page_url}"
                    try:
                        page_response = requests.get(page_content_url, headers=headers, timeout=30)
                        page_response.raise_for_status()
                        page_content_data = page_response.json()
                        page_body_html = page_content_data.get('body')

                        if page_body_html:
                            # --- Parse HTML for potential file links --- 
                            soup = BeautifulSoup(page_body_html, 'html.parser')
                            links_found = 0
                            processed_file_endpoints = set() # Avoid processing same file endpoint multiple times per page
                            
                            for link in soup.find_all('a', href=True):
                                link_text = link.get_text(strip=True).lower()
                                link_title = link.get('title', '').lower()
                                file_api_endpoint = link.get('data-api-endpoint')
                                
                                # Check if link text, title, or api endpoint suggests PDF
                                is_potential_pdf = (link_text.endswith('.pdf') or 
                                                  link_title.endswith('.pdf'))
                                
                                if is_potential_pdf and file_api_endpoint and file_api_endpoint not in processed_file_endpoints:
                                    processed_file_endpoints.add(file_api_endpoint)
                                    links_found += 1
                                    print(f"    Found potential PDF link. Fetching file metadata from: {file_api_endpoint}")
                                    
                                    # --- Get actual file metadata --- 
                                    try:
                                        file_meta_response = requests.get(file_api_endpoint, headers=headers, timeout=30)
                                        file_meta_response.raise_for_status()
                                        file_meta_data = file_meta_response.json()
                                        
                                        pdf_url = file_meta_data.get('url') # The actual download URL
                                        display_name = file_meta_data.get('display_name') # Use filename from metadata
                                        content_type = file_meta_data.get('content-type', '').lower()

                                        # Double-check it's actually a PDF from metadata
                                        if pdf_url and display_name and content_type == 'application/pdf':
                                            filename = unquote(display_name) # Use the authoritative name
                                            save_path = os.path.join(target_dir, filename)

                                            if not os.path.exists(save_path):
                                                download_file(pdf_url, save_path, headers)
                                            else:
                                                print(f"      Skipping {filename}, already exists.")
                                        else:
                                            print(f"      Skipping link - Metadata check failed (URL: {pdf_url}, Name: {display_name}, Type: {content_type})")
                                             
                                    except requests.exceptions.RequestException as e:
                                        print(f"      Error fetching file metadata from {file_api_endpoint}: {e}")
                                    except Exception as e:
                                        print(f"      Error processing file metadata from {file_api_endpoint}: {e}")
                                        
                            if links_found == 0:
                                 print(f"    No potential PDF file API endpoints found on page '{page_info.get('title')}'.")

                    except requests.exceptions.RequestException as e:
                        print(f"    Error fetching content for page '{page_info.get('title')}': {e}")
                    except Exception as e:
                        print(f"    Error processing page '{page_info.get('title')}': {e}")
                #else: # Optional: debug which pages are skipped
                #    if not is_lecture_page:
                #        print(f"  Skipping page (title doesn't match keywords): '{page_info.get('title')}'")
                #    elif html_url in processed_urls:
                #        print(f"  Skipping page (already processed): '{page_info.get('title')}'")

            # --- Handle Pagination for page list --- 
            pages_api_url = None
            if 'next' in response.links:
                 pages_api_url = response.links['next'].get('url')
                 params = None
                 page_num += 1
            else:
                 print("  No more pages found in the list.")
                 break

        except requests.exceptions.RequestException as e:
            print(f"Error fetching page list for course {course_id}: {e}")
            break
        except Exception as e:
            print(f"An unexpected error occurred while fetching page list: {e}")
            break

# --- Main Execution ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download lecture/syllabus PDFs linked from Canvas Pages.")
    parser.add_argument("--course", type=str, help="Specify a single course name (key from config.CANVAS_COURSE_IDS) to process.")
    
    args = parser.parse_args()

    courses_to_process = {}
    if args.course:
        if args.course in config.CANVAS_COURSE_IDS:
            courses_to_process[args.course] = config.CANVAS_COURSE_IDS[args.course]
        else:
            print(f"Error: Course name '{args.course}' not found in config.CANVAS_COURSE_IDS.")
            sys.exit(1)
    else:
        # Process all courses defined in config if no specific one is given
        courses_to_process = config.CANVAS_COURSE_IDS

    if not courses_to_process:
         print("Error: No courses defined in config.CANVAS_COURSE_IDS or specified via --course.")
         sys.exit(1)

    if not config.CANVAS_BASE_URL or not config.CANVAS_API_TOKEN:
         print("Error: CANVAS_BASE_URL or CANVAS_API_TOKEN not set in .env/config.py")
         sys.exit(1)

    base_download_dir = DOWNLOAD_DIR # Defined at top of file ('embeddings')

    print("Starting Canvas page parsing and file download...")
    for course_name, course_id in courses_to_process.items():
        print(f"Processing course: {course_name} (ID: {course_id})")
        
        # --- Create course-specific subdirectory --- 
        course_specific_dir = os.path.join(base_download_dir, course_name)
        os.makedirs(course_specific_dir, exist_ok=True)
        print(f"  Ensuring download directory exists: {course_specific_dir}")
        
        # Call the fetching function with the course-specific directory
        fetch_course_pages_and_download_pdfs(
            config.CANVAS_BASE_URL, 
            config.CANVAS_API_TOKEN, 
            course_id, 
            course_specific_dir # Pass specific dir here
        )
    
    print("\nCanvas page parsing and file download process finished.")
