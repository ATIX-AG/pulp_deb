# coding=utf-8
"""Tests that publish deb plugin repositories."""
import unittest
from random import choice

from pulp_smash import config
from pulp_smash.pulp3.utils import gen_repo, get_content, get_versions, modify_repo

from pulp_deb.tests.functional.constants import (
    DEB_GENERIC_CONTENT_NAME,
    DEB_PACKAGE_NAME,
    DEB_FIXTURE_URL,
    DEB_COMPLEX_DISTS_FIXTURE_URL,
)
from pulp_deb.tests.functional.utils import set_up_module as setUpModule  # noqa:F401
from pulp_deb.tests.functional.utils import (
    gen_deb_remote,
    monitor_task,
    deb_apt_publication_api,
    deb_remote_api,
    deb_repository_api,
    deb_verbatim_publication_api,
    signing_service_api,
)

from pulpcore.client.pulp_deb import (
    RepositorySyncURL,
    DebDebPublication,
    DebVerbatimPublication,
)
from pulpcore.client.pulp_deb.exceptions import ApiException


class PublishAnyRepoVersionSimpleTestCase(unittest.TestCase):
    """Test whether a particular repository version can be published simple.

    This test targets the following issues:

    * `Pulp #3324 <https://pulp.plan.io/issues/3324>`_
    * `Pulp Smash #897 <https://github.com/pulp/pulp-smash/issues/897>`_
    """

    class Meta:
        publication_api = deb_apt_publication_api
        Publication = DebDebPublication

    def _publication_extra_args(self):
        return {"simple": True}

    def test_all(self):
        """Test whether a particular repository version can be published.

        1. Create a repository with at least 2 repository versions.
        2. Create a publication by supplying the latest ``repository_version``.
        3. Assert that the publication ``repository_version`` attribute points
           to the latest repository version.
        4. Create a publication by supplying the non-latest ``repository_version``.
        5. Assert that the publication ``repository_version`` attribute points
           to the supplied repository version.
        6. Assert that an exception is raised when providing two different
           repository versions to be published at same time.
        """
        cfg = config.get_config()
        repo_api = deb_repository_api
        remote_api = deb_remote_api
        publication_api = self.Meta.publication_api

        body = gen_deb_remote()
        remote = remote_api.create(body)
        self.addCleanup(remote_api.delete, remote.pulp_href)

        repo_1 = repo_api.create(gen_repo())
        self.addCleanup(repo_api.delete, repo_1.pulp_href)

        repository_sync_data = RepositorySyncURL(remote=remote.pulp_href)
        sync_response = repo_api.sync(repo_1.pulp_href, repository_sync_data)
        monitor_task(sync_response.task)

        
        repo_1 = repo_api.read(repo_1.pulp_href)
        for deb_generic_content in get_content(repo_1.to_dict())[DEB_GENERIC_CONTENT_NAME]:
            modify_repo(cfg, repo_1.to_dict(), add_units=[deb_generic_content])
        for deb_package in get_content(repo_1.to_dict())[DEB_PACKAGE_NAME]:
            modify_repo(cfg, repo_1.to_dict(), add_units=[deb_package])
        package_1 = get_content(repo_1.to_dict())[DEB_PACKAGE_NAME][3]



        repo_api = deb_repository_api
        remote_api = deb_remote_api
        publication_api = self.Meta.publication_api

        body = gen_deb_remote(url=DEB_COMPLEX_DISTS_FIXTURE_URL, distributions="ragnarok-backports")
        remote = remote_api.create(body)
        self.addCleanup(remote_api.delete, remote.pulp_href)

        repo_2 = repo_api.create(gen_repo())
        self.addCleanup(repo_api.delete, repo_2.pulp_href)

        repository_sync_data = RepositorySyncURL(remote=remote.pulp_href)
        sync_response = repo_api.sync(repo_2.pulp_href, repository_sync_data)
        monitor_task(sync_response.task)

        
        repo_2 = repo_api.read(repo_2.pulp_href)
        for deb_generic_content in get_content(repo_2.to_dict())[DEB_GENERIC_CONTENT_NAME]:
            modify_repo(cfg, repo_2.to_dict(), add_units=[deb_generic_content])
        for deb_package in get_content(repo_2.to_dict())[DEB_PACKAGE_NAME]:
            ct = modify_repo(cfg, repo_2.to_dict(), add_units=[deb_package])

        print("ct", ct)
        package_2 = get_content(repo_2.to_dict())[DEB_PACKAGE_NAME][3]


        repo_api = deb_repository_api
        #remote_api = deb_remote_api
        publication_api = self.Meta.publication_api

        #body = gen_deb_remote(url=DEB_COMPLEX_DISTS_FIXTURE_URL, distributions="ragnarok-backports")
        #remote = remote_api.create(body)
        #self.addCleanup(remote_api.delete, remote.pulp_href)

        repo_3 = repo_api.create(gen_repo())
        self.addCleanup(repo_api.delete, repo_3.pulp_href)

        #repository_sync_data = RepositorySyncURL(remote=remote.pulp_href)
        #sync_response = repo_api.sync(repo_2.pulp_href, repository_sync_data)
        #monitor_task(sync_response.task)

        
        repo_3 = repo_api.read(repo_3.pulp_href)
        print(repo_3, cfg)
        for deb_generic_content in get_content(repo_3.to_dict())[DEB_GENERIC_CONTENT_NAME]:
            modify_repo(cfg, repo_3.to_dict(), add_units=[deb_generic_content])
        modify_repo(cfg, repo_3.to_dict(), add_units=[get_content(repo_2.to_dict())[DEB_PACKAGE_NAME][3]])
        pckg = get_content(repo_1.to_dict())[DEB_PACKAGE_NAME][1]
        pckg["relative_path"] = "moved-" + pckg["relative_path"]
        modify_repo(cfg, repo_3.to_dict(), add_units=[pckg])
        publish_data = self.Meta.Publication(
            repository=repo_3.pulp_href, **self._publication_extra_args()
        )
        publish_response = publication_api.create(publish_data)
        created_resources = monitor_task(publish_response.task)
