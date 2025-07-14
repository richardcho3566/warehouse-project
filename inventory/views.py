from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .forms import ProductForm, CSVUploadForm, SignUpForm, GradeUpdateForm
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_POST
import io
import csv
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth import login
from .models import Profile
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from .decorators import grade_required
from django.db.models import Q

@login_required
def product_list(request):
    query = request.GET.get('q')
    sort = request.GET.get('sort', 'product_name')
    order = request.GET.get('order', 'asc')

    products = Product.objects.all()

    if query:
        products = products.filter(product_name__icontains=query)

    if sort == 'location_code':
        if order == 'asc':
            products = products.order_by('warehouse', 'shelf_number', 'column', 'level')
        else:
            products = products.order_by('-warehouse', '-shelf_number', '-column', '-level')
    else:
        sort_field = sort if order == 'asc' else f'-{sort}'
        products = products.order_by(sort_field)

    return render(request, 'inventory/product_list.html', {
        'products': products,
        'query': query,
        'sort': sort,
        'order': order,
    })


@login_required
@grade_required(['GRADE2', 'GRADE3'])
def add_product(request):
    product_name = request.GET.get('product_name', '')

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '제품이 성공적으로 등록되었습니다.')
            return redirect('add_product')
    else:
        form = ProductForm(initial={'product_name': product_name})

    return render(request, 'inventory/add_product.html', {'form': form})




@require_POST
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()

    from_page = request.GET.get('from')
    query = request.GET.get('q', '')

    if from_page == 'search':
        return redirect(f"{reverse('search_by_location')}?q={query}")
    else:
        return redirect('product_list')


def search_by_location(request):
    query = request.GET.get('q', '').strip().upper()
    products = []

    def parse_code(code):
        code = code.replace("-", "")
        if len(code) < 3:
            return None

        warehouse = code[0]
        shelf = code[1:3]
        rest = code[3:]

        import re
        match = re.match(r'^([A-Z0-9]{1,2})(\d?)$', rest)
        if not match:
            column = ""
            level = ""
        else:
            column = match.group(1)
            level = match.group(2)

        return warehouse, shelf, column, level

    if query:
        parsed = parse_code(query)
        if parsed:
            warehouse, shelf, column, level = parsed
            filters = {
                'warehouse__iexact': warehouse,
                'shelf_number__istartswith': shelf,
            }
            if column:
                filters['column__istartswith'] = column
            if level:
                filters['level__startswith'] = level

            products = Product.objects.filter(**filters)
        else:
            products = Product.objects.filter(product_name__icontains=query)

    return render(request, 'inventory/search_by_location.html', {
        'products': products,
        'query': query
    })



def upload_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.reader(io_string)
            next(reader)

            for row in reader:
                product_name, warehouse, shelf_number, column, level = row
                Product.objects.create(
                    product_name=str(product_name).strip(),
                    warehouse=str(warehouse).strip(),
                    shelf_number=str(shelf_number).strip().zfill(2),
                    column=str(column).strip(),
                    level=str(level).strip()
                )
            return redirect('product_list')
    else:
        form = CSVUploadForm()
    return render(request, 'inventory/upload_csv.html', {'form': form})


def download_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'

    writer = csv.writer(response)
    writer.writerow(['product_name', 'warehouse', 'shelf_number', 'column', 'level'])

    for product in Product.objects.all():
        writer.writerow([
            product.product_name,
            product.warehouse,
            product.shelf_number,
            product.column,
            product.level
        ])

    return response


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user, grade='GRADE1')
            login(request, user)
            return redirect('product_list')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
@grade_required(['GRADE3'])
def user_list(request):
    users = Profile.objects.select_related('user').all()
    return render(request, 'inventory/user_list.html', {'users': users})


@login_required
@grade_required(['GRADE3'])
def update_grade(request, profile_id):
    profile = Profile.objects.get(id=profile_id)
    if request.method == 'POST':
        form = GradeUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = GradeUpdateForm(instance=profile)
    return render(request, 'inventory/update_grade.html', {'form': form, 'profile': profile})
