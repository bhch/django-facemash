from django.conf.urls import patterns, include, url
from facemash.views import ratings_calculator, play, ratings_page

urlpatterns = patterns('',
    url(r'^$', play, name="play"),
    url(r'^calcultor/(?P<winner_id>\d+)-(?P<loser_id>\d+)/$', ratings_calculator, name="calculator"),
    url(r'^ratings/$', ratings_page, name="ratings"),
)
