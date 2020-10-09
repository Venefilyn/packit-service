import pytest
from flexmock import flexmock

from packit.config import PackageConfig, JobConfig, JobType, JobConfigTriggerType
from packit.config.job_config import JobMetadataConfig
from packit_service.service.events import TheJobTriggerType
from packit_service.worker.build.copr_build import CoprBuildJobHelper
from packit_service.worker.build.koji_build import KojiBuildJobHelper

# packit.config.aliases.get_aliases() return value example
ALIASES = {
    "fedora-development": ["fedora-33", "fedora-rawhide"],
    "fedora-stable": ["fedora-31", "fedora-32"],
    "fedora-all": ["fedora-31", "fedora-32", "fedora-33", "fedora-rawhide"],
    "epel-all": ["epel-6", "epel-7", "epel-8"],
}

STABLE_VERSIONS = ALIASES["fedora-stable"]
STABLE_CHROOTS = {f"{version}-x86_64" for version in STABLE_VERSIONS}
ONE_CHROOT_SET = {list(STABLE_CHROOTS)[0]}
STABLE_KOJI_TARGETS = {f"f{version[-2:]}" for version in STABLE_VERSIONS}
ONE_KOJI_TARGET_SET = {list(STABLE_KOJI_TARGETS)[0]}


@pytest.mark.parametrize(
    "jobs,trigger,job_config_trigger_type,build_chroots,test_chroots",
    [
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(targets=STABLE_VERSIONS),
                )
            ],
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            STABLE_CHROOTS,
            set(),
            id="build_with_targets",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(targets=STABLE_VERSIONS),
                )
            ],
            TheJobTriggerType.pr_comment,
            JobConfigTriggerType.pull_request,
            STABLE_CHROOTS,
            set(),
            id="build_with_targets&pr_comment",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.release,
                    metadata=JobMetadataConfig(targets=STABLE_VERSIONS),
                )
            ],
            TheJobTriggerType.release,
            JobConfigTriggerType.release,
            STABLE_CHROOTS,
            set(),
            id="build_with_targets&release",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.commit,
                    metadata=JobMetadataConfig(targets=STABLE_VERSIONS),
                )
            ],
            TheJobTriggerType.push,
            JobConfigTriggerType.commit,
            STABLE_CHROOTS,
            set(),
            id="build_with_targets&push",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(targets=STABLE_VERSIONS),
                ),
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.commit,
                    metadata=JobMetadataConfig(targets=["different", "os", "target"]),
                ),
            ],
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            STABLE_CHROOTS,
            set(),
            id="build_with_targets&pull_request_with_pr_and_push_defined",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(targets=STABLE_VERSIONS),
                ),
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.commit,
                    metadata=JobMetadataConfig(targets=["different", "os", "target"]),
                ),
            ],
            TheJobTriggerType.pr_comment,
            JobConfigTriggerType.pull_request,
            STABLE_CHROOTS,
            set(),
            id="build_with_targets&pr_comment_with_pr_and_push_defined",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(targets=["different", "os", "target"]),
                ),
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.commit,
                    metadata=JobMetadataConfig(targets=STABLE_VERSIONS),
                ),
            ],
            TheJobTriggerType.push,
            JobConfigTriggerType.commit,
            STABLE_CHROOTS,
            set(),
            id="build_with_targets&push_with_pr_and_push_defined",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                )
            ],
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            STABLE_CHROOTS,
            set(),
            id="build_without_targets",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.tests,
                    trigger=JobConfigTriggerType.pull_request,
                )
            ],
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            STABLE_CHROOTS,
            STABLE_CHROOTS,
            id="test_without_targets",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.tests,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(targets=STABLE_VERSIONS),
                )
            ],
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            STABLE_CHROOTS,
            STABLE_CHROOTS,
            id="test_with_targets",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                ),
                JobConfig(
                    type=JobType.tests,
                    trigger=JobConfigTriggerType.pull_request,
                ),
            ],
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            STABLE_CHROOTS,
            STABLE_CHROOTS,
            id="build_without_target&test_without_targets",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(targets=STABLE_VERSIONS),
                ),
                JobConfig(
                    type=JobType.tests,
                    trigger=JobConfigTriggerType.pull_request,
                ),
            ],
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            STABLE_CHROOTS,
            STABLE_CHROOTS,
            id="build_with_target&test_without_targets",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                ),
                JobConfig(
                    type=JobType.tests,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(targets=STABLE_VERSIONS),
                ),
            ],
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            STABLE_CHROOTS,
            STABLE_CHROOTS,
            id="build_without_target&test_with_targets",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                ),
                JobConfig(
                    type=JobType.tests,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(targets=list(ONE_CHROOT_SET)),
                ),
            ],
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            ONE_CHROOT_SET,
            ONE_CHROOT_SET,
            id="build_without_target&test_with_one_str_target",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                ),
                JobConfig(
                    type=JobType.tests,
                    trigger=JobConfigTriggerType.pull_request,
                ),
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.commit,
                ),
            ],
            TheJobTriggerType.push,
            JobConfigTriggerType.commit,
            STABLE_CHROOTS,
            set(),
            id="build[pr+commit]&test[pr]&commit",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                ),
                JobConfig(
                    type=JobType.tests,
                    trigger=JobConfigTriggerType.pull_request,
                ),
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.commit,
                ),
            ],
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            STABLE_CHROOTS,
            STABLE_CHROOTS,
            id="build[pr+commit]&test[pr]&pr",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                ),
                JobConfig(type=JobType.tests, trigger=JobConfigTriggerType.commit),
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.commit,
                ),
            ],
            TheJobTriggerType.push,
            JobConfigTriggerType.commit,
            STABLE_CHROOTS,
            STABLE_CHROOTS,
            id="build[pr+commit]&test[commit]&commit",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.commit,
                ),
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                ),
                JobConfig(type=JobType.tests, trigger=JobConfigTriggerType.commit),
            ],
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            STABLE_CHROOTS,
            set(),
            id="build[pr+commit]&test[commit]&pr",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.commit,
                ),
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.release,
                ),
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                ),
                JobConfig(
                    type=JobType.tests, trigger=JobConfigTriggerType.pull_request
                ),
            ],
            TheJobTriggerType.push,
            JobConfigTriggerType.commit,
            STABLE_CHROOTS,
            set(),
            id="build[pr+commit+release]&test[pr]&commit",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.build,
                    trigger=JobConfigTriggerType.pull_request,
                ),
                JobConfig(
                    type=JobType.tests,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(targets=list(ONE_CHROOT_SET)),
                ),
            ],
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            ONE_CHROOT_SET,
            ONE_CHROOT_SET,
            id="build_with_mixed_build_alias",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.production_build,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(targets=STABLE_VERSIONS),
                )
            ],
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            STABLE_CHROOTS,
            set(),
            id="koji_build_with_targets_for_pr",
        ),
    ],
)
def test_targets(jobs, trigger, job_config_trigger_type, build_chroots, test_chroots):
    copr_build_handler = CoprBuildJobHelper(
        service_config=flexmock(),
        package_config=PackageConfig(jobs=jobs),
        job_config=jobs[0],  # BuildHelper looks at all jobs in the end
        project=flexmock(),
        metadata=flexmock(trigger=trigger, pr_id=None),
        db_trigger=flexmock(job_config_trigger_type=job_config_trigger_type),
    )

    assert copr_build_handler.package_config.jobs
    assert [j.type for j in copr_build_handler.package_config.jobs]

    assert copr_build_handler.build_targets == build_chroots
    assert copr_build_handler.tests_targets == test_chroots


