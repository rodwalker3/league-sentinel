from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


async def get_roster(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(viewport={"width": 1600, "height": 1000})

        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        clicked = False

        try:
            abilities_field = page.locator("text=Abilities").first.locator(
                "xpath=ancestor::div[contains(@class, 'q-field')]"
            ).first
            await abilities_field.locator("input[type='checkbox']").click(force=True)
            clicked = True
            print("Clicked abilities checkbox.")
        except Exception as e:
            print(f"Checkbox click failed: {e}")

        if not clicked:
            try:
                abilities_field = page.locator("text=Abilities").first.locator(
                    "xpath=ancestor::div[contains(@class, 'q-field')]"
                ).first
                await abilities_field.locator(".q-field__native").click(force=True)
                clicked = True
                print("Clicked q-field native area.")
            except Exception as e:
                print(f"Native field click failed: {e}")

        if not clicked:
            await page.screenshot(path="toggle_error.png", full_page=True)
            await browser.close()
            raise ValueError("Could not click the Abilities toggle.")

        await page.wait_for_timeout(4000)

        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table")
    if table is None:
        raise ValueError("No table found after abilities toggle.")

    rows = table.find_all("tr")[1:]
    players = []

    for row in rows:
        cols = row.find_all("td")
        if not cols:
            continue

        name = cols[0].get_text(" ", strip=True)
        team = cols[1].get_text(" ", strip=True)
        pos = cols[2].get_text(" ", strip=True)
        abilities_text = cols[-1].get_text("\n", strip=True)

        abilities = []
        if abilities_text and abilities_text.lower() != "none":
            abilities = [a.strip() for a in abilities_text.split("\n") if a.strip()]

        players.append({
            "name": name,
            "team": team,
            "pos": pos,
            "abilities": abilities
        })

    print("Parsed players:", players[:5])
    return players