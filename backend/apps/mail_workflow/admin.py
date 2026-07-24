from django.contrib import admin
from .models import IncomingMail, MailScanRecord, MailAssignment, MailMovement

admin.site.register(IncomingMail)
admin.site.register(MailScanRecord)
admin.site.register(MailAssignment)
admin.site.register(MailMovement)
