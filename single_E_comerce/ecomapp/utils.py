# import random
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string
# from django.conf import settings
# from .models import EmailOTP

# def generate_otp(email):
#     # 1. 6 digit-er random code
#     code = str(random.randint(100000, 999999))
#     # 2. Database cleanup & save (Ete security bare)
#     EmailOTP.objects.filter(email=email).delete() 
#     EmailOTP.objects.create(email=email, code=code)
#     # 3. Email-er context
#     mail_context = {
#         'otp_code': code,
#         'expiry_minutes': 60,
#     }
#     # 4. Amader custom send_email call kora
#     send_email(
#         mail_to=[email],
#         cc_list=[],
#         bcc_list=[],
#         subject='Your Ecommerce OTP Code',
#         template='website/mail/otp_mail.html', # Check koro ei path-e file-ti ache kina
#         context=mail_context
#     )
#     return code

# def send_email(mail_to,cc_list,bcc_list,subject,template,context):
#     mail_to_set=set(mail_to)
#     cc_list_set=set(cc_list)
#     common_emails = mail_to_set.intersection(cc_list_set)
#     cc_list_set = cc_list_set - common_emails
#     html_body = render_to_string(template, context)
#     if len(mail_to) > 0:
#         email=  EmailMultiAlternatives(
#             subject=subject,
#             body=html_body,
#             from_email=settings.EMAIL_HOST_USER,
#             to=list(mail_to_set),
#             cc=list(cc_list_set),
#             bcc=list(bcc_list)
#         )
#         email.attach_alternative(html_body, "text/html")
#         try:
#             email.send(fail_silently=False)
#         except Exception as e:
#             print(f"Error sending email: {e}")