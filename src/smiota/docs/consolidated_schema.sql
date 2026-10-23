-- =============================================================================
-- Smiota Server - Consolidated Database Schema
-- Target Engine: MySQL 8.0+ / MariaDB 10.3+
-- Default Character Set: utf8mb4 | Collation: utf8mb4_unicode_ci
-- Scope: All migrations v26 to v223 + baseline DDL + stored routines
-- Generated: 2026-10-16
-- =============================================================================

SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';
SET NAMES utf8mb4;

-- -------------------------------------------------------------
-- Table structure for table `account`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `account`;
CREATE TABLE `account` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `LOGIN` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `PASSWORD` varchar(24) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `INACTIVE` tinyint(1) DEFAULT NULL,
  `SESSION_TIMEOUT` int DEFAULT NULL,
  `IS_LOCKED` tinyint(1) DEFAULT NULL,
  `IS_TEMPORARY_PASSWORD` tinyint(1) DEFAULT NULL,
  `temporary_password_expiration` timestamp NULL DEFAULT NULL,
  `CUSTOMER_ID` bigint DEFAULT NULL,
  `LAST_MODIFIED_TIME` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `LOCATION_ID` bigint DEFAULT NULL,
  `language_id` int DEFAULT NULL,
  `SECURITY_CARD_ID` bigint DEFAULT NULL,
  `ENABLE_PING` tinyint(1) DEFAULT NULL,
  `sync_required` tinyint(1) DEFAULT NULL,
  `NUM_LOGIN_RETRIES` int DEFAULT NULL,
  `LAST_FAILED_ATTEMPT` timestamp NULL DEFAULT NULL,
  `FORGOT_PASSWORD_CODE` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `FORGOT_PASSWORD_CODE_NUM_ATTEMPTS` int DEFAULT NULL,
  `FORGOT_PASSWORD_CODE_LAST_FAILED_TIMESTAMP` timestamp NULL DEFAULT NULL,
  `FORGOT_PASSWORD_CODE_EXPIRES` timestamp NULL DEFAULT NULL,
  `password_hash` varchar(1024) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `client_id` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `secret_hash` varchar(1024) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_deleted` tinyint(1) DEFAULT NULL,
  `uuid` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_E4` (`ID`),
  UNIQUE KEY `IDX_ACCOUNT` (`LOGIN`),
  KEY `FK_ACCOUNT_CUSTOMER_INDEX_E` (`CUSTOMER_ID`),
  KEY `FK_ACCOUNT_CARD_INDEX_E` (`SECURITY_CARD_ID`),
  KEY `fk_ACCOUNT_language_id` (`language_id`),
  CONSTRAINT `FK_ACCOUNT_CARD` FOREIGN KEY (`SECURITY_CARD_ID`) REFERENCES `security_card` (`ID`),
  CONSTRAINT `FK_ACCOUNT_CUSTOMER` FOREIGN KEY (`CUSTOMER_ID`) REFERENCES `customer` (`ID`),
  CONSTRAINT `fk_ACCOUNT_language_id` FOREIGN KEY (`language_id`) REFERENCES `language` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `action`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `action`;
CREATE TABLE `action` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `NAME` varchar(60) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_72` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `admin_dashboard_log`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `admin_dashboard_log`;
CREATE TABLE `admin_dashboard_log` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `modified_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `request_method` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `api_path` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `request_body` text COLLATE utf8mb4_unicode_ci,
  `result` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `idx_modified_time` (`modified_time`),
  KEY `fk_admin_dashboard_log_user_id_idx` (`user_id`),
  CONSTRAINT `fk_admin_dashboard_log_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `alternate_address`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `alternate_address`;
CREATE TABLE `alternate_address` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tag_id` int DEFAULT NULL,
  `building_id` bigint DEFAULT NULL,
  `unit_no` varchar(25) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_alt_address_tag_id` (`tag_id`),
  KEY `fk_alt_address_building_id` (`building_id`),
  CONSTRAINT `fk_alt_address_building_id` FOREIGN KEY (`building_id`) REFERENCES `building` (`ID`),
  CONSTRAINT `fk_alt_address_tag_id` FOREIGN KEY (`tag_id`) REFERENCES `tag` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='linked to tag.id reference to the Address to alternatively deliver a Package.  Needs the BUILDING.ID, perhaps USER.unit_no.';

-- -------------------------------------------------------------
-- Table structure for table `alternate_recipient`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `alternate_recipient`;
CREATE TABLE `alternate_recipient` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tag_id` int DEFAULT NULL,
  `recipient_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_template_tag_id` (`tag_id`),
  CONSTRAINT `fk_template_tag_id` FOREIGN KEY (`tag_id`) REFERENCES `tag` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='linked to tag.id and stores the reference to the User.ID will alternatively receive a Package instead of the actuat address to user.';

