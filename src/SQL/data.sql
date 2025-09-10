CREATE DATABASE IF NOT EXISTS `archivos_h`;
USE `archivos_h`;

-- TABLAS PRINCIPALES
CREATE TABLE `tipo_plano` (
  `id_tipo_plano` INT(3) PRIMARY KEY AUTO_INCREMENT,
  `tipo_plano` VARCHAR(100),
  `cod_tipo_plano` INT(3)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `num_plano` (
  `id_num_plano` INT(10) PRIMARY KEY AUTO_INCREMENT,
  `num_plano` INT(10) UNIQUE
) ENGINE=InnoDB AUTO_INCREMENT=3000 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
  `sub_revision` INT(2)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `archivos` (
  `id_archivo` INT(10) PRIMARY KEY AUTO_INCREMENT,
  `archivo_nombre` VARCHAR(300),
  `archivo_path` VARCHAR(300),
  `archivo_mime` VARCHAR(50),
  `archivo_token` VARCHAR(300)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- TABLA PLANOS (SE CREA AL FINAL PARA QUE EXISTAN TODAS LAS TABLAS REFERENCIADAS)
CREATE TABLE `planos` (
  `id_plano` INT(10) PRIMARY KEY AUTO_INCREMENT,
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
  CONSTRAINT `planos_ibfk_1` FOREIGN KEY (`id_revision`) REFERENCES `revision` (`id_revision`),
  CONSTRAINT `planos_ibfk_2` FOREIGN KEY (`id_archivo`) REFERENCES `archivos` (`id_archivo`),
  CONSTRAINT `planos_ibfk_3` FOREIGN KEY (`id_num_plano`) REFERENCES `num_plano` (`id_num_plano`),
  CONSTRAINT `planos_ibfk_4` FOREIGN KEY (`id_tipo_plano`) REFERENCES `tipo_plano` (`id_tipo_plano`),
  CONSTRAINT `planos_ibfk_5` FOREIGN KEY (`id_tamanio`) REFERENCES `tamanio` (`id_tamanio`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- INSERTS
INSERT INTO `tamanio` (`id_tamanio`, `tamanio`) VALUES
(1, '0'), (2, '1'), (3, '2'), (4, '3'), (5, '4');

INSERT INTO `tipo_plano` (`id_tipo_plano`, `tipo_plano`, `cod_tipo_plano`) VALUES
(1, 'ESQUEMA GENERAL', 4),
(2, 'TABLAS DE PRODUCCIÓN', 6),
(3, 'CONJUNTO P.HIDRÁULICA', 11),
(4, 'PIEZAS P.HIDRÁULICA', 12),
(5, 'CURVAS HIDRÁULICAS', 14),
(6, 'CONJUNTO P.SOPORTE', 21),
(7, 'PIEZA P.SOPORTE', 22),
(8, 'CONJUNTO CCMM', 31),
(9, 'PIEZAS CCMM', 32),
(10, 'CROQUIS DE CONJUNTOS', 41),
(11, 'CROQUIS DE PIEZAS', 42),
(12, 'TERCEROS GENERAL', 50),
(13, 'CONJUNTO TERCEROS', 51),
(14, 'PIEZAS TERCEROS', 52),
(15, 'CROQUIS TERCEROS', 53),
(16, 'MODELO TERCEROS', 54),
(17, 'FUNDA TERCEROS', 55),
(18, 'MODELO HIDROSTAL', 56),
(19, 'DESARROLLO CONJUNTOS', 71),
(20, 'DESARROLLO PIEZAS', 72),
(21, 'CONTROL DE INTERNAMIENTO', 0),
(22, 'LABORATORIO DE PRUEBAS', 0),
(23, 'TURBINA SUMERGIBLE', 0),
(24, 'OTRO', 0);

INSERT INTO `revision` (`id_revision`, `revision`) VALUES
(1, '_'), (2, 'Z'), (3, 'Y'), (4, 'X'), (5, 'W'),
(6, 'V'), (7, 'U'), (8, 'T'), (9, 'S'), (10, 'R'),
(11, 'Q'), (12, 'P'), (13, 'O'), (14, 'N'), (15, 'M'),
(16, 'L'), (17, 'K'), (18, 'J'), (19, 'I'), (20, 'H'),
(21, 'G'), (22, 'F'), (23, 'E'), (24, 'D'), (25, 'C'),
(26, 'B'), (27, 'A');

INSERT INTO `sub_revision` (`id_sub_revision`, `sub_revision`) VALUES
(1,1), (2,2), (3,3), (4,4), (5,5), (6,6), (7,7), (8,8), (9,9), (10,10);

COMMIT;
