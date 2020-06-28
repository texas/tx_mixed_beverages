from __future__ import unicode_literals

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.gis.geos import Point

from ..factories import CorrectionFactory
from ..models import Correction
from ..views import FixDetail, CorrectionDetail
from mixed_beverages.apps.receipts.factories import LocationFactory
from mixed_beverages.apps.receipts.models import Location


class FixDetailTests(TestCase):
    def setUp(self):
        super(FixDetailTests, self).setUp()
        self.view = FixDetail()
        self.factory = RequestFactory()

    def test_post_works_with_anonymous(self):
        original_location = Point(12, 34)
        location = LocationFactory(coordinate=original_location)
        self.view.kwargs = {"pk": location.pk}
        request = self.factory.post("/foo/", {"lat": "1", "lng": "2",})
        request.user = AnonymousUser()

        response = self.view.post(request)
        # assert redirects to a thanks page
        self.assertEqual(response.status_code, 302)
        self.assertIn("thanks", response["Location"])

        correction = Correction.objects.all().get()
        # assert correction is in review
        self.assertEqual(correction.status, "submitted")
        # assert location did not change
        location = Location.objects.get(pk=location.pk)
        self.assertEqual(location.coordinate, original_location)


class CorrectionDetailTests(TestCase):
    def setUp(self):
        super(CorrectionDetailTests, self).setUp()
        self.view = CorrectionDetail()
        self.factory = RequestFactory()

    def test_post_by_anon_is_rejected(self):
        correction = CorrectionFactory(status="submitted",)
        self.view.kwargs = {"pk": correction.pk}
        request = self.factory.post("/foo/")
        request.user = AnonymousUser()

        response = self.view.post(request)
        self.assertEqual(response.status_code, 403)
        correction = Correction.objects.get(pk=correction.pk)
        self.assertEqual(correction.status, "submitted")

    def test_post_by_user_is_rejected(self):
        correction = CorrectionFactory(status="submitted",)
        self.view.kwargs = {"pk": correction.pk}
        request = self.factory.post("/foo/")
        user = User.objects.create_user(username="poop", email="poop@example.com")
        request.user = user

        response = self.view.post(request)
        self.assertEqual(response.status_code, 403)
        correction = Correction.objects.get(pk=correction.pk)
        self.assertEqual(correction.status, "submitted")

    def test_post_by_staff_saves(self):
        correction = CorrectionFactory(status="submitted",)
        self.view.kwargs = {"pk": correction.pk}
        request = self.factory.post("/foo/")
        user = User.objects.create_superuser(
            username="poop", email="poop@example.com", password="doop"
        )
        request.user = user
        self.view.request = request  # to support the .get() method

        response = self.view.post(request)
        self.assertEqual(response.status_code, 200)
        correction = Correction.objects.get(pk=correction.pk)
        self.assertEqual(correction.status, "approved")
