CREATE DATABASE IF NOT EXISTS `registros_h`;
USE `registros_h`;

-- TABLAS PRINCIPALES
CREATE TABLE `tipo_plano` (
  `id_tipo_plano` INT(3) PRIMARY KEY AUTO_INCREMENT,
  `tipo_plano` VARCHAR(100),
  `cod_tipo_plano` VARCHAR(4)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `num_plano` (
  `id_num_plano` INT(10) PRIMARY KEY AUTO_INCREMENT
) ENGINE=InnoDB AUTO_INCREMENT=30000 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `tamanio` (
  `id_tamanio` INT(2) PRIMARY KEY AUTO_INCREMENT,
  `tamanio` VARCHAR(2)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci; 

CREATE TABLE `revision` (
  `id_revision` INT(2) PRIMARY KEY AUTO_INCREMENT,
  `revision` VARCHAR(2)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `sub_revision` (
  `id_sub_revision` INT(2) PRIMARY KEY AUTO_INCREMENT,
  `sub_revision` VARCHAR(2)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `archivos` (
  `id_archivo` INT(10) PRIMARY KEY AUTO_INCREMENT,
  `archivo_nombre` VARCHAR(300),
  `archivo_path` VARCHAR(300),
  `archivo_mime` VARCHAR(50),
  `archivo_token` VARCHAR(300)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `roles` (
  `id_rol` INT PRIMARY KEY AUTO_INCREMENT,
  `rol` VARCHAR(20) UNIQUE NOT NULL
 )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `user` (
  `id_user` INT PRIMARY KEY AUTO_INCREMENT,
  `username` VARCHAR(80) UNIQUE NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `nombre_completo` VARCHAR(300),
  `activo` BOOLEAN NOT NULL DEFAULT TRUE,
  `fecha_creacion` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `id_rol` INT(3) NOT NULL DEFAULT 1,
  FOREIGN KEY (`id_rol`) REFERENCES `roles` (`id_rol`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- TABLA PLANOS (SE CREA AL FINAL PARA QUE EXISTAN TODAS LAS TABLAS REFERENCIADAS)
CREATE TABLE `registros` (
  `id_registro` INT(10) PRIMARY KEY AUTO_INCREMENT,
  `identificador_plano` VARCHAR(20),
  `descripcion` VARCHAR(500),
  `dibujante` VARCHAR(100),
  `fecha` DATE,
  `id_tipo_plano` INT(3),
  `id_num_plano` INT(10),
  `id_tamanio` INT(2),
  `id_revision` INT(2),
  `id_sub_revision` INT(2),
  `id_archivo` INT(10),
  FOREIGN KEY (`id_tipo_plano`) REFERENCES `tipo_plano` (`id_tipo_plano`),
  FOREIGN KEY (`id_num_plano`) REFERENCES `num_plano` (`id_num_plano`),
  FOREIGN KEY (`id_tamanio`) REFERENCES `tamanio` (`id_tamanio`),
  FOREIGN KEY (`id_revision`) REFERENCES `revision` (`id_revision`),
  FOREIGN KEY (`id_sub_revision`) REFERENCES `sub_revision` (`id_sub_revision`),
  FOREIGN KEY (`id_archivo`) REFERENCES `archivos` (`id_archivo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- INSERTS
INSERT INTO `tamanio` (`id_tamanio`, `tamanio`) VALUES
(1, '0'), (2, '1'), (3, '2'), (4, '3'), (5, '4');

INSERT INTO `tipo_plano` (`id_tipo_plano`, `tipo_plano`, `cod_tipo_plano`) VALUES
(1, '04 - ESQUEMA GENERAL','04'),
(2, '06 - TABLAS DE PRODUCCIÓN','06'),
(3, '11 - CONJUNTO P.HIDRÁULICA', '11'),
(4, '12 - PIEZAS P.HIDRÁULICA', '12'),
(5, '14 - CURVAS HIDRÁULICAS', '14'),
(6, '21 - CONJUNTO P.SOPORTE', '21'),
(7, '22 - PIEZA P.SOPORTE', '22'),
(8, '31 - CONJUNTO CCMM', '31'),
(9, '32 - PIEZAS CCMM', '32'),
(10, '41 - CROQUIS DE CONJUNTOS', '41'),
(11, '42 - CROQUIS DE PIEZAS', '42'),
(12, '50 - TERCEROS GENERAL', '50'),
(13, '51 - CONJUNTO TERCEROS', '51'),
(14, '52 - PIEZAS TERCEROS', '52'),
(15, '53 - CROQUIS TERCEROS', '53'),
(16, '54 - MODELO TERCEROS', '54'),
(17, '55 - FUNDA TERCEROS', '55'),
(18, '56 - MODELO HIDROSTAL', '56'),
(19, '71 - DESARROLLO CONJUNTOS', '71'),
(20, '72 - DESARROLLO PIEZAS', '72'),
(21, 'CI - CONTROL DE INTERNAMIENTO', 'CI'),
(22, 'LP - LABORATORIO DE PRUEBAS', 'LP'),
(23, 'TS - TURBINA SUMERGIBLE', 'TS'),
(24, 'Z0 - OTRO', 'Z0');

INSERT INTO `revision` (`id_revision`, `revision`) VALUES
(1, '_'), (2, 'Z'), (3, 'Y'), (4, 'X'), (5, 'W'),
(6, 'V'), (7, 'U'), (8, 'T'), (9, 'S'), (10, 'R'),
(11, 'Q'), (12, 'P'), (13, 'O'), (14, 'N'), (15, 'M'),
(16, 'L'), (17, 'K'), (18, 'J'), (19, 'I'), (20, 'H'),
(21, 'G'), (22, 'F'), (23, 'E'), (24, 'D'), (25, 'C'),
(26, 'B'), (27, 'A');

INSERT INTO `sub_revision` (`id_sub_revision`, `sub_revision`) VALUES
(1,'1'), (2,'2'), (3,'3'), (4,'4'), (5,'5'), (6,'6'), (7,'7'), (8,'8'), (9,'9'), (10,'10');

INSERT INTO `roles` (`id_rol`, `rol`) VALUES
(1, 'admin'),
(2, 'dibujante'),
(3, 'trabajador');

# INFORMACION INSERTADA COMO PRIMER REGISTRO EN REGISTRO DE PLANOS:
INSERT INTO `num_plano`(`id_num_plano`) VALUES
  ('30000');

INSERT INTO `registros`(`identificador_plano`, `descripcion`, `dibujante`, `fecha`, `id_tipo_plano`, `id_num_plano`, `id_tamanio`, `id_revision`, `id_sub_revision`) VALUES
  ('xxxxxxx','descripcion01','dibujante01','2025-09-25','1','30000','1','1','1');

# INFORMACION INSERTADA COMO PRIMER USUARIO ADMINISTRADOR
INSERT INTO `user`(`username`, `password_hash`, `activo`, `id_rol`) VALUES
  ('stuart','scrypt:32768:8:1$sqbQum2A9TzCPN2a$f0128f1866a65cf793fee60773e999ab69d90c779c8beb4f35a9353e4b642aee1632161279845cea329c290a8b55ba5e3d1c9e4d4a59faef9b264bb1b40cecf3',1,1),
  ('julio','scrypt:32768:8:1$sqbQum2A9TzCPN2a$f0128f1866a65cf793fee60773e999ab69d90c779c8beb4f35a9353e4b642aee1632161279845cea329c290a8b55ba5e3d1c9e4d4a59faef9b264bb1b40cecf3',1,2);
# username: stuart  /  password: 123
# username: julio  /  password: 123
COMMIT;
