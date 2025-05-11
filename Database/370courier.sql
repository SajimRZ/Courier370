-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 11, 2025 at 01:48 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `370courier`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `AdminID` int(10) NOT NULL,
  `name` varchar(30) NOT NULL,
  `email` varchar(20) NOT NULL,
  `password` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`AdminID`, `name`, `email`, `password`) VALUES
(1, 'Sajim', 'sajim@admin.com', 'sajimsajim'),
(2, 'Jawad', 'jawad@admin.com', 'jawad123'),
(4, 'bob prime', 'thebob@admin.com', 'bob');

-- --------------------------------------------------------

--
-- Table structure for table `courier`
--

CREATE TABLE `courier` (
  `UID` int(10) NOT NULL,
  `name` varchar(30) NOT NULL,
  `city` varchar(20) NOT NULL,
  `licenseNo` varchar(10) NOT NULL,
  `type` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `courier`
--

INSERT INTO `courier` (`UID`, `name`, `city`, `licenseNo`, `type`) VALUES
(1003, 'aa', 'bbbb', 'aa', 'motorcyle'),
(1004, 'courier', 'Dhaka', '164235', 'motorcycle'),
(1006, 'cat', 'Khulna', '123', 'motorcycle'),
(1007, 'dog', 'Dhaka', '1234', 'pickup truck');

-- --------------------------------------------------------

--
-- Table structure for table `customer`
--

CREATE TABLE `customer` (
  `UID` int(10) NOT NULL,
  `houseNo` varchar(20) NOT NULL,
  `road` varchar(20) NOT NULL,
  `city` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `customer`
--

INSERT INTO `customer` (`UID`, `houseNo`, `road`, `city`) VALUES
(1001, '5/2', 'Monipur', 'Dhaka'),
(1002, 'ss', 'ss', 'ss'),
(1005, '15', 'Uttara', '9');

-- --------------------------------------------------------

--
-- Table structure for table `package`
--

CREATE TABLE `package` (
  `PackageID` varchar(10) NOT NULL,
  `S_houseNo` varchar(20) NOT NULL,
  `S_street` varchar(20) NOT NULL,
  `S_city` varchar(20) NOT NULL,
  `D_houseNo` varchar(20) NOT NULL,
  `D_street` varchar(20) NOT NULL,
  `D_city` varchar(20) NOT NULL,
  `type` varchar(20) NOT NULL,
  `status` varchar(20) NOT NULL,
  `WarehouseID` varchar(10) NOT NULL,
  `CourierID` int(4) NOT NULL,
  `CustomerID` int(4) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `package`
--

INSERT INTO `package` (`PackageID`, `S_houseNo`, `S_street`, `S_city`, `D_houseNo`, `D_street`, `D_city`, `type`, `status`, `WarehouseID`, `CourierID`, `CustomerID`) VALUES
('9', '5/2', 'Monipur', 'Dhaka', '66', 'Uttara', 'Dhaka', 'local', 'unconfirmed', '1', -1, 1001);

-- --------------------------------------------------------

--
-- Table structure for table `payment`
--

CREATE TABLE `payment` (
  `acc_number` varchar(10) NOT NULL,
  `amount` int(20) NOT NULL,
  `method` varchar(20) NOT NULL,
  `UID` int(10) NOT NULL,
  `purpose` varchar(20) NOT NULL,
  `PaymentID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `payment`
--

INSERT INTO `payment` (`acc_number`, `amount`, `method`, `UID`, `purpose`, `PaymentID`) VALUES
('222333', 160, 'credit_card', 1001, 'payment', 0),
('11', 160, 'credit_card', 1001, 'payment', 1);

-- --------------------------------------------------------

--
-- Table structure for table `pays`
--

CREATE TABLE `pays` (
  `CustomerID` int(10) NOT NULL,
  `PaymentID` varchar(10) NOT NULL,
  `OrderID` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `transfer`
--

CREATE TABLE `transfer` (
  `From_WH` varchar(10) NOT NULL,
  `To_WH` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `UID` int(10) NOT NULL,
  `email` varchar(20) NOT NULL,
  `name` varchar(30) NOT NULL,
  `password` varchar(10) NOT NULL,
  `phone` int(11) NOT NULL,
  `AdminID` int(10) DEFAULT NULL,
  `wallet` int(16) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`UID`, `email`, `name`, `password`, `phone`, `AdminID`, `wallet`) VALUES
(1001, 'reaz@gmail.com', 'Reaz', 'reaz123', 1842308890, 1, 999369),
(1002, 'sss@sss', 'sss', 'ss', 2147483647, 4, 0),
(1003, 'aa@aa', 'aaaaa', 'aa', 22, 1, 0),
(1004, 'courier@gmail.com', 'cour', '1234', 1234567890, 2, 320),
(1005, 'idur@gmail.com', 'Idur', '1234', 1234567890, 4, 0),
(1006, 'cat@gmail.com', 'cat', 'cat', 2147483647, 1, 160),
(1007, 'dog@gmail.com', 'dog', 'dog', 1111111111, 2, 320);

-- --------------------------------------------------------

--
-- Table structure for table `warehouse`
--

CREATE TABLE `warehouse` (
  `WarehouseID` varchar(10) NOT NULL,
  `Area` varchar(20) NOT NULL,
  `City` varchar(20) NOT NULL,
  `AdminID` int(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `warehouse`
--

INSERT INTO `warehouse` (`WarehouseID`, `Area`, `City`, `AdminID`) VALUES
('1', 'Tejgao', 'Dhaka', 2),
('2', 'Mirpur', 'Dhaka', 2),
('5', 'Greenroad', 'Khulna', 1),
('6', 'Badda', 'Dhaka', 1);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`AdminID`);

--
-- Indexes for table `courier`
--
ALTER TABLE `courier`
  ADD KEY `FK_UID_courier` (`UID`);

--
-- Indexes for table `customer`
--
ALTER TABLE `customer`
  ADD KEY `FK_UID` (`UID`);

--
-- Indexes for table `package`
--
ALTER TABLE `package`
  ADD PRIMARY KEY (`PackageID`),
  ADD KEY `WarehouseID` (`WarehouseID`);

--
-- Indexes for table `transfer`
--
ALTER TABLE `transfer`
  ADD KEY `From_WH` (`From_WH`),
  ADD KEY `To_WH` (`To_WH`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`UID`),
  ADD KEY `FK_adminID` (`AdminID`);

--
-- Indexes for table `warehouse`
--
ALTER TABLE `warehouse`
  ADD PRIMARY KEY (`WarehouseID`),
  ADD KEY `FK_adminID_w` (`AdminID`);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `courier`
--
ALTER TABLE `courier`
  ADD CONSTRAINT `FK_UID_courier` FOREIGN KEY (`UID`) REFERENCES `user` (`UID`);

--
-- Constraints for table `customer`
--
ALTER TABLE `customer`
  ADD CONSTRAINT `FK_UID` FOREIGN KEY (`UID`) REFERENCES `user` (`UID`);

--
-- Constraints for table `package`
--
ALTER TABLE `package`
  ADD CONSTRAINT `package_ibfk_1` FOREIGN KEY (`WarehouseID`) REFERENCES `warehouse` (`WarehouseID`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
