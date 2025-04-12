from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .forms import ProductForm
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_POST

# views.py의 product_list 뷰 수정
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




def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '제품이 등록되었습니다!')
            form = ProductForm()  # 폼 새로 초기화 (빈 입력창)
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

# views.py
# inventory/views.py
def search_by_location(request):
    query = request.GET.get('q')
    products = []

    if query:
        query = query.strip()
        # 위치코드 형식인지 확인: A-12-B3
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


