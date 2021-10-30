from os import stat
from django.db.models import query
from django.db.models.base import Model
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import Count
from django_filters import filterset
from rest_framework import permissions
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from store.pagination import DefaultPagination
from rest_framework import pagination, request, serializers, status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from store.permissions import IsAdminOrReadOnly
from .filters import ProductFilter
from .models import  Customer, Order, OrderItem, Product, Collection, Review, Cart, CartItem
from .serializers import AddCartItemSerializer, CartItemSerializer, CartSerializer, CreateOrderSerializer, CustomerSerializer, OrderSerializer, ProductSerializer, CollectionSerializer, ReviewSerializer, UpdateCartItemSerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']
    permission_classes = [IsAdminOrReadOnly,]

#    filterset_fields = ['collection_id']


#    def get_queryset(self):
#        queryset = Product.objects.all()
#        collection_id = self.request.query_params.get('collection_id')
#        if collection_id is not None:
#            queryset = queryset.filter(collection_id=collection_id)
#        return queryset


    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count()>0:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(prodcuts_count=Count('products')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly,]

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']).count()>0:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)
    
class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}


class CartViewSet(CreateModelMixin, RetrieveModelMixin, GenericViewSet, DestroyModelMixin):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer

class CartItemViewSet(ModelViewSet):

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PUT':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}
    
    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]
    
#    def get_permissions(self):
#        if self.request.method == 'GET':
#            return [AllowAny()]
#        return [IsAuthenticated()]
    @action(detail=False, methods=['GET','PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        if request.method=='GET':
            customer = Customer.objects.get(user_id=request.user.id)
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method=='PUT':
            customer = Customer.objects.get(user_id=request.user.id)
            serializer = CustomerSerializer(customer, request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        (customer_id, _created) = Customer.objects.only('id').get_or_create(user_id=self.request.user.id)
        return Order.objects.filter(customer_id=customer_id)




# Create your views here.
#@api_view(['GET', 'POST'])
#def product_list(request):
#    if request.method == 'GET':
#        queryset = Product.objects.select_related('collection').all()
#        serializer = ProductSerializer(queryset, many=True)
#        return Response(serializer.data)
#    elif request.method == 'POST':
#        serializer = ProductSerializer(data=request.data)
#        serializer.is_valid(raise_exception=True)
#        serializer.save()
#        return Response(serializer.data, status=status.HTTP_201_CREATED)
        

#@api_view(['GET', 'PUT', 'DELETE'])
#def product_detail(request, id):
#    try:
#        product = Product.objects.get(pk=id)
#    except Product.DoesNotExist:
#        return Response(status=status.HTTP_404_NOT_FOUND)
#
#    if request.method == 'GET':
#            serializer = ProductSerializer(product)
#            return Response(serializer.data)
#    elif request.method == 'PUT':
#        serializer = ProductSerializer(product, data=request.data)
#        serializer.is_valid(raise_exception=True)
#        serializer.save()
#        return Response(serializer.data)
#    elif request.method == 'DELETE':
#        if product.orderitems.count()>0:
#            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
#        product.delete()
#        return Response(status=status.HTTP_204_NO_CONTENT)
#
#@api_view(['GET', 'POST'])
#def collection_list(request):
#    if request.method == 'GET':
#        queryset = Collection.objects.annotate(products_count=Count('products')).all()
#        serializer = CollectionSerializer(queryset, many=True)
#        return Response(serializer.data, status=status.HTTP_200_OK)
#    elif request.method == 'POST':
#        serializer = CollectionSerializer(data=request.data)
#        serializer.is_valid(raise_exception=True)
#        serializer.save()
#        return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#@api_view(['GET', 'PUT', 'DELETE'])
#def collection_detail(request, id):
#    try:
#        collection = Collection.objects.annotate(products_count=Count('products')).get(pk=id)
#    except Collection.DoesNotExist:
#        return Response(status=status.HTTP_404_NOT_FOUND)
#    if request.method == 'GET':
#        serializer = CollectionSerializer(collection)
#        return Response(serializer.data, status=status.HTTP_200_OK)
#    elif request.method == 'PUT':
#        serializer = CollectionSerializer(collection, data=request.data)
#        serializer.is_valid(raise_exception=True)
#        serializer.save()
#        return Response(serializer.data)
#    elif request.method == 'DELETE':
#        if collection.products.count()>0:
#            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
#        collection.delete()
#        return Response(status=status.HTTP_204_NO_CONTENT)