@pytest.mark.parametrize(
    "jobs,init_job,trigger,job_config_trigger_type,result_job_build,result_job_tests",
    [
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                )
            ],
            JobConfig(
                type=JobType.copr_build,
                trigger=JobConfigTriggerType.pull_request,
            ),
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            JobConfig(
                type=JobType.copr_build,
                trigger=JobConfigTriggerType.pull_request,
            ),
            None,
            id="copr_build&pull_request",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.build,
                    trigger=JobConfigTriggerType.pull_request,
                )
            ],
            JobConfig(
                type=JobType.build,
                trigger=JobConfigTriggerType.pull_request,
            ),
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            JobConfig(
                type=JobType.build,
                trigger=JobConfigTriggerType.pull_request,
            ),
            None,
            id="build&pull_request",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                )
            ],
            JobConfig(
                type=JobType.copr_build,
                trigger=JobConfigTriggerType.pull_request,
            ),
            TheJobTriggerType.pr_comment,
            JobConfigTriggerType.pull_request,
            JobConfig(
                type=JobType.copr_build,
                trigger=JobConfigTriggerType.pull_request,
            ),
            None,
            id="copr_build&pr_comment",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.release,
                )
            ],
            JobConfig(
                type=JobType.copr_build,
                trigger=JobConfigTriggerType.release,
            ),
            TheJobTriggerType.release,
            JobConfigTriggerType.release,
            JobConfig(
                type=JobType.copr_build,
                trigger=JobConfigTriggerType.release,
            ),
            None,
            id="copr_build&release",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.commit,
                )
            ],
            JobConfig(
                type=JobType.copr_build,
                trigger=JobConfigTriggerType.commit,
            ),
            TheJobTriggerType.push,
            JobConfigTriggerType.commit,
            JobConfig(
                type=JobType.copr_build,
                trigger=JobConfigTriggerType.commit,
            ),
            None,
            id="copr_build&push",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                ),
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.commit,
                ),
            ],
            JobConfig(
                type=JobType.copr_build,
                trigger=JobConfigTriggerType.pull_request,
            ),
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            JobConfig(
                type=JobType.copr_build,
                trigger=JobConfigTriggerType.pull_request,
            ),
            None,
            id="copr_build[pr+commit]&pull_request",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.commit,
                ),
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                ),
            ],
            JobConfig(
                type=JobType.copr_build,
                trigger=JobConfigTriggerType.pull_request,
            ),
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            JobConfig(
                type=JobType.copr_build,
                trigger=JobConfigTriggerType.pull_request,
            ),
            None,
            id="copr_build[commit+pr]&pull_request",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                ),
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.commit,
                ),
            ],
            JobConfig(
                type=JobType.copr_build,
                trigger=JobConfigTriggerType.commit,
            ),
            TheJobTriggerType.push,
            JobConfigTriggerType.commit,
            JobConfig(
                type=JobType.copr_build,
                trigger=JobConfigTriggerType.commit,
            ),
            None,
            id="copr_build[pr+commit]&push",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.tests,
                    trigger=JobConfigTriggerType.pull_request,
                )
            ],
            JobConfig(
                type=JobType.tests,
                trigger=JobConfigTriggerType.pull_request,
            ),
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            None,
            JobConfig(
                type=JobType.tests,
                trigger=JobConfigTriggerType.pull_request,
            ),
            id="test&pr",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                ),
                JobConfig(
                    type=JobType.tests,
                    trigger=JobConfigTriggerType.pull_request,
                ),
            ],
            JobConfig(
                type=JobType.copr_build,
                trigger=JobConfigTriggerType.pull_request,
            ),
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            JobConfig(
                type=JobType.copr_build,
                trigger=JobConfigTriggerType.pull_request,
            ),
            JobConfig(
                type=JobType.tests,
                trigger=JobConfigTriggerType.pull_request,
            ),
            id="copr_build+test&pr",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.build,
                    trigger=JobConfigTriggerType.pull_request,
                ),
                JobConfig(
                    type=JobType.tests,
                    trigger=JobConfigTriggerType.pull_request,
                ),
            ],
            JobConfig(
                type=JobType.build,
                trigger=JobConfigTriggerType.pull_request,
            ),
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            JobConfig(
                type=JobType.build,
                trigger=JobConfigTriggerType.pull_request,
            ),
            JobConfig(
                type=JobType.tests,
                trigger=JobConfigTriggerType.pull_request,
            ),
            id="build+test&pr",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                ),
                JobConfig(
                    type=JobType.tests,
                    trigger=JobConfigTriggerType.pull_request,
                ),
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.commit,
                ),
            ],
            JobConfig(
                type=JobType.copr_build,
                trigger=JobConfigTriggerType.pull_request,
            ),
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            JobConfig(
                type=JobType.copr_build,
                trigger=JobConfigTriggerType.pull_request,
            ),
            JobConfig(
                type=JobType.tests,
                trigger=JobConfigTriggerType.pull_request,
            ),
            id="copr_build[pr+commit]+test[pr]&pr",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                ),
                JobConfig(
                    type=JobType.tests,
                    trigger=JobConfigTriggerType.pull_request,
                ),
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.commit,
                ),
            ],
            JobConfig(
                type=JobType.copr_build,
                trigger=JobConfigTriggerType.commit,
            ),
            TheJobTriggerType.push,
            JobConfigTriggerType.commit,
            JobConfig(
                type=JobType.copr_build,
                trigger=JobConfigTriggerType.commit,
            ),
            None,
            id="copr_build[pr+commit]+test[pr]&commit",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                ),
                JobConfig(
                    type=JobType.tests,
                    trigger=JobConfigTriggerType.pull_request,
                ),
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.commit,
                ),
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.release,
                ),
            ],
            JobConfig(
                type=JobType.copr_build,
                trigger=JobConfigTriggerType.release,
            ),
            TheJobTriggerType.release,
            JobConfigTriggerType.release,
            JobConfig(
                type=JobType.copr_build,
                trigger=JobConfigTriggerType.release,
            ),
            None,
            id="copr_build[pr+commit]+test[pr]&commit",
        ),
    ],
)
def test_build_handler_job_and_test_properties(
    jobs,
    init_job,
    trigger,
    job_config_trigger_type,
    result_job_build,
    result_job_tests,
):
    copr_build_handler = CoprBuildJobHelper(
        service_config=flexmock(),
        package_config=PackageConfig(jobs=jobs),
        job_config=init_job,
        project=flexmock(),
        metadata=flexmock(trigger=trigger, pr_id=None),
        db_trigger=flexmock(job_config_trigger_type=job_config_trigger_type),
    )

    assert copr_build_handler.package_config.jobs
    assert [j.type for j in copr_build_handler.package_config.jobs]

    assert copr_build_handler.job_build == result_job_build
    assert copr_build_handler.job_tests == result_job_tests


