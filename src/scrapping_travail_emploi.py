import time
import requests
import xmltodict
import json
import subprocess
from bs4 import BeautifulSoup 
import os
from slugify import slugify
from urllib.parse import urlparse

from markdownify import MarkdownConverter
import base64


# URL of the XML file
sitemapurl = "https://travail-emploi.gouv.fr/sitemap.xml"

base_url = 'https://travail-emploi.gouv.fr/'
target_url = base_url + 'droit-du-travail/'

target_urls = []
    


class CustomMarkdownConverter(MarkdownConverter):


    def convert_script(self, el, text, convert_as_inline):
        return ''

    def convert_style(self, el, text, convert_as_inline):
        return ''
    
    """
    Create a custom MarkdownConverter that adds two newlines after an image
    """
    def convert_img(self, el, text, convert_as_inline):
        return super().convert_img(el, text, convert_as_inline) + '\n\n' if text else ''

# Create shorthand method for conversion
def md(html, **options):
    return CustomMarkdownConverter(**options).convert(html)

# ----------------------

def parse_site_map () :
    

    # Fetch the XML content from the URL
    response = requests.get(sitemapurl)

    # Check if the request was successful
    if response.status_code == 200:
    
        # Convert XML to Python dictionary
        xml_dict = xmltodict.parse(response.content)

        urls=xml_dict['urlset']['url']


        for idx, url in  enumerate(urls):

            # if idx > 2 : break

            location = url['loc']
            if len(location) >= len(target_url)  and location.startswith(target_url):
                target_urls.append(url)
            
    else:
        print(f"Failed to retrieve XML. Status code: {response.status_code}")
    
    
def parse_urls():
    
  for idx, url  in enumerate(target_urls) :
      
    
    url['loc'] = url['loc'] if url['loc'].startswith(base_url) else base_url + url['loc']
    # Fetch the XML content from the URL
    response = requests.get(url['loc'])


    # Check if the request was successful
    if response.status_code == 200:
        # Convert XML to Python dictionary
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')
        main_content = soup.find('main') 
        aside_content = soup.find('aside') 
        # url['content'] = str(main_content)  

        
        # aside_links_filter = lambda x: x.string != None and len(x.string) > 0 and '/article/' in x.get("href")
        aside_links_filter = lambda x: x.string != None and len(x.string) > 0

        
        aside_links = aside_content.find_all("a") # Find all elements with the tag <a>
        result = filter(aside_links_filter, aside_links)
        new_aside_links = list(result)   
        url['menu_links'] = [{'loc': link.get("href") if link.get("href") .startswith(base_url) else base_url + link.get("href") , 'text': link.string.strip()} for link in new_aside_links]
        


def get_as_base64(url):

    return base64.b64encode(requests.get(url).content)


def scrap_site_links_to_md (in_target_links) : 
    
    
    links = set([])
    for idx, link in enumerate(in_target_links):

        time.sleep(1.2)
        
        links.add(link['loc'])
        
        if len(link['menu_links']) > 0 :
            for menu_link in link['menu_links']:
                links.add(menu_link['loc'])
    
    for loc in list(links):
        
        output_folder_path =  os.path.join(os.getcwd(), 'output/articles' if '/article/' in loc else 'output')
        
        if '/article/' in loc:
            # on  ne veut que les articles
            
            # Fetch the XML content from the URL
            response = requests.get(loc)

            # Check if the request was successful
            if response.status_code == 200:
                # Convert XML to Python dictionary
                html_content = response.content
                soup = BeautifulSoup(html_content, 'html.parser')
                body_content = soup.find('main') 

                urlparsed = urlparse(loc)
                md_file = slugify(urlparsed.path) + '.md'
                md_path = os.path.join(output_folder_path, md_file)
            
                if body_content:
                    markdown_content = md(str(body_content), heading_style='ATX')  # Convertir le contenu du body en Markdown
                else:
                    markdown_content = md(html_content, heading_style='ATX')  # Fallback si pas de body

                os.makedirs(output_folder_path, exist_ok=True)

                with open(md_path, 'w', encoding='utf-8') as output_file:
                    
                    output_file.write(markdown_content)
        
            


if __name__ == "__main__":


    parse_site_map()
    
    
    parse_urls()
    
    # print(json.dumps(target_urls, indent=4), '\n\n')

    scrap_site_links_to_md(target_urls)