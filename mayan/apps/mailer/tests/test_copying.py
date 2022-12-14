from mayan.apps.common.tests.mixins import ObjectCopyTestMixin
from mayan.apps.testing.tests.base import BaseTestCase

from .mixins import MailerTestMixin


class MailerCopyTestCase(MailerTestMixin, ObjectCopyTestMixin, BaseTestCase):
    def setUp(self):
        super().setUp()
        self._create_test_user_mailer()
        self._test_object = self._test_user_mailer
