from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.shortcuts import get_object_or_404, render
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from catalogue.categories import Category
from catalogue.product_details import Brand
from catalogue.product_attritubes import Attribute, Characteristics, ProductCharacteristics, CharacteristicsValue
from catalogue.models import Product, ProductPhotos, ProductClass

from site_settings.models import Banner
from .mixins import ListViewMixin
from .tools import category_and_brands_filter_data
from cart.forms import ProductCartForm
from cart.tools import check_or_create_cart
from cart.models import CartItem
from newsletter.models import NewsLetter
from contact.forms import ContactFrontEndForm
from .forms import AskForm
import datetime
import csv
import urllib.request
import pandas as pd
from django.core.files import File


def test_csv(request):
    path = 'C:/Users/Monastiraki/Desktop/optika_kotsalis-master/data.xlsx'
    print(path)
    data = pd.read_excel(path)
    print('data', data.head())
    for index, row in data.iterrows():
        product_class = ProductClass.objects.get(id=1) 
        print(row['main-image'])
        data_image = row['main-image']
        product, created = Product.objects.get_or_create(title=row['title'], product_class=product_class)
        if data_image.startswith('http'):
            content = urllib.request.urlretrieve(data_image)
            image = ProductPhotos.objects.create(image=File(open(content[0])), product=product, is_primary=True)
    return HttpResponseRedirect('/')


class HomepageView(TemplateView):
    template_name = 'frontend/index.html'
    
    def get_context_data(self, **kwargs):
        context = super(HomepageView, self).get_context_data(**kwargs)
        page_title = 'Αρχική Σελίδα'
        banners = Banner.browser.active()
        big_banners, small_banners = [banners.filter(category='a'), banners.filter(category='c')[:4]]
        featured_products = Product.my_query.featured_products()[:8]
        only_info_products = Product.my_query.only_info_products()
        new_products = Product.objects.all()[:10]
        offers = Product.my_query.products_with_offer()[:4]
        brands = Brand.objects.filter(active=True)
        context.update(locals())
        return context


class NewProductsListView(ListViewMixin, ListView):
    template_name = 'frontend/list_view.html'
    model = Product

    def get_queryset(self):
        self.initial_queryset = Product.my_query.active_for_site().filter(
            timestamp__gt=datetime.datetime.today() - datetime.timedelta(days=60)
        )
        qs = Product.filters_data(self.request, self.initial_queryset)
        if self.request.GET.getlist('attr_name', None):
            qs = Attribute.product_filter_data(self.request, qs)
        if self.request.GET.getlist('char_name', None):
            try:
                ids = ProductCharacteristics.filters_data(self.request,
                                                          ProductCharacteristics.objects.all()).values_list(
                    'product_related__id')
                qs = qs.filter(id__in=ids)
            except:
                qs = qs
        return qs

    def get_context_data(self, **kwargs):
        context = super(NewProductsListView, self).get_context_data(**kwargs)
        page_title, description = ['Νεα Προϊοντα',
                                   'Ανακαλύψτε την τελευταία λέξη της μόδας στα γυαλιά οράσεως και ηλίου, στα Οπτικά Κότσαλης.']
        
        new_products = True
        characteristics = Characteristics.objects.filter(is_filter=True)
        product_characteristics = ProductCharacteristics.objects.filter(product_related__in=self.object_list, title__in=characteristics).distinct()
        context.update(locals())
        return context


class OfferView(ListViewMixin, ListView):
    model = Product
    template_name = 'frontend/list_view.html'

    def get_queryset(self):
        self.initial_queryset = Product.my_query.products_with_offer()
        qs = Product.filters_data(self.request, self.initial_queryset)
        if self.request.GET.get('attr_name', None):
            qs = Attribute.product_filter_data(self.request, qs)
        if self.request.GET.getlist('char_name', None):
            try:
                ids = ProductCharacteristics.filters_data(self.request,
                                                          ProductCharacteristics.objects.all()).values_list(
                    'product_related__id')
                qs = qs.filter(id__in=ids)
            except:
                qs = qs
        return qs

    def get_context_data(self, **kwargs):
        context = super(OfferView, self).get_context_data(**kwargs)
        page_title, description = ['Προσφορές',
                                   'Καλώς ήρθατε στο κατάστημά μας, optika kotsalis.'
                                   'Εδώ θα βρείτε όλες μας τις προσφορές στα γυαία ηλίου και οράσεως']
        offer = True
        greek_url, eng_url = reverse('offer_view'), reverse('eng:offer_view')
        context.update(locals())
        return context


