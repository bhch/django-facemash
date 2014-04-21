from django.db import models


class FaceMash(models.Model):
    """
    Model for facemash.
    The default values for ratings, rd (rating deviation) and
    sigma (volatility) are set as per suggested by the author
    of GLicko-2 algorithm.
    """

    name = models.CharField(max_length=10)
    photo = models.ImageField(upload_to="facemash_photos")
    ratings = models.FloatField(default=1500)
    # rd = rating deviation
    rd = models.FloatField(default=350)
    # sigma is used as the expression for volatility
    sigma = models.FloatField(default=0.06)

    class Meta:
        verbose_name_plural = 'Facemash'

    def __unicode__(self):
        return self.name
