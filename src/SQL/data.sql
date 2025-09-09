----------------------------------- TABLAS DE LA DATA BASE ----------------------------
CREATE DATABASE IF NOT EXISTS `archivos_h`;

USE `archivos_h`;

CREATE TABLE `planos` (
  `id_plano` int(10) PRIMARY KEY AUTO_INCREMENT,
  `identificador_plano` varchar(20),
  `descripcion` varchar(500),
  `dibujante` varchar(100),
  `fecha` date,
  `id_tipo_plano` int(3),
  `id_num_plano` int(10),
  `id_tamanio` int(2),
  `id_revision` int(2),
  `id_sub_revision` int(2),
  `id_archivo` int(2)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `tipo_plano` (
  `id_tipo_plano` int(3) PRIMARY KEY AUTO_INCREMENT,
  `tipo_plano` varchar(100)
  `cod_tipo_plano` varchar(3)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `num_plano` (
  `id_num_plano` int(10) PRIMARY KEY AUTO_INCREMENT,
  `num_plano` varchar(10) AUTO_INCREMENT=30000
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `tamanio` (
  `id_tamanio` int(2) PRIMARY KEY AUTO_INCREMENT,
  `tamanio` varchar(2) 
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `revision` (
  `id_revision` int(2) PRIMARY KEY AUTO_INCREMENT,
  `revision` varchar(2) 
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `sub_revision` (
  `id_sub_revision` int(2) PRIMARY KEY AUTO_INCREMENT,
  `sub_revision` int(2) 
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `archivos` (
  `id_archivo` int(10) PRIMARY KEY AUTO_INCREMENT,
  `archivo_nombre` varchar(300),
  `archivo_path` varchar(300),
  `archivo_mime` varchar(50),
  `archivo_token` varchar(300)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
------------------------------- DATOS INSERTADOS -----------------------------

INSERT INTO `tamanio` (`id_tamanio`, `tamanio`) VALUES
(1, '0'),
(2, '1'),
(3, '2'),
(4, '3'),
(5, '4');

-- --------------------------------------------------------

INSERT INTO `tipo_plano` (`id_tplano`, `tipo_plano`, `cod_tplano`) VALUES
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

-- --------------------------------------------------------

INSERT INTO `version` (`id_version`, `version`) VALUES
(1, '_'),
(2, 'Z'),
(3, 'Y'),
(4, 'X'),
(5, 'W'),
(6, 'V'),
(7, 'U'),
(8, 'T'),
(9, 'S'),
(10, 'R'),
(11, 'Q'),
(12, 'P'),
(13, 'O'),
(14, 'N'),
(15, 'M'),
(16, 'L'),
(17, 'K'),
(18, 'J'),
(19, 'I'),
(20, 'H'),
(21, 'G'),
(22, 'F'),
(23, 'E'),
(24, 'D'),
(25, 'C'),
(26, 'B'),
(27, 'A');

ALTER TABLE `planos`
  ADD CONSTRAINT `planos_ibfk_1` FOREIGN KEY (`revision`) REFERENCES `version` (`id_version`),
  ADD CONSTRAINT `planos_ibfk_2` FOREIGN KEY (`archivo`) REFERENCES `archivos` (`id_archivos`),
  ADD CONSTRAINT `planos_ibfk_3` FOREIGN KEY (`num_plano`) REFERENCES `num_plano` (`id_num_plano`),
  ADD CONSTRAINT `planos_ibfk_4` FOREIGN KEY (`tipo_plano`) REFERENCES `tipo_plano` (`id_tplano`),
  ADD CONSTRAINT `planos_ibfk_5` FOREIGN KEY (`tamanio`) REFERENCES `tamanio` (`id_tamanio`);
COMMIT;