class CategoryView(ListViewMixin, ListView):
    template_name = 'frontend/list_view.html'
    model = Product

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        qs = Product.my_query.active_for_site().filter(category_site=self.category)
        self.initial_queryset = qs

        qs = self.initial_queryset
        qs = Product.filters_data(self.request, qs)
        if self.request.GET.getlist('char_name', None):
            try:
                ids = ProductCharacteristics.filters_data(self.request,
                                                          ProductCharacteristics.objects.all()).values_list(
                    'product_related__id')
                qs = qs.filter(id__in=ids)
            except:
                qs = qs
        return qs

    def get_context_data(self, **kwargs):
        context = super(CategoryView, self).get_context_data(**kwargs)
        page_title, description = f'{self.category.name}', f'Καλώς ήρθατε στο κατάστημά μας, optika kotsalis. Όλα τα προϊόντα της κατηγορίας {self.category.name} είναι εδώ.'
        categories, brands = category_and_brands_filter_data(self.initial_queryset, cate_id=self.category.id)
        low, max = 0, self.queryset.order_by('final_value')[0].final_value if self.queryset else 200

        context.update(locals())
        return context


class SearchView(ListViewMixin, ListView):
    model = Product
    template_name = 'frontend/list_view.html'

    def get_queryset(self):
        qs = Product.my_query.active_for_site()
        qs = Product.filters_data(self.request, qs)
        self.initial_queryset = qs
        if self.request.GET.getlist('char_name', None):
            try:
                ids = ProductCharacteristics.filters_data(self.request,
                                                          ProductCharacteristics.objects.all()).values_list(
                    'product_related__id')
                qs = qs.filter(id__in=ids)
            except:
                qs = qs
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_name = self.request.GET.get('search_name', None)
        page_title = 'Απότελέσμα της αναζήτησης %s' % search_name
        greek_url, eng_url = reverse('search_page'), reverse('eng:search_page')
        context.update(locals())
        return context


class BrandListView(ListView):
    template_name = 'frontend/brand_view.html'
    model = Brand
    queryset = Brand.objects.filter(active=True)

    def get_context_data(self, **kwargs):
        context = super(BrandListView, self).get_context_data(**kwargs)
        seo_title = 'Σελίδα Brands'
        greek_url, eng_url = reverse('brands_view'), reverse('eng:brands_view')
        context.update(locals())
        return context


class BrandDetailView(ListViewMixin, ListView):
    template_name = 'frontend/list_view.html'
    model = Product

    def get_queryset(self):
        brand = self.brand = get_object_or_404(Brand, slug=self.kwargs['slug'])
        qs = Product.my_query.active_for_site().filter(brand=brand)
        self.initial_queryset = qs
        qs = Product.filters_data(self.request, qs)
        if self.request.GET.getlist('char_name', None):
            try:
                ids = ProductCharacteristics.filters_data(self.request,
                                                          ProductCharacteristics.objects.all()).values_list(
                    'product_related__id')
                qs = qs.filter(id__in=ids)
            except:
                qs = qs
        return qs

    def get_context_data(self, **kwargs):
        context = super(BrandDetailView, self).get_context_data(**kwargs)
        seo_title = f'{self.brand.title}'
        page_title, description = f'{self.brand}', f'Καλώς ήρθατε στο κατάστημά μας, optika kotsalis. Όλα τα προϊόντα του brand {self.brand.title} είναι εδώ.'
        greek_url, eng_url = self.brand.get_absolute_url(), self.brand.get_absolute_eng_url()
        context.update(locals())
        return context


class ProductView(DetailView, FormView):
    template_name = 'frontend/product_view.html'
    model = Product
    form_class = ProductCartForm
    queryset = Product.my_query.active_for_site()

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        attributes = None
        if product.have_attr:
            attributes = Attribute.my_query.product_attributes_with_qty(product)
        contact_form = ContactFrontEndForm()
        categories_p = self.object.category_site.all()
        same_cate_products = Product.my_query.active_for_site().filter(category_site__in=categories_p).exclude(id=self.object.id)[:4]
        related_products = Product.my_query.active_for_site().filter(related_products=product)[:8]
        different_color_products = Product.my_query.active_for_site().filter(different_color_products=product)
        ask_form = AskForm()
        context.update(locals())
        return context

    def form_valid(self, form):
        product = get_object_or_404(Product, slug=self.kwargs['slug'])
        qty = form.cleaned_data.get('qty', 1)
        attribute_id = self.request.POST.get('attribute', None)
        cart = check_or_create_cart(self.request)
        result, message = CartItem.create_cart_item(cart, product, qty, attribute_id)
        messages.success(self.request, message)
        return super(ProductView, self).form_valid(form)

    def form_invalid(self, form):
        return super(ProductView, self).form_invalid(form)


def newsletter_form_view(request):
    email = request.POST.get('newsletter_email', None)
    if email:
        new_newsletter, created = NewsLetter.objects.get_or_create(email=email)
        if created:
            new_newsletter.confirm = True
            new_newsletter.save()
            messages.success(request, f'Το email σας, {email}  , καταχωρήθηκε. Ευχαριστούμε!')
        else:
            messages.warning(request, 'Το email σας έχει ήδη  καταχωρηθεί')
    else:
        messages.warning(request, 'Κάτι πήγε λάθος με την διαδικασία. '
                                  'Δοκιμάστε ξανά ή επικοινωνίστε με τους διαχειριστές.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def demo_only_view_restart_session(request):
    del request.session['cart_id']
    return HttpResponseRedirect('/')


def error_404(request, exception):
    data = {}
    return render(request, 'frontend/extra/404.html', data)
