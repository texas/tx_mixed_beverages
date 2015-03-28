#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import django

from mixed_beverages.apps.receipts.utils import slurp

django.setup()
slurp(sys.argv[1])
