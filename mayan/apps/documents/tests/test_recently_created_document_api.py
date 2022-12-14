from rest_framework import status

from mayan.apps.rest_api.tests.base import BaseAPITestCase

from ..models.document_models import RecentlyCreatedDocument
from ..permissions import permission_document_view

from .mixins.document_mixins import DocumentTestMixin
from .mixins.recently_created_document_mixins import (
    RecentlyCreatedDocumentAPIViewTestMixin
)


class RecentlyCreatedDocumentAPIViewTestCase(
    DocumentTestMixin, RecentlyCreatedDocumentAPIViewTestMixin,
    BaseAPITestCase
):
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()
        self._create_test_document_stub()

    def test_recently_created_document_api_list_view_no_permission(self):
        recently_created_document_count = RecentlyCreatedDocument.valid.count()

        self._clear_events()

        response = self._request_recently_created_document_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['count'], recently_created_document_count - 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_recently_created_document_api_list_view_with_access(self):
        recently_created_document_count = RecentlyCreatedDocument.valid.count()

        self.grant_access(
            obj=self._test_document, permission=permission_document_view
        )

        self._clear_events()

        response = self._request_recently_created_document_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['count'], recently_created_document_count
        )
        self.assertEqual(
            response.data['results'][0]['id'], self._test_document.pk
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_trashed_document_recently_created_document_api_list_view_with_access(self):
        recently_created_document_count = RecentlyCreatedDocument.valid.count()

        self.grant_access(
            obj=self._test_document, permission=permission_document_view
        )

        self._test_document.delete()

        self._clear_events()

        response = self._request_recently_created_document_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['count'], recently_created_document_count - 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)
