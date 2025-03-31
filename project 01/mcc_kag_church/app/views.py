from django.shortcuts import render
from django.shortcuts import render, redirect
from .models import FirstTimeVisitor
from django.contrib import messages
from .forms import FirstTimeVisitorForm
from .forms import ContactForm
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
def home(request):
    return render(request, 'church/index.html')

from .models import Leadership, Belief

def about(request):
    leaders = Leadership.objects.filter(is_active=True).order_by('order')
    beliefs = Belief.objects.all().order_by('order')
    return render(request, 'church/about.html', {
        'leaders': leaders,
        'beliefs': beliefs
    })

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Create but don't save yet
            contact_message = form.save(commit=False)
            # Set default status and empty admin notes
            contact_message.status = 'new'
            contact_message.admin_notes = ''
            # Now save to database
            contact_message.save()
            
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('church:contact')  # Use your URL namespace
    else:
        form = ContactForm()
    
    return render(request, 'church/contact.html', {'form': form})


from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import ContactMessage, FirstTimeVisitor

@staff_member_required
def custom_admin_dashboard(request):
    recent_messages = ContactMessage.objects.order_by('-created_at')[:5]
    recent_visitors = FirstTimeVisitor.objects.order_by('-created_at')[:5]
    message_stats = {
        'total': ContactMessage.objects.count(),
        'new': ContactMessage.objects.filter(status='new').count(),
        'in_progress': ContactMessage.objects.filter(status='in_progress').count(),
        'resolved': ContactMessage.objects.filter(status='resolved').count(),
    }
    visitor_stats = {
        'total': FirstTimeVisitor.objects.count(),
        'this_month': FirstTimeVisitor.objects.filter(
            created_at__month=timezone.now().month
        ).count(),
    }
    
    return render(request, 'admin/dashboard.html', {
        'recent_messages': recent_messages,
        'recent_visitors': recent_visitors,
        'message_stats': message_stats,
        'visitor_stats': visitor_stats,
    })


def visit(request):
    if request.method == 'POST':
        form = FirstTimeVisitorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for submitting your visit information! We look forward to seeing you.')
            return redirect('visit')
    else:
        form = FirstTimeVisitorForm()
    
    return render(request, 'church/visit.html', {'form': form})
