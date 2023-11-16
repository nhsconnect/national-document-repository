from enums.repository_role import RepositoryRole


def test_repository_role_list_returns_all_roles():
    roles = RepositoryRole.list()
    assert len(roles) == 4
    assert RepositoryRole.GP_CLINICAL.value in roles
    assert RepositoryRole.GP_ADMIN.value in roles
    assert RepositoryRole.PCSE.value in roles
    assert RepositoryRole.NONE.value in roles


def test_repository_role_list_returns_all_roles_as_list():
    assert isinstance(RepositoryRole.list(), list)
