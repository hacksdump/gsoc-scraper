import scrapy


class OrgSpider(scrapy.Spider):
    name = "orgs"
    base_url = "https://summerofcode.withgoogle.com"

    def start_requests(self):
        urls = [
            "https://summerofcode.withgoogle.com/archive/2018/organizations/"
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        with open("dump.html", "w") as f:
            org_list_elements = response.css('li.organization-card__container')
            for org_list_element in org_list_elements:
                projects_link__relative = org_list_element.css('a::attr(href)').get()
                projects_link__absolute = self.base_url + projects_link__relative
                yield scrapy.Request(projects_link__absolute, callback=self.parse_projects_page)

    def parse_projects_page(self, response):
        org_name = response.css('h3.banner__title::text').get()
        print(org_name)
        projects = response.css('ul.project-list-container').css('li')
        print(len(projects))
