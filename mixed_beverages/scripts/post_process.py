#!/usr/bin/env python
# -*- coding: utf-8 -*-
import django

django.setup()

from mixed_beverages.apps.receipts.utils import post_process

post_process()
