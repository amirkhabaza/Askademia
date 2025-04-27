import sys
import os
import requests

# Add project root to sys.path to allow sibling imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

try:
    import config # Load configuration
except ImportError:
    print("Error: config.py not found or cannot be imported.")
    sys.exit(1)

def fetch_courses(base_url, token):
    """
    Fetches active courses for the user associated with the token.
    """
    if not base_url or not token:
        print("Error: Canvas Base URL or API Token is missing in config/.env.")
        return

    # API endpoint for listing user's courses
    # Added enrollment_state=active to filter for currently active courses
    courses_url = f"{base_url.rstrip('/')}/api/v1/courses"
    headers = {'Authorization': f'Bearer {token}'}
    params = {
        'enrollment_state': 'active',
        'per_page': 50 # Fetch more per page just in case
    }
    
    print(f"Fetching active course list from: {courses_url}")

    active_courses = []
    page = 1
    while courses_url:
        print(f"  Fetching page {page}...")
        try:
            response = requests.get(courses_url, headers=headers, params=params, timeout=30)
            response.raise_for_status() # Raise HTTPError for bad responses
            courses_data = response.json()

            if not courses_data:
                print("  No courses found on this page.")
                break

            # Add courses from the current page to our list
            active_courses.extend(courses_data)

            # Handle Pagination using Link header
            courses_url = None # Reset for next iteration
            if 'next' in response.links:
                 courses_url = response.links['next'].get('url')
                 params = None # Parameters are included in the next URL
                 page += 1
            else:
                 print("  No more pages found.")
                 break # Exit loop if no next page

        except requests.exceptions.RequestException as e:
            print(f"Error fetching course list: {e}")
            if response is not None:
                print(f"Response status: {response.status_code}")
                print(f"Response text: {response.text[:200]}...") # Print beginning of error text
            return None # Indicate failure
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None # Indicate failure
            
    return active_courses

# --- Main Execution --- 
if __name__ == "__main__":
    if not config.CANVAS_BASE_URL or not config.CANVAS_API_TOKEN:
         print("Error: CANVAS_BASE_URL or CANVAS_API_TOKEN not set in .env/config.py")
         sys.exit(1)

    print("Attempting to fetch your active Canvas courses...")
    courses = fetch_courses(config.CANVAS_BASE_URL, config.CANVAS_API_TOKEN)

    if courses:
        print("\nFound the following active courses:")
        print("-------------------------------------")
        # Sort courses by name for readability
        for course in sorted(courses, key=lambda x: x.get('name', '')):
            course_id = course.get('id')
            course_name = course.get('name', '[No Name Found]')
            course_code = course.get('course_code', '[No Code]') # Often useful too
            if course_id:
                 print(f"- Name: {course_name}")
                 print(f"  Code: {course_code}")
                 print(f"  ID:   {course_id}")
                 print("    (Add to config.CANVAS_COURSE_IDS as '{course_name}': '{course_id}')")
        print("-------------------------------------")
        print(f"Total active courses found: {len(courses)}")
    else:
        print("Could not retrieve course list.") 