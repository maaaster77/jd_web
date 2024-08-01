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


CREATE TABLE `keyword_search_queue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `batch_id` varchar(64) NOT NULL DEFAULT '' COMMENT '批次id',
  `search_type` int(11) NOT NULL DEFAULT '1' COMMENT '1-baidu 2-google',
  `keyword` varchar(80) NOT NULL DEFAULT '' COMMENT '黑词',
  `status` int(11) NOT NULL DEFAULT '0' COMMENT '状态 0-待处理 1-处理中 2-已处理',
  `page` int(11) NOT NULL DEFAULT '10' COMMENT '所需页码',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_batch_id` (`batch_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='黑词搜索队列';


CREATE TABLE `result_tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(32) not null default '' comment '标签名称',
  `status` int not null default 0 comment '状态 0-正常 1-无效',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_title` (`title`)
) ENGINE=InnoDB  CHARSET=utf8mb4 COMMENT='标签';


CREATE TABLE `tg_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL DEFAULT '' COMMENT '群组名称',
  `chat_id` varchar(128) NOT NULL DEFAULT '' COMMENT '聊天室id',
  `status` int NOT NULL DEFAULT 0 COMMENT '0-未加入 1-加入成功 2-加入失败',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `udx_name` (`name`)
) ENGINE=InnoDB  CHARSET=utf8mb4 COMMENT='tg群组表';

CREATE TABLE `tg_group_chat_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `chat_id` varchar(128) NOT NULL DEFAULT '' COMMENT '聊天室id',
  `message_id` varchar(128) NOT NULL DEFAULT '' COMMENT '消息id',
  `user_id` varchar(128) NOT NULL DEFAULT '' COMMENT '用户id',
  `username` varchar(128) NOT NULL DEFAULT '' COMMENT '用户名',
  `nickname` varchar(128) NOT NULL DEFAULT '' COMMENT '用户昵称',
  `postal_time` timestamp NOT NULL DEFAULT '1990-10-30 00:00:00',
  `reply_to_msg_id` varchar(128) NOT NULL DEFAULT '' COMMENT '回复的消息id',
  `message` text COMMENT '信息',
  `photo_path`   varchar(256) default ''  not null comment '图片地址',
  `status` int(11) NOT NULL DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8mb4 COMMENT='tg群组聊天记录';


CREATE TABLE `tg_group_user_info`
(
    `id`         int(11)      NOT NULL AUTO_INCREMENT,
    `chat_id`    varchar(128)          NOT NULL DEFAULT '' COMMENT '群组id',
    `user_id`    varchar(128)          not null default '' comment '用户id',
    `username`   varchar(128) not null default '' comment '用户名',
    `nickname`   varchar(128) not null default '' comment '用户昵称',
    `desc`       varchar(1024) not null  default '' comment '描述信息',
    `photo`     varchar(1024) not null default '' comment '头像地址',
    `status`     int          not null default 0,
    `created_at` timestamp    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` timestamp    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE = InnoDB
  CHARSET = utf8mb4 COMMENT ='tg群组用户信息';