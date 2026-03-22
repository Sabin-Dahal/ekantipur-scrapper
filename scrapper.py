import json
from playwright.sync_api import sync_playwright

def scrape_entertainment_news(page):
    #for entertainment news section
    try:
        print("Navigating to entertainment page...")
        page.goto("https://ekantipur.com/entertainment", wait_until="networkidle")
    except Exception as e:
        print(f"Error navigating to entertainment page: {e}")
        return []

    
    # Wait for article cards to be present
    page.wait_for_selector("div.category-inner-wrapper")

    # Scroll down to trigger lazy image loading
    try:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        page.wait_for_timeout(2000)

        # Grab all article cards
        cards = page.query_selector_all("div.category-inner-wrapper")
        print(f"Found {len(cards)} article cards")
    except Exception as e:
        print(f"Error during scrolling or grabbing article cards: {e}")
        cards = []

    articles = []
    category_el = page.query_selector("div.category-name p a") 
    category = category_el.text_content().strip() #since extracting from /entertainment we extract category from another tag and use it for all since the corresponding news cards dont have category element
    
    for card in cards[:5]: 
        try:
            #grab title inside category-description h2->a tag
            title_el = card.query_selector("div.category-description h2 a")
            title = title_el.text_content().strip() if title_el else None
            #grab author inside author-name p>a tag
            author_el = card.query_selector("div.author-name p a")
            author = author_el.text_content().strip() if author_el else None
            #grab images inside cateogy-image. loaded inside img tag and using src since scrolling is simulated
            img_el = card.query_selector("div.category-image img")
            image_url = img_el.get_attribute("src") if img_el else None



            articles.append({
                "title": title,
                "image_url": image_url,
                "category": category,
                "author": author
            })

            print(f"  Scraped: {title[:40] if title else 'N/A'}...")

        except Exception as e:
            print(f"  Error scraping card: {e}")
            continue

    return articles


def scrape_cartoon_of_the_day(page):

    try:
        print("Navigating to cartoon page...")
        page.goto("https://ekantipur.com/cartoon", wait_until="networkidle")
    except Exception as e:
        print(f"Error navigating to cartoon page: {e}")
        return None


    try:
        page.evaluate("window.scrollTo(0, 300)")
        page.wait_for_timeout(2000)

        page.wait_for_selector("div.cartoon-wrapper")

        cartoon = page.query_selector("div.cartoon-wrapper")
    except Exception as e:
        print(f"Error during scrolling or selecting cartoon wrapper: {e}")
        cartoon = None

    if not cartoon:
        print("No cartoon found!")
        return None

    try:
        img_el = cartoon.query_selector("div.cartoon-image img")
        image_url = img_el.get_attribute("src") if img_el else None

        desc_el = cartoon.query_selector("div.cartoon-description p")
        desc_text = desc_el.text_content().strip() if desc_el else ""

        if " - " in desc_text:
            parts = desc_text.split(" - ", 1)  
            title = parts[0].strip()
            author = parts[1].strip()
        else:
            title = desc_text
            author = None

        print(f"  Cartoon: {title} by {author}")

        return {
            "title": title,
            "image_url": image_url,
            "author": author
        }

    except Exception as e:
        print(f"  Error scraping cartoon: {e}")
        return None


def main():
    with sync_playwright() as p:
       
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        entertainment_news = scrape_entertainment_news(page)
        print(f"\nExtracted {len(entertainment_news)} entertainment articles")

        cartoon = scrape_cartoon_of_the_day(page)
        print(f"\nExtracted cartoon: {cartoon}")

        browser.close()

        output = {
            "entertainment_news": entertainment_news,
            "cartoon_of_the_day": cartoon
        }

        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print("\nDone! Data saved to output.json")


if __name__ == "__main__":
    main()