-- -------------------------------------------------------------
-- Table structure for table `api_result`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `api_result`;
CREATE TABLE `api_result` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `base_url` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `context_path` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `method` varchar(7) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `headers` varchar(2000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `request_data` varchar(2000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `request_data_type` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status_code` smallint DEFAULT NULL,
  `is_success` tinyint(1) DEFAULT NULL,
  `response_data` varchar(5000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `request_time` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `customer_id` bigint DEFAULT NULL,
  `location_id` bigint DEFAULT NULL,
  `last_retry_time` timestamp(3) NULL DEFAULT NULL,
  `retry` tinyint(1) DEFAULT '0',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `response_time` timestamp NULL DEFAULT NULL,
  `transaction_id` varchar(2000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_is_success_time_sent` (`is_success`,`request_time`),
  KEY `idx_customer_location` (`customer_id`,`location_id`),
  KEY `fk_api_result_location` (`location_id`),
  CONSTRAINT `fk_api_result_customer` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `fk_api_result_location` FOREIGN KEY (`location_id`) REFERENCES `location` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Save results of HTTP API requests.  Failed requests may be reattempted by reconstructing the request from this data.';

-- -------------------------------------------------------------
-- Table structure for table `app_ui`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `app_ui`;
CREATE TABLE `app_ui` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `auth_config`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `auth_config`;
CREATE TABLE `auth_config` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `sub_domain` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Sub domain set for a specific Customer used to identify an externally authenticated enabled client.  ie dubs.smiotaapps.com',
  `customer_id` bigint NOT NULL COMMENT 'The particular Customer that uses an external authentication service.',
  `location_id` bigint DEFAULT NULL,
  `tenant_id` bigint DEFAULT NULL,
  `idp_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'The ENTITY ID in SAML.  Unique String which identifies the Customer configured Identity Provider for external Auth Services. ie http://www.okta.com/exko3fu3vSNTXNgvY356',
  `auth_url` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'AuthServer endpoint for external login authentication; should be Smiota Auth Server.  ie https://auth-sandbox.smiotaapps.com:8443/auth-server/saml/login',
  `onboard_mode` int NOT NULL DEFAULT '0' COMMENT 'Indicates how a User is onboarded into the Smiota system.  See application UserOnboardModeEnum.',
  `inactive` bit(1) NOT NULL DEFAULT b'0',
  `created_by` bigint NOT NULL,
  `updated_by` bigint NOT NULL,
  `created_time` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `updated_time` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `disallow_password_login` tinyint(1) DEFAULT NULL,
  `uuid` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sub_domain` (`sub_domain`),
  UNIQUE KEY `unique_auth_config_customer_location_tenant` (`customer_id`,`location_id`,`tenant_id`),
  KEY `fk_auth_config_location_id` (`location_id`),
  KEY `fk_auth_config_tenant_id` (`tenant_id`),
  CONSTRAINT `fk_auth_config_customer_id` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `fk_auth_config_location_id` FOREIGN KEY (`location_id`) REFERENCES `location` (`ID`),
  CONSTRAINT `fk_auth_config_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenant` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Auth related configurations per Customer.  Location and Tenant information is defaulted on authenticated Users';

-- -------------------------------------------------------------
-- Table structure for table `beacon`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `beacon`;
CREATE TABLE `beacon` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `GLOBAL_ID` bigint DEFAULT NULL,
  `MINOR_ID` int DEFAULT NULL,
  `LOCKER_UNIT_ID` bigint DEFAULT NULL,
  `BUILDING_ID` bigint DEFAULT NULL,
  `LOCATION_ID` bigint DEFAULT NULL,
  `CUSTOMER_ID` bigint DEFAULT NULL,
  `UUID` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_74` (`ID`),
  KEY `FK_BEACON_LOCKER_UNIT_INDEX_7` (`LOCKER_UNIT_ID`),
  KEY `FK_BEACON_LOCATION_INDEX_7` (`LOCATION_ID`),
  KEY `FK_BEACON_GLOBAL_INDEX_7` (`GLOBAL_ID`),
  KEY `FK_BEACON_CUSTOMER_INDEX_7` (`CUSTOMER_ID`),
  CONSTRAINT `FK_BEACON_CUSTOMER` FOREIGN KEY (`CUSTOMER_ID`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_BEACON_GLOBAL` FOREIGN KEY (`GLOBAL_ID`) REFERENCES `beacon_global` (`ID`),
  CONSTRAINT `FK_BEACON_LOCATION` FOREIGN KEY (`LOCATION_ID`) REFERENCES `location` (`ID`),
  CONSTRAINT `FK_BEACON_LOCKER_UNIT` FOREIGN KEY (`LOCKER_UNIT_ID`) REFERENCES `locker_unit` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `beacon_global`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `beacon_global`;
CREATE TABLE `beacon_global` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `BEACON_UUID` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_D4` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `building`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `building`;
CREATE TABLE `building` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `NAME` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `INACTIVE` tinyint(1) DEFAULT NULL,
  `PHONE` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `EMAIL` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ADDRESS_LINE1` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ADDRESS_LINE2` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `CITY` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `POST_CODE` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `LOCATION_ID` bigint NOT NULL,
  `CUSTOMER_ID` bigint NOT NULL,
  `LAST_MODIFIED_TIME` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `external_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_receiving_hub` tinyint(1) DEFAULT NULL,
  `has_package_desk` tinyint(1) DEFAULT NULL,
  `HAS_PACKAGE_ROOM` tinyint(1) DEFAULT '0',
  `PACKAGE_ROOM_DISPLAY_NAME` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `PACKAGE_DOESNT_FIT_PACKAGE_LOCATION_MESSAGE_IN_EMAIL` varchar(250) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `MAILROOM_DISPLAY_NAME` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `OFFICE_HOURS` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `UUID` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_D9` (`ID`),
  KEY `FK_BUILDING_LOCATION_INDEX_D` (`LOCATION_ID`),
  KEY `FK_BUILDING_CUSTOMER_INDEX_D` (`CUSTOMER_ID`),
  CONSTRAINT `FK_BUILDING_CUSTOMER` FOREIGN KEY (`CUSTOMER_ID`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_BUILDING_LOCATION` FOREIGN KEY (`LOCATION_ID`) REFERENCES `location` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `client_app`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `client_app`;
CREATE TABLE `client_app` (
  `ID` int NOT NULL,
  `APPID` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `NAME` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `MIN_VERSION` double DEFAULT NULL,
  `DOWNLOAD_URL` varchar(1024) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `LAST_MODIFIED_TIME` timestamp NULL DEFAULT NULL,
  `DESCRIPTION` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_5E` (`ID`),
  UNIQUE KEY `IDX_CLIENT_APP` (`APPID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `config_props`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `config_props`;
CREATE TABLE `config_props` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(400) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `default_value` longtext COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `config_values`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `config_values`;
CREATE TABLE `config_values` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `config_props_id` bigint DEFAULT NULL,
  `value` varchar(2000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `customer_id` bigint DEFAULT NULL,
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` bigint DEFAULT NULL,
  `location_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_customer_id_customer_property_id` (`customer_id`,`location_id`,`config_props_id`),
  KEY `fk_config_values_user` (`user_id`),
  KEY `fk_config_values_config_props` (`config_props_id`),
  KEY `fk_config_values_location` (`location_id`),
  CONSTRAINT `fk_config_values_config_props` FOREIGN KEY (`config_props_id`) REFERENCES `config_props` (`id`),
  CONSTRAINT `fk_config_values_customer` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `fk_config_values_location` FOREIGN KEY (`location_id`) REFERENCES `location` (`ID`),
  CONSTRAINT `fk_config_values_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `country`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `country`;
CREATE TABLE `country` (
  `ID` int NOT NULL,
  `CODE` varchar(2) COLLATE utf8mb4_unicode_ci NOT NULL,
  `NAME` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_6` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `courier`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `courier`;
CREATE TABLE `courier` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `NAME` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `DISPLAY_NAME` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `DESCRIPTION` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ICON` blob,
  `COLOR` varchar(9) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_63` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `courier_user`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `courier_user`;
CREATE TABLE `courier_user` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `COURIER_ID` int DEFAULT NULL,
  `USER_ID` bigint DEFAULT NULL,
  `CUSTOMER_ID` bigint DEFAULT NULL,
  `CAN_PICK_UP_PACKAGES` tinyint(1) DEFAULT NULL,
  `label` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `IS_MASTER_COURIER` tinyint(1) DEFAULT NULL,
  `enable_outgoing_notification` tinyint(1) DEFAULT '0' COMMENT 'Helps to determine if a courier user can get a notification that has packages deposited by recipients which are to be picked up by couriers',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_2F` (`ID`),
  KEY `FK_COURIER_USER_COURIER_INDEX_2` (`COURIER_ID`),
  KEY `FK_COURIER_USER_USER_INDEX_2` (`USER_ID`),
  KEY `FK_COURIER_USER_CUSTOMER_INDEX_2` (`CUSTOMER_ID`),
  CONSTRAINT `FK_COURIER_USER_COURIER` FOREIGN KEY (`COURIER_ID`) REFERENCES `courier` (`ID`),
  CONSTRAINT `FK_COURIER_USER_CUSTOMER` FOREIGN KEY (`CUSTOMER_ID`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_COURIER_USER_USER` FOREIGN KEY (`USER_ID`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `customer`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `customer`;
CREATE TABLE `customer` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `NAME` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `PHONE` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `EMAIL` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `INACTIVE` tinyint(1) DEFAULT NULL,
  `COMMENTS` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `LAST_MODIFIED_TIME` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `ENABLE_PACKAGE_REMINDERS` tinyint(1) DEFAULT NULL,
  `ALLOW_RECIPIENTS_TO_SELF_RELEASE_PACKAGES` tinyint(1) DEFAULT NULL,
  `ENABLE_EXPIRED_PACKAGE_REMINDERS_FOR_ADMINS` tinyint(1) DEFAULT NULL,
  `UUID` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_test_customer` tinyint(1) DEFAULT NULL,
  `ADMIN_NOTIFICATIONS_PHONE` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `image_url` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `access_key` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `access_id` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `TWILIO_LONG_CODE` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `IDX_CUSTOMER` (`NAME`),
  UNIQUE KEY `PRIMARY_KEY_A2` (`ID`),
  UNIQUE KEY `idx_CUSTOMER_TWILIO_LONG_CODE` (`TWILIO_LONG_CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `customer_package_type`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `customer_package_type`;
CREATE TABLE `customer_package_type` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `PACKAGE_TYPE` int DEFAULT NULL,
  `REGEX` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `CUSTOMER_ID` bigint DEFAULT NULL,
  `LAST_MODIFIED_TIME` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `REMINDER_FREQUENCY_HOURS` int DEFAULT NULL,
  `EXPIRES_AFTER_HOURS` int DEFAULT NULL,
  `EXPIRED_EMAIL_MESSAGE_TEMPLATE` varchar(2000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `EXPIRED_PHONE_MESSAGE_TEMPLATE` varchar(2000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `LOCATION_ID` bigint DEFAULT NULL,
  `ORDINAL` smallint NOT NULL COMMENT 'Specifies the priority of a Type for Customer and Location. 1 is highest.',
  `INTERVAL_REMINDER_HOURS` int DEFAULT '48',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_4F` (`ID`),
  UNIQUE KEY `PACKAGE_TYPE` (`PACKAGE_TYPE`,`LOCATION_ID`,`CUSTOMER_ID`),
  KEY `FK_CUSTOMER_PACKAGE_TYPE_TYPE_INDEX_4` (`PACKAGE_TYPE`),
  KEY `FK_CUSTOMER_PACKAGE_TYPE_CUSTOMER_INDEX_4` (`CUSTOMER_ID`),
  KEY `CUSTOMER_PACKAGE_TYPE_LOCATION` (`LOCATION_ID`),
  CONSTRAINT `customer_package_type_ibfk_1` FOREIGN KEY (`LOCATION_ID`) REFERENCES `location` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `FK_CUSTOMER_PACKAGE_TYPE_CUSTOMER` FOREIGN KEY (`CUSTOMER_ID`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_CUSTOMER_PACKAGE_TYPE_TYPE` FOREIGN KEY (`PACKAGE_TYPE`) REFERENCES `package_type` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `data_purge_result`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `data_purge_result`;
CREATE TABLE `data_purge_result` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `customer_id` bigint NOT NULL,
  `start_time` timestamp NOT NULL,
  `end_time` timestamp NULL DEFAULT NULL,
  `settings_json` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `count_json` varchar(5000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `errors_json` varchar(5000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_test_run` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `fk_data_purge_result_customer_id_idx` (`customer_id`),
  CONSTRAINT `fk_data_purge_result_customer_id` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `data_purge_settings`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `data_purge_settings`;
CREATE TABLE `data_purge_settings` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `customer_id` bigint NOT NULL,
  `enable_data_purge` tinyint(1) DEFAULT NULL,
  `data_purge_months` int NOT NULL DEFAULT '36',
  `data_purge_frequency_id` smallint NOT NULL DEFAULT '6',
  `created_by` bigint DEFAULT NULL,
  `last_modified_by` bigint DEFAULT NULL,
  `created_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_modified_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `delete_courier_users` tinyint(1) DEFAULT NULL,
  `is_test_run` tinyint(1) DEFAULT NULL,
  `result_email` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `fk_data_purge_settings_customer_id_idx` (`customer_id`),
  KEY `fk_data_purge_settings_frequency_id_idx` (`data_purge_frequency_id`),
  KEY `fk_data_purge_settings_created_by_idx` (`created_by`),
  KEY `fk_data_purge_settings_last_modified_by_idx` (`last_modified_by`),
  CONSTRAINT `fk_data_purge_settings_created_by` FOREIGN KEY (`created_by`) REFERENCES `user` (`ID`),
  CONSTRAINT `fk_data_purge_settings_customer_id` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `fk_data_purge_settings_frequency_id` FOREIGN KEY (`data_purge_frequency_id`) REFERENCES `maint_frequency` (`ID`),
  CONSTRAINT `fk_data_purge_settings_last_modified_by` FOREIGN KEY (`last_modified_by`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `day_use_pod`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `day_use_pod`;
CREATE TABLE `day_use_pod` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `inactive` tinyint(1) DEFAULT NULL,
  `customer_id` bigint NOT NULL,
  `location_id` bigint DEFAULT NULL,
  `building_id` bigint DEFAULT NULL,
  `UUID` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `last_modified_time` timestamp NULL DEFAULT NULL,
  `updated_by` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `fk_pod_customer_id_idx` (`customer_id`),
  KEY `fk_pod_location_id_idx` (`location_id`),
  KEY `fk_pod_building_id_idx` (`building_id`),
  KEY `fk_pod_updated_by_user_idx` (`updated_by`),
  CONSTRAINT `fk_pod_building_id` FOREIGN KEY (`building_id`) REFERENCES `building` (`ID`),
  CONSTRAINT `fk_pod_customer_id` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `fk_pod_location_id` FOREIGN KEY (`location_id`) REFERENCES `location` (`ID`),
  CONSTRAINT `fk_pod_updated_by_user` FOREIGN KEY (`updated_by`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `delivery_building`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `delivery_building`;
CREATE TABLE `delivery_building` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `building_id` bigint DEFAULT NULL,
  `delivery_building_id` bigint DEFAULT NULL,
  `location_id` bigint DEFAULT NULL,
  `customer_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_delivery_building_building` (`building_id`),
  KEY `fk_delivery_building_delivery_building` (`delivery_building_id`),
  KEY `fk_delivery_building_location` (`location_id`),
  KEY `fk_delivery_building_customer` (`customer_id`),
  CONSTRAINT `fk_delivery_building_building` FOREIGN KEY (`building_id`) REFERENCES `building` (`ID`),
  CONSTRAINT `fk_delivery_building_customer` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `fk_delivery_building_delivery_building` FOREIGN KEY (`delivery_building_id`) REFERENCES `building` (`ID`),
  CONSTRAINT `fk_delivery_building_location` FOREIGN KEY (`location_id`) REFERENCES `location` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `device_type`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `device_type`;
CREATE TABLE `device_type` (
  `ID` int NOT NULL,
  `TYPE` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_2` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `distributor`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `distributor`;
CREATE TABLE `distributor` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `inactive` tinyint(1) DEFAULT NULL,
  `comments` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `last_modified_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `uuid` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `uuid_UNIQUE` (`uuid`),
  KEY `idx_DISTRIBUTOR` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `distributor_customer`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `distributor_customer`;
CREATE TABLE `distributor_customer` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `distributor_id` bigint NOT NULL,
  `customer_id` bigint NOT NULL,
  `created_by` bigint NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `fk_DISTRIBUTOR_CUSTOMER_distributor_id_idx_idx` (`distributor_id`),
  KEY `fk_DISTRIBUTOR_CUSTOMER_customer_id_idx_idx` (`customer_id`),
  KEY `fk_DISTRIBUTOR_CUSTOMER_created_by_idx_idx` (`created_by`),
  CONSTRAINT `fk_DISTRIBUTOR_CUSTOMER_created_by_idx` FOREIGN KEY (`created_by`) REFERENCES `user` (`ID`),
  CONSTRAINT `fk_DISTRIBUTOR_CUSTOMER_customer_id_idx` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `fk_DISTRIBUTOR_CUSTOMER_distributor_id_idx` FOREIGN KEY (`distributor_id`) REFERENCES `distributor` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `event`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `event`;
CREATE TABLE `event` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(256) COLLATE utf8mb4_unicode_ci NOT NULL,
  `display_name` varchar(256) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(512) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_modified_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by_user_id` bigint NOT NULL,
  `last_modified_by_user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_event_name` (`name`),
  KEY `FK_event_created_by_USER` (`created_by_user_id`),
  KEY `FK_event_last_modified_by_USER` (`last_modified_by_user_id`),
  CONSTRAINT `FK_event_created_by_USER` FOREIGN KEY (`created_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `FK_event_last_modified_by_USER` FOREIGN KEY (`last_modified_by_user_id`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `event_definition`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `event_definition`;
CREATE TABLE `event_definition` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `event_id` int NOT NULL,
  `max_value` decimal(5,2) DEFAULT NULL,
  `min_value` decimal(5,2) DEFAULT NULL,
  `eligible_time_for_event_to_generate` int DEFAULT NULL,
  `locker_id` bigint DEFAULT NULL,
  `locker_unit_controller_id` bigint DEFAULT NULL,
  `locker_unit_id` bigint DEFAULT NULL,
  `location_id` bigint NOT NULL,
  `customer_id` bigint NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_modified_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by_user_id` bigint NOT NULL,
  `last_modified_by_user_id` bigint NOT NULL,
  `locker_device_address_id` bigint DEFAULT NULL,
  `locker_device_type_id` bigint DEFAULT NULL,
  `inactive` bit(1) DEFAULT b'0',
  PRIMARY KEY (`id`),
  KEY `FK_event_definition_event` (`event_id`),
  KEY `FK_event_definition_LOCKER` (`locker_id`),
  KEY `FK_event_definition_LOCKER_UNIT_CONTROLLER` (`locker_unit_controller_id`),
  KEY `FK_event_definition_LOCKER_UNIT` (`locker_unit_id`),
  KEY `FK_event_definition_LOCATION` (`location_id`),
  KEY `FK_event_definition_CUSTOMER` (`customer_id`),
  KEY `FK_event_definition_created_by_USER` (`created_by_user_id`),
  KEY `FK_event_definition_last_modified_by_USER` (`last_modified_by_user_id`),
  KEY `FK_event_definition_locker_device_address` (`locker_device_address_id`),
  KEY `FK_event_definition_locker_device_type` (`locker_device_type_id`),
  CONSTRAINT `FK_event_definition_created_by_USER` FOREIGN KEY (`created_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `FK_event_definition_CUSTOMER` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_event_definition_event` FOREIGN KEY (`event_id`) REFERENCES `event` (`id`),
  CONSTRAINT `FK_event_definition_last_modified_by_USER` FOREIGN KEY (`last_modified_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `FK_event_definition_LOCATION` FOREIGN KEY (`location_id`) REFERENCES `location` (`ID`),
  CONSTRAINT `FK_event_definition_LOCKER` FOREIGN KEY (`locker_id`) REFERENCES `locker` (`ID`),
  CONSTRAINT `FK_event_definition_locker_device_address` FOREIGN KEY (`locker_device_address_id`) REFERENCES `locker_device_address` (`id`),
  CONSTRAINT `FK_event_definition_locker_device_type` FOREIGN KEY (`locker_device_type_id`) REFERENCES `locker_device_type` (`id`),
  CONSTRAINT `FK_event_definition_LOCKER_UNIT` FOREIGN KEY (`locker_unit_id`) REFERENCES `locker_unit` (`ID`),
  CONSTRAINT `FK_event_definition_LOCKER_UNIT_CONTROLLER` FOREIGN KEY (`locker_unit_controller_id`) REFERENCES `locker_unit_controller` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `event_definition_log`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `event_definition_log`;
CREATE TABLE `event_definition_log` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `event_definition_id` bigint NOT NULL,
  `event_id` int NOT NULL,
  `max_value` decimal(5,2) DEFAULT NULL,
  `min_value` decimal(5,2) DEFAULT NULL,
  `eligible_time_for_event_to_generate` int DEFAULT NULL,
  `locker_id` bigint DEFAULT NULL,
  `locker_unit_controller_id` bigint DEFAULT NULL,
  `locker_unit_id` bigint DEFAULT NULL,
  `location_id` bigint NOT NULL,
  `customer_id` bigint NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by_user_id` bigint NOT NULL,
  `locker_device_address_id` bigint DEFAULT NULL,
  `locker_device_type_id` bigint DEFAULT NULL,
  `inactive` bit(1) DEFAULT b'0',
  PRIMARY KEY (`id`),
  KEY `FK_event_definition_log_EVENT_DEFINITION` (`event_definition_id`),
  KEY `FK_event_definition_log_LOCKER` (`locker_id`),
  KEY `FK_event_definition_log_LOCKER_UNIT_CONTROLLER` (`locker_unit_controller_id`),
  KEY `FK_event_definition_log_LOCKER_UNIT` (`locker_unit_id`),
  KEY `FK_event_definition_log_LOCATION` (`location_id`),
  KEY `FK_event_definition_log_CUSTOMER` (`customer_id`),
  KEY `FK_event_definition_log_created_by_USER` (`created_by_user_id`),
  KEY `FK_event_definition_log_locker_device_address` (`locker_device_address_id`),
  KEY `FK_event_definition_log_locker_device_type` (`locker_device_type_id`),
  KEY `FK_event_definition_log_event` (`event_id`),
  CONSTRAINT `FK_event_definition_log_created_by_USER` FOREIGN KEY (`created_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `FK_event_definition_log_CUSTOMER` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_event_definition_log_event` FOREIGN KEY (`event_id`) REFERENCES `event` (`id`),
  CONSTRAINT `FK_event_definition_log_EVENT_DEFINITION` FOREIGN KEY (`event_definition_id`) REFERENCES `event_definition` (`id`),
  CONSTRAINT `FK_event_definition_log_LOCATION` FOREIGN KEY (`location_id`) REFERENCES `location` (`ID`),
  CONSTRAINT `FK_event_definition_log_LOCKER` FOREIGN KEY (`locker_id`) REFERENCES `locker` (`ID`),
  CONSTRAINT `FK_event_definition_log_locker_device_address` FOREIGN KEY (`locker_device_address_id`) REFERENCES `locker_device_address` (`id`),
  CONSTRAINT `FK_event_definition_log_locker_device_type` FOREIGN KEY (`locker_device_type_id`) REFERENCES `locker_device_type` (`id`),
  CONSTRAINT `FK_event_definition_log_LOCKER_UNIT` FOREIGN KEY (`locker_unit_id`) REFERENCES `locker_unit` (`ID`),
  CONSTRAINT `FK_event_definition_log_LOCKER_UNIT_CONTROLLER` FOREIGN KEY (`locker_unit_controller_id`) REFERENCES `locker_unit_controller` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `integration_parameter_value`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `integration_parameter_value`;
CREATE TABLE `integration_parameter_value` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `PARM` int DEFAULT NULL,
  `VALUE` varchar(5000) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `CUSTOMER_ID` bigint DEFAULT NULL,
  `LOCATION_ID` bigint DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `FK_INTEGRATION_PARAMETER_VALUE_PARM` (`PARM`),
  KEY `FK_INTEGRATION_PARAMETER_VALUE_CUSTOMER` (`CUSTOMER_ID`),
  KEY `FK_INTEGRATION_PARAMETER_VALUE_LOCATION` (`LOCATION_ID`),
  CONSTRAINT `FK_INTEGRATION_PARAMETER_VALUE_CUSTOMER` FOREIGN KEY (`CUSTOMER_ID`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_INTEGRATION_PARAMETER_VALUE_LOCATION` FOREIGN KEY (`LOCATION_ID`) REFERENCES `location` (`ID`),
  CONSTRAINT `FK_INTEGRATION_PARAMETER_VALUE_PARM` FOREIGN KEY (`PARM`) REFERENCES `integration_parmeter_definition` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `integration_parmeter_definition`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `integration_parmeter_definition`;
CREATE TABLE `integration_parmeter_definition` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `TYPE` int NOT NULL,
  `NAME` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `DESCRIPTION` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `FK_INTEGRATION_PARAMETER_TYPE` (`TYPE`),
  CONSTRAINT `FK_INTEGRATION_PARAMETER_TYPE` FOREIGN KEY (`TYPE`) REFERENCES `integration_type` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `integration_retry`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `integration_retry`;
CREATE TABLE `integration_retry` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `data` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `retrycount` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `integration_status`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `integration_status`;
CREATE TABLE `integration_status` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `TYPE` int DEFAULT NULL,
  `LAST_SYNC_TIME` timestamp NULL DEFAULT NULL,
  `LOCATION_ID` bigint DEFAULT NULL,
  `CUSTOMER_ID` bigint DEFAULT NULL,
  `number_updated` int DEFAULT NULL,
  `orders_updated` int DEFAULT NULL,
  `number_failed` int DEFAULT NULL,
  `details` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`ID`),
  KEY `FK_INTEGRATION_STATUS_LOCATION` (`LOCATION_ID`),
  KEY `FK_INTEGRATION_STATUS_CUSTOMER` (`CUSTOMER_ID`),
  CONSTRAINT `FK_INTEGRATION_STATUS_CUSTOMER` FOREIGN KEY (`CUSTOMER_ID`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_INTEGRATION_STATUS_LOCATION` FOREIGN KEY (`LOCATION_ID`) REFERENCES `location` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `integration_type`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `integration_type`;
CREATE TABLE `integration_type` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `NAME` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `DESCRIPTION` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `job_data`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `job_data`;
CREATE TABLE `job_data` (
  `id` int NOT NULL AUTO_INCREMENT,
  `job_status` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `response_json` longtext COLLATE utf8mb4_unicode_ci,
  `customer_id` bigint DEFAULT NULL,
  `location_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_JOB_DATA_customer_id` (`customer_id`),
  KEY `FK_JOB_DATA_location_id` (`location_id`),
  CONSTRAINT `FK_JOB_DATA_customer_id` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_JOB_DATA_location_id` FOREIGN KEY (`location_id`) REFERENCES `location` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `label_template_configs`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `label_template_configs`;
CREATE TABLE `label_template_configs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` int NOT NULL,
  `description` varchar(250) COLLATE utf8mb4_unicode_ci NOT NULL,
  `customer_id` bigint NOT NULL,
  `location_id` bigint DEFAULT NULL,
  `is_outbound` bit(1) DEFAULT b'0' COMMENT 'Flag to indicate if the template configurations are applicable for inbound or outbound. TRUE: for outbound, FALSE/NULL: for inbound',
  PRIMARY KEY (`id`),
  KEY `idx_label_template_configs_customer_location` (`customer_id`,`location_id`),
  KEY `fk_label_template_configs_location` (`location_id`),
  CONSTRAINT `fk_label_template_configs_customer` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `fk_label_template_configs_location` FOREIGN KEY (`location_id`) REFERENCES `location` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='This table is used to store the label property values like font style, margin left, margin top, line height, etc';

-- -------------------------------------------------------------
-- Table structure for table `language`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `language`;
CREATE TABLE `language` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` char(2) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ISO 639-1 language codes',
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_supported` tinyint NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `code_UNIQUE` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `location`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `location`;
CREATE TABLE `location` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `NAME` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `INACTIVE` tinyint(1) DEFAULT NULL,
  `PHONE` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `EMAIL` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ADDRESS_LINE1` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ADDRESS_LINE2` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `CITY` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `STATE_ID` int DEFAULT NULL,
  `COUNTRY_CODE` varchar(2) COLLATE utf8mb4_unicode_ci NOT NULL,
  `POST_CODE` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `language_id` int DEFAULT NULL,
  `PHONE_MESSAGE_TEMPLATE` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `EMAIL_MESSAGE_TEMPLATE` varchar(5000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `CUSTOMER_ID` bigint NOT NULL,
  `LAST_MODIFIED_TIME` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `ALLOWS_OUTBOUND_PACKAGES` tinyint(1) DEFAULT NULL,
  `TENANT_LABEL` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `TENANT_LABEL_PLURAL` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `external_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `DO_NOT_DISPLAY_UNIT_INFO` tinyint(1) DEFAULT NULL,
  `allow_in_app_editing` tinyint(1) DEFAULT NULL,
  `reply_to_email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'support@com' COMMENT 'Comma delimited String of emails set to notification email reply to.',
  `from_email` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `timezone` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `from_email_name` varchar(300) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `enable_package_doesnt_fit_feature` tinyint(1) DEFAULT NULL,
  `package_doesnt_fit_courier_message` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `package_doesnt_fit_recipient_message` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `time_zone_id` bigint DEFAULT NULL,
  `COURIER_LABEL` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `SEND_APP_NOTIFICATION` tinyint(1) DEFAULT NULL,
  `EXPECT_A_DELAY_MESSAGE` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'EXPECTING A DELAY?',
  `ADDITIONAL_MESSAGE_IN_EMAIL` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `NOTIFY_FOR_EVERY_SCAN` tinyint(1) DEFAULT '0',
  `ENABLE_OUTGOING_PACKAGE_DOESNT_FIT` tinyint(1) DEFAULT '0',
  `SUPPORT_EMAIL` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'support@com',
  `SUPPORT_PHONE` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '19252704321',
  `contact_message` varchar(1024) COLLATE utf8mb4_unicode_ci DEFAULT 'Have questions? Need help? Feel free to call us at <a href="tel:19253903022" style="text-decoration: none;color: grey;font-weight: bold;">(925)390-3022</a> or email us at <a href="mailto:help@com?Subject=Need%20help%20with%20locker" style="text-decoration: none;color: grey;font-weight: bold;">help@com</a>',
  `DELAY_IN_PICKUP_BODY_MESSAGE` varchar(512) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Hello, I will not be able to pick up my packages right away. I will be able to retrieve my package(s) by this date: MM/DD/YY.',
  `PACKAGE_DOESNT_FIT_MESSAGE_IN_EMAIL` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `MAILROOM_MESSAGE_IN_EMAIL` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `POD_DUPLICATE_NAME_MESSAGE` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `NOTIFY_PACKAGE_RELEASE` tinyint(1) DEFAULT '0',
  `PACKAGE_RELEASE_PHONE_MESSAGE_TEMPLATE` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `IS_BOPIS` tinyint(1) DEFAULT '0',
  `SPECIAL_STATUS_MESSAGE` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT 'Leave packages at employee''s desk.',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `cc_email` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Comma delimited String of emails set to notification email cc.',
  `courier_can_retrieve_expired_packages` tinyint(1) DEFAULT '1',
  `UUID` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `image_url` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_9F` (`ID`),
  KEY `FK_LOCATION_STATE_ID_INDEX_9` (`STATE_ID`),
  KEY `FK_LOCATION_CUSTOMER_ID_INDEX_9` (`CUSTOMER_ID`),
  KEY `FK_LOCATION_TIME_ZONE` (`time_zone_id`),
  KEY `fk_LOCATION_language_id` (`language_id`),
  CONSTRAINT `FK_LOCATION_CUSTOMER_ID` FOREIGN KEY (`CUSTOMER_ID`) REFERENCES `customer` (`ID`),
  CONSTRAINT `fk_LOCATION_language_id` FOREIGN KEY (`language_id`) REFERENCES `language` (`id`),
  CONSTRAINT `FK_LOCATION_STATE_ID` FOREIGN KEY (`STATE_ID`) REFERENCES `state` (`ID`),
  CONSTRAINT `FK_LOCATION_TIME_ZONE` FOREIGN KEY (`time_zone_id`) REFERENCES `time_zone` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `location_properties`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `location_properties`;
CREATE TABLE `location_properties` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `customer_id` bigint DEFAULT NULL,
  `location_id` bigint DEFAULT NULL,
  `frequency_id` smallint DEFAULT '1',
  `frequency_value` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `enable_package_reminder_recipient` tinyint(1) DEFAULT '0',
  `enable_package_reminder_admin` tinyint(1) DEFAULT '0',
  `enable_package_sent_back` tinyint(1) DEFAULT '0',
  `notify_sub_par_level_products` tinyint(1) DEFAULT '0',
  `pri_sla_start_time` varchar(5) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `pri_sla_end_time` varchar(5) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `std_sla_start_time` varchar(5) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `std_sla_end_time` varchar(5) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `enable_pack_notify_recipient` tinyint(1) DEFAULT '1',
  `is_package_group` tinyint(1) DEFAULT '0' COMMENT 'Represents packageGroup feature is enabled',
  `is_package_group_passcode` tinyint(1) DEFAULT NULL,
  `package_group_regex` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Contains regex for validating package group external id',
  `package_group_alphanumeric` tinyint(1) DEFAULT NULL,
  `package_group_min_length` int DEFAULT NULL,
  `package_group_max_length` int DEFAULT NULL,
  `package_group_retrieval_code_length` int DEFAULT NULL COMMENT 'Contains package group retrieval code length',
  `package_group_trim` tinyint(1) NOT NULL DEFAULT '0',
  `package_group_trim_front` int DEFAULT NULL,
  `package_group_trim_end` int DEFAULT NULL,
  `show_review_packages_option` bit(1) NOT NULL DEFAULT b'0',
  `show_package_delete_option` bit(1) NOT NULL DEFAULT b'0',
  `restricted_entry` bit(1) NOT NULL DEFAULT b'0',
  `package_arrival_mandatory` bit(1) NOT NULL DEFAULT b'0',
  `enable_attempted_to_deliver` bit(1) NOT NULL DEFAULT b'0',
  `has_mailroom` bit(1) NOT NULL DEFAULT b'0' COMMENT 'Enables web based Mailroom application feature for a Customer and Location.',
  `can_receive_packages_for_other_locations` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'When true the field will be used to receive packages for users who are part of different location and same customer',
  `is_external_scanner` bit(1) NOT NULL DEFAULT b'0' COMMENT 'Flag to indicate if the external scanner (when value = 1) or camera scanner (when value = 0) .',
  `enable_outbound_recipient_notification` tinyint(1) DEFAULT '0' COMMENT 'The field is used to send notifications to recipients when outbound packages are deposited. True: recipients should receive notifications.',
  `enable_outgoing_courier_user_notification` tinyint(1) DEFAULT '0' COMMENT 'Helps to determine if a courier user belonging to a location can get a notification that has packages deposited by recipients which are to be picked up by couriers',
  `package_passcode_generation` int DEFAULT '0' COMMENT 'Describes the validity of recipient/tenant passcode for a location. 0 represents default recipient/tenant passcode functionlity. Anything positive represents short-lived passcode generation feature is enabled and the value represents recipient/tenant passcode''s validity in days',
  `enable_passcode_download` bit(1) DEFAULT b'0',
  `is_enable_outbound_label_print` bit(1) NOT NULL DEFAULT b'0' COMMENT 'Flag to indicate if the outbound package label to be printed or not (0 -> no print, 1-> Print)',
  `is_require_outbound_signature` bit(1) NOT NULL DEFAULT b'0' COMMENT 'Flag to indicate if the signature required for outbound package or not (0 -> no sign required, 1-> sign required)',
  `is_network_printer` bit(1) NOT NULL DEFAULT b'0' COMMENT 'Flag to indicate if the printer is a network printer (when value = 1) or local printer (when value = 0) .',
  `printer_ip_address` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'IP Address of the printer',
  `can_talk_to_locker_unit` tinyint(1) DEFAULT '0',
  `package_num_subitems_min` smallint NOT NULL DEFAULT '0',
  `package_num_subitems_max` smallint DEFAULT '100',
  `use_dmy` tinyint(1) DEFAULT NULL,
  `ecommerce_flow` tinyint(1) DEFAULT NULL,
  `ui_skin_id` bigint NOT NULL DEFAULT '1',
  `is_user_registration_enabled` tinyint(1) DEFAULT '0',
  `unit_no_label` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `track_package_transactions` tinyint(1) DEFAULT '0',
  `package_transaction_timeout` int DEFAULT NULL,
  `cla_deposit_timeout` int DEFAULT NULL,
  `cla_retrieve_timeout` int DEFAULT NULL,
  `force_notifications` tinyint(1) DEFAULT NULL,
  `show_orders_with_recipient` tinyint(1) DEFAULT NULL,
  `it_flow` tinyint(1) DEFAULT '0',
  `integration_config` varchar(1024) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `enable_notification_unsubscribe` tinyint(1) DEFAULT NULL,
  `enable_temp_alert_voice_call` tinyint(1) DEFAULT NULL,
  `voice_call_default_phone` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `enable_shift_management` tinyint(1) DEFAULT NULL,
  `require_sso_on_urban_admin_login` tinyint(1) DEFAULT NULL,
  `mobile_sso_base_url` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `EMAIL_MAX_REMINDERS` int DEFAULT '0',
  `PHONE_MAX_REMINDERS` int DEFAULT '3',
  `ENFORCE_MAX_IF_ONLY_CONTACT_INFO` tinyint(1) DEFAULT '0',
  `show_user_passcode` tinyint DEFAULT NULL,
  `show_waiver_before_release` tinyint DEFAULT NULL,
  `waiver_urls` varchar(5000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `waiver_text` varchar(5000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ignore_duplicate_order_id` tinyint DEFAULT NULL,
  `mailroom_app_ui` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `mailroom_screen_saver_file` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `mailroom_screen_saver_mode` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `mailroom_screen_saver_animation_duration` int DEFAULT NULL,
  `mailroom_screen_saver_item_count` int DEFAULT NULL,
  `show_notifications_in_package_details` tinyint DEFAULT NULL,
  `allow_complex_courier_codes` tinyint DEFAULT NULL,
  `enable_expired_reminder_recipient` tinyint DEFAULT '0',
  `package_group_validate_locker_unit` tinyint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_key_customer_location` (`customer_id`,`location_id`),
  KEY `fk_location_properties_location` (`location_id`),
  KEY `fk_location_properties_maint_frequency` (`frequency_id`),
  KEY `fk_location_properties_ui_skin` (`ui_skin_id`),
  CONSTRAINT `fk_location_properties_customer` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `fk_location_properties_location` FOREIGN KEY (`location_id`) REFERENCES `location` (`ID`),
  CONSTRAINT `fk_location_properties_maint_frequency` FOREIGN KEY (`frequency_id`) REFERENCES `maint_frequency` (`ID`),
  CONSTRAINT `fk_location_properties_ui_skin` FOREIGN KEY (`ui_skin_id`) REFERENCES `ui_skin` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `location_role`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `location_role`;
CREATE TABLE `location_role` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `location_id` bigint NOT NULL,
  `role_id` int NOT NULL,
  `refresh_token_expiration_interval` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNIQUE_ROLE_ID_LOCATION_ID` (`location_id`,`role_id`),
  KEY `FK_LOCATION_ROLE_ROLE` (`role_id`),
  CONSTRAINT `location_role_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `location` (`ID`),
  CONSTRAINT `location_role_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `role` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `lock`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `lock`;
CREATE TABLE `lock` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `label` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `inactive` tinyint(1) DEFAULT NULL,
  `battery_percentage` tinyint(1) DEFAULT NULL,
  `passcode` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_wheelchair_accessible` tinyint(1) DEFAULT NULL,
  `serial` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `customer_id` bigint NOT NULL,
  `day_use_pod_id` bigint DEFAULT NULL,
  `UUID` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `assigned_to` bigint DEFAULT NULL,
  `last_modified_time` timestamp NULL DEFAULT NULL,
  `updated_by` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `fk_lock_customer_id_idx` (`customer_id`),
  KEY `fk_lock_pod_id_idx` (`day_use_pod_id`),
  KEY `fk_lock_assigned_to_user_idx` (`assigned_to`),
  KEY `fk_lock_updated_by_user_idx` (`updated_by`),
  CONSTRAINT `fk_lock_assigned_to_user` FOREIGN KEY (`assigned_to`) REFERENCES `user` (`ID`),
  CONSTRAINT `fk_lock_customer_id` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `fk_lock_pod_id` FOREIGN KEY (`day_use_pod_id`) REFERENCES `day_use_pod` (`id`),
  CONSTRAINT `fk_lock_updated_by_user` FOREIGN KEY (`updated_by`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `lock_codes`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `lock_codes`;
CREATE TABLE `lock_codes` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `lock_id` bigint NOT NULL,
  `passcode` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_id` bigint DEFAULT NULL,
  `time` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `fk_lock_codes_lock_id_idx` (`lock_id`),
  KEY `fk_lock_codes_user_id` (`user_id`),
  CONSTRAINT `fk_lock_codes_lock_id` FOREIGN KEY (`lock_id`) REFERENCES `lock` (`id`),
  CONSTRAINT `fk_lock_codes_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `locker`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `locker`;
CREATE TABLE `locker` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `INACTIVE` tinyint(1) DEFAULT NULL,
  `SIZE` int DEFAULT NULL,
  `RELAY_ID` int DEFAULT NULL,
  `note` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `IS_GATE_OPEN` tinyint(1) DEFAULT NULL,
  `IS_IN_ERROR_STATE` tinyint(1) DEFAULT NULL,
  `ERROR_MESSAGE` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `CUSTOMER_ID` bigint NOT NULL,
  `NAME` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `TYPE` int DEFAULT NULL,
  `UNIT_CONTROLLER_ID` bigint DEFAULT NULL,
  `STATUS_CODE` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `do_not_detect_presence` tinyint(1) DEFAULT NULL,
  `LAST_MODIFIED_TIME` datetime DEFAULT NULL,
  `USER_ID` bigint DEFAULT NULL,
  `locker_device_address_id` bigint DEFAULT NULL,
  `UUID` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_86` (`ID`),
  KEY `FK_LOCKER_UNIT_CONTROLLER_INDEX_8` (`UNIT_CONTROLLER_ID`),
  KEY `FK_LOCKER_CUSTOMER_INDEX_8` (`CUSTOMER_ID`),
  KEY `FK_LOCKER_TYPE_INDEX_8` (`TYPE`),
  KEY `FK_LOCKER_SIZE_INDEX_8` (`SIZE`),
  KEY `fk_locker_locker_device_address` (`locker_device_address_id`),
  CONSTRAINT `FK_LOCKER_CUSTOMER` FOREIGN KEY (`CUSTOMER_ID`) REFERENCES `customer` (`ID`),
  CONSTRAINT `fk_locker_locker_device_address` FOREIGN KEY (`locker_device_address_id`) REFERENCES `locker_device_address` (`id`),
  CONSTRAINT `FK_LOCKER_SIZE` FOREIGN KEY (`SIZE`) REFERENCES `locker_size` (`ID`),
  CONSTRAINT `FK_LOCKER_TYPE` FOREIGN KEY (`TYPE`) REFERENCES `locker_type` (`ID`),
  CONSTRAINT `FK_LOCKER_UNIT_CONTROLLER` FOREIGN KEY (`UNIT_CONTROLLER_ID`) REFERENCES `locker_unit_controller` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `locker_controller`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `locker_controller`;
CREATE TABLE `locker_controller` (
  `ID` int NOT NULL,
  `RELAY_ID` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `NAME` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `DESCRIPTION` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `TYPE` bigint DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_8` (`ID`),
  KEY `FK_LOCKER_CONTROLLER_TYPE` (`TYPE`),
  CONSTRAINT `FK_LOCKER_CONTROLLER_TYPE` FOREIGN KEY (`TYPE`) REFERENCES `locker_controller_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `locker_controller_type`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `locker_controller_type`;
CREATE TABLE `locker_controller_type` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `locker_device_address`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `locker_device_address`;
CREATE TABLE `locker_device_address` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `locker_unit_id` bigint NOT NULL,
  `locker_device_info_id` bigint NOT NULL,
  `address` bigint NOT NULL,
  `updated_by` bigint DEFAULT NULL,
  `inactive` tinyint(1) DEFAULT NULL,
  `modified_time` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  `baud_rate` int DEFAULT NULL COMMENT 'Column to store the locker baud rate',
  `status_code` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `temperature_unit_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `locker_device_info_address_name_unique` (`locker_unit_id`,`locker_device_info_id`,`address`,`name`),
  KEY `idx_locker_unit_id` (`locker_unit_id`),
  KEY `fk_locker_device_address_device_info` (`locker_device_info_id`),
  KEY `fk_locker_device_address_locker_unit` (`locker_unit_id`),
  KEY `fk_locker_device_address_updated_by_user` (`updated_by`),
  KEY `lda_temperature_unit_id` (`temperature_unit_id`),
  CONSTRAINT `fk_locker_device_address_device_info` FOREIGN KEY (`locker_device_info_id`) REFERENCES `locker_device_info` (`id`),
  CONSTRAINT `fk_locker_device_address_locker_unit` FOREIGN KEY (`locker_unit_id`) REFERENCES `locker_unit` (`ID`),
  CONSTRAINT `fk_locker_device_address_updated_by_user` FOREIGN KEY (`updated_by`) REFERENCES `user` (`ID`),
  CONSTRAINT `lda_temperature_unit_id` FOREIGN KEY (`temperature_unit_id`) REFERENCES `temperature_unit` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Locker device address configuration table.  The address definitions of devices in a Locker Unit are found here.';

-- -------------------------------------------------------------
-- Table structure for table `locker_device_address_info_settings`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `locker_device_address_info_settings`;
CREATE TABLE `locker_device_address_info_settings` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `locker_device_address_id` bigint NOT NULL,
  `locker_device_info_settings_id` bigint NOT NULL,
  `value` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_modified_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by_user_id` bigint NOT NULL,
  `last_modified_by_user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_locker_device_address_info_settings` (`locker_device_address_id`,`locker_device_info_settings_id`),
  KEY `FK_locker_device_address_info_settings_device_info_settings` (`locker_device_info_settings_id`),
  KEY `FK_locker_device_address_info_settings_created_by_USER` (`created_by_user_id`),
  KEY `FK_locker_device_address_info_settings_last_modified_by_USER` (`last_modified_by_user_id`),
  CONSTRAINT `FK_locker_device_address_info_settings_created_by_USER` FOREIGN KEY (`created_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `FK_locker_device_address_info_settings_device_info_settings` FOREIGN KEY (`locker_device_info_settings_id`) REFERENCES `locker_device_info_settings` (`id`),
  CONSTRAINT `FK_locker_device_address_info_settings_last_modified_by_USER` FOREIGN KEY (`last_modified_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `FK_locker_device_address_info_settings_locker_device_address` FOREIGN KEY (`locker_device_address_id`) REFERENCES `locker_device_address` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `locker_device_address_info_settings_log`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `locker_device_address_info_settings_log`;
CREATE TABLE `locker_device_address_info_settings_log` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `locker_device_address_info_settings_id` bigint NOT NULL,
  `value` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by_user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_locker_device_address_info_settings_log_address_info_settings` (`locker_device_address_info_settings_id`),
  KEY `FK_locker_device_address_info_settings_log_created_by_USER` (`created_by_user_id`),
  CONSTRAINT `FK_locker_device_address_info_settings_log_address_info_settings` FOREIGN KEY (`locker_device_address_info_settings_id`) REFERENCES `locker_device_address_info_settings` (`id`),
  CONSTRAINT `FK_locker_device_address_info_settings_log_created_by_USER` FOREIGN KEY (`created_by_user_id`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `locker_device_info`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `locker_device_info`;
CREATE TABLE `locker_device_info` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `model` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `locker_device_type_id` bigint NOT NULL,
  `inactive` tinyint(1) DEFAULT NULL,
  `modified_time` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  `manufacturer_id` int DEFAULT NULL COMMENT 'Column to store the locker manufacturer id',
  PRIMARY KEY (`id`),
  UNIQUE KEY `make_model_unique` (`model`),
  KEY `fk_locker_device_type_id` (`locker_device_type_id`),
  KEY `fk_locker_manufacturer_id` (`manufacturer_id`),
  CONSTRAINT `fk_locker_device_type_id` FOREIGN KEY (`locker_device_type_id`) REFERENCES `locker_device_type` (`id`),
  CONSTRAINT `fk_locker_manufacturer_id` FOREIGN KEY (`manufacturer_id`) REFERENCES `locker_manufacturer` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Provides information regarding a Locker device.  This includes the model, make, descrption, and locker_device_type.';

-- -------------------------------------------------------------
-- Table structure for table `locker_device_info_settings`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `locker_device_info_settings`;
CREATE TABLE `locker_device_info_settings` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `locker_device_info_id` bigint NOT NULL,
  `locker_device_settings_id` bigint NOT NULL,
  `default_value` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_modified_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by_user_id` bigint NOT NULL,
  `last_modified_by_user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_locker_device_info_settings` (`locker_device_settings_id`,`locker_device_info_id`),
  KEY `FK_locker_device_info_settings_locker_device_info` (`locker_device_info_id`),
  KEY `FK_locker_device_info_settings_created_by_USER` (`created_by_user_id`),
  KEY `FK_locker_device_info_settings_last_modified_by_USER` (`last_modified_by_user_id`),
  CONSTRAINT `FK_locker_device_info_settings_created_by_USER` FOREIGN KEY (`created_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `FK_locker_device_info_settings_last_modified_by_USER` FOREIGN KEY (`last_modified_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `FK_locker_device_info_settings_locker_device_info` FOREIGN KEY (`locker_device_info_id`) REFERENCES `locker_device_info` (`id`),
  CONSTRAINT `FK_locker_device_info_settings_locker_device_settings` FOREIGN KEY (`locker_device_settings_id`) REFERENCES `locker_device_settings` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `locker_device_settings`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `locker_device_settings`;
CREATE TABLE `locker_device_settings` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(256) COLLATE utf8mb4_unicode_ci NOT NULL,
  `display_name` varchar(256) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_locker_device_settings_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `locker_device_type`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `locker_device_type`;
CREATE TABLE `locker_device_type` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `inactive` tinyint(1) DEFAULT NULL,
  `modified_time` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_unique` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Describes the type of Locker device.  ie, refrigerator, freezer, etc.';

-- -------------------------------------------------------------
-- Table structure for table `locker_dimension`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `locker_dimension`;
CREATE TABLE `locker_dimension` (
  `ID` int NOT NULL,
  `NAME` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_7F` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `locker_manufacturer`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `locker_manufacturer`;
CREATE TABLE `locker_manufacturer` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `last_modified_time` datetime NOT NULL,
  `last_updated_by` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_locker_manufacturer_modified_by` (`last_updated_by`),
  CONSTRAINT `fk_locker_manufacturer_modified_by` FOREIGN KEY (`last_updated_by`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='this table is used to store the locker manufacturers names. in future can be extended to store the locker manufacturer address as well';

-- -------------------------------------------------------------
-- Table structure for table `locker_size`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `locker_size`;
CREATE TABLE `locker_size` (
  `ID` int NOT NULL,
  `DESCRIPTION` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `DIMENSION_ID` int DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_A6` (`ID`),
  KEY `FK_LOCKER_SIZE_DIMENSION_INDEX_A` (`DIMENSION_ID`),
  CONSTRAINT `FK_LOCKER_SIZE_DIMENSION` FOREIGN KEY (`DIMENSION_ID`) REFERENCES `locker_dimension` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `locker_type`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `locker_type`;
CREATE TABLE `locker_type` (
  `ID` int NOT NULL,
  `NAME` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `DESCRIPTION` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_A6CD` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `locker_unit`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `locker_unit`;
CREATE TABLE `locker_unit` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `NAME` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `INACTIVE` tinyint(1) DEFAULT NULL,
  `BUILDING_ID` bigint DEFAULT NULL,
  `CUSTOMER_ID` bigint NOT NULL,
  `LAST_MODIFIED_TIME` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `ACCOUNT_ID` bigint DEFAULT NULL,
  `BLUETOOTH_MAC_ADDRESS` varchar(25) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ip_address` varchar(130) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `port_number` int DEFAULT NULL,
  `STATUS_CODE` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `BTN_TENANT_LABEL` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `BTN_COURIER_LABEL` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `UPDATED_BY` bigint DEFAULT NULL,
  `UUID` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_A6C` (`ID`),
  KEY `FK_LOCKER_UNIT_ACCOUNT_INDEX_A` (`ACCOUNT_ID`),
  KEY `FK_LOCKER_UNIT_BUILDING_INDEX_A` (`BUILDING_ID`),
  KEY `FK_LOCKER_UNIT_CUSTOMER_INDEX_A` (`CUSTOMER_ID`),
  KEY `FK_LOCKER_UNIT_USER` (`UPDATED_BY`),
  CONSTRAINT `FK_LOCKER_UNIT_ACCOUNT` FOREIGN KEY (`ACCOUNT_ID`) REFERENCES `account` (`ID`),
  CONSTRAINT `FK_LOCKER_UNIT_BUILDING` FOREIGN KEY (`BUILDING_ID`) REFERENCES `building` (`ID`),
  CONSTRAINT `FK_LOCKER_UNIT_CUSTOMER` FOREIGN KEY (`CUSTOMER_ID`) REFERENCES `customer` (`ID`),
  CONSTRAINT `locker_unit_ibfk_1` FOREIGN KEY (`UPDATED_BY`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `locker_unit_config`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `locker_unit_config`;
CREATE TABLE `locker_unit_config` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `locker_unit_id` bigint NOT NULL,
  `is_allows_out_bound_packages` tinyint(1) DEFAULT NULL,
  `is_enable_package_doesnt_fit_feature` tinyint(1) DEFAULT NULL,
  `is_enable_outgoing_package_doesnt_fit` tinyint(1) DEFAULT NULL,
  `is_displays_unit_numbers` tinyint(1) DEFAULT NULL,
  `is_courier_auth` tinyint(1) DEFAULT NULL COMMENT 'Specifies if the app requires couriers to authenticate with a courier badge or code in order to use the locker',
  `is_recipient_confirmation` tinyint(1) DEFAULT NULL COMMENT 'Specifies if a confirmation window is displayed when a courier selects a recipient for deposit',
  `is_existing_packages` tinyint(1) DEFAULT NULL COMMENT 'Enables/Disables existing package feature for the urban app',
  `is_new_packages` tinyint(1) DEFAULT NULL COMMENT 'Enables/Disables depositing of new packages for the urban app',
  `is_pkg_info_page` tinyint(1) DEFAULT NULL COMMENT 'Enables/Disables the Scan/Package info page',
  `is_voice_alerts` tinyint(1) DEFAULT NULL COMMENT 'Enables/Disables voice alerts during locker use',
  `is_retrieve_all` tinyint(1) DEFAULT NULL COMMENT 'When active, this will cause all the lockers to open during the retrieval process',
  `is_external_package_flow` tinyint(1) DEFAULT NULL,
  `deposit_timeout_seconds` bigint DEFAULT NULL COMMENT 'In seconds, the time limit for a deposit transaction',
  `retrieve_timeout_seconds` bigint DEFAULT NULL COMMENT 'In second, the time limit for a retrieval transaction',
  `item_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'This name is used throughout the app to describe the item that is being deposited in the lockers.',
  `item_name_plural` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'This name is used throughout the app to describe the items that are being deposited in the lockers',
  `returns_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'This label is applied to the "Returns" button if a value is present.',
  `app_mode` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Specifies different app flows for different customer use cases. Retail customers require the home page of the app to be customer centric, etc.',
  `app_ui` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Generates ui that is custom to specific customers',
  `door_open_audio_mode` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Sets the type of audio that is played when locker doors are open',
  `screen_saver_file` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Specifies which screen saver file to use',
  `created_by` bigint NOT NULL,
  `updated_by` bigint NOT NULL,
  `created_time` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `updated_time` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `lockers_per_user` int DEFAULT NULL COMMENT 'Max number of Lockers for a specific User.',
  `packages_per_locker` int DEFAULT NULL COMMENT 'Max number of Packages for a specific Locker.',
  `user_external_id_select_from_list_users` tinyint(1) DEFAULT '0' COMMENT 'true: UrbanApp can use scanner to scan user''s external id to uniquely identify a user, false: the feature is disabled. Couriers should select a user from a list of users',
  `authenticate_recipient_flow` tinyint(1) DEFAULT '0' COMMENT 'true: UrbanApp enforces a constraint in recipient for a recipient has to authenticate to deposit a package., false: UrbanApp does not enforce a constraint in recipient flow for a recipient to deposit a package.',
  `courier_can_retrieve_expired_packages` tinyint(1) DEFAULT '1',
  `temperature_interval` int DEFAULT '10',
  `latitude` decimal(8,6) DEFAULT NULL,
  `longitude` decimal(9,6) DEFAULT NULL,
  `track_package_transactions` tinyint(1) DEFAULT '0',
  `existing_package_group` tinyint(1) DEFAULT NULL,
  `private_recipient_list` tinyint(1) DEFAULT '0',
  `hide_duplicate_users` tinyint(1) DEFAULT '0',
  `enable_light_settings` tinyint(1) DEFAULT NULL,
  `light_on_time` varchar(8) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `light_off_time` varchar(8) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `xxl_multi_package_max` int DEFAULT NULL,
  `retrieval_confirmation` tinyint(1) DEFAULT NULL,
  `backloading` tinyint(1) DEFAULT NULL,
  `satellite` tinyint(1) DEFAULT NULL,
  `recipient_email_cell_search` tinyint(1) DEFAULT NULL,
  `enable_setting_scanner` tinyint(1) DEFAULT NULL,
  `did_you_deposit` int DEFAULT NULL,
  `screen_saver_animation_duration` int DEFAULT NULL,
  `screen_saver_item_count` int DEFAULT NULL,
  `enable_remote_logging` tinyint(1) DEFAULT NULL,
  `skip_outbound_scan` tinyint(1) DEFAULT NULL,
  `allow_tablet_developer_settings` tinyint(1) DEFAULT NULL,
  `show_complete_unit_no` tinyint DEFAULT NULL,
  `enter_name_before_release` tinyint DEFAULT NULL,
  `recipient_search_only_name_and_unit` tinyint DEFAULT NULL,
  `disable_skip_scan` tinyint DEFAULT NULL,
  `enable_package_consolidation` tinyint DEFAULT NULL,
  `enable_scan_confirmation` tinyint DEFAULT NULL,
  `enable_rfid_support` tinyint DEFAULT NULL,
  `show_language_toggle` tinyint DEFAULT NULL,
  `disable_locker_location_display` tinyint DEFAULT NULL,
  `disable_onscreen_keyboard` tinyint DEFAULT NULL,
  `hide_text_fields_on_scan_page` tinyint DEFAULT NULL,
  `limit_to_single_deposit` tinyint DEFAULT NULL,
  `scan_badge_text` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `scan_package_text` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `scan_code_text` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `show_expired_option_in_deposit` tinyint DEFAULT NULL,
  `show_custom_scan_messages` tinyint DEFAULT NULL,
  `done_timeout_seconds` int DEFAULT NULL,
  `done_button_label` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `locker_unit_id` (`locker_unit_id`),
  KEY `config_locker_unit_id_index` (`locker_unit_id`),
  CONSTRAINT `fk_config_locker_unit` FOREIGN KEY (`locker_unit_id`) REFERENCES `locker_unit` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Configuration settings for LockerUnits.  There should be at most one record associated with one LockerUnit.  Primarily used for Urban App.';

-- -------------------------------------------------------------
-- Table structure for table `locker_unit_controller`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `locker_unit_controller`;
CREATE TABLE `locker_unit_controller` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `LOCKER_UNIT_ID` bigint DEFAULT NULL,
  `LOCKER_CONTROLLER_ID` int DEFAULT NULL,
  `CUSTOMER_ID` bigint NOT NULL,
  `IP_ADDRESS` varchar(25) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'IP address for locker bank, created originally for Zhilia.',
  `PORT_NUM` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Port number for locker bank, created originally for Zhilia.',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_EE` (`ID`),
  UNIQUE KEY `UNIQUE_LOCKER_UNIT_ID_CONTROLLER_ID` (`LOCKER_UNIT_ID`,`LOCKER_CONTROLLER_ID`),
  KEY `FK_LOCKER_UNIT_CONTROLLER_UNIT_INDEX_E` (`LOCKER_UNIT_ID`),
  KEY `FK_LOCKER_UNIT_CONTROLLER_CUSTOMER_INDEX_E` (`CUSTOMER_ID`),
  KEY `FK_LOCKER_UNIT_CONTROLLER_CONTROLLER_INDEX_E` (`LOCKER_CONTROLLER_ID`),
  CONSTRAINT `FK_LOCKER_UNIT_CONTROLLER_CONTROLLER` FOREIGN KEY (`LOCKER_CONTROLLER_ID`) REFERENCES `locker_controller` (`ID`),
  CONSTRAINT `FK_LOCKER_UNIT_CONTROLLER_CUSTOMER` FOREIGN KEY (`CUSTOMER_ID`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_LOCKER_UNIT_CONTROLLER_UNIT` FOREIGN KEY (`LOCKER_UNIT_ID`) REFERENCES `locker_unit` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `locker_wallpapers`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `locker_wallpapers`;
CREATE TABLE `locker_wallpapers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'NOT TO BE MODIFIED - internally used name.',
  `display_name` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Name for display usages, can be edited.',
  `url` varchar(256) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Required URL to the hosted image file.',
  `customer_id` bigint DEFAULT NULL COMMENT 'ID of Customer which this wallpaper is available for.  NULL indicates available to all.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_locker_wallpapers_name` (`name`),
  KEY `fk_locker_wallpaper_customer_idx` (`customer_id`),
  CONSTRAINT `fk_locker_wallpaper_customer` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Contains the various available wallpapers for the Urban application running on Lockers.';

-- -------------------------------------------------------------
-- Table structure for table `magic_box`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `magic_box`;
CREATE TABLE `magic_box` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `account_id` bigint DEFAULT NULL,
  `locker_unit_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_MAGIC_BOX_ACCOUNT` (`account_id`),
  KEY `FK_MAGIC_BOX_LOCKER_UNIT` (`locker_unit_id`),
  CONSTRAINT `FK_MAGIC_BOX_ACCOUNT` FOREIGN KEY (`account_id`) REFERENCES `account` (`ID`),
  CONSTRAINT `FK_MAGIC_BOX_LOCKER_UNIT` FOREIGN KEY (`locker_unit_id`) REFERENCES `locker_unit` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `mail_template`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `mail_template`;
CREATE TABLE `mail_template` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` varchar(250) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `mail_content` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `customer_id` int DEFAULT NULL,
  `location_id` int DEFAULT NULL,
  `status_id` int NOT NULL,
  `to_recipient` bit(1) DEFAULT NULL,
  `to_location_admin` bit(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `mail_template_mails_assignment`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `mail_template_mails_assignment`;
CREATE TABLE `mail_template_mails_assignment` (
  `mail_template_id` int NOT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  KEY `fk_mail_templte_id1_idx` (`mail_template_id`),
  CONSTRAINT `fk_mail_templte_id1` FOREIGN KEY (`mail_template_id`) REFERENCES `mail_template` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `mail_template_recipient_assignment`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `mail_template_recipient_assignment`;
CREATE TABLE `mail_template_recipient_assignment` (
  `mail_template_id` int NOT NULL,
  `recipient_id` bigint NOT NULL,
  KEY `fk_mail_template_recipient_idx` (`recipient_id`),
  KEY `fk_mail_template_id_idx` (`mail_template_id`),
  CONSTRAINT `fk_mail_template_id` FOREIGN KEY (`mail_template_id`) REFERENCES `mail_template` (`id`),
  CONSTRAINT `fk_mail_template_recipient` FOREIGN KEY (`recipient_id`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `maint_frequency`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `maint_frequency`;
CREATE TABLE `maint_frequency` (
  `ID` smallint NOT NULL,
  `NAME` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `DESCRIPTION` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `UNIQUE_NAME` (`NAME`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Defines the specific range of days or specific day(s) for services to be completed.';

-- -------------------------------------------------------------
-- Table structure for table `maint_location`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `maint_location`;
CREATE TABLE `maint_location` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `NAME` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `INACTIVE` tinyint(1) NOT NULL DEFAULT '0',
  `CUSTOMER_ID` bigint NOT NULL,
  `LOCATION_ID` bigint NOT NULL,
  `BUILDING_ID` bigint NOT NULL,
  `MAINT_TYPE_ID` bigint NOT NULL,
  `TIME_ZONE_ID` bigint NOT NULL,
  `UPDATED_BY` bigint NOT NULL,
  `MODIFIED_TIME` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  `EXTERNAL_ID` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `CREATED_TIME` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `CREATED_BY` bigint DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `MAINT_LOCATION_UNIQUE` (`NAME`,`MAINT_TYPE_ID`,`CUSTOMER_ID`,`LOCATION_ID`,`BUILDING_ID`),
  UNIQUE KEY `EXTERNAL_ID_UNIQUE` (`CUSTOMER_ID`,`LOCATION_ID`,`EXTERNAL_ID`),
  KEY `IDX_CUSTOMER_ID_LOCATION_ID_BUILDING_ID` (`CUSTOMER_ID`,`LOCATION_ID`,`BUILDING_ID`),
  KEY `FK_MAINT_LOCATION_CUSTOMER_ID` (`CUSTOMER_ID`),
  KEY `FK_MAINT_LOCATION_LOCATION_ID` (`LOCATION_ID`),
  KEY `FK_MAINT_LOCATION_BUILDING_ID` (`BUILDING_ID`),
  KEY `FK_MAINT_LOCATION_MAINT_TYPE_ID` (`MAINT_TYPE_ID`),
  KEY `FK_MAINT_LOCATION_TIME_ZONE_ID` (`TIME_ZONE_ID`),
  KEY `FK_MAINT_LOCATION_UPDATED_BY` (`UPDATED_BY`),
  KEY `FK_MAINT_LOCATION_USER` (`CREATED_BY`),
  CONSTRAINT `FK_MAINT_LOCATION_BUILDING_ID` FOREIGN KEY (`BUILDING_ID`) REFERENCES `building` (`ID`),
  CONSTRAINT `FK_MAINT_LOCATION_CUSTOMER_ID` FOREIGN KEY (`CUSTOMER_ID`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_MAINT_LOCATION_LOCATION_ID` FOREIGN KEY (`LOCATION_ID`) REFERENCES `location` (`ID`),
  CONSTRAINT `FK_MAINT_LOCATION_MAINT_TYPE_ID` FOREIGN KEY (`MAINT_TYPE_ID`) REFERENCES `maint_type` (`ID`),
  CONSTRAINT `FK_MAINT_LOCATION_TIME_ZONE_ID` FOREIGN KEY (`TIME_ZONE_ID`) REFERENCES `time_zone` (`ID`),
  CONSTRAINT `FK_MAINT_LOCATION_UPDATED_BY` FOREIGN KEY (`UPDATED_BY`) REFERENCES `user` (`ID`),
  CONSTRAINT `maint_location_ibfk_1` FOREIGN KEY (`CREATED_BY`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Maintenance Locations which reside within a Building in a Location defined for a Customer.';

-- -------------------------------------------------------------
-- Table structure for table `maint_schedule`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `maint_schedule`;
CREATE TABLE `maint_schedule` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `MAINT_LOCATION_ID` bigint NOT NULL,
  `INACTIVE` tinyint(1) NOT NULL DEFAULT '0',
  `MAINT_FREQUENCY_ID` smallint NOT NULL,
  `MAINT_FREQUENCY_VALUE` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Comma delimited String of numbers representing days.',
  `START_TIME` time DEFAULT NULL COMMENT 'Optional, the minimum time per day expected for a service to be completed.',
  `END_TIME` time DEFAULT NULL COMMENT 'Optional, the maximum time per day expected for a service to be completed.',
  `CREATED_TIME` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `CREATED_BY` bigint NOT NULL,
  `MODIFIED_TIME` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `UPDATED_BY` bigint NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `IDX_MAINT_LOCATION` (`MAINT_LOCATION_ID`),
  KEY `FK_MAINT_SCHEDULE_MAINT_FREQUENCY` (`MAINT_FREQUENCY_ID`),
  KEY `FK_MAINT_SCHEDULE_CREATED_BY` (`CREATED_BY`),
  KEY `FK_MAINT_SCHEDULE_UPDATED_BY` (`UPDATED_BY`),
  CONSTRAINT `FK_MAINT_SCHEDULE_CREATED_BY` FOREIGN KEY (`CREATED_BY`) REFERENCES `user` (`ID`),
  CONSTRAINT `FK_MAINT_SCHEDULE_MAINT_FREQUENCY` FOREIGN KEY (`MAINT_FREQUENCY_ID`) REFERENCES `maint_frequency` (`ID`),
  CONSTRAINT `FK_MAINT_SCHEDULE_MAINT_LOCATION` FOREIGN KEY (`MAINT_LOCATION_ID`) REFERENCES `maint_location` (`ID`),
  CONSTRAINT `FK_MAINT_SCHEDULE_UPDATED_BY` FOREIGN KEY (`UPDATED_BY`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Specifies the expected frequency of services performed at a Maint Location.  Specifications are the basis for SLA reports.';

-- -------------------------------------------------------------
-- Table structure for table `maint_service`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `maint_service`;
CREATE TABLE `maint_service` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `MAINT_LOCATION_ID` bigint NOT NULL,
  `USER_ID` bigint NOT NULL,
  `START_DATE` timestamp(3) NULL DEFAULT NULL,
  `END_DATE` timestamp(3) NULL DEFAULT NULL,
  `NOTE` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `IS_COMPLETE` tinyint(1) NOT NULL DEFAULT '0',
  `UUID` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `IDX_MAINT_LOCATION_ID` (`MAINT_LOCATION_ID`),
  KEY `FK_MAINT_SERVICE_MAINT_LOCATION_ID` (`MAINT_LOCATION_ID`),
  KEY `FK_MAINT_SERVICE_USER_ID` (`USER_ID`),
  CONSTRAINT `FK_MAINT_SERVICE_MAINT_LOCATION_ID` FOREIGN KEY (`MAINT_LOCATION_ID`) REFERENCES `maint_location` (`ID`),
  CONSTRAINT `FK_MAINT_SERVICE_USER_ID` FOREIGN KEY (`USER_ID`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Maintenance Service represents a maintenance event for a Maintenance Location where user checks in and out after completing tasks.';

-- -------------------------------------------------------------
-- Table structure for table `maint_service_task`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `maint_service_task`;
CREATE TABLE `maint_service_task` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `MAINT_SERVICE_ID` bigint NOT NULL,
  `MAINT_TASK_ID` bigint NOT NULL,
  `NOTE` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `IS_COMPLETE` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `FK_MAINT_SERVICE_TASK_MAINT_SERVICE_ID` (`MAINT_SERVICE_ID`),
  KEY `FK_MAINT_SERVICE_TASK_MAINT_TASK_ID` (`MAINT_TASK_ID`),
  CONSTRAINT `FK_MAINT_SERVICE_TASK_MAINT_SERVICE_ID` FOREIGN KEY (`MAINT_SERVICE_ID`) REFERENCES `maint_service` (`ID`),
  CONSTRAINT `FK_MAINT_SERVICE_TASK_MAINT_TASK_ID` FOREIGN KEY (`MAINT_TASK_ID`) REFERENCES `maint_task` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Relationship table describing all Maintenance Tasks for a partiular Maintenance Service.  Includes the resulting state of a task and allows for custom notes or comments.';

-- -------------------------------------------------------------
-- Table structure for table `maint_service_task_product_inventory`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `maint_service_task_product_inventory`;
CREATE TABLE `maint_service_task_product_inventory` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `maint_service_task_id` bigint NOT NULL,
  `product_inventory_id` bigint NOT NULL,
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by_user_id` bigint NOT NULL,
  `last_modified_by_user_id` bigint NOT NULL,
  `last_modified_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_maint_service_task_product_inventory_created_user` (`created_by_user_id`),
  KEY `fk_maint_service_task_product_inventory_modified_user` (`last_modified_by_user_id`),
  KEY `fk_maint_service_task_product_inventory_maint_service_task` (`maint_service_task_id`),
  KEY `fk_maint_service_task_product_inventory_product_inventory` (`product_inventory_id`),
  CONSTRAINT `fk_maint_service_task_product_inventory_created_user` FOREIGN KEY (`created_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `fk_maint_service_task_product_inventory_maint_service_task` FOREIGN KEY (`maint_service_task_id`) REFERENCES `maint_service_task` (`ID`),
  CONSTRAINT `fk_maint_service_task_product_inventory_modified_user` FOREIGN KEY (`last_modified_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `fk_maint_service_task_product_inventory_product_inventory` FOREIGN KEY (`product_inventory_id`) REFERENCES `product_inventory` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `maint_task`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `maint_task`;
CREATE TABLE `maint_task` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `NAME` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `DESCRIPTION` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `INACTIVE` tinyint(1) DEFAULT NULL,
  `CUSTOMER_ID` bigint NOT NULL,
  `LOCATION_ID` bigint NOT NULL,
  `MAINT_TYPE_ID` bigint NOT NULL,
  `UPDATED_BY` bigint NOT NULL,
  `MODIFIED_TIME` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  `CREATED_TIME` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `CREATED_BY` bigint DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `NAME_CUSTOMER_ID_LOCATION_ID_UNIQUE` (`NAME`,`CUSTOMER_ID`,`LOCATION_ID`),
  KEY `IDX_MAINT_TYPE_ID_CUSTOMER_ID_LOCATION_ID` (`MAINT_TYPE_ID`,`CUSTOMER_ID`,`LOCATION_ID`),
  KEY `FK_MAINT_TASK_MAINT_TYPE_ID` (`MAINT_TYPE_ID`),
  KEY `FK_MAINT_TASK_CUSTOMER_ID` (`CUSTOMER_ID`),
  KEY `FK_MAINT_TASK_LOCATION_ID` (`LOCATION_ID`),
  KEY `FK_MAINT_TASK_UPDATED_BY` (`UPDATED_BY`),
  KEY `FK_MAINT_TASK_USER` (`CREATED_BY`),
  CONSTRAINT `FK_MAINT_TASK_CUSTOMER_ID` FOREIGN KEY (`CUSTOMER_ID`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_MAINT_TASK_LOCATION_ID` FOREIGN KEY (`LOCATION_ID`) REFERENCES `location` (`ID`),
  CONSTRAINT `FK_MAINT_TASK_MAINT_TYPE_ID` FOREIGN KEY (`MAINT_TYPE_ID`) REFERENCES `maint_type` (`ID`),
  CONSTRAINT `FK_MAINT_TASK_UPDATED_BY` FOREIGN KEY (`UPDATED_BY`) REFERENCES `user` (`ID`),
  CONSTRAINT `maint_task_ibfk_1` FOREIGN KEY (`CREATED_BY`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Maintenance Tasks represent the tasks to be carried out by users.';

-- -------------------------------------------------------------
-- Table structure for table `maint_task_product`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `maint_task_product`;
CREATE TABLE `maint_task_product` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `maint_task_id` bigint NOT NULL,
  `product_id` bigint NOT NULL,
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by_user_id` bigint NOT NULL,
  `last_modified_by_user_id` bigint NOT NULL,
  `last_modified_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `inactive` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_maint_task_product` (`maint_task_id`,`product_id`),
  KEY `fk_maint_task_product_created_user` (`created_by_user_id`),
  KEY `fk_maint_task_product_modified_user` (`last_modified_by_user_id`),
  KEY `fk_maint_task_product_product` (`product_id`),
  CONSTRAINT `fk_maint_task_product_created_user` FOREIGN KEY (`created_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `fk_maint_task_product_maint_task` FOREIGN KEY (`maint_task_id`) REFERENCES `maint_task` (`ID`),
  CONSTRAINT `fk_maint_task_product_modified_user` FOREIGN KEY (`last_modified_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `fk_maint_task_product_product` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `maint_type`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `maint_type`;
CREATE TABLE `maint_type` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `NAME` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `DESCRIPTION` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `INACTIVE` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `NAME_UNIQUE` (`NAME`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Maintenance Type categories describe the available maintenance type of tasks.  Each MAINT_TASK belongs to a MAINT_TYPE.';

-- -------------------------------------------------------------
-- Table structure for table `meta_field`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `meta_field`;
CREATE TABLE `meta_field` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `OBJECT_NAME` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `COLUMN_NAME` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `COLUMN_DISPLAY_NAME` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `REQUIRED` tinyint(1) DEFAULT NULL,
  `HIDDEN` tinyint(1) DEFAULT NULL,
  `READ_ONLY` tinyint(1) DEFAULT NULL,
  `HASHED` tinyint(1) DEFAULT NULL,
  `DISPLAY_TYPE` int DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_9` (`ID`),
  KEY `FK_META_FIELD_DISPLAY_TYPE_INDEX_9` (`DISPLAY_TYPE`),
  CONSTRAINT `FK_META_FIELD_DISPLAY_TYPE` FOREIGN KEY (`DISPLAY_TYPE`) REFERENCES `meta_field_display_type` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `meta_field_display_type`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `meta_field_display_type`;
CREATE TABLE `meta_field_display_type` (
  `ID` int NOT NULL,
  `NAME` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_7` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `meta_object`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `meta_object`;
CREATE TABLE `meta_object` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `NAME` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `DISPLAY_NAME` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `DISPLAY_NAME_PLURAL` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `PRIMARY_DISPLAY_COLUMN` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_D` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `notification_control`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `notification_control`;
CREATE TABLE `notification_control` (
  `id` int NOT NULL AUTO_INCREMENT,
  `notification_template_id` int DEFAULT NULL,
  `tag_id` int DEFAULT NULL,
  `to_actual_recipient` tinyint DEFAULT '1',
  `to_delegated_recipient` tinyint DEFAULT '1',
  `to_alternate_recipient` tinyint DEFAULT '0',
  `to_location_admin` tinyint DEFAULT NULL,
  `to_external_recipients` tinyint DEFAULT NULL,
  `to_external_emails` tinyint DEFAULT NULL,
  `disable_all_notifications` tinyint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tag_id_idx` (`tag_id`),
  CONSTRAINT `tag_id` FOREIGN KEY (`tag_id`) REFERENCES `tag` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- -------------------------------------------------------------
-- Table structure for table `notification_type`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `notification_type`;
CREATE TABLE `notification_type` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `NAME` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `DESCRIPTION` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `oauth2_code_grants`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `oauth2_code_grants`;
CREATE TABLE `oauth2_code_grants` (
  `code` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'The retrival code',
  `client_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'The client ID passed during the transaction',
  `code_expiration` timestamp NOT NULL,
  `scope` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'The scope of the token',
  PRIMARY KEY (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `package`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package`;
CREATE TABLE `package` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `UUID` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `RECIPIENT_ID` bigint DEFAULT NULL,
  `IS_RECIPIENT_TENANT` tinyint(1) DEFAULT NULL,
  `RECEIVED_BY_ID` bigint DEFAULT NULL,
  `LABEL_OCR` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `LABEL_PHOTO` blob,
  `PASSCODE` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `NOTES` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `COURIER` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `tracking_number` varchar(750) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `SENDER_INFO` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `TYPE` int DEFAULT NULL,
  `CUSTOMER_ID` bigint DEFAULT NULL,
  `LOCATION_ID` bigint DEFAULT NULL,
  `STATUS` int DEFAULT NULL,
  `RECEIVED_TIME` timestamp NULL DEFAULT NULL,
  `LAST_MODIFIED_TIME` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `received_at_building_id` bigint DEFAULT NULL,
  `LOCKER_ID` bigint DEFAULT NULL,
  `IS_OUTBOUND` tinyint(1) DEFAULT NULL,
  `COURIER_ID` bigint DEFAULT NULL,
  `intended_for_building_id` bigint DEFAULT NULL,
  `currently_at_building_id` bigint DEFAULT NULL,
  `didnt_fit` tinyint(1) DEFAULT NULL,
  `dimension_1` decimal(5,2) DEFAULT NULL,
  `dimension_2` decimal(5,2) DEFAULT NULL,
  `dimension_3` decimal(5,2) DEFAULT NULL,
  `deposited_by_user_id` bigint DEFAULT NULL,
  `IS_PRIORITY_MAIL` tinyint(1) DEFAULT '0',
  `SENDER_ID` bigint DEFAULT NULL,
  `OCR_TEXT` text COLLATE utf8mb4_unicode_ci,
  `EXTERNAL_ID` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `EXPIRATION_TIME` timestamp NULL DEFAULT NULL,
  `is_at_destination` tinyint(1) NOT NULL DEFAULT '0',
  `is_deleted` bit(1) NOT NULL DEFAULT b'0' COMMENT 'Indicates a package has been deleted from the system - soft delete.',
  `has_label_pic` tinyint(1) DEFAULT '0' COMMENT 'Describes if a package has a package image stored',
  `tenant_id` bigint DEFAULT NULL,
  `status_change_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_F` (`ID`),
  UNIQUE KEY `IDX_PACKAGE_UUID` (`UUID`),
  UNIQUE KEY `unique_passcode_for_location` (`PASSCODE`,`LOCATION_ID`),
  KEY `FK_PACKAGE_COURIER_USER_INDEX_F` (`COURIER_ID`),
  KEY `FK_PACKAGE_LOCKER_INDEX_F` (`LOCKER_ID`),
  KEY `FK_PACKAGE_CUSTOMER_INDEX_F` (`CUSTOMER_ID`),
  KEY `FK_PACKAGE_STATUS_INDEX_F` (`STATUS`),
  KEY `FK_PACKAGE_USER_INDEX_F` (`RECIPIENT_ID`),
  KEY `FK_PACKAGE_BUILDING_INDEX_F` (`received_at_building_id`),
  KEY `FK_PACKAGE_LOCATION_INDEX_F` (`LOCATION_ID`),
  KEY `FK_PACKAGE_RECEIVED_BY_INDEX_F` (`RECEIVED_BY_ID`),
  KEY `FK_PACKAGE_TYPE_INDEX_F` (`TYPE`),
  KEY `fk_package_intended_for_building` (`intended_for_building_id`),
  KEY `fk_package_currently_at_building` (`currently_at_building_id`),
  KEY `IDX_PACKAGE_TRACKING_NUMBER` (`tracking_number`(255)),
  KEY `FK_PACKAGE_USER_DEPOSIT` (`deposited_by_user_id`),
  KEY `FK_PACKAGE_SENDER` (`SENDER_ID`),
  KEY `fk_package_tenant_idx` (`tenant_id`),
  KEY `idx_PACKAGE_LOCATION_ID_TRACKING_NUMBER` (`LOCATION_ID`,`tracking_number`),
  CONSTRAINT `FK_PACKAGE_COURIER_USER` FOREIGN KEY (`COURIER_ID`) REFERENCES `courier_user` (`ID`),
  CONSTRAINT `fk_package_currently_at_building` FOREIGN KEY (`currently_at_building_id`) REFERENCES `building` (`ID`),
  CONSTRAINT `FK_PACKAGE_CUSTOMER` FOREIGN KEY (`CUSTOMER_ID`) REFERENCES `customer` (`ID`),
  CONSTRAINT `fk_package_intended_for_building` FOREIGN KEY (`intended_for_building_id`) REFERENCES `building` (`ID`),
  CONSTRAINT `FK_PACKAGE_LOCATION` FOREIGN KEY (`LOCATION_ID`) REFERENCES `location` (`ID`),
  CONSTRAINT `FK_PACKAGE_LOCKER` FOREIGN KEY (`LOCKER_ID`) REFERENCES `locker` (`ID`),
  CONSTRAINT `fk_package_received_at_building` FOREIGN KEY (`received_at_building_id`) REFERENCES `building` (`ID`),
  CONSTRAINT `FK_PACKAGE_RECEIVED_BY` FOREIGN KEY (`RECEIVED_BY_ID`) REFERENCES `user` (`ID`),
  CONSTRAINT `FK_PACKAGE_SENDER` FOREIGN KEY (`SENDER_ID`) REFERENCES `sender` (`ID`),
  CONSTRAINT `fk_package_status` FOREIGN KEY (`STATUS`) REFERENCES `package_status` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_package_tenant` FOREIGN KEY (`tenant_id`) REFERENCES `tenant` (`ID`),
  CONSTRAINT `FK_PACKAGE_TYPE` FOREIGN KEY (`TYPE`) REFERENCES `package_type` (`ID`),
  CONSTRAINT `FK_PACKAGE_USER` FOREIGN KEY (`RECIPIENT_ID`) REFERENCES `user` (`ID`),
  CONSTRAINT `FK_PACKAGE_USER_DEPOSIT` FOREIGN KEY (`deposited_by_user_id`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `package_advanced_properties`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_advanced_properties`;
CREATE TABLE `package_advanced_properties` (
  `id` int NOT NULL AUTO_INCREMENT,
  `package_id` bigint NOT NULL,
  `po_number` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `deliver_to_recipient` bigint DEFAULT NULL,
  `package_content_type` int DEFAULT NULL,
  `package_problem_reason` int DEFAULT NULL,
  `is_perishable` bit(1) DEFAULT NULL,
  `number_of_subitems` smallint DEFAULT NULL,
  `locker_size_id` int DEFAULT NULL COMMENT 'Stores locker size which will be used for reservation',
  `locker_type_id` int DEFAULT NULL COMMENT 'Stores locker type that will be used for reservation',
  `pickup_delivery_external_id` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Holds pickup and delivery external id',
  `receive_transaction_id` bigint DEFAULT NULL,
  `release_transaction_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_package_id` (`package_id`),
  KEY `fk_package_deliver_to_id` (`deliver_to_recipient`),
  KEY `fk_package_content_id` (`package_content_type`),
  KEY `fk_package_problem` (`package_problem_reason`),
  KEY `fk_package_advanced_properties_locker_size` (`locker_size_id`),
  KEY `fk_package_advanced_properties_locker_type` (`locker_type_id`),
  KEY `FK_pap_receive_transaction` (`receive_transaction_id`),
  KEY `FK_pap_release_transaction` (`release_transaction_id`),
  CONSTRAINT `fk_package_adv_pros_id` FOREIGN KEY (`package_id`) REFERENCES `package` (`ID`),
  CONSTRAINT `fk_package_advanced_properties_locker_size` FOREIGN KEY (`locker_size_id`) REFERENCES `locker_size` (`ID`),
  CONSTRAINT `fk_package_advanced_properties_locker_type` FOREIGN KEY (`locker_type_id`) REFERENCES `locker_type` (`ID`),
  CONSTRAINT `fk_package_content_id` FOREIGN KEY (`package_content_type`) REFERENCES `package_content_types` (`id`),
  CONSTRAINT `fk_package_deliver_to_id` FOREIGN KEY (`deliver_to_recipient`) REFERENCES `user` (`ID`),
  CONSTRAINT `fk_package_problem` FOREIGN KEY (`package_problem_reason`) REFERENCES `package_problem_reason` (`id`),
  CONSTRAINT `FK_pap_receive_transaction` FOREIGN KEY (`receive_transaction_id`) REFERENCES `transaction` (`id`),
  CONSTRAINT `FK_pap_release_transaction` FOREIGN KEY (`release_transaction_id`) REFERENCES `transaction` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='This tabel is used to define the package status rules which decides the package status based on the current package status';

-- -------------------------------------------------------------
-- Table structure for table `package_advanced_props_config`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_advanced_props_config`;
CREATE TABLE `package_advanced_props_config` (
  `id` int NOT NULL AUTO_INCREMENT,
  `location_properties_id` bigint NOT NULL,
  `name` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` bit(1) NOT NULL DEFAULT b'0',
  PRIMARY KEY (`id`),
  KEY `fk_package_props_location_props` (`location_properties_id`),
  CONSTRAINT `fk_package_props_location_props` FOREIGN KEY (`location_properties_id`) REFERENCES `location_properties` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='This table is used to define the properties that are going to be shown in the receive form';

-- -------------------------------------------------------------
-- Table structure for table `package_communication`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_communication`;
CREATE TABLE `package_communication` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `PACKAGE_ID` bigint DEFAULT NULL,
  `COMMUNICATION_ID` bigint DEFAULT NULL,
  `COMMUNICATION_TYPE` int DEFAULT NULL,
  `CUSTOMER_ID` bigint DEFAULT NULL,
  `TIME_SENT` timestamp NULL DEFAULT NULL,
  `USER_ID` bigint DEFAULT NULL,
  `NOTIFICATION_TYPE_ID` bigint DEFAULT NULL,
  `STATUS_LOG_ID` bigint DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_BA` (`ID`),
  KEY `FK_PACKAGE_COMMUNICATION_TYPE_INDEX_B` (`COMMUNICATION_TYPE`),
  KEY `FK_PACKAGE_COMMUNICATION_CUSTOMER_INDEX_B` (`CUSTOMER_ID`),
  KEY `FK_PACKAGE_COMMUNICATION_PACKAGE_INDEX_B` (`PACKAGE_ID`),
  KEY `PACKAGE_COMMUNICATION_USER` (`USER_ID`),
  KEY `PACKAGE_COMMUNICATION_NOTIFICATION_TYPE` (`NOTIFICATION_TYPE_ID`),
  KEY `fk_pack_comm_status_log_id` (`STATUS_LOG_ID`),
  KEY `Idx_time_sent` (`TIME_SENT`,`PACKAGE_ID`),
  KEY `idx_PACKAGE_COMMUNICATION_time_sent` (`TIME_SENT`),
  CONSTRAINT `fk_pack_comm_status_log_id` FOREIGN KEY (`STATUS_LOG_ID`) REFERENCES `status_log` (`ID`),
  CONSTRAINT `FK_PACKAGE_COMMUNICATION_CUSTOMER` FOREIGN KEY (`CUSTOMER_ID`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_PACKAGE_COMMUNICATION_PACKAGE` FOREIGN KEY (`PACKAGE_ID`) REFERENCES `package` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `FK_PACKAGE_COMMUNICATION_TYPE` FOREIGN KEY (`COMMUNICATION_TYPE`) REFERENCES `package_communication_type` (`ID`),
  CONSTRAINT `package_communication_ibfk_1` FOREIGN KEY (`USER_ID`) REFERENCES `user` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `package_communication_ibfk_2` FOREIGN KEY (`NOTIFICATION_TYPE_ID`) REFERENCES `notification_type` (`ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `package_communication_app`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_communication_app`;
CREATE TABLE `package_communication_app` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `MESSAGE_ID` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `AUTH_TOKEN` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `DEVICE_TOKEN` varchar(1024) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `BODY` varchar(1024) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `STATUS` int DEFAULT NULL,
  `TIME_SENT` timestamp NULL DEFAULT NULL,
  `CUSTOMER_ID` bigint DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `FK_PACKAGE_COMMUNICATION_APP_CUSTOMER_INDEX_E` (`CUSTOMER_ID`),
  CONSTRAINT `FK_PACKAGE_COMMUNICATION_APP_CUSTOMER` FOREIGN KEY (`CUSTOMER_ID`) REFERENCES `customer` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `package_communication_email`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_communication_email`;
CREATE TABLE `package_communication_email` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `MESSAGE_ID` varchar(300) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `FROM_EMAIL` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `TO_EMAIL` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `BODY` varchar(2000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `STATUS` int DEFAULT NULL,
  `STATUS_MESSAGE` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `TIME_SENT` timestamp NULL DEFAULT NULL,
  `CUSTOMER_ID` bigint DEFAULT NULL,
  `provider` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_A` (`ID`),
  KEY `FK_PACKAGE_COMMUNICATION_EMAIL_STATUS_INDEX_A` (`STATUS`),
  KEY `FK_PACKAGE_COMMUNICATION_EMAIL_CUSTOMER_INDEX_A` (`CUSTOMER_ID`),
  KEY `idx_PACKAGE_COMMUNICATION_EMAIL_time_sent` (`TIME_SENT`),
  CONSTRAINT `FK_PACKAGE_COMMUNICATION_EMAIL_CUSTOMER` FOREIGN KEY (`CUSTOMER_ID`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_PACKAGE_COMMUNICATION_EMAIL_STATUS` FOREIGN KEY (`STATUS`) REFERENCES `package_communication_status` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `package_communication_sms`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_communication_sms`;
CREATE TABLE `package_communication_sms` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `MESSAGE_ID` varchar(300) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `FROM_PHONE` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `TO_PHONE` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `BODY` varchar(2000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `STATUS` int DEFAULT NULL,
  `STATUS_MESSAGE` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `TIME_SENT` timestamp NULL DEFAULT NULL,
  `CUSTOMER_ID` bigint DEFAULT NULL,
  `provider` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_E` (`ID`),
  KEY `FK_PACKAGE_COMMUNICATION_SMS_STATUS_INDEX_E` (`STATUS`),
  KEY `FK_PACKAGE_COMMUNICATION_SMS_CUSTOMER_INDEX_E` (`CUSTOMER_ID`),
  KEY `idx_PACKAGE_COMMUNICATION_SMS_time_sent` (`TIME_SENT`),
  CONSTRAINT `FK_PACKAGE_COMMUNICATION_SMS_CUSTOMER` FOREIGN KEY (`CUSTOMER_ID`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_PACKAGE_COMMUNICATION_SMS_STATUS` FOREIGN KEY (`STATUS`) REFERENCES `package_communication_status` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `package_communication_status`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_communication_status`;
CREATE TABLE `package_communication_status` (
  `ID` int NOT NULL,
  `NAME` varchar(55) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `DESCRIPTION` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_2C` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `package_communication_type`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_communication_type`;
CREATE TABLE `package_communication_type` (
  `ID` int NOT NULL,
  `NAME` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_70` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `package_communication_voice`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_communication_voice`;
CREATE TABLE `package_communication_voice` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `message_id` varchar(300) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `from_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `to_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `body` varchar(2000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` int DEFAULT NULL,
  `status_message` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `time_sent` timestamp NULL DEFAULT NULL,
  `customer_id` bigint DEFAULT NULL,
  `provider` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_PACKAGE_COMMUNICATION_VOICE_CUSTOMER_idx` (`customer_id`),
  KEY `FK_PACKAGE_COMMUNICATION_VOICE_STATUS_idx` (`status`),
  CONSTRAINT `FK_PACKAGE_COMMUNICATION_VOICE_CUSTOMER` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_PACKAGE_COMMUNICATION_VOICE_STATUS` FOREIGN KEY (`status`) REFERENCES `package_communication_status` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `package_content_types`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_content_types`;
CREATE TABLE `package_content_types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `location_properties_id` bigint DEFAULT NULL,
  `name` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` varchar(250) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `order_display` smallint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_location_properties_content_type` (`location_properties_id`),
  CONSTRAINT `fk_location_properties_content_type` FOREIGN KEY (`location_properties_id`) REFERENCES `location_properties` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='This table is used to define the package content types. This is diffrent from package type that we already have in smiota system';

-- -------------------------------------------------------------
-- Table structure for table `package_edit_log`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_edit_log`;
CREATE TABLE `package_edit_log` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `package_id` bigint NOT NULL,
  `tracking_number` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Tracking number of the Package, if exists.',
  `status_id` int NOT NULL DEFAULT '0' COMMENT 'The Package Status ID value.',
  `updated_by_user_id` bigint NOT NULL COMMENT 'ID of User who performed the Package edit.',
  `updated_by_user_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Concatenated User firstName and lastName of User who performed the Package edit.',
  `updated_time` timestamp(3) NOT NULL COMMENT 'Time at which Package was updated.',
  `package_data` varchar(2000) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'JSON representation of the Package object edited.',
  `customer_id` bigint NOT NULL,
  `location_id` bigint NOT NULL,
  `building_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_package_edit_package_customer_location_id` (`package_id`,`customer_id`,`location_id`),
  KEY `fk_package_edit_status_id` (`status_id`),
  KEY `fk_package_edit_customer_id` (`customer_id`),
  KEY `fk_package_edit_location_id` (`location_id`),
  KEY `fk_package_edit_updated_by_user_id` (`updated_by_user_id`),
  KEY `fk_package_edit_building_id` (`building_id`),
  CONSTRAINT `fk_package_edit_building_id` FOREIGN KEY (`building_id`) REFERENCES `building` (`ID`),
  CONSTRAINT `fk_package_edit_customer_id` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `fk_package_edit_location_id` FOREIGN KEY (`location_id`) REFERENCES `location` (`ID`),
  CONSTRAINT `fk_package_edit_package_id` FOREIGN KEY (`package_id`) REFERENCES `package` (`ID`),
  CONSTRAINT `fk_package_edit_status_id` FOREIGN KEY (`status_id`) REFERENCES `package_status` (`id`),
  CONSTRAINT `fk_package_edit_updated_by_user_id` FOREIGN KEY (`updated_by_user_id`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Records each Package update event providing who, when, as well as the entire Package object in the serialized JSON format.';

-- -------------------------------------------------------------
-- Table structure for table `package_edit_modes`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_edit_modes`;
CREATE TABLE `package_edit_modes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(250) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Table to define the package information edit modes and decides whether the package information cab be edited or not';

-- -------------------------------------------------------------
-- Table structure for table `package_external_data`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_external_data`;
CREATE TABLE `package_external_data` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `customer_id` bigint NOT NULL,
  `location_id` bigint NOT NULL,
  `package_external_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `data` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `idx_package_external_data_package_external_id` (`customer_id`,`location_id`,`package_external_id`),
  KEY `fk_package_external_data_customer_id_idx` (`customer_id`),
  KEY `fk_package_external_data_location_id_idx` (`location_id`),
  CONSTRAINT `fk_package_external_data_customer_id` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `fk_package_external_data_location_id` FOREIGN KEY (`location_id`) REFERENCES `location` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `package_flow`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_flow`;
CREATE TABLE `package_flow` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `package_id` bigint DEFAULT NULL,
  `building_id` bigint DEFAULT NULL,
  `locker_unit_id` bigint DEFAULT NULL,
  `received_at_building_time` timestamp NULL DEFAULT NULL,
  `received_at_building_by_id` bigint DEFAULT NULL,
  `delivered_to_building_by_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_package_flow_package` (`package_id`),
  KEY `fk_package_flow_building` (`building_id`),
  KEY `fk_package_flow_locker_unit` (`locker_unit_id`),
  KEY `fk_package_flow_received_at_building_by` (`received_at_building_by_id`),
  KEY `fk_package_flow_delivered_to_building_by` (`delivered_to_building_by_id`),
  CONSTRAINT `fk_package_flow_building` FOREIGN KEY (`building_id`) REFERENCES `building` (`ID`),
  CONSTRAINT `fk_package_flow_delivered_to_building_by` FOREIGN KEY (`delivered_to_building_by_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `fk_package_flow_locker_unit` FOREIGN KEY (`locker_unit_id`) REFERENCES `locker_unit` (`ID`),
  CONSTRAINT `fk_package_flow_package` FOREIGN KEY (`package_id`) REFERENCES `package` (`ID`),
  CONSTRAINT `fk_package_flow_received_at_building_by` FOREIGN KEY (`received_at_building_by_id`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `package_group`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_group`;
CREATE TABLE `package_group` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `uuid` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `package_group_external_id` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by_user_id` bigint NOT NULL,
  `created_time` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `last_modified_by_user_id` bigint NOT NULL,
  `last_modified_time` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `status_change_time` timestamp NULL DEFAULT NULL,
  `package_group_status_id` bigint NOT NULL,
  `location_id` bigint NOT NULL,
  `customer_id` bigint NOT NULL,
  `tenant_id` bigint DEFAULT NULL,
  `order_id` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_deleted` bit(1) DEFAULT NULL,
  `package_group_recipient_id` bigint DEFAULT NULL,
  `customer_data` varchar(1024) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `passcode` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniqe_package_group` (`package_group_external_id`,`location_id`),
  KEY `fk_pg_created_user` (`created_by_user_id`),
  KEY `fk_pg_last_modified_user` (`last_modified_by_user_id`),
  KEY `fk_pgpsl_package_group_status` (`package_group_status_id`),
  KEY `fk_pg_location` (`location_id`),
  KEY `fk_pg_customer` (`customer_id`),
  KEY `fk_tenant_id_idx` (`tenant_id`),
  KEY `fk_pkg_group_recipient_id` (`package_group_recipient_id`),
  CONSTRAINT `fk_package_group_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenant` (`ID`),
  CONSTRAINT `fk_pg_created_user` FOREIGN KEY (`created_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `fk_pg_last_modified_user` FOREIGN KEY (`last_modified_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `fk_pgpsl_package_group_status` FOREIGN KEY (`package_group_status_id`) REFERENCES `package_group_status` (`id`),
  CONSTRAINT `fk_pkg_group_recipient_id` FOREIGN KEY (`package_group_recipient_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `package_group_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `location` (`ID`),
  CONSTRAINT `package_group_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `package_group_package`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_group_package`;
CREATE TABLE `package_group_package` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `package_group_id` bigint NOT NULL,
  `package_id` bigint NOT NULL,
  `created_by_user_id` bigint NOT NULL,
  `created_time` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_package_group_package_id` (`package_id`),
  KEY `fk_pgp_package_group` (`package_group_id`),
  KEY `fk_pgp_created_user` (`created_by_user_id`),
  CONSTRAINT `fk_pgp_created_user` FOREIGN KEY (`created_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `fk_pgp_package` FOREIGN KEY (`package_id`) REFERENCES `package` (`ID`),
  CONSTRAINT `fk_pgp_package_group` FOREIGN KEY (`package_group_id`) REFERENCES `package_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `package_group_status`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_group_status`;
CREATE TABLE `package_group_status` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(300) COLLATE utf8mb4_unicode_ci NOT NULL,
  `color` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `package_group_status_log`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_group_status_log`;
CREATE TABLE `package_group_status_log` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `package_group_id` bigint NOT NULL,
  `package_group_status_id` bigint NOT NULL,
  `created_time` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `created_by_user_id` bigint NOT NULL,
  `package_status_log_id` bigint DEFAULT NULL,
  `uuid` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `current_building_id` bigint DEFAULT NULL,
  `status_change_time` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_pgpsl_package_group` (`package_group_id`),
  KEY `fk_pgpsl_package_group_status_log` (`package_group_status_id`),
  KEY `fk_pgsl_created_user` (`created_by_user_id`),
  KEY `fk_pgsl_package_status_log` (`package_status_log_id`),
  KEY `fk_current_building_id_idx` (`current_building_id`),
  CONSTRAINT `fk_current_building_id` FOREIGN KEY (`current_building_id`) REFERENCES `building` (`ID`),
  CONSTRAINT `fk_pgpsl_package_group` FOREIGN KEY (`package_group_id`) REFERENCES `package_group` (`id`),
  CONSTRAINT `fk_pgpsl_package_group_status_log` FOREIGN KEY (`package_group_status_id`) REFERENCES `package_group_status` (`id`),
  CONSTRAINT `fk_pgsl_created_user` FOREIGN KEY (`created_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `package_group_status_log_ibfk_1` FOREIGN KEY (`package_status_log_id`) REFERENCES `package_status_log` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `package_group_status_to_package_status`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_group_status_to_package_status`;
CREATE TABLE `package_group_status_to_package_status` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `package_group_status_id` bigint DEFAULT NULL,
  `package_status_id` int DEFAULT NULL,
  `customerid` bigint DEFAULT NULL,
  `locationid` bigint DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `FK_package-group_status_id_idx` (`package_group_status_id`),
  KEY `FK_package_status_id_idx` (`package_status_id`),
  KEY `FK_cudtomer_id_idx` (`customerid`),
  KEY `FK_location_id_idx` (`locationid`),
  CONSTRAINT `FK_customer_id` FOREIGN KEY (`customerid`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_location_id` FOREIGN KEY (`locationid`) REFERENCES `location` (`ID`),
  CONSTRAINT `FK_package_group_status_id` FOREIGN KEY (`package_group_status_id`) REFERENCES `package_group_status` (`id`),
  CONSTRAINT `FK_package_status_id` FOREIGN KEY (`package_status_id`) REFERENCES `package_status` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `package_group_status_transition`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_group_status_transition`;
CREATE TABLE `package_group_status_transition` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `package_group_status_id` bigint NOT NULL,
  `package_group_allowed_status_id` bigint NOT NULL,
  `inactive` tinyint(1) DEFAULT '0',
  `location_id` bigint DEFAULT NULL,
  `customer_id` bigint DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `last_modified_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by_user_id` bigint DEFAULT NULL,
  `last_modified_by_user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_pgst_status_id_allowed_status_id` (`package_group_status_id`,`package_group_allowed_status_id`,`location_id`),
  KEY `FK_pgst_allowed_status_id` (`package_group_allowed_status_id`),
  KEY `FK_pgst_location_id` (`location_id`),
  KEY `FK_pgst_customer_id` (`customer_id`),
  KEY `FK_pgst_last_modified_by_user_id` (`last_modified_by_user_id`),
  KEY `FK_pgst_created_by_user_id` (`created_by_user_id`),
  CONSTRAINT `FK_pgst_allowed_status_id` FOREIGN KEY (`package_group_allowed_status_id`) REFERENCES `package_group_status` (`id`),
  CONSTRAINT `FK_pgst_created_by_user_id` FOREIGN KEY (`created_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `FK_pgst_customer_id` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_pgst_last_modified_by_user_id` FOREIGN KEY (`last_modified_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `FK_pgst_location_id` FOREIGN KEY (`location_id`) REFERENCES `location` (`ID`),
  CONSTRAINT `FK_pgst_package_group_status_id` FOREIGN KEY (`package_group_status_id`) REFERENCES `package_group_status` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `package_group_status_transition_log`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_group_status_transition_log`;
CREATE TABLE `package_group_status_transition_log` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `package_group_status_transition_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `package_group_status_id` bigint NOT NULL,
  `package_group_allowed_status_id` bigint NOT NULL,
  `inactive` tinyint(1) DEFAULT '0',
  `location_id` bigint DEFAULT NULL,
  `customer_id` bigint DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by_user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_pgstl_package_group_status_transition_id` (`package_group_status_transition_id`),
  KEY `FK_pgstl_package_group_status_id` (`package_group_status_id`),
  KEY `FK_pgstl_allowed_status_id` (`package_group_allowed_status_id`),
  KEY `FK_pgstl_location_id` (`location_id`),
  KEY `FK_pgstl_customer_id` (`customer_id`),
  KEY `FK_pgstl_created_by_user_id` (`created_by_user_id`),
  CONSTRAINT `FK_pgstl_allowed_status_id` FOREIGN KEY (`package_group_allowed_status_id`) REFERENCES `package_group_status` (`id`),
  CONSTRAINT `FK_pgstl_created_by_user_id` FOREIGN KEY (`created_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `FK_pgstl_customer_id` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_pgstl_location_id` FOREIGN KEY (`location_id`) REFERENCES `location` (`ID`),
  CONSTRAINT `FK_pgstl_package_group_status_id` FOREIGN KEY (`package_group_status_id`) REFERENCES `package_group_status` (`id`),
  CONSTRAINT `FK_pgstl_package_group_status_transition_id` FOREIGN KEY (`package_group_status_transition_id`) REFERENCES `package_group_status_transition` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `package_label_templates`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_label_templates`;
CREATE TABLE `package_label_templates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `customer_id` bigint NOT NULL,
  `location_id` bigint DEFAULT NULL,
  `template` varchar(2000) COLLATE utf8mb4_unicode_ci NOT NULL,
  `inactive` bit(1) NOT NULL DEFAULT b'0',
  `is_outbound` bit(1) DEFAULT b'0' COMMENT 'Flag to indicate if the template is applicable for inbound or outbound. TRUE: for outbound, FALSE/NULL: for inbound',
  PRIMARY KEY (`id`),
  KEY `idx_package_label_template_customer_location` (`customer_id`,`location_id`),
  KEY `fk_package_label_template_location` (`location_id`),
  CONSTRAINT `fk_package_label_template_customer` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `fk_package_label_template_location` FOREIGN KEY (`location_id`) REFERENCES `location` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Stores the label templates that are applicable for the specified Customer and Location';

-- -------------------------------------------------------------
-- Table structure for table `package_priority_types`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_priority_types`;
CREATE TABLE `package_priority_types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `location_properties_id` bigint NOT NULL,
  `name` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(250) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `flag` bit(1) DEFAULT NULL,
  `is_selected` bit(1) DEFAULT NULL,
  `order_display` smallint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_location_properties_priority_types` (`location_properties_id`),
  CONSTRAINT `fk_location_properties_priority_types` FOREIGN KEY (`location_properties_id`) REFERENCES `location_properties` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='This table is used to define the package priority types';

-- -------------------------------------------------------------
-- Table structure for table `package_problem_reason`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_problem_reason`;
CREATE TABLE `package_problem_reason` (
  `id` int NOT NULL AUTO_INCREMENT,
  `location_properties_id` bigint NOT NULL,
  `name` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` varchar(250) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `order_display` smallint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_location_properties_problem_reason` (`location_properties_id`),
  CONSTRAINT `fk_location_properties_problem_reason` FOREIGN KEY (`location_properties_id`) REFERENCES `location_properties` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='This table is used to define the package problem reasons';

-- -------------------------------------------------------------
-- Table structure for table `package_release`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_release`;
CREATE TABLE `package_release` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `PACKAGE_ID` bigint DEFAULT NULL,
  `RELEASE_TO_USER_ID` bigint DEFAULT NULL,
  `RELEASE_TO_NAME` varchar(300) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `RELEASE_TO_EXTERNAL` tinyint(1) DEFAULT NULL,
  `RELEASED_BY_USER_ID` bigint DEFAULT NULL,
  `TIME_RELEASED` timestamp NULL DEFAULT NULL,
  `NOTES` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ID_NUMBER` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ID_TYPE` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `CUSTOMER_ID` bigint DEFAULT NULL,
  `LOCATION_ID` bigint DEFAULT NULL,
  `LAST_MODIFIED_TIME` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_98` (`ID`),
  KEY `FK_PACKAGE_RELEASE_PACKAGE_INDEX_9` (`PACKAGE_ID`),
  KEY `FK_PACKAGE_RELEASE_BY_USER_INDEX_9` (`RELEASED_BY_USER_ID`),
  KEY `FK_PACKAGE_RELEASE_TO_USER_INDEX_9` (`RELEASE_TO_USER_ID`),
  KEY `FK_PACKAGE_RELEASE_CUSTOMER_INDEX_9` (`CUSTOMER_ID`),
  CONSTRAINT `FK_PACKAGE_RELEASE_BY_USER` FOREIGN KEY (`RELEASED_BY_USER_ID`) REFERENCES `user` (`ID`),
  CONSTRAINT `FK_PACKAGE_RELEASE_CUSTOMER` FOREIGN KEY (`CUSTOMER_ID`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_PACKAGE_RELEASE_PACKAGE` FOREIGN KEY (`PACKAGE_ID`) REFERENCES `package` (`ID`) ON DELETE CASCADE,
  CONSTRAINT `FK_PACKAGE_RELEASE_TO_USER` FOREIGN KEY (`RELEASE_TO_USER_ID`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `package_release_blobs`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_release_blobs`;
CREATE TABLE `package_release_blobs` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `PACKAGE_ID` bigint DEFAULT NULL,
  `SIGNATURE` mediumblob,
  `ID_PHOTO` mediumblob,
  `PACKAGE_STATUS_LOG_ID` bigint DEFAULT NULL,
  `PACKAGE_STATUS_ID` int DEFAULT NULL,
  `CREATED_TIME` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `CREATED_BY_USER_ID` bigint DEFAULT NULL,
  `SOURCE_APP_ID` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_98` (`ID`),
  KEY `fk_package_blob_id` (`PACKAGE_ID`),
  KEY `fk_prb_status_log_id` (`PACKAGE_STATUS_LOG_ID`),
  CONSTRAINT `fk_package_blob_id` FOREIGN KEY (`PACKAGE_ID`) REFERENCES `package` (`ID`),
  CONSTRAINT `fk_prb_status_log_id` FOREIGN KEY (`PACKAGE_STATUS_LOG_ID`) REFERENCES `package_status_log` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `package_status`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_status`;
CREATE TABLE `package_status` (
  `id` int NOT NULL AUTO_INCREMENT,
  `NAME` varchar(24) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `COMMENT` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `color` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ordinal` int DEFAULT NULL,
  `customer_id` bigint DEFAULT NULL,
  `location_id` bigint DEFAULT NULL,
  `is_required` bit(1) NOT NULL DEFAULT b'0' COMMENT 'Indicates option is a mandatory status for ALL.',
  `package_status_group_id` int DEFAULT NULL COMMENT 'Each Package Status belongs to a specific phase within a Package lifetime.',
  `inactive` bit(1) NOT NULL DEFAULT b'0' COMMENT 'Indicates if PackageStatus has been deleted.  System statuses should not be INACTIVE ever.',
  `edit_mode` int DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `PRIMARY_KEY_20` (`id`),
  UNIQUE KEY `unique_package_status_name_customer_location` (`NAME`,`customer_id`,`location_id`),
  KEY `fk_package_status_group` (`package_status_group_id`),
  KEY `fk_ps_edit_mode` (`edit_mode`),
  CONSTRAINT `fk_package_status_group` FOREIGN KEY (`package_status_group_id`) REFERENCES `package_status_group` (`id`),
  CONSTRAINT `fk_ps_edit_mode` FOREIGN KEY (`edit_mode`) REFERENCES `package_edit_modes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `package_status_assignment`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_status_assignment`;
CREATE TABLE `package_status_assignment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `status_id` int NOT NULL,
  `name` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ordinal` int DEFAULT NULL,
  `color` varchar(40) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `customer_id` bigint DEFAULT NULL,
  `location_id` bigint DEFAULT NULL,
  `edit_mode` int DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_status_name_customer_location` (`name`,`customer_id`,`location_id`),
  UNIQUE KEY `unique_status_customer_location` (`status_id`,`customer_id`,`location_id`),
  UNIQUE KEY `uc_package_status` (`name`,`customer_id`,`location_id`),
  KEY `fk_package_status_assignment_customer_id` (`customer_id`),
  KEY `fk_package_status_assignment_location_id` (`location_id`),
  KEY `fk_psa_edit_mode` (`edit_mode`),
  CONSTRAINT `fk_package_status_assignment_customer_id` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `fk_package_status_assignment_location_id` FOREIGN KEY (`location_id`) REFERENCES `location` (`ID`),
  CONSTRAINT `fk_package_status_assignment_package_status_id` FOREIGN KEY (`status_id`) REFERENCES `package_status` (`id`),
  CONSTRAINT `fk_psa_edit_mode` FOREIGN KEY (`edit_mode`) REFERENCES `package_edit_modes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Primarily used Package Status configs defining the active statuses per Customer and Location. References the base PACKAGE_STATUS data.';

-- -------------------------------------------------------------
-- Table structure for table `package_status_edit_mode_assignment`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_status_edit_mode_assignment`;
CREATE TABLE `package_status_edit_mode_assignment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `package_status_assignment_id` int NOT NULL COMMENT 'The PackageStatusAssignment to associate to one or more Edit Modes.',
  `edit_mode` int NOT NULL COMMENT 'Allowed Edit Mode for PackageStatusAssignment.',
  PRIMARY KEY (`id`),
  KEY `fk_package_status_assignment` (`package_status_assignment_id`),
  KEY `fk_edit_mode` (`edit_mode`),
  CONSTRAINT `fk_edit_mode` FOREIGN KEY (`edit_mode`) REFERENCES `package_edit_modes` (`id`),
  CONSTRAINT `fk_package_status_assignment` FOREIGN KEY (`package_status_assignment_id`) REFERENCES `package_status_assignment` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Defines the one or more Package Edit Modes associated to a Package Status for a Customer and Location.';

-- -------------------------------------------------------------
-- Table structure for table `package_status_flow`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_status_flow`;
CREATE TABLE `package_status_flow` (
  `id` int NOT NULL AUTO_INCREMENT,
  `current_status` int NOT NULL,
  `allowed_status` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_status_flow_id` FOREIGN KEY (`id`) REFERENCES `package_status` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `package_status_group`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_status_group`;
CREATE TABLE `package_status_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(250) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Defines the expected phases of a Package lifecycle in Smiota system.';

-- -------------------------------------------------------------
-- Table structure for table `package_status_log`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_status_log`;
CREATE TABLE `package_status_log` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `PACKAGE_ID` bigint NOT NULL,
  `PACKAGE_STATUS_ID` int DEFAULT NULL,
  `TRANSACTION_RECORDED_TIME` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `UPDATED_BY_USER_ID` bigint NOT NULL,
  `CURRENT_BUILDING` bigint DEFAULT NULL,
  `DESTINATION_BUILDING` bigint DEFAULT NULL,
  `STATUS_CHANGE_TIME` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`),
  KEY `FK_PACKAGE_STATUS_LOG_PACKAGE` (`PACKAGE_ID`),
  KEY `FK_PACKAGE_STATUS_LOG_USER` (`UPDATED_BY_USER_ID`),
  KEY `FK_CURRENT_BUILDING` (`CURRENT_BUILDING`),
  KEY `FK_DESTINATION_BUILDING` (`DESTINATION_BUILDING`),
  KEY `FK_PACKAGE_STATUS_LOG_PACKAGE_STATUS` (`PACKAGE_STATUS_ID`),
  CONSTRAINT `FK_PACKAGE_STATUS_LOG_PACKAGE` FOREIGN KEY (`PACKAGE_ID`) REFERENCES `package` (`ID`),
  CONSTRAINT `FK_PACKAGE_STATUS_LOG_PACKAGE_STATUS` FOREIGN KEY (`PACKAGE_STATUS_ID`) REFERENCES `package_status` (`id`),
  CONSTRAINT `FK_PACKAGE_STATUS_LOG_USER` FOREIGN KEY (`UPDATED_BY_USER_ID`) REFERENCES `user` (`ID`),
  CONSTRAINT `package_status_log_ibfk_1` FOREIGN KEY (`CURRENT_BUILDING`) REFERENCES `building` (`ID`),
  CONSTRAINT `package_status_log_ibfk_2` FOREIGN KEY (`DESTINATION_BUILDING`) REFERENCES `building` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `package_status_rules`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_status_rules`;
CREATE TABLE `package_status_rules` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `status_id` int NOT NULL COMMENT 'The Package Status to configure a rule for.',
  `allowed_status_id` int DEFAULT NULL COMMENT 'The Package Status allowed to transition to from status_id.',
  `customer_id` bigint DEFAULT NULL,
  `location_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_status_rules_status_id` (`status_id`),
  KEY `idx_status_rules_customer_location` (`customer_id`,`location_id`),
  KEY `fk_allowed_rules_package_status_id` (`allowed_status_id`),
  KEY `fk_status_rules_location_id` (`location_id`),
  CONSTRAINT `fk_allowed_rules_package_status_id` FOREIGN KEY (`allowed_status_id`) REFERENCES `package_status` (`id`),
  CONSTRAINT `fk_status_rules_customer_id` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `fk_status_rules_location_id` FOREIGN KEY (`location_id`) REFERENCES `location` (`ID`),
  CONSTRAINT `fk_status_rules_package_status_id` FOREIGN KEY (`status_id`) REFERENCES `package_status` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='This tabel is used to define the package status rules which decides the package status based on the current package status';

-- -------------------------------------------------------------
-- Table structure for table `package_type`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `package_type`;
CREATE TABLE `package_type` (
  `ID` int NOT NULL,
  `NAME` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `COMMENT` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_1` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `pending_package_communication`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `pending_package_communication`;
CREATE TABLE `pending_package_communication` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `PACKAGE_ID` bigint DEFAULT NULL,
  `TRIED_BUT_FAILED` tinyint(1) DEFAULT NULL,
  `ERROR_MSG` varchar(300) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `CUSTOMER_ID` bigint DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `FK_PENDING_PACKAGE_COMMUNICATION_PACKAGE` (`PACKAGE_ID`),
  KEY `FK_PENDING_PACKAGE_COMMUNICATION_CUSTOMER` (`CUSTOMER_ID`),
  CONSTRAINT `FK_PENDING_PACKAGE_COMMUNICATION_CUSTOMER` FOREIGN KEY (`CUSTOMER_ID`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_PENDING_PACKAGE_COMMUNICATION_PACKAGE` FOREIGN KEY (`PACKAGE_ID`) REFERENCES `package` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `product`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `product`;
CREATE TABLE `product` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `model_name` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `brand_name` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `min_count` smallint DEFAULT NULL,
  `location_id` bigint NOT NULL,
  `customer_id` bigint NOT NULL,
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by_user_id` bigint NOT NULL,
  `last_modified_by_user_id` bigint NOT NULL,
  `last_modified_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_product` (`model_name`,`brand_name`,`location_id`,`customer_id`),
  KEY `fk_product_location` (`location_id`),
  KEY `fk_product_customer` (`customer_id`),
  KEY `fk_product_created_user` (`created_by_user_id`),
  KEY `fk_product_modified_user` (`last_modified_by_user_id`),
  CONSTRAINT `fk_product_created_user` FOREIGN KEY (`created_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `fk_product_customer` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `fk_product_location` FOREIGN KEY (`location_id`) REFERENCES `location` (`ID`),
  CONSTRAINT `fk_product_modified_user` FOREIGN KEY (`last_modified_by_user_id`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `product_configuration`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `product_configuration`;
CREATE TABLE `product_configuration` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `product_id` bigint NOT NULL,
  `product_package_id` bigint NOT NULL,
  `count` smallint DEFAULT '1',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by_user_id` bigint NOT NULL,
  `last_modified_by_user_id` bigint NOT NULL,
  `last_modified_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `product_configuration_prod_pack` (`product_id`,`product_package_id`),
  KEY `fk_product_configuration_created_user` (`created_by_user_id`),
  KEY `fk_product_configuration_modified_user` (`last_modified_by_user_id`),
  CONSTRAINT `fk_product_configuration_created_user` FOREIGN KEY (`created_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `fk_product_configuration_modified_user` FOREIGN KEY (`last_modified_by_user_id`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `product_inventory`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `product_inventory`;
CREATE TABLE `product_inventory` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `product_id` bigint NOT NULL,
  `package_id` bigint DEFAULT NULL,
  `status` smallint NOT NULL,
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by_user_id` bigint NOT NULL,
  `currently_with_user_id` bigint DEFAULT NULL,
  `last_modified_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `currently_at_maint_location_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_product_inventory_product` (`product_id`),
  KEY `fk_product_inventory_product_inventory_status` (`status`),
  KEY `fk_product_inventory_created_user` (`created_by_user_id`),
  KEY `fk_product_inventory_modified_user` (`currently_with_user_id`),
  KEY `product_inventory_maintenance_location` (`currently_at_maint_location_id`),
  CONSTRAINT `fk_product_inventory_created_user` FOREIGN KEY (`created_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `fk_product_inventory_modified_user` FOREIGN KEY (`currently_with_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `fk_product_inventory_product` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`),
  CONSTRAINT `fk_product_inventory_product_inventory_status` FOREIGN KEY (`status`) REFERENCES `product_inventory_status` (`id`),
  CONSTRAINT `product_inventory_ibfk_1` FOREIGN KEY (`currently_at_maint_location_id`) REFERENCES `maint_location` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `product_inventory_status`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `product_inventory_status`;
CREATE TABLE `product_inventory_status` (
  `id` smallint NOT NULL AUTO_INCREMENT,
  `name` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_product_inventory_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `product_inventory_status_log`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `product_inventory_status_log`;
CREATE TABLE `product_inventory_status_log` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `product_inventory_id` bigint NOT NULL,
  `status` smallint NOT NULL,
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `action_from_user_id` bigint DEFAULT NULL,
  `currently_with_user_id` bigint DEFAULT NULL,
  `action_from_maint_location_id` bigint DEFAULT NULL,
  `currently_at_maint_location_id` bigint DEFAULT NULL,
  `transaction_uuid` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_item_status_log` (`product_inventory_id`,`status`),
  KEY `fk_product_inventory_status_log_from_user` (`action_from_user_id`),
  KEY `fk_product_inventory_status_log_to_user` (`currently_with_user_id`),
  KEY `fk_product_inventory_status_log_from_maint_location` (`action_from_maint_location_id`),
  KEY `fk_product_inventory_status_log_to_maint_location` (`currently_at_maint_location_id`),
  KEY `fk_product_inventory_status_log_item_status` (`status`),
  CONSTRAINT `fk_product_inventory_status_log_from_maint_location` FOREIGN KEY (`action_from_maint_location_id`) REFERENCES `maint_location` (`ID`),
  CONSTRAINT `fk_product_inventory_status_log_from_user` FOREIGN KEY (`action_from_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `fk_product_inventory_status_log_item` FOREIGN KEY (`product_inventory_id`) REFERENCES `product_inventory` (`id`),
  CONSTRAINT `fk_product_inventory_status_log_item_status` FOREIGN KEY (`status`) REFERENCES `product_inventory_status` (`id`),
  CONSTRAINT `fk_product_inventory_status_log_to_maint_location` FOREIGN KEY (`currently_at_maint_location_id`) REFERENCES `maint_location` (`ID`),
  CONSTRAINT `fk_product_inventory_status_log_to_user` FOREIGN KEY (`currently_with_user_id`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `product_package`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `product_package`;
CREATE TABLE `product_package` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `barcode` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `location_id` bigint NOT NULL,
  `customer_id` bigint NOT NULL,
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by_user_id` bigint NOT NULL,
  `last_modified_by_user_id` bigint NOT NULL,
  `last_modified_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_product_package` (`barcode`,`location_id`,`customer_id`),
  KEY `fk_product_package_location` (`location_id`),
  KEY `fk_product_package_customer` (`customer_id`),
  KEY `fk_product_package_created_user` (`created_by_user_id`),
  KEY `fk_product_package_modified_user` (`last_modified_by_user_id`),
  CONSTRAINT `fk_product_package_created_user` FOREIGN KEY (`created_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `fk_product_package_customer` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `fk_product_package_location` FOREIGN KEY (`location_id`) REFERENCES `location` (`ID`),
  CONSTRAINT `fk_product_package_modified_user` FOREIGN KEY (`last_modified_by_user_id`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `registration_status`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `registration_status`;
CREATE TABLE `registration_status` (
  `ID` int NOT NULL,
  `NAME` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `reserve`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `reserve`;
CREATE TABLE `reserve` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `reserve_status_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `start_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `end_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `hold_start_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `hold_end_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `last_modified_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by_user_id` bigint NOT NULL,
  `last_modified_by_user_id` bigint DEFAULT NULL,
  `notes` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_reserve_created_by_user_id` (`created_by_user_id`),
  KEY `FK_reserve_last_modified_by_user_id` (`last_modified_by_user_id`),
  KEY `idx_reserve_status_id` (`reserve_status_id`),
  CONSTRAINT `FK_reserve_created_by_user_id` FOREIGN KEY (`created_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `FK_reserve_last_modified_by_user_id` FOREIGN KEY (`last_modified_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `FK_reserve_reserve_status_id` FOREIGN KEY (`reserve_status_id`) REFERENCES `reserve_status` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `reserve_log`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `reserve_log`;
CREATE TABLE `reserve_log` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `reserve_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `reserve_status_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `start_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `end_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `hold_start_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `hold_end_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by_user_id` bigint DEFAULT NULL,
  `notes` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_reserve_log_reserve_id` (`reserve_id`),
  KEY `FK_reserve_log_reserve_status_id` (`reserve_status_id`),
  KEY `FK_reserve_log_created_by_user_id` (`created_by_user_id`),
  CONSTRAINT `FK_reserve_log_created_by_user_id` FOREIGN KEY (`created_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `FK_reserve_log_reserve_id` FOREIGN KEY (`reserve_id`) REFERENCES `reserve` (`id`),
  CONSTRAINT `FK_reserve_log_reserve_status_id` FOREIGN KEY (`reserve_status_id`) REFERENCES `reserve_status` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `reserve_package`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `reserve_package`;
CREATE TABLE `reserve_package` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `reserve_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `package_id` bigint NOT NULL,
  `locker_id` bigint DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `last_modified_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by_user_id` bigint NOT NULL,
  `last_modified_by_user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_reserve_package_locker_id` (`locker_id`),
  KEY `FK_reserve_package_created_by_user_id` (`created_by_user_id`),
  KEY `FK_reserve_package_last_modified_by_user_id` (`last_modified_by_user_id`),
  KEY `idx_reserve_package_reserve_id` (`reserve_id`),
  KEY `idx_reserve_package_package_id` (`package_id`),
  CONSTRAINT `FK_reserve_package_created_by_user_id` FOREIGN KEY (`created_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `FK_reserve_package_last_modified_by_user_id` FOREIGN KEY (`last_modified_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `FK_reserve_package_locker_id` FOREIGN KEY (`locker_id`) REFERENCES `locker` (`ID`),
  CONSTRAINT `FK_reserve_package_package_id` FOREIGN KEY (`package_id`) REFERENCES `package` (`ID`),
  CONSTRAINT `FK_reserve_package_reserve_id` FOREIGN KEY (`reserve_id`) REFERENCES `reserve` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `reserve_package_log`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `reserve_package_log`;
CREATE TABLE `reserve_package_log` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `reserve_package_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `reserve_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `package_id` bigint NOT NULL,
  `locker_id` bigint DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by_user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_reserve_package_log_reserve_id` (`reserve_id`),
  KEY `FK_reserve_package_log_package_id` (`package_id`),
  KEY `FK_reserve_package_log_locker_id` (`locker_id`),
  KEY `FK_reserve_package_log_created_by_user_id` (`created_by_user_id`),
  KEY `FK_reserve_package_log_reserve_package_id` (`reserve_package_id`),
  CONSTRAINT `FK_reserve_package_log_created_by_user_id` FOREIGN KEY (`created_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `FK_reserve_package_log_locker_id` FOREIGN KEY (`locker_id`) REFERENCES `locker` (`ID`),
  CONSTRAINT `FK_reserve_package_log_package_id` FOREIGN KEY (`package_id`) REFERENCES `package` (`ID`),
  CONSTRAINT `FK_reserve_package_log_reserve_id` FOREIGN KEY (`reserve_id`) REFERENCES `reserve` (`id`),
  CONSTRAINT `FK_reserve_package_log_reserve_package_id` FOREIGN KEY (`reserve_package_id`) REFERENCES `reserve_package` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `reserve_status`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `reserve_status`;
CREATE TABLE `reserve_status` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(72) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `reserve_status_transition`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `reserve_status_transition`;
CREATE TABLE `reserve_status_transition` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `reserve_status_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `reserve_allowed_status_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_rst_status_id_allowed_status_id` (`reserve_status_id`,`reserve_allowed_status_id`),
  KEY `FK_reserve_allowed_status_id_reserve_status` (`reserve_allowed_status_id`),
  CONSTRAINT `FK_reserve_allowed_status_id_reserve_status` FOREIGN KEY (`reserve_allowed_status_id`) REFERENCES `reserve_status` (`id`),
  CONSTRAINT `FK_reserve_status_id_reserve_status` FOREIGN KEY (`reserve_status_id`) REFERENCES `reserve_status` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `role`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `role`;
CREATE TABLE `role` (
  `ID` int NOT NULL,
  `NAME` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'NOT TO BE MODIFIED - unique and internally used NAME.',
  `COMMENT` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `DISPLAY_NAME` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Name to be displayed on the UI.  Can be edited.',
  `ROLE_LEVEL_ID` int DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_26` (`ID`),
  UNIQUE KEY `unique_role_name` (`NAME`),
  KEY `fk_role_role_level` (`ROLE_LEVEL_ID`),
  CONSTRAINT `fk_role_role_level` FOREIGN KEY (`ROLE_LEVEL_ID`) REFERENCES `role_level` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `role_level`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `role_level`;
CREATE TABLE `role_level` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'NOT TO BE MODIFIED - internally used name.',
  `display_name` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Name for display usages, can be edited.',
  `description` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Describes the role_level.',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Defines and groups the various levels of Roles supported for Accounts.  Allows for filtration of Roles to return.';

-- -------------------------------------------------------------
-- Table structure for table `role_scope`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `role_scope`;
CREATE TABLE `role_scope` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `display_name` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `comment` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `satellite_locker_unit`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `satellite_locker_unit`;
CREATE TABLE `satellite_locker_unit` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `locker_unit_id` bigint DEFAULT NULL,
  `satellite_locker_unit_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_unique_locker_satellite` (`satellite_locker_unit_id`,`locker_unit_id`),
  KEY `fk_satellite_locker_unit_id_idx` (`satellite_locker_unit_id`),
  KEY `fk_locker_unit_id` (`locker_unit_id`),
  CONSTRAINT `fk_locker_unit_id` FOREIGN KEY (`locker_unit_id`) REFERENCES `locker_unit` (`ID`),
  CONSTRAINT `fk_satellite_locker_unit_id` FOREIGN KEY (`satellite_locker_unit_id`) REFERENCES `locker_unit` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `scheduled_reminders_results`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `scheduled_reminders_results`;
CREATE TABLE `scheduled_reminders_results` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `customer_id` bigint NOT NULL COMMENT 'ID of CUSTOMER record.',
  `location_id` bigint NOT NULL COMMENT 'ID of LOCATION record.',
  `num_of_users` int NOT NULL COMMENT 'Number of USER records processed to received reminders.',
  `process_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Time at which the current scheduled reminder process executes.',
  `scheduled_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'The configured time for scheduled reminders based on the Customer and Location setting in config_values.',
  `is_ran_at_scheduled_time` bit(1) NOT NULL DEFAULT b'0' COMMENT 'Scheduled reminders executed via scheduler indicated by true, otherwise those triggered on demand indicated by false.',
  PRIMARY KEY (`id`),
  KEY `idx_customer_location_expire_time` (`customer_id`,`location_id`,`scheduled_time`),
  KEY `fk_scheduled_reminder_results_location` (`location_id`),
  CONSTRAINT `fk_scheduled_reminder_results_customer` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `fk_scheduled_reminder_results_location` FOREIGN KEY (`location_id`) REFERENCES `location` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Summary of Scheduled Reminder Notification results by Customer and Location.';

-- -------------------------------------------------------------
-- Table structure for table `scim_entitlement`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `scim_entitlement`;
CREATE TABLE `scim_entitlement` (
  `id` int NOT NULL AUTO_INCREMENT,
  `value` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `display` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `value_UNIQUE` (`value`),
  CONSTRAINT `FK_SCIM_ENTITLEMENT_VALUE` FOREIGN KEY (`value`) REFERENCES `role` (`NAME`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `scim_group`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `scim_group`;
CREATE TABLE `scim_group` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `customer_id` bigint NOT NULL,
  `external_id` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created` timestamp NOT NULL,
  `last_modified` timestamp NOT NULL,
  `display_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_deleted` tinyint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `FK_SCIM_GROUP_CUSTOMER_ID_idx` (`customer_id`),
  KEY `idx_SCIM_GROUP_created` (`created`),
  CONSTRAINT `FK_SCIM_GROUP_CUSTOMER_ID_idx` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `scim_group_members`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `scim_group_members`;
CREATE TABLE `scim_group_members` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `scim_group_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `scim_resource_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'can be either SCIM_USER or SCIM_GROUP, as they are UUIDs we will assume there are not ever any collisions',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `idx_SCIM_GROUP_MEMBERS_SCIM_GROUP_ID_SCIM_RESOURCE_ID` (`scim_group_id`,`scim_resource_id`),
  KEY `FK_SCIM_GROUP_MEMBERS_SCIM_GROUP_ID_idx` (`scim_group_id`),
  CONSTRAINT `FK_SCIM_GROUP_MEMBERS_SCIM_GROUP_ID` FOREIGN KEY (`scim_group_id`) REFERENCES `scim_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `scim_user`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `scim_user`;
CREATE TABLE `scim_user` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `customer_id` bigint NOT NULL,
  `external_id` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created` timestamp NOT NULL,
  `last_modified` timestamp NOT NULL,
  `user_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `last_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `active` tinyint NOT NULL,
  `is_deleted` tinyint NOT NULL,
  `employee_number` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cost_center` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `organization` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `division` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `department` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `manager` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `rfid_badge` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `FK_SCIM_USER_CUSTOMER_ID_idx` (`customer_id`),
  KEY `idx_SCIM_USER_created` (`created`),
  CONSTRAINT `FK_SCIM_USER_CUSTOMER_ID` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `scim_user_entitlement`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `scim_user_entitlement`;
CREATE TABLE `scim_user_entitlement` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `scim_entitlement_id` int NOT NULL,
  `scim_user_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `FK_SCIM_USER_ENTITLEMENT_ID_idx` (`scim_entitlement_id`),
  KEY `FK_SCIM_USER_ENTITLEMENT_USER_ID` (`scim_user_id`),
  CONSTRAINT `FK_SCIM_USER_ENTITLEMENT_ID` FOREIGN KEY (`scim_entitlement_id`) REFERENCES `scim_entitlement` (`id`),
  CONSTRAINT `FK_SCIM_USER_ENTITLEMENT_USER_ID` FOREIGN KEY (`scim_user_id`) REFERENCES `scim_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `scim_user_map`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `scim_user_map`;
CREATE TABLE `scim_user_map` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `scim_user_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `user_id_UNIQUE` (`user_id`),
  KEY `FK_SCIM_USER_MAP_SCIM_USER_ID_idx` (`scim_user_id`),
  CONSTRAINT `FK_SCIM_USER_MAP_SCIM_USER_ID` FOREIGN KEY (`scim_user_id`) REFERENCES `scim_user` (`id`),
  CONSTRAINT `FK_SCIM_USER_MAP_USER_ID` FOREIGN KEY (`user_id`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `security_card`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `security_card`;
CREATE TABLE `security_card` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `INACTIVE` tinyint(1) DEFAULT NULL,
  `CARD_ID` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `DESCRIPTION` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `CUSTOMER_ID` bigint NOT NULL,
  `LAST_MODIFIED_TIME` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `LOCATION_ID` bigint DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_91` (`ID`),
  UNIQUE KEY `unique_security_card` (`CARD_ID`,`LOCATION_ID`,`CUSTOMER_ID`),
  KEY `FK_SECURITY_CARD_CUSTOMER_INDEX_9` (`CUSTOMER_ID`),
  KEY `FK_SECURITY_CARD_LOCATION_INDEX_9` (`LOCATION_ID`),
  CONSTRAINT `FK_SECURITY_CARD_CUSTOMER` FOREIGN KEY (`CUSTOMER_ID`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_SECURITY_CARD_LOCATION` FOREIGN KEY (`LOCATION_ID`) REFERENCES `location` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `sender`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `sender`;
CREATE TABLE `sender` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `NAME` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ADDRESS` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ZIP_CODE` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `first_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `last_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by` bigint DEFAULT NULL,
  `modified_time` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `customer_id` bigint DEFAULT NULL,
  `location_id` bigint DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_sender_customer` (`customer_id`),
  KEY `fk_sender_location` (`location_id`),
  KEY `updated_by` (`updated_by`),
  CONSTRAINT `fk_sender_customer` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `fk_sender_location` FOREIGN KEY (`location_id`) REFERENCES `location` (`ID`),
  CONSTRAINT `sender_ibfk_1` FOREIGN KEY (`updated_by`) REFERENCES `user` (`ID`),
  CONSTRAINT `sender_ibfk_2` FOREIGN KEY (`updated_by`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `shift`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `shift`;
CREATE TABLE `shift` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `uuid` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `customer_id` bigint NOT NULL,
  `location_id` bigint NOT NULL,
  `building_id` bigint DEFAULT NULL,
  `start_time` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '24hr format, based on location timezone',
  `end_time` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '24hr format, based on location timezone',
  `days_of_week` varchar(7) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '1111111' COMMENT '0 for disabled, 1 for enabled, starting from Monday. for cross-day shifts, marks the day at the start of the shift. based on location timezone.',
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'New Shift',
  `inactive` tinyint(1) DEFAULT NULL,
  `is_deleted` tinyint(1) DEFAULT NULL,
  `only_notify_shift_assets` tinyint(1) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `created_by` bigint DEFAULT NULL,
  `last_modified_at` timestamp NULL DEFAULT NULL,
  `last_modified_by` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `uuid_UNIQUE` (`uuid`),
  KEY `FK_SHIFT_CUSTOMER_ID` (`customer_id`),
  KEY `FK_SHIFT_LOCATION_ID` (`location_id`),
  KEY `FK_SHIFT_BUILDING_ID` (`building_id`),
  KEY `FK_SHIFT_CREATED_BY` (`created_by`),
  KEY `FK_SHIFT_LAST_MODIFIED_BY` (`last_modified_by`),
  CONSTRAINT `FK_SHIFT_BUILDING_ID` FOREIGN KEY (`building_id`) REFERENCES `building` (`ID`),
  CONSTRAINT `FK_SHIFT_CREATED_BY` FOREIGN KEY (`created_by`) REFERENCES `user` (`ID`),
  CONSTRAINT `FK_SHIFT_CUSTOMER_ID` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_SHIFT_LAST_MODIFIED_BY` FOREIGN KEY (`last_modified_by`) REFERENCES `user` (`ID`),
  CONSTRAINT `FK_SHIFT_LOCATION_ID` FOREIGN KEY (`location_id`) REFERENCES `location` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `shift_asset`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `shift_asset`;
CREATE TABLE `shift_asset` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `shift_id` bigint NOT NULL,
  `asset_tag` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `FK_SHIFT_PACKAGE_SHIFT_ID_idx` (`shift_id`),
  CONSTRAINT `FK_SHIFT_PACKAGE_SHIFT_ID` FOREIGN KEY (`shift_id`) REFERENCES `shift` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `state`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `state`;
CREATE TABLE `state` (
  `ID` int NOT NULL,
  `CODE` varchar(2) COLLATE utf8mb4_unicode_ci NOT NULL,
  `NAME` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_4` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `status_code`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `status_code`;
CREATE TABLE `status_code` (
  `CODE` int NOT NULL,
  `TYPE` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `DESCRIPTION` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `BIT_INDEX` int DEFAULT NULL,
  `APPLIES_TO_LOCKER` tinyint(1) DEFAULT NULL,
  `ID` int NOT NULL,
  `APPLIES_TO_LOCKER_DEVICE_ADDRESS` tinyint(1) DEFAULT '0',
  `USED_BY_CLIENTS` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_4C` (`CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `status_log`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `status_log`;
CREATE TABLE `status_log` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `AUTH_TOKEN` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `LOCKER_ID` bigint DEFAULT NULL,
  `MESSAGE` varchar(2000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `RECEIVED_TIME` timestamp NULL DEFAULT NULL,
  `CUSTOMER_ID` bigint DEFAULT NULL,
  `STATUS_CODE` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `LOCKER_UNIT_ID` bigint DEFAULT NULL,
  `LOCKER_DEVICE_ADDRESS_ID` bigint DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_2B` (`ID`),
  KEY `FK_STATUS_LOG_CUSTOMER_INDEX_2` (`CUSTOMER_ID`),
  KEY `FK_STATUS_LOG_TOKEN_INDEX_2` (`AUTH_TOKEN`),
  KEY `FK_STATUS_LOG_LOCKER_INDEX_2` (`LOCKER_ID`),
  KEY `FK_LOCKER_UNIT_ID_LOCKER_UNIT` (`LOCKER_UNIT_ID`),
  KEY `fk_status_log_locker_device_address` (`LOCKER_DEVICE_ADDRESS_ID`),
  CONSTRAINT `FK_STATUS_LOG_CUSTOMER` FOREIGN KEY (`CUSTOMER_ID`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_STATUS_LOG_LOCKER` FOREIGN KEY (`LOCKER_ID`) REFERENCES `locker` (`ID`),
  CONSTRAINT `fk_status_log_locker_device_address` FOREIGN KEY (`LOCKER_DEVICE_ADDRESS_ID`) REFERENCES `locker_device_address` (`id`),
  CONSTRAINT `FK_STATUS_LOG_TOKEN` FOREIGN KEY (`AUTH_TOKEN`) REFERENCES `user_session` (`AUTH_TOKEN`),
  CONSTRAINT `status_log_ibfk_1` FOREIGN KEY (`LOCKER_UNIT_ID`) REFERENCES `locker_unit` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `super_locker_admins`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `super_locker_admins`;
CREATE TABLE `super_locker_admins` (
  `ID` int NOT NULL,
  `FIRST_NAME` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `LAST_NAME` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `PHONE` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `EMAIL` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `INACTIVE` tinyint(1) DEFAULT NULL,
  `NOTIFY_ON_ERROR` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_96` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `system_properties`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `system_properties`;
CREATE TABLE `system_properties` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` varchar(5000) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_modified_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNIQUE_SYSTEM_PROPERTIES_NAME` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `tag`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `tag`;
CREATE TABLE `tag` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tag_type_id` int NOT NULL,
  `tag_option_id` int NOT NULL,
  `start_time` timestamp(3) NOT NULL COMMENT 'Start date-time for Tag to become active.',
  `end_time` timestamp(3) NULL DEFAULT NULL COMMENT 'End date-time for Tag to become inactive; NULL indicates indefinitely active.',
  `notes` varchar(250) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `customer_id` bigint NOT NULL,
  `location_id` bigint NOT NULL,
  `tracking_number` varchar(750) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_last_modified` bigint DEFAULT NULL,
  `sender_id` int DEFAULT NULL,
  `inactive` bit(1) DEFAULT b'0',
  `recipient_id` bigint DEFAULT NULL COMMENT 'Stores the Recipient id from User.ID column. Used to mark the particular TAG to the recipient',
  `signature_waived` tinyint DEFAULT '0',
  `package_group_external_id` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_tag_customer_id` (`customer_id`),
  KEY `fk_tag_tag_type_id` (`tag_type_id`),
  KEY `fk_tag_tag_option_id` (`tag_option_id`),
  KEY `fk_user_recipient_id1` (`recipient_id`),
  KEY `fk_tag_pkg_group_id` (`package_group_external_id`),
  KEY `idx_tag_location_id_tracking_number` (`location_id`,`tracking_number`),
  CONSTRAINT `fk_tag_customer_id` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`),
  CONSTRAINT `fk_tag_location_id` FOREIGN KEY (`location_id`) REFERENCES `location` (`ID`),
  CONSTRAINT `fk_tag_pkg_group_id` FOREIGN KEY (`package_group_external_id`) REFERENCES `package_group` (`package_group_external_id`),
  CONSTRAINT `fk_tag_tag_option_id` FOREIGN KEY (`tag_option_id`) REFERENCES `tag_option` (`id`),
  CONSTRAINT `fk_tag_tag_type_id` FOREIGN KEY (`tag_type_id`) REFERENCES `tag_type` (`id`),
  CONSTRAINT `fk_user_recipient_id1` FOREIGN KEY (`recipient_id`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='User defined Tags based on the TagType (entity) and TagOption (how to handle).';

-- -------------------------------------------------------------
-- Table structure for table `tag_option`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `tag_option`;
CREATE TABLE `tag_option` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tag_type_id` int NOT NULL,
  `name` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` varchar(250) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_tag_type_id` (`tag_type_id`),
  CONSTRAINT `fk_tag_type_id` FOREIGN KEY (`tag_type_id`) REFERENCES `tag_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Defines the handling for a Tag - notes only, set alt recipient, set alt address.';

-- -------------------------------------------------------------
-- Table structure for table `tag_type`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `tag_type`;
CREATE TABLE `tag_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` varchar(250) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Defines the entity type to apply a Tag to - User, Package, Sender.';

-- -------------------------------------------------------------
-- Table structure for table `task`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `task`;
CREATE TABLE `task` (
  `ID` int NOT NULL,
  `LABEL` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `OBJECT_NAME` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `DESCRIPTION` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_272` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `task_action_role`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `task_action_role`;
CREATE TABLE `task_action_role` (
  `ID` int NOT NULL,
  `TASK_ID` int DEFAULT NULL,
  `ACTION_ID` int DEFAULT NULL,
  `ROLE_ID` int DEFAULT NULL,
  `LAST_MODIFIED_TIME` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_AB` (`ID`),
  KEY `FK_TASK_ACTION_ROLE_ACTION_INDEX_A` (`ACTION_ID`),
  KEY `FK_TASK_ACTION_ROLE_TASK_INDEX_A` (`TASK_ID`),
  KEY `FK_TASK_ACTION_ROLE_ROLE_INDEX_A` (`ROLE_ID`),
  CONSTRAINT `FK_TASK_ACTION_ROLE_ACTION` FOREIGN KEY (`ACTION_ID`) REFERENCES `action` (`ID`),
  CONSTRAINT `FK_TASK_ACTION_ROLE_ROLE` FOREIGN KEY (`ROLE_ID`) REFERENCES `role` (`ID`),
  CONSTRAINT `FK_TASK_ACTION_ROLE_TASK` FOREIGN KEY (`TASK_ID`) REFERENCES `task` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `temperature_unit`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `temperature_unit`;
CREATE TABLE `temperature_unit` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `tenant`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `tenant`;
CREATE TABLE `tenant` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `NAME` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `INACTIVE` tinyint(1) DEFAULT NULL,
  `UNIT` varchar(24) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `PHONE` varchar(24) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `EMAIL` varchar(225) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `LOCATION_ID` bigint NOT NULL,
  `CUSTOMER_ID` bigint NOT NULL,
  `LAST_MODIFIED_TIME` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `PASSCODE` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `external_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `represents_customer` tinyint(1) DEFAULT NULL,
  `building_id` bigint DEFAULT NULL,
  `last_passcode_created_time` timestamp NULL DEFAULT NULL,
  `modified_by_user_id` bigint DEFAULT NULL,
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by_user_id` bigint DEFAULT NULL,
  `latitude` decimal(8,6) DEFAULT NULL,
  `longitude` decimal(9,6) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_93` (`ID`),
  UNIQUE KEY `IDX_UNIQUE_PASSCODE` (`PASSCODE`,`CUSTOMER_ID`),
  KEY `FK_TENANT_CUSTOMER_INDEX_9` (`CUSTOMER_ID`),
  KEY `FK_TENANT_LOCATION_INDEX_9` (`LOCATION_ID`),
  KEY `IDX_TENANT_PASSCODE` (`PASSCODE`),
  KEY `fk_tenant_building` (`building_id`),
  CONSTRAINT `fk_tenant_building` FOREIGN KEY (`building_id`) REFERENCES `building` (`ID`),
  CONSTRAINT `FK_TENANT_CUSTOMER` FOREIGN KEY (`CUSTOMER_ID`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_TENANT_LOCATION` FOREIGN KEY (`LOCATION_ID`) REFERENCES `location` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `time_zone`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `time_zone`;
CREATE TABLE `time_zone` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `time_zone` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `transaction`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `transaction`;
CREATE TABLE `transaction` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `transaction_session_id` bigint NOT NULL,
  `is_deposit` tinyint(1) NOT NULL,
  `start_time` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `end_time` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`id`),
  KEY `idx_transaction_transaction_session_id` (`transaction_session_id`),
  CONSTRAINT `FK_transaction_transaction_session_id` FOREIGN KEY (`transaction_session_id`) REFERENCES `transaction_session` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `transaction_session`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `transaction_session`;
CREATE TABLE `transaction_session` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `start_time` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `end_time` timestamp(3) NULL DEFAULT NULL,
  `is_timeout` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_transaction_session_user_id` (`user_id`),
  CONSTRAINT `FK_transaction_session_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `twilio_incoming_message`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `twilio_incoming_message`;
CREATE TABLE `twilio_incoming_message` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `to` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `customer_id` bigint DEFAULT NULL,
  `from` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `body` varchar(300) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `action_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'should be "opt_in", "opt_out", or "info"',
  `response` varchar(300) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `received_time` timestamp NOT NULL,
  `created_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `is_twilio_keyword` tinyint(1) DEFAULT NULL,
  `is_delayed` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_TWILIO_INCOMING_MESSAGE_CUSTOMER` (`customer_id`),
  CONSTRAINT `FK_TWILIO_INCOMING_MESSAGE_CUSTOMER` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `ui_skin`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `ui_skin`;
CREATE TABLE `ui_skin` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `user`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `FIRST_NAME` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `LAST_NAME` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `DESCRIPTION` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `INACTIVE` tinyint(1) DEFAULT NULL,
  `PHOTO` blob,
  `PHONE` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `EMAIL` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `IS_AUTHORIZED_USER_FOR_TENANT` tinyint(1) DEFAULT NULL,
  `ACCOUNT_ID` bigint DEFAULT NULL,
  `CUSTOMER_ID` bigint DEFAULT NULL,
  `LOCATION_ID` bigint DEFAULT NULL,
  `TENANT_ID` bigint DEFAULT NULL,
  `LAST_MODIFIED_TIME` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `PASSCODE` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `BUILDING_ID` bigint DEFAULT NULL,
  `external_id` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `unit_no` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `updated_by_user_id` bigint DEFAULT NULL,
  `delegate_notifications_to_user_id` bigint DEFAULT NULL,
  `keep_local_changes` tinyint(1) DEFAULT NULL,
  `needs_wheel_chair_access` tinyint(1) DEFAULT NULL,
  `preferred_communication_method1` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `preferred_communication_method2` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `preferred_communication_method3` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `OPT_OUT_OPTION` tinyint(1) DEFAULT NULL,
  `EMAIL_UNSUBSCRIBE` tinyint(1) DEFAULT NULL,
  `PHONE_UNSUBSCRIBE` tinyint(1) DEFAULT NULL,
  `NUM_LOGIN_RETRIES` int DEFAULT NULL,
  `LAST_FAILED_ATTEMPT` timestamp NULL DEFAULT NULL,
  `HAS_SPECIAL_STATUS` tinyint(1) DEFAULT '0',
  `ADDRESS_LINE1` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ADDRESS_LINE2` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `CITY` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `STATE` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ZIP_CODE` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `last_passcode_created_time` timestamp NULL DEFAULT NULL,
  `auth_id` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Identifer for an externally authenticated User used to reconcile the internal User record.',
  `UUID` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `voice_call_phone` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `badge_id` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_273` (`ID`),
  UNIQUE KEY `user_external_id_idx` (`CUSTOMER_ID`,`LOCATION_ID`,`external_id`),
  UNIQUE KEY `IDX_UNIQUE_PASSCODE` (`PASSCODE`,`CUSTOMER_ID`),
  UNIQUE KEY `idx_USER_auth_id_CUSTOMER_ID_LOCATION_ID_unique` (`auth_id`,`CUSTOMER_ID`,`LOCATION_ID`),
  KEY `IX_USER_LAST_NAME` (`LAST_NAME`),
  KEY `FK_USER_TENANT_INDEX_2` (`TENANT_ID`),
  KEY `FK_USER_ACCOUNT_INDEX_2` (`ACCOUNT_ID`),
  KEY `IDX_USER_PASSCODE` (`PASSCODE`),
  KEY `FK_USER_CUSTOMER_INDEX_2` (`CUSTOMER_ID`),
  KEY `IX_USER_FIRST_NAME` (`FIRST_NAME`),
  KEY `FK_USER_LOCATION_INDEX_2` (`LOCATION_ID`),
  KEY `FK_USER_BUILDING_INDEX_2` (`BUILDING_ID`),
  KEY `last_modified_idx` (`CUSTOMER_ID`,`LOCATION_ID`,`LAST_MODIFIED_TIME`),
  CONSTRAINT `FK_USER_ACCOUNT` FOREIGN KEY (`ACCOUNT_ID`) REFERENCES `account` (`ID`),
  CONSTRAINT `FK_USER_BUILDING` FOREIGN KEY (`BUILDING_ID`) REFERENCES `building` (`ID`),
  CONSTRAINT `FK_USER_CUSTOMER` FOREIGN KEY (`CUSTOMER_ID`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_USER_LOCATION` FOREIGN KEY (`LOCATION_ID`) REFERENCES `location` (`ID`),
  CONSTRAINT `FK_USER_TENANT` FOREIGN KEY (`TENANT_ID`) REFERENCES `tenant` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `user_alerts`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `user_alerts`;
CREATE TABLE `user_alerts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `alert` varchar(250) COLLATE utf8mb4_unicode_ci NOT NULL,
  `expires_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_user_alert_idx` (`user_id`),
  CONSTRAINT `fk_user_alert` FOREIGN KEY (`user_id`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='        ';

-- -------------------------------------------------------------
-- Table structure for table `user_purge_results`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `user_purge_results`;
CREATE TABLE `user_purge_results` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `customer_id` bigint NOT NULL COMMENT 'ID of CUSTOMER record.',
  `location_id` bigint NOT NULL COMMENT 'ID of LOCATION record.',
  `num_of_users` int NOT NULL COMMENT 'Number of USER records purged.',
  `num_of_user_sessions` int NOT NULL COMMENT 'Number of USER_SESSION records deleted.',
  `num_of_emails` int NOT NULL COMMENT 'Number of PACKAGE_COMMUNICATION_EMAIL records purged.',
  `num_of_sms` int NOT NULL COMMENT 'Number of PACAKGE_COMMUNICATION_SMS records purged.',
  `purge_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Time at which the current purge job executes.',
  `expire_purge_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'The configured time for purge based on the Customer and Location setting in config_values.',
  `is_ran_at_expire_time` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Purge job executed via scheduler indicated by true, otherwise on demand purge indicated by false.',
  PRIMARY KEY (`id`),
  KEY `idx_customer_location_expire_time` (`customer_id`,`location_id`,`expire_purge_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Summary of User Registration purge results by Customer and Location.';

-- -------------------------------------------------------------
-- Table structure for table `user_registration`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `user_registration`;
CREATE TABLE `user_registration` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `reg_status_id` int NOT NULL,
  `last_modified_time` datetime NOT NULL,
  `last_modified_user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`,`reg_status_id`),
  KEY `id_idx` (`user_id`),
  KEY `reg_status_id_idx` (`reg_status_id`),
  KEY `last_modified_user_id_idx` (`last_modified_user_id`),
  CONSTRAINT `last_modified_user_id` FOREIGN KEY (`last_modified_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `reg_status_id` FOREIGN KEY (`reg_status_id`) REFERENCES `registration_status` (`ID`),
  CONSTRAINT `user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `user_registration_status_log`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `user_registration_status_log`;
CREATE TABLE `user_registration_status_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` bigint DEFAULT NULL,
  `reg_status_id` int NOT NULL,
  `created_by_user_id` bigint DEFAULT NULL,
  `created_by_user_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`,`reg_status_id`),
  KEY `user_id_idx` (`user_id`),
  KEY `reg_status_id_idx` (`reg_status_id`),
  KEY `fk_usrlog_created_by_user_id` (`created_by_user_id`),
  CONSTRAINT `fk_usrlog_created_by_user_id` FOREIGN KEY (`created_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `fk_usrlog_reg_status_id` FOREIGN KEY (`reg_status_id`) REFERENCES `registration_status` (`ID`),
  CONSTRAINT `fk_usrlog_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `user_role`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `user_role`;
CREATE TABLE `user_role` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ROLE_ID` int DEFAULT NULL,
  `USER_ID` bigint DEFAULT NULL,
  `SCOPE` bigint DEFAULT NULL,
  `SCOPE_ID` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `LAST_MODIFIED_TIME` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `v_scope` bigint GENERATED ALWAYS AS (ifnull(`SCOPE`,-(1))) VIRTUAL,
  `v_scope_id` varchar(36) COLLATE utf8mb4_unicode_ci GENERATED ALWAYS AS (ifnull(`SCOPE_ID`,_utf8mb4'-1')) VIRTUAL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `PRIMARY_KEY_B` (`id`),
  UNIQUE KEY `idx_USER_ROLE_USER_ID_ROLE_ID_v_scope_v_scope_id` (`USER_ID`,`ROLE_ID`,`v_scope`,`v_scope_id`),
  KEY `FK_USER_ROLE_USER_INDEX_B` (`USER_ID`),
  KEY `FK_USER_ROLE_ROLE_INDEX_B` (`ROLE_ID`),
  KEY `FK_USER_ROLE_SCOPE` (`SCOPE`),
  CONSTRAINT `FK_USER_ROLE_ROLE` FOREIGN KEY (`ROLE_ID`) REFERENCES `role` (`ID`),
  CONSTRAINT `FK_USER_ROLE_SCOPE` FOREIGN KEY (`SCOPE`) REFERENCES `role_scope` (`id`),
  CONSTRAINT `FK_USER_ROLE_USER` FOREIGN KEY (`USER_ID`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `user_role_status_log`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `user_role_status_log`;
CREATE TABLE `user_role_status_log` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `role_id` int DEFAULT NULL,
  `SCOPE` bigint DEFAULT NULL,
  `SCOPE_ID` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `created_by_user_id` bigint NOT NULL,
  `revoked` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `FK_USER_STATUS_LOG_USER` (`user_id`),
  KEY `FK_USER_STATUS_LOG_ROLE` (`role_id`),
  KEY `FK_USER_STATUS_LOG_CREATED_USER` (`created_by_user_id`),
  KEY `FK_user_role_status_log_SCOPE` (`SCOPE`),
  CONSTRAINT `FK_user_role_status_log_SCOPE` FOREIGN KEY (`SCOPE`) REFERENCES `role_scope` (`id`),
  CONSTRAINT `user_role_status_log_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `user_role_status_log_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `role` (`ID`),
  CONSTRAINT `user_role_status_log_ibfk_3` FOREIGN KEY (`created_by_user_id`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `user_session`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `user_session`;
CREATE TABLE `user_session` (
  `ID` bigint NOT NULL AUTO_INCREMENT,
  `USER_ID` bigint DEFAULT NULL,
  `AUTH_TOKEN` varchar(36) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `TEMP_PASSCODE` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `TEMP_PASSCODE_EXPIRES` timestamp NULL DEFAULT NULL,
  `USER_AGENT` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `DEVICE_TYPE` int DEFAULT NULL,
  `DEVICE_TOKEN` varchar(1024) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `INACTIVE` tinyint(1) DEFAULT NULL,
  `CUSTOMER_ID` bigint DEFAULT NULL,
  `SIGNIN_TIME` timestamp NULL DEFAULT NULL,
  `expiration_time` timestamp NULL DEFAULT NULL,
  `SIGNOUT_TIME` timestamp NULL DEFAULT NULL,
  `LAST_MODIFIED_TIME` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `LAST_PING_TIME` timestamp NULL DEFAULT NULL,
  `LAST_NOTIFICATION_TIME` timestamp NULL DEFAULT NULL,
  `building_id` bigint DEFAULT NULL,
  `REFRESH_TOKEN` varchar(2048) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `REFRESH_TOKEN_EXPIRES_AFTER` timestamp NULL DEFAULT NULL,
  `app_token` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `do_not_refresh` tinyint DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_5` (`ID`),
  KEY `IDX_USER_SESSION_TIME_DESC` (`SIGNIN_TIME`),
  KEY `IDX_USER_SESSION_LAST_PING_TIME` (`LAST_PING_TIME`),
  KEY `IDX_USER_SESSION_AUTH_TOKEN` (`AUTH_TOKEN`),
  KEY `IDX_USER_SESSION_LAST_NOTIFICATION_TIME` (`LAST_NOTIFICATION_TIME`),
  KEY `FK_USER_SESSION_DEVICE_TYPE_INDEX_5` (`DEVICE_TYPE`),
  KEY `FK_USER_SESSION_CUSTOMER_ID_INDEX_5` (`CUSTOMER_ID`),
  KEY `IDX_USER_SESSION_SIGNOUT_TIME` (`SIGNOUT_TIME`),
  KEY `IDX_USER_SESSION_USER_ID` (`USER_ID`),
  KEY `fk_user_session_building` (`building_id`),
  CONSTRAINT `fk_user_session_building` FOREIGN KEY (`building_id`) REFERENCES `building` (`ID`),
  CONSTRAINT `FK_USER_SESSION_CUSTOMER_ID` FOREIGN KEY (`CUSTOMER_ID`) REFERENCES `customer` (`ID`),
  CONSTRAINT `FK_USER_SESSION_DEVICE_TYPE` FOREIGN KEY (`DEVICE_TYPE`) REFERENCES `device_type` (`ID`),
  CONSTRAINT `FK_USER_SESSION_USER_ID` FOREIGN KEY (`USER_ID`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `user_setting_props`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `user_setting_props`;
CREATE TABLE `user_setting_props` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `default_value` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Here we can store -1 which indicates that this setting should not be returned unless it is overriden in the child table',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='table used to store the user level setting definitions like scanner preferences, page size, report duration, etc.';

-- -------------------------------------------------------------
-- Table structure for table `user_setting_values`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `user_setting_values`;
CREATE TABLE `user_setting_values` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_setting_props_id` bigint DEFAULT NULL,
  `value` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_id_setting_property_id` (`user_setting_props_id`,`user_id`),
  KEY `fk_setting_values_user` (`user_id`),
  CONSTRAINT `fk_setting_values_setting_props` FOREIGN KEY (`user_setting_props_id`) REFERENCES `user_setting_props` (`id`),
  CONSTRAINT `fk_setting_values_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='table used to store the user level settings like scanner preferences, page size, report duration, etc.';

-- -------------------------------------------------------------
-- Table structure for table `user_tenants`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `user_tenants`;
CREATE TABLE `user_tenants` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `tenant_id` bigint NOT NULL,
  `last_modified_by_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `last_modified_by_user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_USER_ID_idx` (`user_id`),
  KEY `FK_TENANT_ID_idx` (`tenant_id`),
  KEY `FK_LAT_MODIFIED_ID_idx` (`last_modified_by_user_id`),
  CONSTRAINT `FK_LAT_MODIFIED_ID` FOREIGN KEY (`last_modified_by_user_id`) REFERENCES `user` (`ID`),
  CONSTRAINT `FK_TENANT_ID` FOREIGN KEY (`tenant_id`) REFERENCES `tenant` (`ID`),
  CONSTRAINT `FK_USER_ID` FOREIGN KEY (`user_id`) REFERENCES `user` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `verified_transactional_email_domains`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `verified_transactional_email_domains`;
CREATE TABLE `verified_transactional_email_domains` (
  `id` int NOT NULL AUTO_INCREMENT,
  `domain` varchar(300) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table structure for table `version`
-- -------------------------------------------------------------
DROP TABLE IF EXISTS `version`;
CREATE TABLE `version` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `CURRENT` int DEFAULT NULL,
  `DESCRIPTION` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PRIMARY_KEY_3` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================
-- Stored Functions and Procedures
-- =============================================================

-- -------------------------------------------------------------
-- Function: STRINGDECODE
-- Decodes unicode escape sequences (e.g. \uXXXX) in text strings
-- -------------------------------------------------------------
DROP FUNCTION IF EXISTS `STRINGDECODE`;
DELIMITER $$
CREATE FUNCTION `STRINGDECODE`(str TEXT CHARSET utf8mb4)
RETURNS text CHARSET utf8mb4 DETERMINISTIC
BEGIN
declare pos int;
declare escape char(6) charset utf8mb4;
declare unescape char(3) charset utf8mb4;
set pos = locate('\\u', str);
while pos > 0 do
    set escape = substring(str, pos, 6);
    set unescape = char(conv(substring(escape,3),16,10) using ucs2);
    set str = replace(str, escape, unescape);
    set pos = locate('\\u', str, pos+1);
end while;
return str;
END$$
DELIMITER ;

-- -------------------------------------------------------------
-- Function: GetUserRoleNames
-- Returns comma-delimited role names for a given user ID
-- -------------------------------------------------------------
DROP FUNCTION IF EXISTS `GetUserRoleNames`;
DELIMITER $$
CREATE FUNCTION `GetUserRoleNames` (
 	userId BIGINT
)
RETURNS VARCHAR(255) CHARSET utf8mb4
READS SQL DATA
BEGIN
	DECLARE roleStr VARCHAR(255);
	SELECT 
		GROUP_CONCAT(R.NAME) AS Roles
	FROM 
		`user` U, `role` R, `user_role` UR  
	WHERE
		U.ID = UR.USER_ID AND 
	    R.ID = UR.ROLE_ID AND
	    U.ID = userId
	INTO 
		roleStr;
	RETURN roleStr;
END$$
DELIMITER ;

-- -------------------------------------------------------------
-- Procedure: GetUpdatedTenantsUsers
-- Retrieves updated tenants and users for a customer location
-- -------------------------------------------------------------
DROP PROCEDURE IF EXISTS `GetUpdatedTenantsUsers`;
DELIMITER $$
CREATE PROCEDURE `GetUpdatedTenantsUsers` (
 	IN lastModifiedTime TIMESTAMP,
 	IN customerId BIGINT,
 	IN locationId BIGINT
)
BEGIN
	SELECT 
		ID AS 'tenant.id', 
		NAME AS 'tenant.name', 
		INACTIVE AS 'tenant.inactive', 
		UNIT AS 'tenant.unit', 
		PHONE AS 'tenant.phone', 
		EMAIL AS 'tenant.email', 
		LOCATION_ID AS 'tenant.location_id',
		CUSTOMER_ID AS 'tenant.customer_id', 
		LAST_MODIFIED_TIME, 
		PASSCODE AS 'tenant.passcode', 
		represents_customer AS 'represents_customer', 
		building_id AS 'tenant.building_id',
		external_id AS 'tenant.external_id',
		latitude AS 'tenant.latitude',
		longitude AS 'tenant.longitude'
	FROM 
		`tenant` 
	WHERE
		CUSTOMER_ID = customerId AND LOCATION_ID = locationId AND LAST_MODIFIED_TIME >= lastModifiedTime;
	
	SELECT     
		ID, FIRST_NAME, LAST_NAME, DESCRIPTION, INACTIVE, PHONE, EMAIL, IS_AUTHORIZED_USER_FOR_TENANT, 
		CUSTOMER_ID, LOCATION_ID, TENANT_ID, BUILDING_ID, unit_no, needs_wheel_chair_access, OPT_OUT_OPTION,
		GetUserRoleNames(ID) AS ROLES
	FROM 
		`user` 
	WHERE
		CUSTOMER_ID = customerId AND LOCATION_ID = locationId 
		AND LAST_MODIFIED_TIME >= lastModifiedTime AND TENANT_ID IS NOT NULL;		
END$$
DELIMITER ;

-- -------------------------------------------------------------
-- Procedure: get_maint_location_schedule_status
-- Returns schedule settings and last service date for maintenance location
-- -------------------------------------------------------------
DROP PROCEDURE IF EXISTS `get_maint_location_schedule_status`;
DELIMITER $$
CREATE PROCEDURE `get_maint_location_schedule_status` (
	IN _maint_location_id BIGINT(20),
	OUT _schedule_start_time TIME,
    OUT _schedule_end_time TIME,
    OUT _last_service_date TIMESTAMP,
    OUT _freq_id SMALLINT(2),
    OUT _freq_value VARCHAR(128),
    OUT _timezone VARCHAR(100),
    OUT _maintLocationCount SMALLINT(2)
)
BEGIN
	SELECT COUNT(*) INTO _maintLocationCount FROM `maint_location` WHERE ID = _maint_location_id AND (INACTIVE IS NULL OR INACTIVE = 0);

	IF ( _maintLocationCount > 0 ) THEN 
		SELECT START_TIME, END_TIME, MAINT_FREQUENCY_ID, MAINT_FREQUENCY_VALUE, TZ.time_zone  
		INTO _schedule_start_time, _schedule_end_time, _freq_id, _freq_value, _timezone
		FROM `maint_schedule` MS 
			LEFT JOIN `maint_location` ML ON ML.ID = MS.MAINT_LOCATION_ID
			LEFT JOIN `time_zone` TZ ON TZ.ID = ML.TIME_ZONE_ID
			WHERE MS.MAINT_LOCATION_ID = _maint_location_id AND ( MS.INACTIVE IS NULL OR MS.INACTIVE = 0 )
			ORDER BY MS.ID DESC LIMIT 1;
			
		SELECT MAX(MS.END_DATE) INTO _last_service_date FROM `maint_service` MS, `maint_location` ML
			WHERE MS.MAINT_LOCATION_ID = ML.ID AND ( ML.INACTIVE = 0 OR ML.INACTIVE IS NULL )
				AND MS.MAINT_LOCATION_ID = _maint_location_id; 
	END IF;
END$$
DELIMITER ;

-- -------------------------------------------------------------
-- Procedure: init_package_status_for_customer_location
-- Initializes default package status configuration for customer location
-- -------------------------------------------------------------
-- #####################################################################################
--
-- PROC NAME: init_package_status_for_customer_location
--
-- INPUT: 
--	_customerId BIGINT(20) : ID of Customer
--	_locationId BIGINT(20) : ID of Location
--
-- RETURN:
-- String summarizing the number of rows inserted into the relevant tables.
-- On success, the value should always be 'PS Assignments: 13 | PS Rules: 44 | PS EditModes: 15 | PGS Transitions : 14'.
--
-- USAGE: CALL init_package_status_for_customer_location(2,4);
--
-- DESCRIPTION: 
-- Creates all the default Package Status configurations for the specified
-- Customer and Location by inserting the required information into the tables:
-- package_status_assignment, package_status_rules, package_status_edit_mode_assignment
--
-- PURPOSE:
-- Initialization procedure to call when Customer is onboarded and with each new Location.
-- For the revamped Mailroom application which introduced custom Package Status 
-- configuration, this procedure is executed for all existing Customers and Locations.
--
-- #####################################################################################

DROP PROCEDURE IF EXISTS `init_package_status_for_customer_location`;
DELIMITER $$

CREATE PROCEDURE `init_package_status_for_customer_location` (
	IN _customerId BIGINT(20),
	IN _locationId BIGINT(20)
)

BEGIN

DECLARE total_psa INT DEFAULT 0;
DECLARE total_psr INT DEFAULT 0;
DECLARE total_psema INT DEFAULT 0;
DECLARE total_pgst INT DEFAULT 0;


DECLARE package_status_config_exists CONDITION FOR SQLSTATE '45000'; -- SET MESSAGE_TEXT = 'Order No not found in orders table'; 01234

DECLARE EXIT HANDLER FOR package_status_config_exists
	BEGIN
		SELECT CONCAT('Customer:',_customerId,', Location:',_locationId,' has already configured Package Status.') AS MESSAGE;
		ROLLBACK;
        RESIGNAL;        
	END;

DECLARE EXIT HANDLER FOR SQLEXCEPTION
	BEGIN
		SELECT CONCAT('SQLEXCEPTION for (',_customerId,',',_locationId,') occurred.  Procedure has rollbacked.') AS MESSAGE;
		ROLLBACK;
        RESIGNAL;        
	END;

DECLARE EXIT HANDLER FOR SQLWARNING
	BEGIN
		SELECT CONCAT('SQLWARNING for (',_customerId,',',_locationId,') occurred.  Procedure has rollbacked.') AS MESSAGE;
		ROLLBACK;
        RESIGNAL;        
	END;

	IF EXISTS 
		( SELECT 1 FROM package_status_assignment WHERE customer_id = _customerId AND location_id = _locationId LIMIT 1 )
	THEN
		SIGNAL package_status_config_exists;
	END IF;	
	
START TRANSACTION;
	
	INSERT INTO package_status_assignment (status_id, name, ordinal, color, customer_id, location_id) VALUES 
    (0, 'received', 1, '#3c3bee', _customerId, _locationId),
    (1, 'delivered to station', 3, '#4ce554', _customerId, _locationId),
    (2, 'released', 4, '#a0f84e', _customerId, _locationId),
    (3, 'sent back', 7, '#f2de68', _customerId, _locationId),
    (4, 'attempted to deliver', 6, '#ea3030', _customerId, _locationId),
    (5, 'courier to mailroom', 0, '#8248f1', _customerId, _locationId),
    (6, 'in transit', 2, '#4aebf2', _customerId, _locationId),
    (7, 'return to hub', 5, '#f5973f', _customerId, _locationId);
    

	SET total_psa = ROW_COUNT();
    
	-- received
	INSERT INTO package_status_rules (status_id, allowed_status_id, customer_id, location_id) VALUES 
    -- (0, 0, _customerId, _locationId),	-- received
	(0, 1, _customerId, _locationId),	-- delivered_to_station
	(0, 2, _customerId, _locationId),	-- released
	(0, 3, _customerId, _locationId),	-- sent back
	(0, 4, _customerId, _locationId),	-- attempted to deliver
	(0, 6, _customerId, _locationId),	-- in transit
	(0, 7, _customerId, _locationId),	-- return to hub
	
	-- delivered_to_station
	-- (1, 1, _customerId, _locationId),	-- delivered_to_station
	(1, 2, _customerId, _locationId),	-- released
	(1, 3, _customerId, _locationId),	-- sent back
	(1, 4, _customerId, _locationId),	-- attempted to deliver
	(1, 6, _customerId, _locationId),	-- in transit
	(1, 7, _customerId, _locationId),	-- return to hub
		
	-- released
	-- INSERT INTO package_status_rules (status_id, allowed_status_id, customer_id, location_id) VALUES (2, ?, _customerId, _locationId);
	
	-- sent back
	-- INSERT INTO package_status_rules (status_id, allowed_status_id, customer_id, location_id) VALUES (3, ?, _customerId, _locationId);
	
	-- attempted to deliver
	(4, 4, _customerId, _locationId),	-- attempted to deliver
	(4, 1, _customerId, _locationId),	-- delivered_to_station
	(4, 2, _customerId, _locationId),	-- released
	(4, 3, _customerId, _locationId),	-- sent back
	(4, 6, _customerId, _locationId),	-- in transit
	(4, 7, _customerId, _locationId),	-- return to hub
	
	-- courier to mailroom
	-- (5, 5, _customerId, _locationId),	-- courier to mailroom
	(5, 0, _customerId, _locationId),	-- received
	(5, 1, _customerId, _locationId),	-- delivered_to_station
	(5, 2, _customerId, _locationId),	-- released
	(5, 3, _customerId, _locationId),	-- sent back
	
	-- in transit
	(6, 6, _customerId, _locationId),	-- in transit
	(6, 1, _customerId, _locationId),	-- delivered_to_station
	(6, 2, _customerId, _locationId),	-- released
	(6, 3, _customerId, _locationId),	-- sent back
	(6, 4, _customerId, _locationId),	-- attempted to deliver
	(6, 7, _customerId, _locationId),	-- return to hub

	-- return to hub
	(7, 7, _customerId, _locationId),	-- return to hub
	(7, 1, _customerId, _locationId),	-- delivered_to_station
	(7, 2, _customerId, _locationId),	-- released
	(7, 3, _customerId, _locationId),	-- sent back
	(7, 4, _customerId, _locationId),	-- attempted to deliver
	(7, 6, _customerId, _locationId),	-- in transit
	(1, 2, _customerId,  _locationId),
	(1, 3, _customerId,  _locationId);
	
    SET total_psr = ROW_COUNT();

    
	INSERT INTO package_status_edit_mode_assignment (package_status_assignment_id, edit_mode) VALUES 
	-- received
	( (SELECT ID FROM package_status_assignment WHERE customer_id = _customerId AND location_id = _locationId AND status_id = 0), 2),
	( (SELECT ID FROM package_status_assignment WHERE customer_id = _customerId AND location_id = _locationId AND status_id = 0), 4),
	
	-- delivered_to_station
	( (SELECT ID FROM package_status_assignment WHERE customer_id = _customerId AND location_id = _locationId AND status_id = 1), 3),
	
	-- released
	( (SELECT ID FROM package_status_assignment WHERE customer_id = _customerId AND location_id = _locationId AND status_id = 2), 1),
	
	-- sent back
	( (SELECT ID FROM package_status_assignment WHERE customer_id = _customerId AND location_id = _locationId AND status_id = 3), 1),
	
	-- attempted to deliver
	( (SELECT ID FROM package_status_assignment WHERE customer_id = _customerId AND location_id = _locationId AND status_id = 4), 3),
	
	-- courier to mailroom
	( (SELECT ID FROM package_status_assignment WHERE customer_id = _customerId AND location_id = _locationId AND status_id = 5), 2),
	( (SELECT ID FROM package_status_assignment WHERE customer_id = _customerId AND location_id = _locationId AND status_id = 5), 4),
	
	-- in transit
	( (SELECT ID FROM package_status_assignment WHERE customer_id = _customerId AND location_id = _locationId AND status_id = 6), 3),
	
	-- return to hub
	( (SELECT ID FROM package_status_assignment WHERE customer_id = _customerId AND location_id = _locationId AND status_id = 7), 3);
    
    SET total_psema = ROW_COUNT();
    
INSERT INTO package_group_status_transition ( package_group_status_id, package_group_allowed_status_id, location_id, customer_id) VALUES (7, 5, _locationId, _customerId),
(5, 10, _locationId, _customerId),
(5, 11, _locationId, _customerId),
(11, 12, _locationId, _customerId),
(11, 13, _locationId, _customerId),
(12, 13, _locationId, _customerId),
(13, 5, _locationId, _customerId),
(10, 14, _locationId, _customerId),
(10, 11, _locationId, _customerId),
(14, 8, _locationId, _customerId),
(14, 9, _locationId, _customerId),
(6, 5, _locationId, _customerId),
(10, 2, _locationId, _customerId),
(5, 2, _locationId, _customerId),
(5, 14, _locationId, _customerId);

   SET total_pgst = ROW_COUNT();

	SELECT CONCAT('PS Assignments: ', total_psa, ' | PS Rules: ',total_psr, ' | PS EditModes: ', total_psema, '| PG Transitions: ', total_pgst);

COMMIT;


END$$


DELIMITER ;

SET FOREIGN_KEY_CHECKS = 1;