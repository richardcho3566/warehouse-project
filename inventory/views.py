from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .forms import ProductForm, CSVUploadForm
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_POST
import io
import csv
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.http import HttpResponse
from django.contrib.auth import login
from .forms import SignUpForm
from .models import Profile
from django.contrib.admin.views.decorators import staff_member_required
from .forms import GradeUpdateForm
from django.contrib.auth.models import User



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
def add_product(request):
    if request.user.profile.grade not in ['GRADE2', 'GRADE3']:
        return HttpResponseForbidden("권한이 없습니다.")  # 403 오류 반환

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '제품이 등록되었습니다!')
            form = ProductForm()
    else:
        form = ProductForm()
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
    query = request.GET.get('q')
    products = []

    if query:
        query = query.strip()
        if '-' in query and len(query.split('-')) == 3:
            try:
                parts = query.upper().split('-')
                warehouse = parts[0]
                shelf = parts[1]
                column = parts[2][0]
                level = int(parts[2][1:])
                products = Product.objects.filter(
                    warehouse=warehouse,
                    shelf_number=shelf,
                    column=column,
                    level=level
                )
            except:
                products = []
        else:
            # 제품명 기준 검색
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
            next(reader)  # 첫 줄 (헤더) 건너뛰기

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
            # 기본 등급 GRADE1 부여
            Profile.objects.create(user=user, grade='GRADE1')
            login(request, user)  # 회원가입 후 자동 로그인
            return redirect('product_list')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def user_list(request):
    if not request.user.profile.grade == 'GRADE3':
        return redirect('product_list')

    users = Profile.objects.select_related('user').all()
    return render(request, 'inventory/user_list.html', {'users': users})

@login_required
def update_grade(request, profile_id):
    if not request.user.profile.grade == 'GRADE3':
        return redirect('product_list')

    profile = Profile.objects.get(id=profile_id)
    if request.method == 'POST':
        form = GradeUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = GradeUpdateForm(instance=profile)
    return render(request, 'inventory/update_grade.html', {'form': form, 'profile': profile})


def create_admin(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin1234'
        )
        return HttpResponse("✅ 슈퍼유저 'admin' 생성 완료!")
    else:
        return HttpResponse("ℹ️ 이미 admin 계정이 존재합니다.")