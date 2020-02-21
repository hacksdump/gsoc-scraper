import scrapy
from datetime import datetime


class OrgSpider(scrapy.Spider):
    name = "orgs"
    base_url = dict(
        pre_2016="https://www.google-melange.com",
        since_2016="https://summerofcode.withgoogle.com",
    )

    def start_requests(self):
        this_year = datetime.now().year
        for year in range(2016, this_year):
            url = "https://summerofcode.withgoogle.com/archive/{}/organizations/".format(year)
            yield scrapy.Request(url=url, callback=self.parse_since_2016, meta=dict(year=year))

    def parse_since_2016(self, response):
        org_list_elements = response.css('li.organization-card__container')
        year = response.meta['year']
        for org_list_element in org_list_elements:
            projects_link__relative = org_list_element.css('a::attr(href)').get()
            projects_link__absolute = self.base_url['since_2016'] + projects_link__relative
            yield scrapy.Request(projects_link__absolute, callback=self.parse_projects_page, meta=dict(year=year))

    def parse_projects_page(self, response):
        year = response.meta['year']
        org_name = response.css('h3.banner__title::text').get()
        projects = response.css('ul.project-list-container').css('li')
        print(year, org_name, len(projects))