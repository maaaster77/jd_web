insert into jd.role (id, name, detail, status)
values  (1, '超级管理员', '超级管理员，权限较大', 1),
        (2, '普通用户', '基础角色', 1);


insert into jd.user (id, username, password, status) values (1, 'admin', '111111', 1);


insert into jd.user_role (id, user_id, role_id, status) values (1, 1, 1, 1);
