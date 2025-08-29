
CREATE TABLE `archivos` (
  `id_archivos` int(10) NOT NULL,
  `archivo_nombre` varchar(255) DEFAULT NULL,
  `archivo_path` varchar(300) DEFAULT NULL,
  `archivo_mime` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `num_plano`
--

CREATE TABLE `num_plano` (
  `id_num_plano` int(10) NOT NULL,
  `num_plano` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `planos`
--

CREATE TABLE `planos` (
  `id_plano` int(10) NOT NULL,
  `identificador_plano` varchar(20) DEFAULT NULL,
  `descripcion` varchar(300) DEFAULT NULL,
  `dibujante` varchar(100) DEFAULT NULL,
  `fecha` date DEFAULT NULL,
  `tipo_plano` int(3) DEFAULT NULL,
  `num_plano` int(10) DEFAULT NULL,
  `tamanio` int(2) DEFAULT NULL,
  `version` int(2) DEFAULT NULL,
  `archivo` int(2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tamanio`
--

CREATE TABLE `tamanio` (
  `id_tamanio` int(2) NOT NULL,
  `tamanio` varchar(2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tipo_plano`
--

CREATE TABLE `tipo_plano` (
  `id_tplano` int(3) NOT NULL,
  `tipo_plano` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `version`
--

CREATE TABLE `version` (
  `id_version` int(2) NOT NULL,
  `version` varchar(2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `archivos`
--
ALTER TABLE `archivos`
  ADD PRIMARY KEY (`id_archivos`);

--
-- Indices de la tabla `num_plano`
--
ALTER TABLE `num_plano`
  ADD PRIMARY KEY (`id_num_plano`);

--
-- Indices de la tabla `planos`
--
ALTER TABLE `planos`
  ADD PRIMARY KEY (`id_plano`),
  ADD KEY `version` (`version`),
  ADD KEY `archivo` (`archivo`),
  ADD KEY `num_plano` (`num_plano`),
  ADD KEY `tipo_plano` (`tipo_plano`),
  ADD KEY `tamanio` (`tamanio`);

--
-- Indices de la tabla `tamanio`
--
ALTER TABLE `tamanio`
  ADD PRIMARY KEY (`id_tamanio`);

--
-- Indices de la tabla `tipo_plano`
--
ALTER TABLE `tipo_plano`
  ADD PRIMARY KEY (`id_tplano`);

--
-- Indices de la tabla `version`
--
ALTER TABLE `version`
  ADD PRIMARY KEY (`id_version`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `archivos`
--
ALTER TABLE `archivos`
  MODIFY `id_archivos` int(10) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `num_plano`
--
ALTER TABLE `num_plano`
  MODIFY `id_num_plano` int(10) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `planos`
--
ALTER TABLE `planos`
  MODIFY `id_plano` int(10) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tamanio`
--
ALTER TABLE `tamanio`
  MODIFY `id_tamanio` int(2) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tipo_plano`
--
ALTER TABLE `tipo_plano`
  MODIFY `id_tplano` int(3) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `version`
--
ALTER TABLE `version`
  MODIFY `id_version` int(2) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `planos`
--
ALTER TABLE `planos`
  ADD CONSTRAINT `planos_ibfk_1` FOREIGN KEY (`version`) REFERENCES `version` (`id_version`),
  ADD CONSTRAINT `planos_ibfk_2` FOREIGN KEY (`archivo`) REFERENCES `archivos` (`id_archivos`),
  ADD CONSTRAINT `planos_ibfk_3` FOREIGN KEY (`num_plano`) REFERENCES `num_plano` (`id_num_plano`),
  ADD CONSTRAINT `planos_ibfk_4` FOREIGN KEY (`tipo_plano`) REFERENCES `tipo_plano` (`id_tplano`),
  ADD CONSTRAINT `planos_ibfk_5` FOREIGN KEY (`tamanio`) REFERENCES `tamanio` (`id_tamanio`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
