#This file is basically database tables in django it is treated as model
from django.contrib.auth.models import User  #this is djangos inbuilt user table
from django.db import models


EMAIL_TYPE_CHOICES = [
    (0, 'Inbox'),
    (1,'Upload_eml'),
    (2, 'Sent'),
   
]

class Email(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='emails',db_comment="Foreign key to the user table who owns this email.")
    from_email = models.CharField(max_length=255,db_comment="Email address from which the email was sent")
    to = models.TextField(db_comment="Recipients email address")  # Comma-separated or JSON
    cc = models.TextField(blank=True, null=True,db_comment="Carbon copy (CC) recipient email addresses, comma-separated.")
    bcc = models.TextField(blank=True, null=True,db_comment="Blind carbon copy (BCC) recipient email addresses, comma-separated (not visible to other recipients")
    subject = models.CharField(max_length=255,db_comment="Subject line of email")
    body_plain = models.TextField(blank=True, null=True,db_comment="Plain text content of an email body")
    body_html = models.TextField(blank=True, null=True,db_comment="Html content of an email body")
    timestamp = models.DateTimeField(auto_now_add=True,db_comment="Data / Time when the email record is created or recevied")
    email_type = models.IntegerField(choices=EMAIL_TYPE_CHOICES,default=1,db_comment="Categories of emaillll")
    is_read = models.BooleanField(default=False,db_comment="Flag to indicate if the email has been read by the user")


    def __str__(self):
        return f"{self.subject} - {self.from_email}"

    

class Attachment(models.Model):
    email = models.ForeignKey(Email, related_name='attachments', on_delete=models.CASCADE,db_comment="Foreign key linking to the email message this attachment belongs to.")
    filename = models.CharField(max_length=255,db_comment="original filename of attached file")
    file = models.FileField(upload_to='attachments/',db_comment="path to store attached file on server")

    class Meta:
        db_table_comment = "Stores details about files attached to email messages."
        verbose_name = "Attachment"
        verbose_name_plural = "Attachments"


    def __str__(self):
        return f"{self.filename}- {self.email.from_email}"