@pytest.mark.parametrize(
    "jobs,trigger,job_config_trigger_type,job_owner,job_project",
    [
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(),
                )
            ],
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            "nobody",
            "git.instance.io-the-example-namespace-the-example-repo-the-event-identifier",
            id="default-values",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(owner="custom-owner"),
                )
            ],
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            "custom-owner",
            "git.instance.io-the-example-namespace-the-example-repo-the-event-identifier",
            id="custom-owner&default-project",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(project="custom-project"),
                )
            ],
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            "nobody",
            "custom-project",
            id="default-owner&custom-project",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(
                        owner="custom-owner", project="custom-project"
                    ),
                )
            ],
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            "custom-owner",
            "custom-project",
            id="custom-owner&custom-project",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.build,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(
                        owner="custom-owner", project="custom-project"
                    ),
                )
            ],
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            "custom-owner",
            "custom-project",
            id="custom-owner-build&custom-project",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.commit,
                    metadata=JobMetadataConfig(),
                )
            ],
            TheJobTriggerType.commit,
            JobConfigTriggerType.commit,
            "nobody",
            "git.instance.io-the-example-namespace-the-example-repo-the-event-identifier",
            id="commit&default-owner&default-project",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.commit,
                    metadata=JobMetadataConfig(
                        owner="commit-owner", project="commit-project"
                    ),
                ),
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(owner="pr-owner", project="pr-project"),
                ),
            ],
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            "pr-owner",
            "pr-project",
            id="two-copr-builds&custom-owner&custom-project",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(),
                ),
                JobConfig(
                    type=JobType.tests,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(),
                ),
            ],
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            "nobody",
            "git.instance.io-the-example-namespace-the-example-repo-the-event-identifier",
            id="build+test&default-owner&default-project",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(
                        owner="custom-owner", project="custom-project"
                    ),
                ),
                JobConfig(
                    type=JobType.tests,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(),
                ),
            ],
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            "custom-owner",
            "custom-project",
            id="build+test&custom-owner&custom-project-from-build",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(),
                ),
                JobConfig(
                    type=JobType.tests,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(
                        owner="custom-owner", project="custom-project"
                    ),
                ),
            ],
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            "custom-owner",
            "custom-project",
            id="build+test&custom-owner&custom-project-from-test",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(owner="pr-owner", project="pr-project"),
                ),
                JobConfig(
                    type=JobType.tests,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(),
                ),
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.commit,
                    metadata=JobMetadataConfig(
                        owner="commit-owner", project="commit-project"
                    ),
                ),
            ],
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            "pr-owner",
            "pr-project",
            id="two-copr-builds+test-pr&custom-owner&custom-project",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(owner="pr-owner", project="pr-project"),
                ),
                JobConfig(
                    type=JobType.tests,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(),
                ),
                JobConfig(
                    type=JobType.copr_build,
                    trigger=JobConfigTriggerType.commit,
                    metadata=JobMetadataConfig(
                        owner="commit-owner", project="commit-project"
                    ),
                ),
            ],
            TheJobTriggerType.commit,
            JobConfigTriggerType.commit,
            "commit-owner",
            "commit-project",
            id="two-copr-builds+test-commit&custom-owner&custom-project",
        ),
    ],
)
def test_copr_project_and_namespace(
    jobs, trigger, job_config_trigger_type, job_owner, job_project
):
    copr_build_handler = CoprBuildJobHelper(
        service_config=flexmock(deployment="stg"),
        package_config=PackageConfig(jobs=jobs),
        job_config=jobs[0],  # BuildHelper looks at all jobs in the end
        project=flexmock(
            namespace="the/example/namespace",
            repo="the-example-repo",
            service=flexmock(instance_url="https://git.instance.io"),
        ),
        metadata=flexmock(
            trigger=trigger, pr_id=None, identifier="the-event-identifier"
        ),
        db_trigger=flexmock(job_config_trigger_type=job_config_trigger_type),
    )
    copr_build_handler._api = flexmock(
        copr_helper=flexmock(copr_client=flexmock(config={"username": "nobody"}))
    )

    assert copr_build_handler.job_project == job_project
    assert copr_build_handler.job_owner == job_owner


