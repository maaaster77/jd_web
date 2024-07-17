

CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(80) not null default '' comment '用户名',
  `password` varchar(256) not null default '' comment '密码',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `udx_username` (`username`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8mb4 COMMENT='用户表';