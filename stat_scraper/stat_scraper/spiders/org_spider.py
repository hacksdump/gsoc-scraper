import scrapy
from datetime import datetime
from peewee import SqliteDatabase, Model, CharField, ForeignKeyField, IntegerField


class OrgSpider(scrapy.Spider):
    name = "orgs"
    base_url = dict(
        pre_2016="https://www.google-melange.com",
        since_2016="https://summerofcode.withgoogle.com",
    )
    db_name = "orgs.db"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        db = SqliteDatabase(self.db_name)

        class BaseModel(Model):
            class Meta:
                database = db

        class Org(BaseModel):
            name = CharField(unique=True)

        class ProjectCount(BaseModel):
            org = ForeignKeyField(Org)
            year = IntegerField()
            count = IntegerField()

        models = [Org, ProjectCount]

        db.connect()
        db.drop_tables(models)
        db.create_tables(models)

        self._OrgModel = Org
        self._ProjectCountModel = ProjectCount

    def add_org(self, name):
        return self._OrgModel.get_or_create(name=name)[0]

    def add_project_count(self, org_object, year, count):
        self._ProjectCountModel.create(org=org_object, year=year, count=count)

    def start_requests(self):
        this_year = datetime.now().year
        for year in range(2016, this_year):
            url = "{}/archive/{}/organizations/".format(self.base_url['since_2016'], year)
            yield scrapy.Request(url=url, callback=self.parse_since_2016, meta=dict(year=year))

        for year in range(2009, 2016):
            url = "{}/archive/gsoc/{}".format(self.base_url['pre_2016'], year)
            yield scrapy.Request(url=url, callback=self.parse_before_2016, meta=dict(year=year))

    def parse_before_2016(self, response):
        org_list_elements = response.css('ul.mdl-list').css('li')
        year = response.meta['year']
        for org_list_element in org_list_elements:
            projects_link__relative = org_list_element.css('a::attr(href)').get()
            projects_link__absolute = self.base_url['pre_2016'] + projects_link__relative
            yield scrapy.Request(projects_link__absolute,
                                 callback=self.parse_projects_page__pre_2016,
                                 meta=dict(year=year))

    def parse_projects_page__pre_2016(self, response):
        year = response.meta['year']
        org_name = response.css('h3::text').get()
        projects = response.css('ul.mdl-list').css('li')
        project_count = len(projects)
        org_object = self.add_org(org_name)
        self.add_project_count(org_object, year, project_count)

    def parse_since_2016(self, response):
        org_list_elements = response.css('li.organization-card__container')
        year = response.meta['year']
        for org_list_element in org_list_elements:
            projects_link__relative = org_list_element.css('a::attr(href)').get()
            projects_link__absolute = self.base_url['since_2016'] + projects_link__relative
            yield scrapy.Request(projects_link__absolute,
                                 callback=self.parse_projects_page__since_2016,
                                 meta=dict(year=year))

    def parse_projects_page__since_2016(self, response):
        year = response.meta['year']
        org_name = response.css('h3.banner__title::text').get()
        projects = response.css('ul.project-list-container').css('li')
        project_count = len(projects)
        org_object = self.add_org(org_name)
        self.add_project_count(org_object, year, project_count)
