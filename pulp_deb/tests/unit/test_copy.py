from uuid import UUID

import pytest

from pulp_deb.app.models import (
    AptRepository,
    Package,
    PackageReleaseComponent,
    ReleaseComponent,
)
from pulp_deb.app.tasks.copy import find_structured_publish_content


@pytest.mark.django_db
def test_structured_copy_handles_query_exceeding_psycopg_parameter_limit():
    repository = AptRepository.objects.create(name="oversized-copy-source")

    package = Package.objects.create(
        package="test-package",
        version="1.0",
        architecture="amd64",
        relative_path="pool/t/test-package/test-package_1.0_amd64.deb",
        sha256="a" * 64,
    )
    release_component = ReleaseComponent.objects.create(
        distribution="stable",
        component="main",
    )
    package_release_component = PackageReleaseComponent.objects.create(
        package=package,
        release_component=release_component,
    )

    with repository.new_version() as source_version:
        source_version.add_content(Package.objects.filter(pk=package.pk))
        source_version.add_content(
            PackageReleaseComponent.objects.filter(pk=package_release_component.pk)
        )
        source_version.add_content(ReleaseComponent.objects.filter(pk=release_component.pk))

    # Reproduce content selection large enhough to exceet postgres limits
    # when evaluating through a server side cursor.
    content_pks = [UUID(int=value) for value in range(1, 65_537)]
    content_pks.append(package.pk)
    content = source_version.content.filter(pk__in=content_pks)

    result = find_structured_publish_content(content, source_version)
    assert result.filter(pk=package.pk).exists()
    assert result.filter(pk=package_release_component.pk).exists()
    assert result.filter(pk=release_component.pk).exists()
