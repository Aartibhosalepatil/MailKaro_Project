from django.contrib.auth.decorators import login_required # for authentication
from django.shortcuts import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import EmailForm, EMLUploadForm
from django.db.models import Q   # Q is basically used to create complex queries
from django.views.decorators.csrf import csrf_exempt
from email import message_from_bytes
from email.policy import default as default_policy
from datetime import datetime
from .models import Email, Attachment
from django.core.files.base import ContentFile   #used to create file object from bytes
import email
from email import policy # for parsing emails we used policy
from django.contrib import messages
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage  # used for pagination
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.urls import reverse


# This view for Inbox Functionality

# views.py

@login_required
def inbox_view(request):
    query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', 'date')
    order = request.GET.get('order', 'desc') 

    # advance search fields
    from_email = request.GET.get('from_email', '')
    to_email = request.GET.get('to_email', '')
    subject = request.GET.get('subject', '')
    date_on_str = request.GET.get('date_on', '') 


    # Start with the base queryset for the logged-in user's inbox
    emails_queryset = Email.objects.filter(user=request.user, email_type=0)
    
    # --- Build the dynamic filter using Q objects ---
    filters = Q() # Start with an empty Q object

    # Apply general keyword search if 'q' is present
    if query:
        filters &= (
            Q(subject__icontains=query) |
            Q(from_email__icontains=query) |
            Q(to__icontains=query) |
            Q(body_plain__icontains=query)
        )
    
    # Apply advanced search filters if they are provided
    if from_email:
        filters &= Q(from_email__icontains=from_email)
    
    if to_email:
        # Search the 'to', 'cc', and 'bcc' fields for the recipient's email
        filters &= (Q(to__icontains=to_email) |
                    Q(cc__icontains=to_email) |
                    Q(bcc__icontains=to_email))
    
    if subject:
        filters &= Q(subject__icontains=subject)


    if date_on_str:
        try:
            date_on = datetime.strptime(date_on_str, '%Y-%m-%d').date()
            filters &= Q(timestamp__date=date_on)
        except ValueError:
            pass # Ignore invalid date format

    # Apply all accumulated filters to the queryset
    emails_queryset = emails_queryset.filter(filters)

    inbox_total_count = emails_queryset.count()
    
    # Apply sorting based on 'sort_by' and 'order'
    if sort_by == 'from':
        sort_field = 'from_email'
    elif sort_by == 'subject':
        sort_field = 'subject'
    elif sort_by == 'date':
        sort_field = 'timestamp'
    else:
        sort_field = 'timestamp'

    if order == 'desc':
        emails_queryset = emails_queryset.order_by(f'-{sort_field}')
    else:
        emails_queryset = emails_queryset.order_by(sort_field)

    # This is Pagination Logic
    paginator = Paginator(emails_queryset, 10)
    page_num = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    context = {
        'page_obj': page_obj,
        'query': query,
        'sort_by': sort_by,
        'order': order,
        'inbox_total_count': inbox_total_count,
        'from_email': from_email,
        'to_email': to_email,
        'subject': subject,
        'date_on': date_on_str, # NEW: Pass the single date back
    }
    return render(request, 'mail/inbox.html', context)




