CREATE DATABASE  IF NOT EXISTS `mydb` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `mydb`;


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
DROP TABLE IF EXISTS `Device`;
CREATE TABLE `Device` (
  `deviceId` varchar(255) NOT NULL,
  `relay` varchar(10) DEFAULT NULL,
  `pubKey` varchar(255) NOT NULL,
  `ifaceType` varchar(10) NOT NULL,
  `hwAddress` varchar(17) DEFAULT NULL,
  `ipv4` varchar(15) DEFAULT NULL,
  `wifiSSID` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`deviceId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = 'utf8' */;

DROP TABLE IF EXISTS `Neighbor`;
CREATE TABLE `Neighbor` (
  `neighborId` varchar(255) NOT NULL,
  `deviceId` varchar(255) NOT NULL,
  `neighborIface` varchar(10) NOT NULL,
  `neighborIpv4` varchar(15) DEFAULT NULL,
  `neighborHwAddress` varchar(17) DEFAULT NULL,
  PRIMARY KEY (`neighborId`),
  KEY `deviceId_idx` (`deviceId`),
  CONSTRAINT `deviceId` FOREIGN KEY (`deviceId`) REFERENCES `Device` (`deviceId`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = 'utf8' */;

DROP TABLE IF EXISTS `QosRequirements`;
CREATE TABLE `QosRequirements` (
  `qosId` varchar(10) NOT NULL DEFAULT '',
  `deviceId` varchar(255) NOT NULL DEFAULT '',
  `providingId` varchar(20) NOT NULL,
  `metricName` varchar(20) DEFAULT NULL,
  `metricUnit` varchar(20) DEFAULT NULL,
  `metricValue` varchar(20) DEFAULT NULL,
  `metricOperator` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`qosId`),
  KEY `deviceId_qr_idx` (`deviceId`),
  KEY `providingId_idx` (`providingId`),
  CONSTRAINT `deviceId_qr` FOREIGN KEY (`deviceId`) REFERENCES `Device` (`deviceId`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `providingId` FOREIGN KEY (`providingId`) REFERENCES `RegisterList` (`providingId`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = 'utf8' */;

DROP TABLE IF EXISTS `RegisterList`;
CREATE TABLE `RegisterList` (
  `providingId` varchar(255) NOT NULL,
  `deviceId` varchar(255) NOT NULL DEFAULT '',
  `hash` varchar(15) NOT NULL,
  `registerType` varchar(15) NOT NULL,
  `category` varchar(15) NOT NULL,
  `attr1` varchar(50) DEFAULT NULL,
  `attr2` varchar(50) DEFAULT '.',
  `attr3` varchar(50) DEFAULT '.',
  PRIMARY KEY (`providingId`,`deviceId`),
  KEY `deviceId_rl_idx` (`deviceId`),
  CONSTRAINT `deviceId1` FOREIGN KEY (`deviceId`) REFERENCES `Device` (`deviceId`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = 'utf8' */;

DROP TABLE IF EXISTS `GroupList`;
CREATE TABLE `GroupList` (
  `groupId` varchar(255) NOT NULL,
  `attr1` varchar(50) DEFAULT NULL,
  `attr2` varchar(50) DEFAULT NULL,
  `attr3` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`groupId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = 'utf8' */;

DROP TABLE IF EXISTS `GroupMember`;
CREATE TABLE `GroupMember` (
  `groupId` varchar(255) NOT NULL,
  `memberId` varchar(255) NOT NULL,
  PRIMARY KEY (`groupId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = 'utf8' */;


/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

