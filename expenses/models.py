from django.db import models

class Expense(models.Model):
    user_id = models.CharField(max_length=255)
    date = models.DateField()
    amount = models.FloatField()
    category = models.CharField(max_length=100)
    description = models.TextField()
    raw_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.amount}"


class Receipt(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    file_url = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
