from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import models
from accounts.models import ShopOwnerProfile, CustomerProfile, EmailOTP, User
from shops.models import Shop
from django.utils.text import slugify
from admin_management.utils import generate_otp, send_email

#------------------------------Admin Authentication Views------------------------------#
@login_required
def merchant_register(request):
    if request.method == "POST":
        u_name    = request.POST.get('username')
        email     = request.POST.get('email')
        pass_word = request.POST.get('password')
        s_name    = request.POST.get('shop_name')
        phone     = request.POST.get('phone')

        if not all([u_name, email, pass_word, phone]):
            messages.error(request, "Required fields are missing!")
            return render(request, 'merchant_register')

        if User.objects.filter(username=u_name).exists():
            messages.error(request, "Username already exists!")
            return redirect('merchant_register')

        try:
            with transaction.atomic():
                new_user = User.objects.create_user(
                    username=u_name, 
                    email=email, 
                    password=pass_word,
                    is_shop_owner=True,
                    is_customer = True,
                    is_active=True 
                )
                new_user.set_password(pass_word)
                new_user.save()

                profile, created = ShopOwnerProfile.objects.get_or_create(user=new_user)
                profile.phone = phone
                profile.profile_pic = request.FILES.get('profile_pic')
                profile.trade_license = request.POST.get('trade_license')
                profile.nid_number = request.POST.get('nid_number')
                profile.date_of_birth = request.POST.get('date_of_birth') or None
                profile.gender = request.POST.get('gender')
                profile.district = request.POST.get('district')
                profile.thana = request.POST.get('thana')
                profile.address_details = request.POST.get('address_details')
                profile.is_active = False
                profile.is_verified = False
                profile.save()

                base_slug = slugify(s_name)
                Shop.objects.create(
                    owner=profile,
                    shop_name=s_name,
                    shop_slug=base_slug,
                    shop_logo=request.FILES.get('shop_logo'),
                    shop_description=request.POST.get('shop_description'),
                    phone=phone,
                    email=email,
                    shop_address=request.POST.get('shop_address'),
                    trade_license=request.POST.get('trade_license'),
                    is_active=False,   
                    is_verified=False 
                )
            messages.success(request, "Merchant account and shop created successfully!")
            request.session['pending_user_id'] = new_user.id
            return redirect('merchant_login')
        except Exception as e:
            print(f"Registration Error: {e}")
            messages.error(request, "Something went wrong during registration.")
            return render(request, 'accounts/merchant/merchant_register.html')
    return render(request, 'accounts/merchant/merchant_register.html')

def merchant_login(request):
    if request.user.is_authenticated: 
        return redirect('owner_dashboard')
    
    if request.method == 'POST':
        identifier = request.POST.get('phone')
        password = request.POST.get('password')
        user_obj = None
        profile = ShopOwnerProfile.objects.filter(
            models.Q(phone=identifier) | models.Q(user__username=identifier) #| models.Q(user__email=identifier)
        ).select_related('user').first() 
        if profile:
            user_obj = profile.user
        else:
            user_obj = User.objects.filter(username=identifier).first()
    
        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                if not profile:
                    messages.error(request, "You have not any Merchant account. For a merchant account, please contact with support.")
                    return redirect('merchant_login')
                
                shop = Shop.objects.filter(owner=profile).first() if profile else None
                if shop and not shop.is_verified:
                    messages.warning(request, "Your shop is not verified. Please verify with mail.")
                    return redirect(f"{reverse('verify_otp_shop_account')}?email={shop.email}")
                
                if shop and not shop.is_active:
                    messages.error(request, "Your shop account is suspend by HaatBazar. Please contact for details.")
                    return redirect('merchant_login')
                
                if not profile.is_active:
                    messages.error(request, "The shop owner account is currently disabled. Contact support.")
                    return redirect('merchant_login')
                
                if not profile.is_verified:
                    messages.warning(request, "The shop owner is not verified. Please contact support for verification.")
                    return redirect('merchant_login')

                login(request, user)
                shop_name = shop.shop_name if shop else user.username
                messages.success(request, f"Welcome back to {shop_name}!")
                return redirect('owner_dashboard')
            else:
                messages.error(request, "Invalid password. Please try again.")
        else:
            messages.error(request, "No account found with this username or phone.")
        return redirect('merchant_login')
    return render(request, 'accounts/merchant/merchant_login.html')

@login_required
def merchant_logout(request):
    logout(request)
    return redirect('merchant_login')

