import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re
import os

async def main():
    async with async_playwright() as a:
        browser = await a.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto('https://www.rwbaird.com/who-we-are/locations/')
        content = await page.content()
        soup = BeautifulSoup(content, 'lxml')

        block = soup.find('div', {'class': 'row no-mar-btm'})

        with open('contentblock.html', 'w', encoding='utf-8') as b:
            b.write(block.prettify())

        link = re.compile(r'(http:\/\/www\.bairdoffices\.com\/[^\"]*?\/)\s*\"')
        link_list = link.findall(str(block))

        with open('url_list.txt', 'w', encoding='utf-8') as c:
            for l in link_list:
                c.write(l + "\n")

        link_str = re.compile(r'http:\/\/www\.bairdoffices\.com\/[^\/]*?\/')
        urls = []
        with open('url_list.txt', 'r', encoding='utf-8') as s:
            content = s.read()
            urls = link_str.findall(content)

        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)

        for url in urls:
            try:
                await page.goto(url)
                pagecache = await page.content()
                pattern = re.compile(r'http:\/\/www\.bairdoffices\.com\/([^\/]*?)\/')
                match = pattern.search(url)
                if match:
                    name_file = match.group(1)
                    filename = f"{name_file}.html"
                    filename = os.path.join(output_dir, filename)
                    with open(filename, 'w', encoding='utf-8') as file:
                        file.write(pagecache)
                        soup = BeautifulSoup(pagecache,'lxml')
                        block = soup.find('div',{'class':'addresscontent'})
                        maincontent = str(block)

                        regex = re.compile(r'<h2>\s*([^\<]*?)\s*<\/h2>\s*<p>\s*([^<]*?)\s*<br\/>\s*([^<]*?)\s*\<\/p>\s*<p.\s*<a[^>]*?\>\s*([^<]*?)\s*\<\/a>\s*<\/p>')
                        match = regex.search(maincontent)

                        if match:
                            cityname = match.group(1)
                            address = match.group(2,3)
                            contact = match.group(4)

                            print(cityname, "\n", address, "\n", contact, "\n")

                            with open('output.txt', 'a', encoding='utf-8') as b:
                                b.write(f"City: {cityname}\n")
                                b.write(f"Address: {address}\n")
                                b.write(f"Contact: {contact}\n\n")
                                
                            print(f"Saved content from {url} to {filename}")
                        else:
                            with open('error_page.txt', 'a', encoding='utf-8') as file:
                                file.write(url + " - No match found\n")
                            print(f"No match found for {url}")

            except Exception as e:
                with open('error_page.txt', 'a', encoding='utf-8') as file:
                    file.write(url + "\n")
                print(f"Failed to retrieve {url}: {e}")
                        
    await browser.close()

# Run the main function
asyncio.run(main())
