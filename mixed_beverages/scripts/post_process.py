#!/usr/bin/env python
# -*- coding: utf-8 -*-
import django

from mixed_beverages.apps.receipts.utils import post_process

django.setup()
post_process()