# This view for compose functionality
@login_required
def compose_view(request):
    if request.method == 'POST':
        form = EmailForm(request.POST, request.FILES)
        if form.is_valid():
            # Sender copy
            email_obj = form.save(commit=False)
            email_obj.user = request.user
            email_obj.from_email = request.user.email
            email_obj.email_type = 2  # for sent emails
            email_obj.save()
            form.save_m2m() #this is used to save many to many relationships if any

            # Save attachments for sender copy
            for f in request.FILES.getlist('attachments'):
                Attachment.objects.create(
                    email=email_obj,
                    filename=f.name,
                    file=f
                )

            # Recipient copies
            recipient_emails = [email.strip() for email in form.cleaned_data['to'].split(',')]
            for recipient_email in recipient_emails:
                try:
                    recipient_user = User.objects.get(email=recipient_email)

                    recipient_email_obj = Email.objects.create(
                        user=recipient_user,
                        from_email=email_obj.from_email,
                        to=email_obj.to,
                        cc=email_obj.cc,
                        bcc=email_obj.bcc,
                        subject=email_obj.subject,
                        body_plain=email_obj.body_plain,
                        body_html=email_obj.body_html,
                        email_type=0,  # this is for inbox emails
                        is_read=False
                    )

                    # Copy attachments
                    for att in email_obj.attachments.all():
                        Attachment.objects.create(
                            email=recipient_email_obj,
                            filename=att.filename,
                            file=att.file
                        )

                except User.DoesNotExist:
                    messages.warning(request, f"User with email {recipient_email} not found. Mail skipped.")

            messages.success(request, "Email sent successfully!")
            return redirect('sent')  # redirect to Sent folder
    else:
        form = EmailForm()

    return render(request, 'mail/compose.html', {'form': form})


# This view for message_details means after clicking on subject link detailed email message will come
@login_required
def message_detail_view(request, type, email_id):
    # This checks if the email belongs to the user OR if the user is a recipient (to, cc, or bcc)
    email_obj = get_object_or_404(Email, 
        Q(id=email_id) & (
            Q(user=request.user) |
            Q(to__icontains=request.user.email) |
            Q(cc__icontains=request.user.email) |
            Q(bcc__icontains=request.user.email)
        )
        
    )

    email_obj.is_read = True
    email_obj.save()
     # Decide back link based on "type"
    if type == "sent":
        back_url = reverse("sent")   # make sure your url name for sent list is 'sent'
        back_text = "← Back to Sent"
    else:
        back_url = reverse("inbox")  # make sure your url name for inbox list is 'inbox'
        back_text = "← Back to Inbox"

    return render(request, "mail/message_detail.html", {
        "email": email_obj,
        "back_url": back_url,
        "back_text": back_text,
    })
  

@login_required
def sent_mail_view(request):
    emails = Email.objects.filter(user=request.user, email_type=2).order_by('-timestamp')
    return render(request, 'mail/sent.html', {'emails': emails})


@login_required
def eml_upload_view(request):
    if request.method == 'POST' and request.FILES.get('eml_file'):
        eml_file = request.FILES['eml_file']

        # Validate file extension
        if not eml_file.name.lower().endswith('.eml'):
            messages.error(request, "Only .eml files are allowed.")
            return render(request, 'mail/eml_upload.html')

        try:
            eml_bytes = eml_file.read()   # it reads the file content in bytes
            msg = email.message_from_bytes(eml_bytes, policy=policy.default)   

            user = request.user
            from_email = msg['from']
            to = msg['to']
            cc = msg['cc']
            bcc = msg['bcc']
            subject = msg['subject']
            body_plain = None
            body_html = None

            # Extract body
            if msg.is_multipart():
                for part in msg.walk():
                    ctype = part.get_content_type()
                    if ctype == "text/plain":
                        body_plain = part.get_content()
                    elif ctype == "text/html":
                        body_html = part.get_content()
            else:
                body_plain = msg.get_content()

            # Save Email object
            email_obj = Email.objects.create(
                user=user,
                from_email=from_email or "",
                to=to or "",
                cc=cc or "",
                bcc=bcc or "",
                subject=subject or "No Subject",
                body_plain=body_plain,
                body_html=body_html,
                email_type=0,
            )

            # Saving the attachments
            for part in msg.walk():
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    file_content = part.get_payload(decode=True) # bascially this retrives the actual file content
                    if filename and file_content:
                        attachment = Attachment(email=email_obj, filename=filename) 
                        attachment.file.save(filename, ContentFile(file_content))  # by default django will have filesystemstorage which handles the name colision and saves the file and renames it if already exists.This function actually works behind this get_available_name(self, name, max_length=None):
                        attachment.save()

            return redirect('inbox')

        except Exception as e:
            messages.error(request, f"Failed to process the file: {str(e)}")
            return render(request, 'mail/eml_upload.html')

    return render(request, 'mail/eml_upload.html')


