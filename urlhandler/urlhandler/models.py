#-*- coding: UTF-8 -*-
from django.db import models
import uuid


class User(models.Model):
    weixin_id = models.CharField(max_length=255)
    stu_id = models.CharField(max_length=255)
    status = models.IntegerField()
    seed = models.FloatField(default=1024)

class Activity(models.Model):
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    place = models.CharField(max_length=255)
    book_start = models.DateTimeField()
    book_end = models.DateTimeField()
    seat_status = models.IntegerField(default=0)
    total_tickets = models.IntegerField()
    status = models.IntegerField()
    pic_url = models.CharField(max_length=255)
    remain_tickets = models.IntegerField()
    menu_url = models.CharField(max_length=255, null=True)
    # Something about status:
    # -1: deleted
    # 0: saved but not published
    # 1: published
    # Something about seat_status:
    # 0: no seat
    # 1: seat B and seat C

class Ticket(models.Model):
    stu_id = models.CharField(max_length=255)
    unique_id = models.CharField(max_length=255)
    activity = models.ForeignKey(Activity)
    status = models.IntegerField()
    seat = models.CharField(max_length=255)
    # Something about isUsed
    # 0: ticket order is cancelled
    # 1: ticket order is valid
    # 2: ticket is used


class Vote(models.Model):
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    description = models.TextField()
    pic_url = models.CharField(max_length=255)
    max_num = models.IntegerField(default=1)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.IntegerField(default=0)
    # -1: deleted
    # 0: saved but not publihsed
    # 1: published
    display = models.IntegerField(default=0)
    # 0: do not present to users
    # 1: present to uesrs
    layout_style = models.IntegerField(default=0)
    has_images = models.IntegerField(default=1)
    background = models.CharField(max_length=255)
    vote_type = models.IntegerField(default=0)
    # 0:  only once
    # 1:  every day can vote once

class VoteItem(models.Model):
    name = models.CharField(max_length=255)
    pic_url = models.CharField(max_length=255)
    description = models.TextField()
    description_simply = models.CharField(max_length=255)
    vote = models.ForeignKey(Vote)
    vote_key = models.CharField(max_length=255)
    vote_num = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    # -1: deleted
    # 0: saved but not published
    # 1: published

class SingleVote(models.Model):
    item_id = models.CharField(max_length=255)
    stu_id = models.CharField(max_length=255)
    time = models.DateTimeField()
    status = models.IntegerField(default=0)
    # 0: Cancelled
    # 1: Valid

