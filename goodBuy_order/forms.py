from django import forms
from .models import Order
from goodBuy_web.models import UserAddress
from goodBuy_order.models import OrderPayment, Order, Comment

from django import forms
from goodBuy_shop.models import ShopPayment

# -------------------------
# 地址、付款方式選擇
# -------------------------
PAYMENT_KIND_BANK = 'bank'
PAYMENT_KIND_COD  = 'cod'  

class ChoosePaymentForm(forms.Form):
    payment_method = forms.ChoiceField(
        choices=[(PAYMENT_KIND_COD, '取貨付款'), (PAYMENT_KIND_BANK, '銀行匯款')],
        widget=forms.RadioSelect
    )
    payment_account = forms.ModelChoiceField(
        queryset=ShopPayment.objects.none(),  # 預設空 QuerySet
        required=False,
        empty_label=None,
        widget=forms.RadioSelect
    )

    def __init__(self, *args, shop=None, remittance_qs=None, **kwargs):
        """
        shop: 當前訂單所屬商店（目前僅做語意保留）
        remittance_qs: 該商店的「銀行匯款」ShopPayment 查詢集
        """
        super().__init__(*args, **kwargs)
        self.shop = shop
        self.remittance_qs = remittance_qs if remittance_qs is not None else ShopPayment.objects.none()
        self.fields['payment_account'].queryset = self.remittance_qs

    def clean(self):
        cleaned = super().clean()
        method = cleaned.get('payment_method')
        account = cleaned.get('payment_account')

        if method == PAYMENT_KIND_BANK:
            if not self.remittance_qs.exists():
                raise forms.ValidationError('此商店未設定銀行匯款帳戶')
            if not account:
                self.add_error('payment_account', '請選擇匯款帳戶')
            elif not self.remittance_qs.filter(pk=account.pk).exists():
                self.add_error('payment_account', '匯款帳戶無效')

        return cleaned
    
# -------------------------
# 上傳付款憑證
# -------------------------
class OrderPaymentForm(forms.ModelForm):
    class Meta:
        model = OrderPayment
        fields = ['amount', 'pay_proof', 'remark']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '請輸入匯款金額',
                'min': 1
            }),
            'pay_proof': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'remark': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '其他備註（可選）'
            }),
        }
        labels = {
            'amount': '匯款金額',
            'pay_proof': '匯款憑證上傳',
            'remark': '備註',
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError('金額必須大於 0')
        return amount

# -------------------------
# 二次補款金額設定
# -------------------------
class SecondSupplementForm(forms.Form):
    second_supplement = forms.IntegerField(
        required=True,
        min_value=0,
        label='補款金額',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '請輸入金額（元）'})
    )
# -------------------------
# 評論表單
# -------------------------
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['rank', 'comment']
        widgets = {
            # 'rank': forms.HiddenInput(), 改點星星
            'rank': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': '請留下您的評價'}),
        }
        labels = {
            'rank': '評分（1~5）',
            'comment': '評論內容'
        }
