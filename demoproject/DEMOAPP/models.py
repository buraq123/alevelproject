from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.db import models
from django.db import connection
from datetime import date
import datetime
from django.db.models import Sum


class Product(models.Model):
    Name = models.CharField(max_length=100)
    unit = models.CharField(max_length=100)
    consrate = models.PositiveIntegerField()
    delivery = models.PositiveIntegerField()

    class Meta:
        db_table = "product"

    @classmethod
    def ProductValidation(cls, Name):
        list = Product.objects.filter(Name=Name)
        if len(list) > 0:
            return False
        else:
            return True

    @classmethod
    def notificationlist(cls):
        sql = """
        select product.id,product."Name" as name,
        (max(invoice.date) + product.delivery) - CURRENT_DATE nextdelivery, 
        ((max(invoice.date) + product.delivery) - CURRENT_DATE) * product.consrate orderamount,
        sum(stock.amount) /product.consrate getbydate
        from invoice
        JOIN product ON product.id = invoice.productId
        JOIN stock  ON product.id = stock.productid
        group by product.id,product."Name"
        having (max(invoice.date) + product.delivery) - CURRENT_DATE -
        sum(stock.amount) /product.consrate > 0 """
        return NotificationListView.objects.raw(sql)

    @classmethod
    def productlist(cls):
        return Product.objects.raw('SELECT id,"Name",unit,consrate,delivery FROM product')

    @classmethod
    def getUnits(cls):
        units = ["kg", "L", "pc"]
        return units


class Invoice(models.Model):
    productid = models.BigIntegerField()
    amount = models.PositiveIntegerField()
    priceperUnit = models.PositiveIntegerField()
    totalprice = models.PositiveIntegerField(editable=False)
    date = models.DateField(auto_now=True)
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = "invoice"

    @classmethod
    def invoicelist(cls):
        return Invoice.objects.raw('''
        SELECT invoice.id,"productid",product."Name",
        amount,"priceperUnit",totalprice,date,concat(auth_user.first_name,' ',auth_user.last_name) as username
        FROM invoice 
        INNER JOIN product ON invoice."productid"= product.id
        LEFT JOIN auth_user ON invoice."user_id"= auth_user.id
        ''')

    def save(self, *args, **kwargs):
        self.totalprice = self.amount * self.priceperUnit
        super(Invoice, self).save(*args, **kwargs)
        stock = Stock.create(self.productid, self.amount, self.date, self.id)
        stock.stockin()

    def delete(self, *args, **kwargs):
        stock = Stock.objects.filter(invoiceid=self.id).first()
        Stock.validateAmount(stock.productid, self.amount)
        stock.delete()
        super(Invoice, self).delete(*args, **kwargs)

class Stock(models.Model):
    productid = models.BigIntegerField()
    amount = models.IntegerField()
    date = models.DateField(auto_now=True)
    invoiceid = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = "stock"

    @classmethod
    def create(cls, productid, amount, date, invoiceid):
        stock = cls(productid=productid, amount=amount, date=date, invoiceid=invoiceid)
        return stock

    def stockin(self):
        super(Stock, self).save()

    @classmethod
    def stockOutByOne(cls, productid):
        stock = Stock.create(productid=productid, date=date, amount=-1, invoiceid=None)
        stock.stockin()

    @classmethod
    def getProductAmount(cls, productid):
        return Stock.objects.filter(productid=productid).aggregate(amount=Sum('amount'))['amount']

    @classmethod
    def validateAmount(cls, productid, outAmount):
        currentAmount = Stock.getProductAmount(productid)
        if outAmount > currentAmount:
            raise Exception("StockInsufficient")

    def stockout(self, args, kwargs):
        Stock.validateAmount(self.productid, self.amount)
        self.amount = -1 * self.amount
        super(Stock, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.stockout(args, kwargs)

    @classmethod
    def quickstockout(cls):
        return Stock.objects.raw('''SELECT "productid" as id,SUM(amount) amount,product."Name" AS name 
                                    FROM stock 
                                    INNER JOIN product ON stock."productid"=product.id
                                    GROUP BY "productid",product."Name"
                                    HAVING SUM(amount) > 0''')

    @classmethod
    def getsum(cls):
        return Stock.objects.raw('SELECT "productid" as id,SUM(amount) AS amount FROM stock GROUP BY "productid" ')

    @classmethod
    def mostsold(cls):
        tuple2 = Stock.objects.raw('''SELECT "productid" as id,SUM(amount) amount,product."Name" AS name 
    FROM stock 
    INNER JOIN product ON stock."productid"=product.id
    WHERE amount<0 and "date"<=current_date and "date">=current_date-30
    GROUP BY "productid",product."Name"
    ORDER BY amount DESC''')
        mostsoldproduct = tuple2[0]
        return mostsoldproduct

    @classmethod
    def leastsold(cls):
        tuple2 = Stock.objects.raw('''SELECT "productid" as id,SUM(amount) amount,product."Name" AS name 
    FROM stock 
    INNER JOIN product ON stock."productid"=product.id
    WHERE amount<0 and "date"<=current_date and "date">=current_date-30
    GROUP BY "productid",product."Name"
    ORDER BY amount DESC''')
        leastsoldproduct = tuple2[len(tuple2) - 1]
        return leastsoldproduct

    @classmethod
    def StocklistNative(cls):
        return Stock.objects.raw(
            '''SELECT "productid" as id,SUM(amount) amount,product."Name" AS name 
            FROM stock INNER JOIN product 
            ON stock."productid"=product.id 
            GROUP BY "productid",product."Name"''')


    @classmethod
    def graph(cls):
     return Stock.objects.raw('''SELECT "productid" as id,SUM(amount) amount,product."Name" AS name 
                        FROM stock 
                        INNER JOIN product ON stock."productid"=product.id
                        WHERE amount<0 
                        GROUP BY "productid",product."Name"''')


class NotificationListView(models.Model):
    name = models.CharField(max_length=15)
    orderamount = models.IntegerField()
    getbydate = models.IntegerField()