def request_otp_for_shop(request):
    if request.method == 'POST':
        email  = request.POST.get('email')
        shop = Shop.objects.filter(email=email).first()
        if shop:
            if not shop.is_verified:
                generate_otp(email)
                messages.success(request, "A new OTP has been sent to your email.")
                base_url = reverse('verify_otp_shop_account')
                return redirect(f"{base_url}?email={email}")
            else:
                messages.info(request, "This shop is already verified. Please login.")
                return redirect('merchant_login')
        else:
            messages.error(request, "No account found with this email. Please give the registered email or register a new account.")
            return redirect('request_shop_otp')
    return render(request, 'accounts/merchant/request_otp.html')

def verify_otp_shop_account(request):
    email = request.GET.get('email') or request.POST.get('email')
    if not email:
        messages.error(request, "Invalid request. Please provide an email.")
        return redirect('request_shop_otp') 

    shop = Shop.objects.select_related('owner__user').filter(email=email).first()
    if request.method == 'POST':
        otp = request.POST.get('otp')
        otp_obj = EmailOTP.objects.filter(email=email, code=otp).order_by('-created_at').first()
        if otp_obj and not otp_obj.is_expired():
            user = shop.owner.user if shop and shop.owner else User.objects.filter(email=email).first()
            if not user:
                messages.error(request, "User account not found. Please register first.")
                return redirect('request_shop_otp')
            
            if shop:
                shop.is_verified = True
                shop.save()

                if not hasattr(user, 'backend'):
                    user.backend = 'django.contrib.auth.backends.ModelBackend'

                login(request, user) 
                otp_obj.delete()
                messages.success(request, f"Welcome {user.first_name}! Your account is now verified.Please wait for admin approval. You will be notified via email once approved.")
                return redirect('merchant_login') 
            else:
                messages.error(request, "Shop profile not found. Please contact support for your shop registeration.")
                return redirect('request_shop_otp')
        else:
            messages.error(request, "Invalid or expired OTP.")
            return render(request, 'accounts/merchant/verify_otp.html', {'email': email, 'shop': shop})
    return render(request, 'accounts/merchant/verify_otp.html', {'email': email, 'shop': shop})

def merchant_forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            generate_otp(email) 
            messages.success(request, 'A verification code has been sent to your email.')
            return redirect(f"{reverse('merchant_reset_password')}?email={email}")
        else:
            messages.error(request, 'No account found with this email address.')
            return redirect('forgot_password')
    return render(request, 'accounts/merchant/forgot_password.html')

def merchant_reset_password(request):
    email = request.GET.get('email')
    if request.method == 'POST':
        otp_code = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/merchant/reset_password.html', {'email': email})

        otp_obj = EmailOTP.objects.filter(email=email, code=otp_code, is_active=True).last()

        if otp_obj and not otp_obj.is_expired():
            user = User.objects.filter(email=email).first()
            if user:
                user.set_password(new_password)
                user.save()
                otp_obj.is_active = False
                otp_obj.save()

                messages.success(request, 'Password reset successful! Please login with your new password.')
                return redirect('merchant_login')
            else:
                messages.error(request, 'Account not found.')
        else:
            messages.error(request, 'Invalid or expired OTP.')
    return render(request, 'accounts/merchant/reset_password.html', {'email': email})
#------------------------------Customers Authentication Views------------------------------#

def customer_register(request):
    if request.method == 'POST':
        full_name   = request.POST.get('full_name')
        profile_pic = request.FILES.get('profile_pic') 
        email       = request.POST.get('email')
        phone       = request.POST.get('phone')
        gender      = request.POST.get('gender')
        dob         = request.POST.get('date_of_birth')
        password    = request.POST.get('password')
        
        if CustomerProfile.objects.filter(phone=phone).exists():
            messages.error(request, 'This phone number is already taken.')
            return redirect('customer_register')    
        try:
            with transaction.atomic():
                user = User.objects.filter(email=email).first()
                if user:
                    if user.is_customer or hasattr(user, 'customer_profile'):
                        messages.error(request, 'You already have a customer account with this email. Please Login.')
                        return redirect('customer_register')
                    if not user.check_password(password):
                        messages.error(request, 'This email is registered as a Shop Owner. Please enter the correct password to add a Customer profile.')
                        return redirect('customer_register')
                    user.is_customer = True
                    user.first_name = full_name 
                    user.save()
                else:
                    user = User.objects.create_user(
                        username=email, 
                        email=email, 
                        password=password,
                        first_name=full_name,
                        is_customer = True,
                        is_active=True
                    )
                profile, created = CustomerProfile.objects.get_or_create(user=user)
                profile.phone = phone
                profile.gender = gender
                profile.date_of_birth = dob if dob else None
                if profile_pic:
                    profile.profile_pic = profile_pic
                profile.is_active = True 
                profile.is_verified = False 
                profile.save()
                
            generate_otp(email) 
            messages.success(request, 'Registration successful! Please verify OTP.')
            return redirect(f"{reverse('verify_otp_customer_account')}?email={email}")
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('customer_register')
    return render(request, 'accounts/customer/customer_register.html')

