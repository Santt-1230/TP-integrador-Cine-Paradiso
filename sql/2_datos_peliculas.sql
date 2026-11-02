
/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

/*!40000 ALTER TABLE `generos` DISABLE KEYS */;
INSERT  IGNORE INTO `generos` (`id_genero`, `nombre`) VALUES (1,'Acción');
INSERT  IGNORE INTO `generos` (`id_genero`, `nombre`) VALUES (6,'Aventura');
INSERT  IGNORE INTO `generos` (`id_genero`, `nombre`) VALUES (2,'Ciencia ficción');
INSERT  IGNORE INTO `generos` (`id_genero`, `nombre`) VALUES (13,'Comedia');
INSERT  IGNORE INTO `generos` (`id_genero`, `nombre`) VALUES (5,'Crimen');
INSERT  IGNORE INTO `generos` (`id_genero`, `nombre`) VALUES (7,'Drama');
INSERT  IGNORE INTO `generos` (`id_genero`, `nombre`) VALUES (10,'Suspense');
/*!40000 ALTER TABLE `generos` ENABLE KEYS */;

/*!40000 ALTER TABLE `peliculas` DISABLE KEYS */;
INSERT  IGNORE INTO `peliculas` (`id_pelicula`, `id_externo`, `nombre`, `sinopsis`, `poster_url`, `duracion_min`, `clasificacion`, `cartelera_desde`, `cartelera_hasta`, `activo`) VALUES (1,'603','Matrix','Thomas Anderson lleva una doble vida: por el día es programador en una importante empresa de software, y por la noche un hacker informático llamado Neo. Su vida no volverá a ser igual cuando unos misteriosos personajes le inviten a descubrir la respuesta a la pregunta que no le deja dormir: ¿qué es Matrix?','https://image.tmdb.org/t/p/w500/tpW2X2DvxtTHJ61iJ7zNYYrJihs.jpg',138,'+13','2026-10-31','2027-12-31',1);
INSERT  IGNORE INTO `peliculas` (`id_pelicula`, `id_externo`, `nombre`, `sinopsis`, `poster_url`, `duracion_min`, `clasificacion`, `cartelera_desde`, `cartelera_hasta`, `activo`) VALUES (2,'27205','Origen','Dom Cobb es un ladrón hábil, el mejor de todos, especializado en el peligroso arte de extracción: el robo de secretos valiosos desde las profundidades del subconsciente durante el estado de sueño cuando la mente está más vulnerable. Esta habilidad excepcional de Cobb le ha hecho un jugador codiciado en el traicionero nuevo mundo de espionaje corporativo, pero al mismo tiempo, le ha convertido en un fugitivo internacional y ha tenido que sacrificar todo que le importaba. Ahora a Cobb se le ofrece una oportunidad para redimirse. Con un último trabajo podría recuperar su vida anterior, pero solamente si logra lo imposible.','https://image.tmdb.org/t/p/w500/tXQvtRWfkUUnWJAn2tN3jERIUG.jpg',148,'+13','2026-10-31','2027-12-31',1);
INSERT  IGNORE INTO `peliculas` (`id_pelicula`, `id_externo`, `nombre`, `sinopsis`, `poster_url`, `duracion_min`, `clasificacion`, `cartelera_desde`, `cartelera_hasta`, `activo`) VALUES (3,'157336','Interstellar','Un grupo de exploradores hacen uso de un agujero de gusano recientemente descubierto para superar las limitaciones de los viajes espaciales tripulados y vencer las inmensas distancias que tiene un viaje interestelar.','https://image.tmdb.org/t/p/w500/d1QKiYtceF3GDtxvTFXFAqwwah9.jpg',169,'+13','2026-10-31','2027-12-31',1);
INSERT  IGNORE INTO `peliculas` (`id_pelicula`, `id_externo`, `nombre`, `sinopsis`, `poster_url`, `duracion_min`, `clasificacion`, `cartelera_desde`, `cartelera_hasta`, `activo`) VALUES (4,'550','El club de la lucha','Un hombre consumido por el insomnio y una vida sin sentido conoce a Tyler Durden, un carismático anarquista que lo arrastra a un club secreto donde el dolor despierta algo dormido. Lo que comienza como liberación pronto se convierte en una guerra contra el sistema…','https://image.tmdb.org/t/p/w500/sgTAWJFaB2kBvdQxRGabYFiQqEK.jpg',139,'+18','2026-10-31','2027-12-31',1);
INSERT  IGNORE INTO `peliculas` (`id_pelicula`, `id_externo`, `nombre`, `sinopsis`, `poster_url`, `duracion_min`, `clasificacion`, `cartelera_desde`, `cartelera_hasta`, `activo`) VALUES (5,'680','Pulp Fiction','Jules y Vincent, dos asesinos a sueldo con muy pocas luces, trabajan para Marsellus Wallace. Vincent le confiesa a Jules que Marsellus le ha pedido que cuide de Mia, su mujer. Jules le recomienda prudencia porque es muy peligroso sobrepasarse con la novia del jefe. Cuando llega la hora de trabajar, ambos deben ponerse manos a la obra. Su misión: recuperar un misterioso maletín.','https://image.tmdb.org/t/p/w500/hNcQAuquJxTxl2fJFs1R42DrWcf.jpg',154,'+18','2026-10-31','2027-12-31',1);
INSERT  IGNORE INTO `peliculas` (`id_pelicula`, `id_externo`, `nombre`, `sinopsis`, `poster_url`, `duracion_min`, `clasificacion`, `cartelera_desde`, `cartelera_hasta`, `activo`) VALUES (6,'155','El caballero oscuro','Batman/Bruce Wayne regresa para continuar su guerra contra el crimen. Con la ayuda del teniente Jim Gordon y del Fiscal del Distrito Harvey Dent, Batman se propone destruir el crimen organizado en la ciudad de Gotham. El triunvirato demuestra su eficacia, pero, de repente, aparece Joker, un nuevo criminal que desencadena el caos y tiene aterrados a los ciudadanos.','https://image.tmdb.org/t/p/w500/8QDQExnfNFOtabLDKqfDQuHDsIg.jpg',152,'+13','2026-10-31','2027-12-31',1);
/*!40000 ALTER TABLE `peliculas` ENABLE KEYS */;

/*!40000 ALTER TABLE `pelicula_genero` DISABLE KEYS */;
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (1,1);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (2,1);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (6,1);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (1,2);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (2,2);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (3,2);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (2,5);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (5,5);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (6,5);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (3,6);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (3,7);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (4,7);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (4,10);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (5,10);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (6,10);
INSERT  IGNORE INTO `pelicula_genero` (`id_pelicula`, `id_genero`) VALUES (5,13);
/*!40000 ALTER TABLE `pelicula_genero` ENABLE KEYS */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

