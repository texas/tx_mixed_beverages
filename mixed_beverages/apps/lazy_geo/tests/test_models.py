from django.contrib.auth.models import AnonymousUser, User
from django.contrib.gis.geos import Point
from django.core.exceptions import SuspiciousOperation
from django.test import TestCase, RequestFactory
from django.test.utils import override_settings

from mixed_beverages.apps.receipts.factories import LocationFactory
from ..factories import CorrectionFactory
from ..models import Correction


class CorrectionManagerTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='poop',
            email='poop@example.com')

    def test_create_from_request_works(self):
        location = LocationFactory(coordinate=Point(12, 34))
        request = self.factory.post('/foo/', {
            'lat': '1', 'lng': '2',
        })
        request.user = self.user

        correction = Correction.objects.create_from_request(location, request)
        self.assertEqual(correction.fro.x, 12)
        self.assertEqual(correction.fro.y, 34)
        self.assertEqual(correction.to.x, 2)
        self.assertEqual(correction.to.y, 1)
        self.assertEqual(correction.submitter, self.user)
        self.assertEqual(correction.status, 'submitted')

    @override_settings(ALLOW_ANONYMOUS_CORRECTIONS=False)
    def test_create_from_request_rejects_anonymous(self):
        location = LocationFactory(coordinate=Point(12, 34))
        request = self.factory.post('/foo/', {
            'lat': '1', 'lng': '2',
        })
        request.user = AnonymousUser()

        with self.assertRaises(SuspiciousOperation):
            Correction.objects.create_from_request(location, request)

    def test_create_from_request_rejects_missing_data(self):
        location = LocationFactory(coordinate=Point(12, 34))

        request = self.factory.post('/foo/', {})
        request.user = self.user
        with self.assertRaises(TypeError):
            Correction.objects.create_from_request(location, request)

        request = self.factory.post('/foo/', {'lat': '1'})
        request.user = self.user
        with self.assertRaises(TypeError):
            Correction.objects.create_from_request(location, request)

        request = self.factory.post('/foo/', {'lng': '2'})
        request.user = self.user
        with self.assertRaises(TypeError):
            Correction.objects.create_from_request(location, request)


class CorrectionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='poop',
            email='poop@example.com')
        self.user2 = User.objects.create_user(username='dood',
            email='dood@example.com')

    def test_approve_works(self):
        correction = CorrectionFactory(submitter=self.user)
        location = correction.obj
        self.assertEqual(correction.status, 'submitted')
        correction.approve(self.user2)
        self.assertEqual(correction.approved_by, self.user2)
        self.assertEqual(location.coordinate_quality, 'me')
        self.assertEqual(location.coordinate, correction.to)
        self.assertEqual(correction.status, 'approved')
        # TODO self.assertEqual(location.approved_at)
