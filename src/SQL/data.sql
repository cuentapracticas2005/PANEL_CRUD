--
-- Estructura de tabla para la tabla `planos`
--

CREATE TABLE `planos` (
  `id_plano` int(11) PRIMARY KEY AUTO_INCREMENT,
  `fecha` DATE NOT NULL,
  `descripcion` varchar(200) DEFAULT NULL,
  `num_plano` varchar(20) DEFAULT NULL,
  `tamanio` varchar(5) DEFAULT NULL,
  `version` varchar(5) DEFAULT NULL,
  `dibujante` varchar(20) NOT NULL,
  `archivo_nombre` varchar(255) DEFAULT NULL,
  `archivo_path` varchar(300) DEFAULT NULL,
  `archivo_mime` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
