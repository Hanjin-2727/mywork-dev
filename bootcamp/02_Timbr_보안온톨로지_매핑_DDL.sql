-- ====================================================================
-- 🛡️ Timbr 보안 온톨로지 매핑 DDL (부트캠프 5번 정보보안 실습)
-- 데이터소스: bootcamp_supabase (PostgreSQL 17)
-- 스키마: security
-- ====================================================================

-- --------------------------------------------------------------------
-- 1. 방화벽 로그 개념 (firewall_log)
-- --------------------------------------------------------------------
CREATE OR REPLACE CONCEPT `firewall_log` (
    `log_id` string,
    `log_time` timestamp,
    `dev_name` string,
    `src_ip` string,
    `dst_ip` string,
    `dst_port` int,
    `proto` string,
    `action` string,
    `rule` string,
    `bytes` int,
    PRIMARY KEY(`log_id`), LABEL(`rule`)
) INHERITS (`thing`) DESCRIPTION '방화벽 트래픽 허용/차단 이벤트 로그';

CREATE OR REPLACE MAPPING `map_firewall_log` INTO `firewall_log` AS
    SELECT CONCAT(`dev_name`, '_', `timestamp`, '_', CAST(ROW_NUMBER() OVER() AS string)) AS `log_id`,
           CAST(`timestamp` AS timestamp) AS `log_time`,
           `dev_name`,
           `src_ip`,
           `dst_ip`,
           CAST(`dst_port` AS int) AS `dst_port`,
           `proto`,
           `action`,
           `rule`,
           CAST(`bytes` AS int) AS `bytes`
    FROM `security`.`firewall_logs`;

-- [하위개념] 차단된 방화벽 로그 (조건 필터 뷰)
CREATE OR REPLACE CONCEPT `blocked_firewall_log`
    INHERITS (`firewall_log`) FROM `timbr`.`firewall_log`
    WHERE `action` IN ('BLOCK', 'DROP', 'DENY');


-- --------------------------------------------------------------------
-- 2. 침입탐지(IDS/IPS) 로그 개념 (ids_alert)
-- --------------------------------------------------------------------
CREATE OR REPLACE CONCEPT `ids_alert` (
    `alert_id` string,
    `alert_time` timestamp,
    `sensor_id` string,
    `src_ip` string,
    `dst_ip` string,
    `sig_name` string,
    `cve_id` string,
    `severity` string,
    `action` string,
    PRIMARY KEY(`alert_id`), LABEL(`sig_name`)
) INHERITS (`thing`) DESCRIPTION '네트워크 침입탐지(IDS/IPS) 시그니처 경보';

CREATE OR REPLACE MAPPING `map_ids_alert` INTO `ids_alert` AS
    SELECT CONCAT(`sensor_id`, '_', `timestamp`, '_', CAST(ROW_NUMBER() OVER() AS string)) AS `alert_id`,
           CAST(`timestamp` AS timestamp) AS `alert_time`,
           `sensor_id`,
           `src_ip`,
           `dst_ip`,
           `sig_name`,
           `cve_id`,
           `severity`,
           `action`
    FROM `security`.`ids_ips_logs`;

-- [하위개념] 고위험 침입탐지 경보
CREATE OR REPLACE CONCEPT `high_severity_ids_alert`
    INHERITS (`ids_alert`) FROM `timbr`.`ids_alert`
    WHERE `severity` IN ('HIGH', 'CRITICAL');


-- --------------------------------------------------------------------
-- 3. SIEM 보안 인시던트 경보 개념 (siem_incident)
-- --------------------------------------------------------------------
CREATE OR REPLACE CONCEPT `siem_incident` (
    `incident_id` string,
    `incident_time` timestamp,
    `rule_id` string,
    `rule_name` string,
    `src_ip` string,
    `dst_ip` string,
    `severity` string,
    `risk_score` int,
    `status` string,
    `correlated_events_count` int,
    `summary` string,
    PRIMARY KEY(`incident_id`), LABEL(`rule_name`)
) INHERITS (`thing`) DESCRIPTION 'SIEM 통합 상관분석 보안 인시던트 경보';

CREATE OR REPLACE MAPPING `map_siem_incident` INTO `siem_incident` AS
    SELECT `alert_id` AS `incident_id`,
           CAST(`timestamp` AS timestamp) AS `incident_time`,
           `rule_id`,
           `rule_name`,
           `src_ip`,
           `dst_ip`,
           `severity`,
           CAST(`risk_score` AS int) AS `risk_score`,
           `status`,
           CAST(`correlated_events_count` AS int) AS `correlated_events_count`,
           `summary`
    FROM `security`.`siem_alerts`;

-- [하위개념] 긴급 대응 대상 인시던트 (위험 점수 70점 이상)
CREATE OR REPLACE CONCEPT `critical_siem_incident`
    INHERITS (`siem_incident`) FROM `timbr`.`siem_incident`
    WHERE `risk_score` >= 70;


-- --------------------------------------------------------------------
-- 4. WAF 웹 방화벽 로그 개념 (waf_log)
-- --------------------------------------------------------------------
CREATE OR REPLACE CONCEPT `waf_log` (
    `waf_id` string,
    `waf_time` timestamp,
    `client_ip` string,
    `method` string,
    `uri` string,
    `status_code` int,
    `user_agent` string,
    `payload_size` int,
    `waf_action` string,
    PRIMARY KEY(`waf_id`), LABEL(`uri`)
) INHERITS (`thing`) DESCRIPTION '웹 애플리케이션 방화벽(WAF) HTTP 요청 로그';

CREATE OR REPLACE MAPPING `map_waf_log` INTO `waf_log` AS
    SELECT CONCAT('WAF_', `timestamp`, '_', CAST(ROW_NUMBER() OVER() AS string)) AS `waf_id`,
           CAST(`timestamp` AS timestamp) AS `waf_time`,
           `client_ip`,
           `method`,
           `uri`,
           CAST(`status_code` AS int) AS `status_code`,
           `user_agent`,
           CAST(`payload_size` AS int) AS `payload_size`,
           `waf_action`
    FROM `security`.`waf_web_logs`;

-- [하위개념] 차단된 웹 공격 로그
CREATE OR REPLACE CONCEPT `blocked_waf_attack`
    INHERITS (`waf_log`) FROM `timbr`.`waf_log`
    WHERE `waf_action` = 'BLOCK' OR `status_code` >= 400;


-- ====================================================================
-- 🔍 온톨로지 시연 및 검증 질의 (Timbr SQL Lab에서 SCHEMA: dtimbr 선택)
-- ====================================================================

-- 1) 방화벽 총 이벤트 수 확인
-- SELECT count(*) FROM `dtimbr`.`firewall_log`;

-- 2) 차단된 방화벽 이벤트 확인
-- SELECT count(*) FROM `dtimbr`.`blocked_firewall_log`;

-- 3) 위험점수 70점 이상 긴급 SIEM 인시던트 조회
-- SELECT `incident_id`, `rule_name`, `src_ip`, `risk_score`, `summary`
-- FROM `dtimbr`.`critical_siem_incident`
-- ORDER BY `risk_score` DESC LIMIT 10;