def customer_login(request):
    if request.user.is_authenticated: 
        return redirect('haatbazar_home')
    
    if request.method == 'POST':
        identifier = request.POST.get('phone')
        password = request.POST.get('password')
        user_obj = None
        profile = CustomerProfile.objects.filter(
            models.Q(phone=identifier) | models.Q(user__email=identifier)
        ).select_related('user').first() 
        if profile:
            user_obj = profile.user
        else:
            user_obj = User.objects.filter(username=identifier).first()
            
        if user_obj:
            if user_obj.is_customer:
                user = authenticate(request, username=user_obj.username, password=password)
                if user is not None:
                    if profile.is_verified:
                        login(request, user)
                        messages.success(request, f"Welcome back, {user.first_name}!")
                        return redirect('haatbazar_home')
                    else:
                        messages.error(request, "Your account is not verified. Please verify your account first.")
                        return redirect(f"{reverse('verify_otp_customer_account')}?email={user.email}")
                else:
                    messages.error(request, "Invalid password. Please give correct password!")
                    return redirect('customer_login')
            else:
                messages.error(request, 'You are now suspending for not maintained our privecy and policy. Please contact HaatBaar Team for Review!')
                return redirect('customer_login')
        else:
            messages.error(request, "No account found with this phone or email.")
            
        return redirect('customer_login') 
    return render(request, 'accounts/customer/customer_login.html')

@login_required
def customer_logout(request):
    logout(request)
    return redirect('haatbazar_home')

