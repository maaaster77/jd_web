CREATE TABLE `user`
(
    `id`         int          NOT NULL AUTO_INCREMENT,
    `username`   varchar(80)  not null default '' comment '用户名',
    `password`   varchar(256) not null default '' comment '密码',
    `status`     int          not null default 1 not null comment '状态 1-有效 0-无效',
    `created_at` timestamp    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` timestamp    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `udx_username` (`username`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4 COMMENT ='用户表';

# 关键词
CREATE TABLE `black_keyword`
(
    `id`         int          NOT NULL AUTO_INCREMENT,
    `keyword`    varchar(126) not null default '' comment '关键词',
    `status`     int          not null default 0 comment '状态',
    `is_delete`  int          not null default 0 comment '0-正常 1-已删除',
    `created_at` timestamp    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` timestamp    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4 COMMENT ='黑词表';


# 权限相关 #####################################
CREATE TABLE `role`
(
    `id`         int(11) unsigned NOT NULL AUTO_INCREMENT,
    `name`       varchar(31)      NOT NULL DEFAULT '',
    `detail`     varchar(255)     NOT NULL DEFAULT '' COMMENT '角色描述',
    `status`     tinyint(4)       NOT NULL DEFAULT '0' COMMENT '0-无效，1-有效',
    `created_at` timestamp        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` timestamp        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `u_name` (`name`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8 comment '角色';


CREATE TABLE `permission`
(
    `id`         int(11) unsigned NOT NULL AUTO_INCREMENT,
    `name`       varchar(31)      NOT NULL DEFAULT '',
    `perm_key`   varchar(255)     NOT NULL DEFAULT '' COMMENT '权限标识',
    `level`      tinyint(4)       NOT NULL DEFAULT '0' COMMENT '几级，1-一级菜单，2-二级菜单，3-三级功能/页面，4-四级功能；与type字段结合使用',
    `type`       tinyint(4)       NOT NULL DEFAULT '0' COMMENT '类型，1-菜单，2-功能，3-页面',
    `parent_id`  int(11)          NOT NULL DEFAULT '0' COMMENT '父级权限ID',
    `priority`   int(11)          NOT NULL DEFAULT '0' COMMENT '排序值，越小越靠前',
    `status`     tinyint(4)       NOT NULL DEFAULT '0' COMMENT '-1-被删除，0-禁用，1-开启',
    `created_at` timestamp        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` timestamp        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `u_perm_key` (`perm_key`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8 comment '权限';

CREATE TABLE `role_permission`
(
    `id`            int(11) unsigned NOT NULL AUTO_INCREMENT,
    `role_id`       int(11)          NOT NULL DEFAULT '0',
    `permission_id` int(11)          NOT NULL DEFAULT '0',
    `status`        tinyint(4)       NOT NULL DEFAULT '0' COMMENT '0-无效，1-有效',
    `created_at`    timestamp        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`    timestamp        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `u_role_perm` (`role_id`, `permission_id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8 comment '角色-权限';

CREATE TABLE `user_role`
(
    `id`         int(11) unsigned NOT NULL AUTO_INCREMENT,
    `user_id`    int(11)          NOT NULL DEFAULT '0',
    `role_id`    int(11)          NOT NULL DEFAULT '0',
    `status`     tinyint(4)       NOT NULL DEFAULT '0' COMMENT '0-无效，1-有效',
    `created_at` timestamp        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` timestamp        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `u_member_role` (`user_id`, `role_id`),
    KEY `idx_role` (`role_id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8 comment '用户-角色';
# END #####################################


# 黑词结果
CREATE TABLE `keyword_search` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `batch_id` varchar(64) NOT NULL DEFAULT '' COMMENT '批次id',
  `search_type` int(11) NOT NULL DEFAULT '1' COMMENT '1-baidu 2-google',
  `keyword` varchar(80) NOT NULL DEFAULT '' COMMENT '黑词',
  `result` text COMMENT '黑词搜索结果',
  `page` int(11) NOT NULL DEFAULT '1' COMMENT '页数',
  `status` int(11) NOT NULL DEFAULT '0' COMMENT '状态 0-待处理 1-处理中 2-已处理',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `udx_keyword` (`keyword`),
  KEY `udx_batch_id` (`batch_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='黑词搜索结果';


CREATE TABLE `keyword_search_parse_result` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `keyword` varchar(80) NOT NULL DEFAULT '' COMMENT '黑词',
  `url` varchar(1024) not null default '' comment 'url',
  `account` varchar(1024) not null default '' comment '账户内容相关',
  `desc` varchar(1024) not null default '' comment '描述',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_keyword` (`keyword`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='黑词搜索结果解析';

CREATE TABLE `keyword_search_parse_result_tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parse_id` int not null default 0 comment 'keyword_search_parse_result.id',
  `tag_id` int not null default 0 comment '标签id',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_parse_tag` (`parse_id`, `tag_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='黑词解析结果-标签';

alter table keyword_search_parse_result add `is_delete` int not null default 0 comment '0-未删除 1-已删除' after `desc`;
