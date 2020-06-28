#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import django

django.setup()

from mixed_beverages.apps.receipts.utils import slurp

slurp(sys.argv[1])