# This view is for Parsing .eml file
def parse_eml(file):
    msg = message_from_bytes(file.read(), policy=default_policy)  #this will read eml file
    from_email = msg.get('From', '')  # then extract headers 
    to_email = msg.get('To', '')
    cc_email = msg.get('Cc', '')
    bcc_email = msg.get('Bcc', '') 
    subject = msg.get('Subject', '')
    date = msg.get('Date', '')

    #here it will try to parse the date if not available it will use now means current date time
    try:
        parsed_date = datetime.strptime(date[:25], '%a, %d %b %Y %H:%M:%S')
    except Exception:
        parsed_date = datetime.now()

    plain_body = ""
    html_body = ""
    attachments = []

    # it will check for multipart
    if msg.is_multipart():
        for part in msg.walk():  #msg.walk()is method that will iterate through all the parts of the email.
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition") or "")
            if content_type == "text/plain" and "attachment" not in content_disposition: # check if text is plain and not attachment then it will add in plain_text
                try:
                    plain_body += part.get_content()
                except:
                    payload = part.get_payload(decode=True)
                    if payload:
                        plain_body += payload.decode(part.get_content_charset() or 'utf-8', errors='ignore')
            elif content_type == "text/html" and "attachment" not in content_disposition: # check if content is in html and not in attachment then add in html_body
                try:
                    html_body += part.get_content()
                except:
                    payload = part.get_payload(decode=True)
                    if payload:
                        html_body += payload.decode(part.get_content_charset() or 'utf-8', errors='ignore')
            elif "attachment" in content_disposition: # same for attachment
                filename = part.get_filename()
                if filename:
                    payload = part.get_payload(decode=True)
                    attachments.append({'filename': filename, 'content': payload})
    else:
        content_type = msg.get_content_type()  # if contnt not in multipart then it will just read plain_text and html
        if content_type == "text/plain":
            try:
                plain_body = msg.get_content()
            except:
                payload = msg.get_payload(decode=True)
                if payload:
                    plain_body = payload.decode(msg.get_content_charset() or 'utf-8', errors='ignore')
        elif content_type == "text/html":
            try:
                html_body = msg.get_content()
            except:
                payload = msg.get_payload(decode=True)
                if payload:
                    html_body = payload.decode(msg.get_content_charset() or 'utf-8', errors='ignore')

    return {                              # here creating dictionary to pass data in template
        'from_email': from_email,
        'to_email': to_email,
        'cc_email': cc_email,
        'bcc_email': bcc_email,
        'subject': subject,
        'plain_body': plain_body,
        'html_body': html_body,
        'timestamp_date': parsed_date,
        'attachments': attachments,
    }


#This logic is for downloading attachment after going on message_detail page
@csrf_exempt
@login_required
def download_attachment(request, attachment_id):
    att = get_object_or_404(Attachment, id=attachment_id)  # it retrives the attachment obj from db , if not found raise 404 error
    response = HttpResponse(att.file, content_type='application/octet-stream')  # sends actual file data to browser
    response['Content-Disposition'] = f'attachment; filename="{att.filename}"' #C-D means it basically instruct browser to download a file with its original name .
    return response


@require_POST                              # This decorator ensures that the view only accepts POST requests
@csrf_protect
def delete_email_view(request, email_id):
    try:
        email = get_object_or_404(Email, pk=email_id)
        # Check if the email belongs to the logged-in user
        email.delete()
        return JsonResponse({'message': 'Email deleted successfully'}, status=200)
    except Email.DoesNotExist:
        return JsonResponse({'error': 'Email not found'}, status=404)
    except Exception as e:
        # Log the error for debugging on the server side
        print(f"Error deleting email {email_id}: {e}")
        return JsonResponse({'error': 'An internal server error occurred'}, status=500)
    




