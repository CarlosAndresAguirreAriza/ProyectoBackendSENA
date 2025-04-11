from apps.dashboard.domain.entities import CuttingTechnique
from apps.utils import StaticInfoErrorMessages
from apps.exceptions import ResourceNotFoundAPIError
from rest_framework import status
from django.test import Client
from django.urls import reverse
import pytest


# Error messages
CUT_NOT_FOUND = StaticInfoErrorMessages.CUT_NOT_FOUND.value


@pytest.mark.django_db
class TestGetCutAPIView:
    """
    This class encapsulates the tests for the view responsible for getting the
    cutting techniques data.
    """

    path_name = "get_create_cut"

    def test_if_get_all_cuts(self, client: Client, load_static_info) -> None:
        """
        This test is responsible for validating the expected behavior of the
        view responsible for getting all cutting techniques.
        """

        # Simulating the request
        path = reverse(viewname=self.path_name)
        response = client.get(path=path, content_type="application/json")

        # Asserting that response data is correct
        assert response.status_code == status.HTTP_200_OK

        for cut in response.data:
            assert "base_info" in cut
            assert "descriptions" in cut
            assert "images" in cut

    def test_if_not_found_cut(self, client: Client, load_static_info) -> None:
        """
        This test is responsible for validating the expected behavior of the
        view responsible for changing the status of a cutting technique in
        the database when the cutting technique is not found.
        """

        # Prepare the appropriate scenario in the database
        all_cuts = CuttingTechnique.objects.all()

        for cut in all_cuts:
            cut.delete()

        # Simulating the request
        path = reverse(viewname=self.path_name)
        response = client.get(path=path, content_type="application/json")

        # Asserting that response data is correct
        assert response.status_code == ResourceNotFoundAPIError.status_code
        assert response.data["code"] == CUT_NOT_FOUND["code"]
        assert response.data["detail"] == CUT_NOT_FOUND["detail"]
