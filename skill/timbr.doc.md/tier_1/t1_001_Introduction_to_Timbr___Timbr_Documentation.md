# Introduction to Timbr | Timbr Documentation

- **출처 URL**: [https://docs.timbr.ai/doc/docs/getting-started/intro-timbr](https://docs.timbr.ai/doc/docs/getting-started/intro-timbr)
- **계층 (Tier)**: 1
- **수집 일시**: 2026-09-13 16:17:41

---

# Introduction to Timbr

## What is Timbr​

Timbr is an ontology-based semantic layer that provides a semantic context layer for enterprise AI and analytics systems.

It creates a virtual knowledge graph over existing data sources using SQL-native ontologies, allowing organizations to define business entities, relationships, and logic directly on top of their data without moving or duplicating it.

This semantic context layer enables consistent business definitions across SQL queries, BI tools, and AI systems. It acts as the semantic context layer that powers use cases such as NL2SQL, GraphRAG, and AI agents.

**Note:** Timbr does not store your data. It creates a virtual knowledge graph that connects directly to your existing data sources, ensuring your data remains where it is.

Timbr enables you to:

  * Define business entities and relationships as part of an ontology-based semantic layer 
  * Map your data sources to a semantic model to access data by its meaning 
  * Query data using semantic SQL, replacing complex JOIN and UNION logic 
  * Reuse consistent business definitions across analytics and AI systems 
  * Enable AI systems to access structured business context through a semantic context layer 
  * Virtualize and cache data for optimized query performance 
  * Visualize and explore data as a graph of relationships 
  * Use graph algorithms over relational data for advanced analytics 
  * Enable universal data consumption via REST / ODBC / JDBC 
  * Import industry data models, ERDs, and OWL ontologies into SQL-native ontologies 



Unlike traditional semantic web systems, Timbr’s ontologies are SQL-native and operate as a virtual knowledge graph. Queries are translated into optimized SQL and executed directly on the underlying data sources. 

* * *

## What is an Ontology​

An ontology defines a common vocabulary for an organization who need to share information in a domain.  
It includes machine-interpretable definitions of basic concepts in the domain and relations among them. 

An ontology is structured as a graph. Every node of this graph stands for a **concept**.  
A concept could be anything: _Person, Place, Customer, Car, Country, Product, Event etc_. 

SQL ontologies are ontologies designed to provide common business meaning to data distributed in varied sources and enable them as concepts with inference and graph traversal capabilities to facilitate discovery, use and access to data. With Timbr, you can model and explore your ontology visually or in standard SQL. The SQL Ontology is exposed to the SQL user as a virtual schema with virtual tables (concepts) using any SQL client with JDBC/ODBC.

**For Example:**

Ontology example

More information about ontologies: <https://en.wikipedia.org/wiki/Ontology_(information_science)>

* * *

**Timbr** allows multiple inheritance in the concept hierarchy.  
**Timbr** supports transitivity reasoning, which corresponds to chaining of IS-A relationships (inheritance). 

A concept can be a sub-concept of several concepts.  
Sub-concepts of a concept usually have additional properties that the super-concept does not have,  
Or restrictions different from those of the super-concepts,  
Or participate in different relationships than the super-concepts. 

**For Example:**  
If we know that a _Lucy IS-A Dog_ and we also know that a _Dog IS-A Animal_ , then  
We can conclude that a _Lucy IS-A Animal_. 

Higher concepts in the ontology hierarchy represent general concepts.  
Lower concepts in the ontology hierarchy represent specific concepts.

* * *

A relationship in the ontology is a reference that points from one concept to another concept.  
It expresses how the two concepts relate to each other.  
The name of a relationship is normally written next to the relationship link. 

This is very similar to a data member that is a pointer in an Object-Oriented Database or programming language.  
In **Timbr** , relationships are defined using foreign keys. 

**For Example:**  
The concept _Car_ may have a relationship to the concept _Person_. The name of that relationship could be _"Owned"_.

* * *

The main reasons to develop an ontology is:

  * To share common understanding of the structure of information among people or software agents 
  * To enable reuse of domain knowledge 
  * To make domain assumptions explicit 
  * To separate domain knowledge from the operational knowledge 
  * To analyze domain knowledge



It is widely assumed that ontologies represent information in a form that is at least partially similar to how human knowledge is represented.  
Ontologies represent information in a form that can be used for some forms of reasoning that are at least partially similar to human reasoning. 

Ontology development is different from designing classes and relations in object-oriented programming.  
Object-oriented programming centers primarily around methods on classes-a programmer makes design decisions based on the operational properties of a class. 

Whereas an ontology designer makes these decisions based on the structural properties of a class.  
As a result, a class structure and relations among classes in an ontology are different from the structure for a similar domain in an object-oriented program. 

Here you can find a [detailed guide on how to model and develop ontologies](<https://protege.stanford.edu/publications/ontology_development/ontology101.pdf>)

* * *

## Timbr Ontology​

In Timbr, the ontology is made of:

  * **Concepts** \- Business entities which are mapped to OWL Classes and are exposed as virtual tables.
  * **Properties** \- Attributes of the business entities which are mapped to OWL Datatype Properties and act as columns of the virtual tables.
  * **Relationships** \- Semantic connections between the business entities which are mapped to OWL Object Properties and are exposed as columns in Timbr graph schema (_dtimbr_). Relationships are created by SQL foreign keys.
  * **Mappings** \- Paths of the business entities to the data in the source systems where Timbr will push-down and execute the query.
  * **Views** \- allow us to aggregate concepts (build cubes) or provide specific denormalized view of a concept.



## Timbr Concepts​

In Semantic Web ontologies, any concept is a sub-concept of **Thing** (the base concept of every Ontology)  
Which means any concept inherits the properties and relationships from its parent concept. 

The relation between a sub-concept and a super-concept is a **IS-A** relation.  
As opposed to a **HAVE/HAS/CONTAINS** relationship which correspond to **Properties** and **Relationships**. 

For example, the concept **Person** IS-A **Thing**.  
If we want to add a concept of a **Child** which inherits from **Person** it would be valid because a **Child** IS-A **Person**  
Similarly, the concept of **Artist** can also inherit from **Person** since **Artist** IS-A **Person**

However, creating a concept of **Head** which inherits from **Person** is **WRONG** since **Head** IS NOT A **Person**.  
This distinctions are important since **any derived concept inherits the properties and relationships from its parent concepts**

Therefore, if our ontology looks like:  
**Thing** <\--- **Person** <\--- **Artist**

and **Person** has the properties: Name, Age, Birthdate  
Then **Artist** also has the properties: Name, Age, Birthdate  
**Artist** may also have additional properties and relationships such as: Artworks, Shows, Years_Of_Experience which are not necessarily properties of every **Person** , therefor they can be added to the **Artist** concept only. 

* * *

## Timbr Properties​

Just like the columns in a SQL table, the properties can be of different datatypes like: **INTEGER** , **VARCHAR** , **DATE** , **TIMESTAMP** , etc.  
Timbr uses the underlying datatypes of the SQL Engine when referencing properties.

There are two kinds of properties:

  * **Direct Properties** \- Properties that were defined explicitly for a concept
  * **Inherited Properties** \- Properties that were inherited by the parent concepts.



A property can also be defined as a **Multi-value Property**. A multi-value property is a property that has more than one instance mapped to them.

Multi-value properties mappings

Multi-value properties are mapped separately through a table or view in the datasource, referenced as multi-value property mappings.

* * *

## Timbr Relationships​

Relationships in Timbr represent relationships between two concepts that are matched by the properties of each concept.  
In Timbr you can define two types of relationships:

  * **One-to-Many Relationships** \- Represented by a relationship between two concepts when in one instance of a concept may be linked to many instances of another concept. One-to-Many relationship can also be represented this way when only one instance of a concept corresponds to only one other instance of a concept.
  * **Many-to-Many Relationships** \- Represented by a relationship between two concepts where many instances of one concept may be linked to many instances of another concept. Many-to-Many relationships is formed from a linked table with two foreign keys to two different concepts linking them together.



**Both One-to-Many** and **Many-to-Many** relationships can be defined as a **Transitive Relationship**. 

Meaning of a transitive relationship

If **X** is related to **Y**   
and **Y** is related to **Z**  
then **X** will also be related to **Z**.

Typical examples of transitive relationships are **part-whole** type of relations. For example - **part-of** can be a part-whole relationship, if you decide to model a _letter_ as a **part of** a _word_ , and a _word_ as a **part of** a _sentence_ , a _sentence_ as a **part of** a _paragraph_ , etc.

For more information about how to perform graph traversals and query relationships:  
[Queries using the dtimbr schema](</doc/docs/getting-started/query-kg#query-dtimbr-schema>)

* * *

## Timbr Mappings​

Mappings are used to map physical tables to the ontology concepts, properties (in case of a multi-value property), or relationships (in case of a Many-to-Many relationship).  
A table or multiple tables can be mapped to a concept, or multiple concepts based on the user design decisions. 

Tables that represent relationships or multi-value properties aren't mapped directly to a concept:

  * Tables that represent Many-to-Many relationship between business entities (concepts)
  * Multi-value tables that store multiple column value for a specific property



These kind of tables are mapped using foreign keys directly to a relationship or to a property defined in the ontology. 

Users can use the UI to map tables to concepts or alternativly use SQL statements to map tables in code.  
Users can use any function of the underlying data source in the mapping statement.  
Users can restrict access only to specific mappings if needed.  
Users can materialize any mapping to overcome performance challenges in the underlying database. 

Mappings are created using the **CREATE MAPPING** statement that uses SQL to map column names to properties effectively.  
The user can also use the Timbr **Data Mapper** to map tables using the **Visual Mapper** directly to the ontology concepts.

* * *

## Timbr Views​

Views are used to create aggregate concepts (cubes) or specific denormalized views.  
Physical tables or concepts can be queried inside a view.  
Views can be created on top of other views allowing you to create different levels of entity granularity. 

Users can restrict access only to specific views if needed and not the underlying concepts and mappings.  
Users can materialize views on any level to overcome performance challenges. 

Views are created using the **CREATE VIEW** statement and uses SQL to query the concepts and tables.

  * What is Timbr
  * What is an Ontology
  * Timbr Ontology
  * Timbr Concepts
  * Timbr Properties
  * Timbr Relationships
  * Timbr Mappings
  * Timbr Views
