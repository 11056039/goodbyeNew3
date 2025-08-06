from django.db import models
from goodBuy_shop.models import Product
from goodBuy_web.models import User
from django.db.models import Sum

# -------------------------
# 購物車
# -------------------------
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    update = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_user_cart')
        ]

    def add_or_update_product(self, product, quantity):
        if product.stock < 1:
            raise ValueError('此商品已售完，無法加入購物車')

        try:
            obj = Cart.objects.get(user=self.user, product=product)
            obj.quantity = min(obj.quantity + quantity, product.stock)
        except Cart.DoesNotExist:
            obj = Cart(user=self.user, product=product, quantity=min(quantity, product.stock))

        obj.save()
        return obj
    
    def get_quantity(self, product):
        try:
            obj = Cart.objects.get(user=self.user, product=product)
            return obj.quantity
        except Cart.DoesNotExist:
            return 0

    def __str__(self):
        return f'{self.product} * {self.quantity}'
