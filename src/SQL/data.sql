--
-- Estructura de tabla para la tabla `planos`
--

CREATE TABLE `planos` (
  `id_plano` int(11) PRIMARY KEY AUTO_INCREMENT,
  `anio` int(6) NOT NULL,
  `mes` varchar(15) DEFAULT NULL,
  `descripcion` varchar(200) DEFAULT NULL,
  `num_plano` varchar(20) DEFAULT NULL,
  `tamanio` varchar(5) DEFAULT NULL,
  `version` varchar(5) NOT NULL,
  `dibujante` varchar(20) NOT NULL,
  `dibujado_en` varchar(5) NOT NULL,
  `archivo_nombre` varchar(255) DEFAULT NULL,
  `archivo_path` varchar(300) DEFAULT NULL,
  `archivo_mime` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `planos`
--

INSERT INTO `planos` (`id_plano`, `anio`, `mes`, `descripcion`, `num_plano`, `tamanio`, `version`, `dibujante`, `dibujado_en`, `archivo_nombre`, `archivo_path`, `archivo_mime`) VALUES
(47, 1, 'Enero', 'rrrrrr', '456789', 'A2', '2.00', 'fsdgdsfjo', 'CAD', 'DOCUMENTACION_MOTORES_US_MOTORES_-15379.pdf', '63d1d1d47f98415fb0f6872af3c846a9.pdf', 'application/pdf'),
(48, 2, 'Febrero', '2', '2', 'A0', '2', '2', 'CAD', 'EN_10226-1_2004.pdf', '92db80c50a4a4828b309d231722f4067.pdf', 'application/pdf'),
(49, 3, 'Febrero', '3', '3', 'A0', '3', '3', 'CAD', 'Bocinas_Thordon_SXL_poros.pdf', '001d7333bb974cf9bebb770567be273c.pdf', 'application/pdf');
