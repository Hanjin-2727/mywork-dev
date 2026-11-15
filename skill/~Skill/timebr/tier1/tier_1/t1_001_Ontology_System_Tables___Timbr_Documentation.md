# Ontology System Tables | Timbr Documentation

- **출처 URL**: [https://docs.timbr.ai/doc/docs/getting-started/systables](https://docs.timbr.ai/doc/docs/getting-started/systables)
- **계층 (Tier)**: 1
- **수집 일시**: 2026-09-13 16:38:12

---

# Ontology System Tables

The ontology system tables in Timbr expose the internal structure of the ontology-based semantic layer. They provide visibility into how the virtual knowledge graph is defined, including business entities, relationships, mappings, and lineage.

These tables are available under the `timbr` schema in Timbr's SQL Editor and can be queried directly using SQL from any endpoint, allowing users to inspect and work with the semantic model.

FYI

All Ontology System Tables can be queried just like any other table, using "select * from timbr.system_table_name". Users can also query the Ontology System Tables in Timbr's SQL editor using the Timbr commands shown in the examples below.

**ONTOLOGY TABLES:**

  * **SYS_ONTOLOGY:** _all the information on the structure and metadata of a selected ontology._
  * **SYS_ONTOLOGIES:** _an overview of the information on all the ontologies in the platform._
  * **SYS_CONCEPTS:** _all the concepts in the selected ontology._
  * **SYS_PROPERTIES:** _all the properties in the selected ontology._
  * **SYS_RELATIONSHIPS:** _all the relationships between concepts in the selected ontology._
  * **SYS_MAPPINGS:** _all the data mappings within the selected ontology._
  * **SYS_INHERITANCE:** _the inheritance between concepts: base and derived in the selected ontology._
  * **SYS_VIEWS:** _all the information on views within the selected ontology._
  * **SYS_CONCEPT_PROPERTIES:** _all the properties belonging to concepts in the selected ontology._
  * **SYS_CONCEPT_RELATIONSHIPS:** _all the relationships between concepts and their properties._
  * **SYS_CONCEPT_MAPPINGS:** _all the table mappings to concepts._
  * **SYS_LINEAGE:** _all the lineage and data dependencies in the selected ontology._
  * **SYS_TAGS:** _all the tags associated with the resources (concepts, properties, ontology views) of a specific ontology._
  * **SYS_ONTOLOGIES_TAGS:** _all the tags associated with the resources (concepts, properties, ontology views) in the platform._
  * **SYS_DATASOURCES_TAGS:** _all the tags associated with the datasources in the platform._
  * **SYS_LLM_RECOMMENDATION:** _all the relationship recommendations and scores between concepts._



**CACHE/JOBS TABLES:**

  * **SYS_JOBS:** _all the current Jobs that are scheduled._
  * **SYS_JOBS_HISTORY:** _all the historical cached jobs._
  * **SYS_JOBS_RUNNING:** _all the currently running Cached Jobs._
  * **SYS_MATERIALIZATIONS:** _all the materialization configurations and properties within the knowledge graph that are meant to be cached._
  * **SYS_MATERIALIZATIONS_HISTORY:** _all the historical materialization jobs within the selected ontology._
  * **SYS_MATERIALIZED_OBJECTS:** _all currently materialized jobs for cached views and mappings within the knowledge graph, representing real-time materializations._



**SYSTEM TABLES:**

  * **SYS_RUNNING_QUERIES:** _all the information about currently running queries._
  * **SYS_QUERY_HISTORY:** _all the information on historical query executions._
  * **SYS_DATASOURCES:** _all the information on the datasources connected to the selected ontology._
  * **SYS_ALL_DATASOURCES:** _all the information on the datasources connected to the Timbr Platform._
  * **SYS_TIMBR_INSTANCES:** _all the information on Timbr server instances, including operational capacities, memory stats, and current activity._
  * **SYS_TIMBR_CONNECTIONS:** _all the Timbr connection information since the platform's start. This data is nonpersistent and clears after a service restart._
  * **SYS_TIMBR_OPERATIONS:** _all the metadata operations (get tables, get columns, get schemas) logged since the Timbr platform's start. This data is nonpersistent and clears after a service restart._
  * **SYS_TIMBR_LICENSE:** _all the information on the users Timbr License, including experation date and concurrent queries._



**PERMISSION TABLES:**

  * **SYS_PERMISSIONS:** _all the information on the current user permissions._
  * **SYS_ALL_PERMISSIONS:** _all the permissions that the current user can view._
  * **SYS_PERMISSION_HISTORY:** _all the log information of the permission history._
  * **SYS_USERS:** _all the information on users you have permission to view._
  * **SYS_ROLES:** _all the information on roles you have permission to view._
  * **SYS_USERS_ROLES:** _all the users that belong to the roles you have permission to view._
  * **SYS_ASSIGNED_POLICIES:** _all the information on policies assigned to users or roles._



* * *

## ONTOLOGY TABLES​

Below are the **Ontology Tables** and how to query them.

### SYS_ONTOLOGY​

The **SYS_ONTOLOGY** table contains nine columns: `primary_keys`, `label_keys`, `concept`, `query`, `inheritance_level`, `inheritance`, `description`, `query_json`, `properties`

Query example:
    
    
    SHOW ONTOLOGY  
    

* * *

### SYS_ONTOLOGIES​

The **SYS_ONTOLOGIES** table contains fifteen columns: `active_datasource`, `description`, `active`, `version_id`, `changed_by_user`, `created_by_user`, `relationships`, `mappings`, `datasources`, `concepts`, `created_on`, `ontology`, `changed_on`, `properties`, `views`

Query example:
    
    
    SHOW ONTOLOGIES  
    

* * *

### SYS_CONCEPTS​

The **SYS_CONCEPTS** table contains two columns: `concept` and `description`

Query example:
    
    
    SHOW CONCEPTS  
    

* * *

### SYS_PROPERTIES​

The **SYS_PROPERTIES** table contains five columns: `property_type`, `description`, `logic_query`, `property_name`, `is_multi` (1 - means it is multi-value, 0 means it is not)

Query example:
    
    
    SHOW PROPERTIES  
    

* * *

### SYS_RELATIONSHIPS​

The **SYS_RELATIONSHIPS** table contains seven columns: `relationship_name`, `target_concept`, `transitivity`, `concept`, `description`, `inverse_name`, `is_mtm` (1 - means it is many-to-many, 0 means it is not)

Query example:
    
    
    SHOW RELATIONSHIPS  
    

We can also query all the relationships between two concepts.  
For example, all the relationships between concept _Person_ and concept _Place_ :
    
    
    SELECT concept, target_concept, relationship_name FROM timbr.SYS_RELATIONSHIPS  
    WHERE concept = 'person' and target_concept = 'place'  
    

* * *

### SYS_MAPPINGS​

The **SYS_MAPPINGS** table contains seven columns: `query`, `parsed_query` (true/false if Timbr should parse the SQL mapping or send it as is to the DB) , `description`, `mapping_name`, `mapping_json`, `changed_by_user`, `changed_on`

Query example:
    
    
    SHOW MAPPINGS  
    

* * *

### SYS_INHERITANCE​

The **SYS_INHERITANCE** table contains two columns: `derived_concept` and `base_concept`

Query example:
    
    
    SHOW INHERITANCE  
    

* * *

### SYS_VIEWS​

The **SYS_VIEWS** table contains eight columns: `datasource_id`, `view_properties`, `query`, `description`, `view_json`, `changed_by_user`, `changed_on`, `view_name`

Query example:
    
    
    SHOW VIEWS  
    

* * *

### SYS_CONCEPT_PROPERTIES​

The **SYS_CONCEPT_PROPERTIES** table contains ten columns: `source_columns`, `tables`, `datasource_id`, `concept`, `property_type`, `target_properties`, `mapping_name`, `mapping_json`, `mapping_query`, `property_name`

Query example:
    
    
    SHOW CONCEPT_PROPERTIES  
    

* * *

### SYS_CONCEPT_RELATIONSHIPS​

The **SYS_CONCEPT_RELATIONSHIPS** table contains sixteen columns: `relationships_name`, `datasource_id`, `target_concept`, `is_inverse`, `concept`, `description`, `target_properties`, `mapping_name`, `mapping_json`, `inverse_name`, `source_properties`, `tables`, `transitivity`, `additional_properties`, `mapping_query`, `is_mtm`

Query example:
    
    
    SHOW CONCEPT_RELATIONSHIPS  
    

* * *

### SYS_CONCEPT_MAPPINGS​

The **SYS_CONCEPT_MAPPINGS** table contains ten columns: `tables`, `datasource_id`, `concept`, `parsed_query` (true/false if Timbr should parse the SQL mapping or send it as is to the DB), `description`, `mapping_name`, `mapping_json`, `changed_by_user`, `mapping_query`, `changed_on`

Query example:
    
    
    SHOW CONCEPT_MAPPINGS  
    

* * *

### SYS_LINEAGE​

The **SYS_LINEAGE** table contains four columns: `target_type`, `source_type`, `source`, `target`

Query example:
    
    
    SHOW LINEAGE  
    

* * *

### SYS_TAGS​

The **SYS_TAGS** table contains four columns: `target_name`, `target_type`, `tag_name`, `tag_value`

Query example:
    
    
    SHOW TAGS  
    

* * *

### SYS_ONTOLOGIES_TAGS​

The **SYS_ONTOLOGIES_TAGS** table contains three columns: `ontology`, `tag_name`, `tag_value`

Query example:
    
    
    SHOW ONTOLOGIES TAGS  
    

* * *

### SYS_DATASOURCES_TAGS​

The **SYS_DATASOURCES_TAGS** table contains three columns: `datasource`, `tag_name`, `tag_value`

Query example:
    
    
    SHOW DATASOURCES TAGS  
    

* * *

### SYS_LLM_RECOMMENDATION​

The **SYS_LLM_RECOMMENDATION** table contains nine columns: `relationship_name`, `before_relationship_score`, `updated_at`, `target_concept`, `concept`, `before_relationship`, `after_relationship_score`, `after_relationship`, `parsed_relationship_name`

Query example:
    
    
    SHOW LLM RECOMMENDATION  
    

* * *

## CACHE/JOBS TABLES​

Below are the **Cache/Jobs Tables** and how to query them.

### SYS_JOBS​

The **SYS_JOBS** table contains twelve columns: `job_type`, `scheduler_status`, `job_name`, `target_name`, `created_on`, `datasource`, `target_type` `refresh_rate`, `job_sql`, `scheduler_last_update`, `ontology`, `created_by_user`

Query example:
    
    
    SHOW JOBS  
    

* * *

### SYS_JOBS_HISTORY​

The **SYS_JOBS_HISTORY** table contains fifteen columns: `job_type`, `target_name`, `scheduled_by`, `end_time`, `target_type`, `duration`, `start_time`, `job_name`, `datasource`, `job_id`, `number_of_rows`, `status_log`, `job_sql`, `ontology`, `status`

Query example:
    
    
    SHOW JOBS HISTORY  
    

* * *

### SYS_JOBS_RUNNING​

The **SYS_JOBS_RUNNING** table contains thirteen columns: `job_type`, `server`, `target_name`, `scheduled_by`, `target_type`, `start_time`, `job_name`, `datasource`, `job_id`, `last_update`, `job_sql`, `ontology`, `status`

Query example:
    
    
    SHOW RUNNING JOBS  
    

* * *

### SYS_MATERIALIZATIONS​

The **SYS_MATERIALIZATIONS** table contains nine columns: `materialization_name`, `datasource_id`, `materialization_type`, `partition_column`, `schema_name`, `job_datasource_id`, `version`, `index_column`, `partition_granularity`

Query example:
    
    
    SHOW MATERIALIZATIONS  
    

* * *

### SYS_MATERIALIZATIONS_HISTORY​

The **SYS_MATERIALIZATIONS_HISTORY** table contains fourteen columns: `job_type`, `materialization_type`, `scheduled_by`, `end_time`, `duration`, `materialization_name`, `start_time`, `job_name`, `datasource`, `job_id`, `number_of_rows`, `status_log`, `job_sql`, `status`

Query example:
    
    
    SHOW MATERIALIZATIONS HISTORY  
    

* * *

### SYS_MATERIALIZED_OBJECTS​

The **SYS_MATERIALIZED_OBJECTS** table contains ten columns: `materialization_name`, `datasource_id`, `materialization_type`, `materialization_date`, `location_path`, `number_of_rows`, `schema_name`, `partition_column`, `version`, `materialization_query`

Query example:
    
    
    SHOW MATERIALIZED OBJECTS  
    

* * *

## OTHER SYSTEM TABLES​

Below are the **System Tables** and how to query them.

### SYS_RUNNING_QUERIES​

The **SYS_RUNNING_QUERIES** table contains thirteen columns: `server`, `query_id`, `sql`, `rows_fetched`, `platform_session_query_id`, `start_time`, `connection_id`, `datasource`, `last_update`, `query_queue`, `user`, `ontology`, `status`

Query example:
    
    
    SHOW RUNNING QUERIES  
    

* * *

### SYS_QUERY_HISTORY​

The **SYS_QUERY_HISTORY** table contains eighteen columns: `error_message`, `server`, `query_id`, `fetch_duration` (only fetching data from DB duration), `end_time`, `sql`, `rows_fetched`, `duration` (query + fetch), `start_time`, `connection_id`, `datasource`, `parent_query_id` (originating virtualization query), `query_queue`, `user`, `ontology`, `query_duration` (only query on DB duration), `bli` (The BLI Query, meaning the query was generated by the BLI), `status`

Query example:
    
    
    SHOW QUERY HISTORY  
    

* * *

### SYS_DATASOURCES​

The **SYS_DATASOURCES** table contains thirteen columns: `id`, `target_url`, `target_user`, `target_driver`, `target_type` , `is_active`, `json`, `created_on`, `changed_on`, `created_by_user`, `changed_by_user`, `description`, `is_virtualization`

Query example:
    
    
    SHOW DATASOURCES  
    

* * *

### SYS_ALL_DATASOURCES​

The **SYS_ALL_DATASOURCES** table contains fifteen columns: `isolation_level`, `target_url`, `target_type`, `description`, `changed_by_user`, `created_by_user`, `target_driver`, `proxy`, `is_virtualization`, `created_on`, `target_user`, `json`, `init_statement`, `id`, `changed_on`

Query example:
    
    
    SHOW ALL DATASOURCES  
    

* * *

* * *

### SYS_AGENTS​

The **SYS_AGENTS** table contains fifteen columns: `agent_name`, `description`, `created_at`, `created_by_user`

Query example:
    
    
    SHOW AGENTS  
    

* * *

### SYS_TIMBR_INSTANCES​

The **SYS_TIMBR_INSTANCES** table contains thirteen columns: `server`, `max_running_operations`, `max_connections`, `open_connections`, `max_running_queries`, `running_operations`, `ip`, `jvm_free_memory`, `hostname`, `running_queries`, `jvm_max_memory`, `last_update`, `jvm_total_memory`

Query example:
    
    
    SHOW INSTANCES  
    

* * *

### SYS_TIMBR_CONNECTIONS​

The **SYS_TIMBR_CONNECTIONS** table contains eight columns: `server`, `start_time`, `connection_id`, `datasource`, `end_time`, `user`, `ontology`, `status`

Query example:
    
    
    SHOW CONNECTIONS  
    

* * *

### SYS_TIMBR_OPERATIONS​

The **SYS_TIMBR_OPERATIONS** table contains twelve columns: `connection_id`, `datasource`, `end_time`, `error_message`, `operation_id`, `operation_parameters`, `ontology`, `operation_type`, `server`, `start_time`, `status`, `user`

Query example:
    
    
    SHOW OPERATIONS  
    

* * *

### SYS_TIMBR_LICENSE​

The **SYS_TIMBR_LICENSE** table contains three columns: `company_name`, `expiration_date`, `concurrent_queries`

Query example:
    
    
    SHOW LICENSE  
    

* * *

## PERMISSION TABLES​

Below are the **Permission Tables** and how to query them.

### SYS_PERMISSIONS​

The **SYS_PERMISSIONS** table contains fourteen columns: `has_grant`, `is_all`, `permission`, `resource`, `resource_url`, `resource_url_part1`, `resource_url_part2`, `resource_url_part3`, `resource_url_part4`, `resource_url_part5`, `sql`, `sql_revoke`, `target_name`, `target_type`

Query example:
    
    
    SHOW PERMISSIONS  
    

* * *

### SYS_ALL_PERMISSIONS​

The **SYS_ALL_PERMISSIONS** table contains fourteen columns: `has_grant`, `is_all`, `permission`, `resource`, `resource_url`, `resource_url_part1`, `resource_url_part2`, `resource_url_part3`, `resource_url_part4`, `resource_url_part5`, `sql`, `sql_revoke`, `target_name`, `target_type`

Query example:
    
    
    SHOW ALL PERMISSIONS  
    

* * *

### SYS_PERMISSION_HISTORY​

The **SYS_PERMISSION_HISTORY** table contains eleven columns: `connection_id`, `execution_time`, `query_id`, `resource_name`, `resource_type`, `server`, `sql`, `statement_number`, `target_role`, `target_user`, `user`

Query example:
    
    
    SHOW PERMISSION HISTORY  
    

* * *

### SYS_USERS​

The **SYS_USERS** table contains fifteen columns: `last_login`, `last_name`, `active`, `fail_login_count`, `created_by_user_id`, `changed_by_user`, `created_by_user`, `login_count`, `created_by_role`, `created_on`, `id`, `first_name`, `email`, `changed_on`, `username`

Query example:
    
    
    SHOW USERS  
    

* * *

### SYS_ROLES​

The **SYS_ROLES** table contains eleven columns: `created_on`, `name`, `sync_last_update`, `description`, `sync_group_type`, `id`, `sync_group_value`, `changed_by_user`, `sync_group_id`, `changed_on`, `created_by_user`

Query example:
    
    
    SHOW ROLES  
    

* * *

### SYS_USERS_ROLES​

The **SYS_USERS_ROLES** table contains two columns: `role` and `username`

Query example:
    
    
    SHOW USERS ROLES  
    

* * *

### SYS_ASSIGNED_POLICIES​

The **SYS_ASSIGNED_POLICIES** table contains four columns: `policy`, `ontology`, `target_name`, `target_type`

Query example:
    
    
    SHOW ASSIGNED POLICIES  
    

  * ONTOLOGY TABLES
    * SYS_ONTOLOGY
    * SYS_ONTOLOGIES
    * SYS_CONCEPTS
    * SYS_PROPERTIES
    * SYS_RELATIONSHIPS
    * SYS_MAPPINGS
    * SYS_INHERITANCE
    * SYS_VIEWS
    * SYS_CONCEPT_PROPERTIES
    * SYS_CONCEPT_RELATIONSHIPS
    * SYS_CONCEPT_MAPPINGS
    * SYS_LINEAGE
    * SYS_TAGS
    * SYS_ONTOLOGIES_TAGS
    * SYS_DATASOURCES_TAGS
    * SYS_LLM_RECOMMENDATION
  * CACHE/JOBS TABLES
    * SYS_JOBS
    * SYS_JOBS_HISTORY
    * SYS_JOBS_RUNNING
    * SYS_MATERIALIZATIONS
    * SYS_MATERIALIZATIONS_HISTORY
    * SYS_MATERIALIZED_OBJECTS
  * OTHER SYSTEM TABLES
    * SYS_RUNNING_QUERIES
    * SYS_QUERY_HISTORY
    * SYS_DATASOURCES
    * SYS_ALL_DATASOURCES
    * SYS_AGENTS
    * SYS_TIMBR_INSTANCES
    * SYS_TIMBR_CONNECTIONS
    * SYS_TIMBR_OPERATIONS
    * SYS_TIMBR_LICENSE
  * PERMISSION TABLES
    * SYS_PERMISSIONS
    * SYS_ALL_PERMISSIONS
    * SYS_PERMISSION_HISTORY
    * SYS_USERS
    * SYS_ROLES
    * SYS_USERS_ROLES
    * SYS_ASSIGNED_POLICIES
