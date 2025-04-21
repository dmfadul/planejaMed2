# class AbstractShift(models.Model):
#     """Class will be inherited by shift and BaseShift."""
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     time_start = models.TimeField()
#     time_end = models.TimeField()

#     class Meta:
#         abstract = True


# class TemplateShift(AbstractShift):
#     center = models.ForeignKey('Center', on_delete=models.CASCADE, related_name='base_shifts')
#     weekday = models.IntegerField()
#     index = models.IntegerField()


# class Shift(AbstractShift):
#     center = models.ForeignKey('Center', on_delete=models.CASCADE, related_name='shifts')
#     month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='shifts')
#     day = models.IntegerField()