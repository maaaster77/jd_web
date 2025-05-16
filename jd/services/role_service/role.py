from jd import db
from jd.models.user_role import UserRole

ROLE_SUPER_ADMIN = 'super_admin'
ROLE_COMMON_USER = 'common_user'

# role name: role id
ROLE_MAP = {
    ROLE_SUPER_ADMIN: 1,
    ROLE_COMMON_USER: 2,
}


class RoleService:

    @classmethod
    def user_roles(cls, user_id):
        user_roles = db.session.query(UserRole).filter(UserRole.user_id == user_id,
                                                       UserRole.status == UserRole.StatusType.VALID).all()
        role_ids = [role.role_id for role in user_roles]
        return role_ids
