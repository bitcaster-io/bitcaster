import logging

from django.db import models

logger = logging.getLogger(__name__)


class Organization(models.Model):
    name = models.CharField(max_length=255, db_collation="case_insensitive", unique=True)

    def __str__(self) -> str:
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=255, db_collation="case_insensitive", unique=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name


class Application(models.Model):
    name = models.CharField(max_length=255, db_collation="case_insensitive", unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name
