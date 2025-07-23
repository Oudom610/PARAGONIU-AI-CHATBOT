import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from urllib.parse import urljoin


class ParagonSpider(CrawlSpider):
    name = 'paragon'
    allowed_domains = ['paragoniu.edu.kh']
    start_urls = ['https://paragoniu.edu.kh']

    # Define rules for following links
    rules = (
        # Follow all internal links and parse them
        Rule(LinkExtractor(allow_domains=['paragoniu.edu.kh']), 
             callback='parse_page', 
             follow=True),
    )

    def parse_page(self, response):
        """Parse each page and extract relevant information"""
        
        # Extract basic page information
        page_data = {
            'url': response.url,
            'title': response.css('title::text').get(),
            'meta_description': response.css('meta[name="description"]::attr(content)').get(),
            'h1_headings': response.css('h1::text').getall(),
            'h2_headings': response.css('h2::text').getall(),
            'h3_headings': response.css('h3::text').getall(),
        }

        # Extract text content (clean)
        text_content = ' '.join(response.css('p::text, div::text, span::text').getall())
        page_data['text_content'] = ' '.join(text_content.split())  # Clean whitespace

        # Extract images
        images = []
        for img in response.css('img'):
            img_data = {
                'src': urljoin(response.url, img.css('::attr(src)').get()),
                'alt': img.css('::attr(alt)').get(),
                'title': img.css('::attr(title)').get(),
            }
            images.append(img_data)
        page_data['images'] = images

        # Extract links
        links = []
        for link in response.css('a[href]'):
            link_data = {
                'url': urljoin(response.url, link.css('::attr(href)').get()),
                'text': link.css('::text').get(),
                'title': link.css('::attr(title)').get(),
            }
            links.append(link_data)
        page_data['links'] = links

        # Extract contact information (common patterns)
        contact_info = self.extract_contact_info(response)
        if contact_info:
            page_data['contact_info'] = contact_info

        # Extract academic programs/courses if present
        programs = self.extract_programs(response)
        if programs:
            page_data['programs'] = programs

        yield page_data

    def extract_contact_info(self, response):
        """Extract contact information from the page"""
        contact_info = {}
        
        # Get the full page text to search for patterns
        page_text = response.text
        
        # Look for email addresses
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', page_text)
        if emails:
            contact_info['emails'] = list(set(emails))  # Remove duplicates

        # Look for phone numbers (basic pattern)
        phones = re.findall(r'[\+]?[1-9]?[0-9]{7,15}', page_text)
        if phones:
            # Filter out very short numbers that might not be phone numbers
            valid_phones = [phone for phone in phones if len(phone) >= 7]
            if valid_phones:
                contact_info['phones'] = list(set(valid_phones))

        # Look for address (if in specific elements)
        address = response.css('.address::text, .contact-address::text, [class*="address"]::text').getall()
        if address:
            contact_info['addresses'] = [addr.strip() for addr in address if addr.strip()]

        return contact_info if contact_info else None

    def extract_programs(self, response):
        """Extract academic programs/courses information"""
        programs = []
        
        # Look for program listings (adjust selectors based on actual site structure)
        program_elements = response.css('.program, .course, .degree, [class*="program"], [class*="course"]')
        
        for program in program_elements:
            program_data = {
                'name': program.css('::text').get(),
                'description': program.css('.description::text, p::text').get(),
                'link': urljoin(response.url, program.css('a::attr(href)').get()) if program.css('a::attr(href)').get() else None
            }
            if program_data['name']:
                programs.append(program_data)

        return programs if programs else None