# from django.contrib.messages.storage.base import LEVEL_TAGS
# from django.db import models
# from django.utils.safestring import mark_safe
#
# from bitcaster import messages
# from bitcaster.models import (AbstractModel, Application,
#                               ApplicationTriggerKey, Channel, Event,
#                               Message, Organization, Subscription,)
#
# TARGETS = [Organization,
#            Application,
#            Channel, Event, ApplicationTriggerKey, Subscription, Message]
#
# SECTIONS = [m._meta.verbose_name_plural.lower() for m in TARGETS]
#
#
# class ConfigurationIssueManager(models.Manager):
#     def _log(self, level, section, msg):
#         return self.update_or_create(section=section._meta.verbose_name_plural.lower(),
#                                      defaults=dict(message=msg, level=level))
#
#     def error(self, msg, section=Organization):
#         return self._log(messages.ERROR, section, msg)
#
#     def warning(self, msg, section=Organization):
#         return self._log(messages.WARNING, section, msg)
#
#     def get_tag_for(self, section):
#         if section not in SECTIONS:
#             raise ValueError(f'{section} is not in {SECTIONS}')
#         try:
#             return self.filter(section=section).first().tags
#         except AttributeError:
#             return 'success'
#
#
# class ConfigurationIssue(AbstractModel):
#     organization = models.ForeignKey(Organization, on_delete=models.CASCADE,
#                                      related_name='issues')
#     application = models.ForeignKey(Application, on_delete=models.CASCADE,
#                                     related_name='issues',
#                                     blank=True, null=True)
#     section = models.CharField(max_length=20, choices=zip(SECTIONS, SECTIONS))
#     message = models.CharField(max_length=1000)
#     level = models.IntegerField()
#
#     objects = ConfigurationIssueManager()
#
#     class Meta:
#         unique_together = ('application', 'organization', 'section')
#         app_label = 'bitcaster'
#
#     def __str__(self):
#         return f'{self.section:10} {self.message}'
#
#     def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
#         if self.application:
#             self.organization = self.application.organization
#
#         super().save(force_insert, force_update, using, update_fields)
#         self.organization.save()  # change version number
#         if self.application:
#             self.application.save()  # change version number
#
#     @property
#     def tags(self):
#         return ' '.join(tag for tag in [self.level_tag] if tag)
#
#     @property
#     def level_tag(self):
#         return LEVEL_TAGS.get(self.level, '')
#
#
# def as_link(obj):
#     if hasattr(obj, 'get_absolute_url'):
#         return mark_safe('<a href="{0}">{1}</a>'.format(obj.get_absolute_url(), obj))
#     return str(obj)
#
#
# def check_system():
#     ret = []
#     # for org in Organization.objects.all():
#     #     ret.extend(check_organization(org))
#     return ret
#
#
# def check_organization(org):
#     # org.issues.all().delete()
#     # if org.channels.count() == 0:
#     #     org.issues.error('No Channel configured for this Organization', Channel)
#     # elif org.channels.filter(enabled=True).count() == 0:
#     #     org.issues.error('No Channel enabled for this Organization', Channel)
#     #
#     # if org.applications.filter().count() == 0:
#     #     org.issues.warning('No Applications configured for this Organization', Application)
#     # elif org.applications.filter(enabled=True).count() == 0:
#     #     org.issues.warning('No Applications enabled for this Organization', Application)
#
#     return org.issues.all()
#
#
# def check_application(app):
#     # app.issues.all().delete()
#     # if app.events.count() == 0:
#     #     app.issues.warning('No Events configured for this Application', Event)
#     # elif app.events.filter(enabled=True).count() == 0:
#     #     app.issues.error('No Events enabled for Application %s' % as_link(app), Event)
#     #
#     # for event in app.events.all():
#     #     if not event.messages.filter(enabled=True).exists():
#     #         app.issues.error(f"Event '%s' does not have enabled messages" % as_link(event),
#     #                          Event)
#     #     if not event.keys.filter(enabled=True).exists():
#     #         app.issues.error(f"Event '{event}' does not have enabled keys",
#     #                          ApplicationTriggerKey)
#     #
#     # if not app.keys.exists():
#     #     app.issues.warning('No Keys configured for this Application', ApplicationTriggerKey)
#     # elif not app.keys.filter(enabled=True).exists():
#     #     app.issues.warning('No Keys enabled for this Application', ApplicationTriggerKey)
#     #
#     # if app.issues.exists():
#     #     app.save()
#     return app.issues.all()
