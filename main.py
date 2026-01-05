"""
Notion Blog Cover Updater

Automatically updates cover images for blog posts in a Notion database
based on their main theme from a CSV mapping file.
"""

import csv
import os
from dotenv import load_dotenv
from PyToNotion.pyNotion import pyNotion  # Library to interact with Notion API

# Load environment variables
load_dotenv()

# Configuration
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
CSV_PATH = "images.csv"
THEME_PROPERTY = "Tema Principal"

# Initialize Notion client
notion = pyNotion(NOTION_TOKEN)

def load_images(csv_path):
    """
    Load theme-to-image URL mappings from CSV file.
    
    Args:
        csv_path (str): Path to CSV file with theme and image URL pairs
        
    Returns:
        dict: Theme names (lowercase) mapped to image URLs
    """
    theme_map = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row
        for theme, url in reader:
            # Normalize theme name for case-insensitive matching
            theme_map[theme.strip().lower()] = url.strip()
    return theme_map


def update_cover(page_id, image_url):
    """
    Update the cover image of a Notion page.
    
    Args:
        page_id (str): ID of the Notion page to update
        image_url (str): URL of the image to set as cover
        
    Returns:
        dict: Notion API response
    """
    payload = {
        "cover": {
            "type": "external",
            "external": {
                "url": image_url
            }
        }
    }
    # Send update request to Notion API
    page = notion.update_page(page_id, payload)
    return page


def get_blog_pages(database_id):
    """
    Retrieve all blog pages from the Notion database.
    
    Args:
        database_id (str): ID of the Notion database to query
        
    Returns:
        dict: Notion API response with filtered pages
    """
    query = {
        "filter": {
            "property": "Tipo de contenido",  # Content Type property
            "select": {
                "equals": "Blog"
            }
        }
    }
    database = notion.query_database(database_id, query)
    return database


def main():
    """
    Main function to update cover images for blog pages.
    
    Process:
    1. Load theme-image mappings from CSV
    2. Get blog pages from Notion database
    3. Update covers for matching themes
    """
    # Load theme-to-image mappings
    images = load_images(CSV_PATH)
    print(f"Loaded {len(images)} theme mappings")
    
    # Get blog pages from database
    pages = get_blog_pages(DATABASE_ID)
    if "status" in pages:
        return {"message": "Error retrieving pages from database",
                "code": 400}

    print(f"Processing {len(pages['results'])} blog pages")
    
    # Update cover for each page with matching theme
    updated_count = 0
    for page in pages["results"]:
        # Get theme name (case-insensitive)
        theme = page["properties"][THEME_PROPERTY]["select"]["name"].lower()

        if theme not in images:
            print(f"No image found for theme: {theme}")
            continue

        print(f"Updating cover for theme: {theme}")
        response = update_cover(page["id"], images[theme])
        if "status" in response:
            print(f"Error updating cover for theme: {theme}")
        else:
            updated_count += 1
    
    print(f"Successfully updated {updated_count} pages")


if __name__ == "__main__":
    main()