from django.test import TestCase

from ..factories import CorrectionFactory
from ..models import Correction


class CorrectionTests(TestCase):
    CorrectionFactory()