@pytest.mark.parametrize(
    "jobs,trigger,job_config_trigger_type,build_targets,koji_targets",
    [
        pytest.param(
            [
                JobConfig(
                    type=JobType.production_build,
                    trigger=JobConfigTriggerType.pull_request,
                    metadata=JobMetadataConfig(targets=STABLE_VERSIONS),
                )
            ],
            TheJobTriggerType.pull_request,
            JobConfigTriggerType.pull_request,
            set(STABLE_VERSIONS),
            STABLE_KOJI_TARGETS,
            id="koji_build_with_targets_for_pr",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.production_build,
                    trigger=JobConfigTriggerType.commit,
                    metadata=JobMetadataConfig(
                        targets=STABLE_VERSIONS, branch="build-branch"
                    ),
                )
            ],
            TheJobTriggerType.push,
            JobConfigTriggerType.commit,
            set(STABLE_VERSIONS),
            STABLE_KOJI_TARGETS,
            id="koji_build_with_targets_for_commit",
        ),
        pytest.param(
            [
                JobConfig(
                    type=JobType.production_build,
                    trigger=JobConfigTriggerType.release,
                    metadata=JobMetadataConfig(
                        targets=STABLE_VERSIONS, branch="build-branch"
                    ),
                )
            ],
            TheJobTriggerType.release,
            JobConfigTriggerType.release,
            set(STABLE_VERSIONS),
            STABLE_KOJI_TARGETS,
            id="koji_build_with_targets_for_release",
        ),
    ],
)
def test_targets_for_koji_build(
    jobs, trigger, job_config_trigger_type, build_targets, koji_targets
):
    pr_id = 41 if trigger == TheJobTriggerType.pull_request else None
    koji_build_handler = KojiBuildJobHelper(
        service_config=flexmock(),
        package_config=PackageConfig(jobs=jobs),
        job_config=jobs[0],
        project=flexmock(),
        metadata=flexmock(trigger=trigger, pr_id=pr_id),
        db_trigger=flexmock(job_config_trigger_type=job_config_trigger_type),
    )

    assert koji_build_handler.package_config.jobs
    assert [j.type for j in koji_build_handler.package_config.jobs]

    assert koji_build_handler.configured_build_targets == build_targets
    assert koji_build_handler.build_targets == koji_targets