def request_otp_for_customer(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            customer = CustomerProfile.objects.filter(user=user).first()
            if customer:
                if not customer.is_verified:
                    generate_otp(email)
                    messages.success(request, "A new OTP has been sent to your email.")
                    base_url = reverse('verify_otp_customer_account') 
                    return redirect(f"{base_url}?email={email}")
                else:
                    messages.info(request, "This account is already verified. Please login.")
                    return redirect('customer_login')
            else:
                messages.error(request, "Customer profile not found. Please register first with this email.")
                return redirect('request_otp_for_customer')
        else:
            messages.error(request, "No customer account found with this email!")
            return redirect('request_otp_for_customer')
    return render(request, 'accounts/customer/request_otp.html')

def verify_otp_customer_account(request):
    email = request.GET.get('email') or request.POST.get('email')
    if not email:
        messages.error(request, "Invalid request. Please provide an valid email.")
        return redirect('request_otp_for_customer') 
    
    if request.method == 'POST':
        otp = request.POST.get('otp')
        otp_obj = EmailOTP.objects.filter(email=email, code=otp).order_by('-created_at').first()
        if otp_obj and not otp_obj.is_expired():
            user = User.objects.filter(email=email).first()
            if not user:
                messages.error(request, "Account not found or already verified.")
                return redirect('customer_login')
            
            customer = CustomerProfile.objects.filter(user=user).first()
            if customer:
                customer.is_active     = True
                customer.is_verified   = True
                customer.save()
                
                if not hasattr(user, 'backend'):
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                otp_obj.delete()
                messages.success(request, f"Congratulations {user.first_name}! Your account is now verified. Please login once")
                return redirect('customer_login') 
            else:
                messages.error(request, "Customer profile not found. Please register first.")
                return redirect('customer_register')
        else:
            messages.error(request, "Invalid or expired OTP.")
            return render(request, 'accounts/customer/verify_otp.html', {'email': email})
    return render(request, 'accounts/customer/verify_otp.html', {'email': email})

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            generate_otp(email) 
            messages.success(request, 'A verification code has been sent to your email.')
            return redirect(f"{reverse('reset_password')}?email={email}")
        else:
            messages.error(request, 'No account found with this email address.')
            return redirect('forgot_password')
    return render(request, 'accounts/customer/forgot_password.html')

def reset_password(request):
    email = request.GET.get('email')
    if request.method == 'POST':
        otp_code = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/customer/reset_password.html', {'email': email})

        otp_obj = EmailOTP.objects.filter(email=email, code=otp_code, is_active=True).last()

        if otp_obj and not otp_obj.is_expired():
            user = User.objects.filter(email=email).first()
            if user:
                user.set_password(new_password)
                user.save()
                otp_obj.is_active = False
                otp_obj.save()

                messages.success(request, 'Password reset successful! Please login with your new password.')
                return redirect('customer_login')
            else:
                messages.error(request, 'Account not found.')
        else:
            messages.error(request, 'Invalid or expired OTP.')
    return render(request, 'accounts/customer/reset_password.html', {'email': email})


# ############################################################## merchant profile views ##############################################################
@login_required
@user_passes_test(lambda u: u.is_shop_owner or u.is_staff) 
def merchant_account_setting(request):
    # .get_or_create user instance er base e profile track korbe
    merchant_profile, created = ShopOwnerProfile.objects.get_or_create(user=request.user)
    context = {
        'merchant': merchant_profile,
        'page_title': 'Merchant Personal Information'
    }
    return render(request, 'accounts/merchant/merchant_accounts_setting.html', context)

@login_required
def edit_merchant_profile_pic(request):
    if request.method == 'POST':
        try:
            # Fixed: 'customer_profile' errors changed to 'shop_owner_profile'
            merchant_profile = request.user.shop_owner_profile
            if 'profile_pic' in request.FILES:
                merchant_profile.profile_pic = request.FILES['profile_pic']
                merchant_profile.save() 
                messages.success(request, "Profile picture updated successfully!")
            else:
                messages.error(request, "No image selected.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    return redirect('merchant_account_setting')

@login_required
def edit_merchant_profile(request):
    if request.method == "POST":
        try:
            merchant_profile, _ = ShopOwnerProfile.objects.get_or_create(user=request.user)
            full_name = request.POST.get('full_name', '').strip()
            if full_name:
                name_parts = full_name.split(' ', 1)
                request.user.first_name = name_parts[0]
                request.user.last_name = name_parts[1] if len(name_parts) > 1 else ""
                request.user.save()

            merchant_profile.phone = request.POST.get('phone', '').strip()
            
            dob = request.POST.get('date_of_birth')
            merchant_profile.date_of_birth = dob if dob else None
            
            merchant_profile.address_details = request.POST.get('address_details', '').strip()
            merchant_profile.thana = request.POST.get('thana', '').strip()
            merchant_profile.district = request.POST.get('district', '').strip()
            
            merchant_profile.save()

            messages.success(request, "Profile updated successfully!")
        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")
            
    return redirect('merchant_account_setting')


# ############################################################## merchant profile views ##############################################################
@login_required
def customer_account_setting(request):
    # .get_or_create ইউজার ইনস্ট্যান্স এর বেস এ কাস্টমার প্রোফাইল ট্র্যাক করবে
    customer_profile, created = CustomerProfile.objects.get_or_create(user=request.user)
    
    context = {
        'customer': customer_profile,
        'page_title': 'Customer Personal Information'
    }
    return render(request, 'accounts/customer/customer_accounts_setting.html', context)

@login_required
def edit_customer_profile_pic(request):
    if request.method == 'POST':
        try:
            customer_profile = request.user.customer_profile
            if 'profile_pic' in request.FILES:
                customer_profile.profile_pic = request.FILES['profile_pic']
                customer_profile.save() 
                messages.success(request, "Profile picture updated successfully!")
            else:
                messages.error(request, "No image selected.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    return redirect('customer_account_setting')

@login_required
def edit_customer_profile(request):
    if request.method == "POST":
        try:
            customer_profile = request.user.customer_profile
            
            # User Basic Data Update
            full_name = request.POST.get('full_name', '').strip().split(' ')
            request.user.first_name = full_name[0]
            request.user.last_name = " ".join(full_name[1:]) if len(full_name) > 1 else ""
            request.user.username = request.POST.get('username')
            request.user.save()

            # Customer Profile Data Update (আপনার কাস্টমার মডেলের ফিল্ড অনুযায়ী)
            customer_profile.phone = request.POST.get('phone')
            customer_profile.date_of_birth = request.POST.get('dob') or None
            customer_profile.gender = request.POST.get('gender')
            customer_profile.district = request.POST.get('district')
            customer_profile.thana = request.POST.get('thana')
            customer_profile.address_details = request.POST.get('address_details')
            customer_profile.save()

            messages.success(request, "Profile updated successfully!")
        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")
            
    return redirect('customer_account_setting')