import csv
import io

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .decorators import grade_required
from .forms import CSVUploadForm, GradeUpdateForm, ProductForm, SignUpForm
from .models import Product, Profile
from .utils import get_user_grade, parse_location_code, user_grade_context


SAFE_SORT_FIELDS = {
    "product_name": "product_name",
    "warehouse": "warehouse",
    "shelf_number": "shelf_number",
    "column": "column",
    "level": "level",
    "location_code": "location_code",
}


@login_required
def product_list(request):
    # 기존 사용자에게 Profile이 없어도 로그인 직후 500이 나지 않도록 안전하게 보정한다.
    user_grade = get_user_grade(request.user)

    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "product_name")
    order = request.GET.get("order", "asc")

    if sort not in SAFE_SORT_FIELDS:
        sort = "product_name"
    if order not in {"asc", "desc"}:
        order = "asc"

    # q 파라미터가 있을 때만 조회한다.
    # 첫 화면에서 전체 목록을 자동으로 불러오지 않아 대량 데이터에서도 느려지지 않는다.
    if "q" in request.GET:
        products = Product.objects.all()
        if query:
            products = products.filter(product_name__icontains=query)
    else:
        products = Product.objects.none()

    if sort == "location_code":
        order_fields = ["warehouse", "shelf_number", "column", "level"]
        if order == "desc":
            order_fields = [f"-{field}" for field in order_fields]
        products = products.order_by(*order_fields)
    else:
        sort_field = sort if order == "asc" else f"-{sort}"
        products = products.order_by(sort_field)

    paginator = Paginator(products, 100)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "products": page_obj.object_list,
        "page_obj": page_obj,
        "query": query,
        "sort": sort,
        "order": order,
        "is_searched": "q" in request.GET,
        "user_grade": user_grade,
    }
    return render(request, "inventory/product_list.html", context)


@login_required
@grade_required(["GRADE2", "GRADE3"])
def add_product(request):
    product_name = request.GET.get("product_name", "")

    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "제품이 성공적으로 등록되었습니다.")
            return redirect("add_product")
    else:
        form = ProductForm(initial={"product_name": product_name})

    return render(request, "inventory/add_product.html", {"form": form, **user_grade_context(request)})


@login_required
@grade_required(["GRADE3"])
@require_POST
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, "제품 위치 데이터가 삭제되었습니다.")

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or reverse("product_list")
    return redirect(next_url)


@login_required
def search_by_location(request):
    query = request.GET.get("q", "").strip().upper()
    products = Product.objects.none()
    parsed_code = None
    search_mode = ""

    if query:
        parsed_code = parse_location_code(query)
        if parsed_code:
            filters = {
                "warehouse__iexact": parsed_code.warehouse,
                "shelf_number__iexact": parsed_code.shelf_number,
            }
            if parsed_code.column:
                filters["column__iexact"] = parsed_code.column
            if parsed_code.level:
                filters["level__iexact"] = parsed_code.level

            products = Product.objects.filter(**filters).order_by("warehouse", "shelf_number", "column", "level", "product_name")
            search_mode = "정확 위치" if parsed_code.is_exact else "선반 전체"
        else:
            products = Product.objects.filter(product_name__icontains=query).order_by("product_name")
            search_mode = "제품명"

    return render(request, "inventory/search_by_location.html", {
        "products": products,
        "query": query,
        "parsed_code": parsed_code,
        "search_mode": search_mode,
        **user_grade_context(request),
    })


@login_required
@grade_required(["GRADE3"])
def upload_csv(request):
    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES["file"]

            try:
                decoded_file = csv_file.read().decode("utf-8-sig")
            except UnicodeDecodeError:
                messages.error(request, "CSV 파일 인코딩을 읽을 수 없습니다. UTF-8 형식으로 저장한 뒤 다시 업로드하세요.")
                return render(request, "inventory/upload_csv.html", {"form": form, **user_grade_context(request)})

            reader = csv.reader(io.StringIO(decoded_file))
            rows = list(reader)

            if not rows:
                messages.error(request, "CSV 파일이 비어 있습니다.")
                return render(request, "inventory/upload_csv.html", {"form": form, **user_grade_context(request)})

            header = [cell.strip() for cell in rows[0]]
            expected_header = ["product_name", "warehouse", "shelf_number", "column", "level"]

            if header != expected_header:
                messages.error(request, "CSV 헤더가 올바르지 않습니다. product_name, warehouse, shelf_number, column, level 순서여야 합니다.")
                return render(request, "inventory/upload_csv.html", {"form": form, **user_grade_context(request)})

            created_count = 0
            skipped_count = 0
            errors = []

            for line_no, row in enumerate(rows[1:], start=2):
                if not row or all(not str(cell).strip() for cell in row):
                    skipped_count += 1
                    continue

                if len(row) != 5:
                    errors.append(f"{line_no}행: 컬럼 수가 5개가 아닙니다.")
                    continue

                product_name, warehouse, shelf_number, column, level = [str(cell).strip() for cell in row]

                if not all([product_name, warehouse, shelf_number, column, level]):
                    errors.append(f"{line_no}행: 빈 값이 있습니다.")
                    continue

                Product.objects.create(
                    product_name=product_name.upper(),
                    warehouse=warehouse.upper(),
                    shelf_number=shelf_number.upper().zfill(2),
                    column=column.upper(),
                    level=level.upper(),
                )
                created_count += 1

            if errors:
                for error in errors[:10]:
                    messages.error(request, error)
                if len(errors) > 10:
                    messages.error(request, f"그 외 오류 {len(errors) - 10}건이 더 있습니다.")

            messages.success(request, f"CSV 업로드 완료: 등록 {created_count}건, 빈 행 제외 {skipped_count}건")
            return redirect("product_list")
    else:
        form = CSVUploadForm()
    return render(request, "inventory/upload_csv.html", {"form": form, **user_grade_context(request)})


@login_required
@grade_required(["GRADE2", "GRADE3"])
def download_csv(request):
    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = 'attachment; filename="products.csv"'

    response.write("\ufeff")
    writer = csv.writer(response)
    writer.writerow(["product_name", "warehouse", "shelf_number", "column", "level"])

    for product in Product.objects.all().order_by("warehouse", "shelf_number", "column", "level", "product_name"):
        writer.writerow([
            product.product_name,
            product.warehouse,
            product.shelf_number,
            product.column,
            product.level,
        ])

    return response


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user, defaults={"grade": "GRADE1"})
            login(request, user)
            return redirect("product_list")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
@grade_required(["GRADE3"])
def user_list(request):
    users_without_profile = User.objects.filter(profile__isnull=True)
    for user in users_without_profile:
        Profile.objects.get_or_create(user=user, defaults={"grade": "GRADE1"})

    users = Profile.objects.select_related("user").order_by("user__username")
    return render(request, "inventory/user_list.html", {"users": users, **user_grade_context(request)})


@login_required
@grade_required(["GRADE3"])
def update_grade(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    if request.method == "POST":
        form = GradeUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "사용자 등급이 변경되었습니다.")
            return redirect("user_list")
    else:
        form = GradeUpdateForm(instance=profile)
    return render(request, "inventory/update_grade.html", {"form": form, "profile": profile, **user_grade_context(request)})
