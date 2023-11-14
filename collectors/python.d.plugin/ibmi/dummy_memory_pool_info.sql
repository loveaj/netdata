--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4
-- Dumped by pg_dump version 15.4

-- Started on 2023-11-14 12:55:38 GMT

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 215 (class 1259 OID 16395)
-- Name: memory_pool_info; Type: TABLE; Schema: qsys2; Owner: netdataservice
--

CREATE TABLE qsys2.memory_pool_info (
    "SYSTEM_POOL_ID" integer,
    "POOL_NAME" character varying(50),
    "CURRENT_SIZE" real,
    "RESERVED_SIZE" real,
    "DEFINED_SIZE" real,
    "MAXIMUM_ACTIVE_THREADS" integer,
    "CURRENT_THREADS" integer,
    "CURRENT_INELIGIBLE_THREADS" integer,
    "SUBSYSTEM_LIBRARY_NAME" character varying(50),
    "SUBSYSTEM_NAME" character varying(50),
    "DESCRIPTION" character varying(50),
    "PAGING_OPTION" character varying(50),
    "ELAPSED_TIME" integer,
    "ELAPSED_DATABASE_FAULTS" integer,
    "ELAPSED_NON_DATABASE_FAULTS" integer,
    "ELAPSED_TOTAL_FAULTS" integer,
    "ELAPSED_DATABASE_PAGES" integer,
    "ELAPSED_NON_DATABASE_PAGES" integer,
    "ELAPSED_ACTIVE_TO_WAIT" real,
    "ELAPSED_WAIT_TO_INELIGIBLE" integer,
    "ELAPSED_ACTIVE_TO_INELIGIBLE" integer,
    "TUNING_PRIORITY" integer,
    "TUNING_MINIMUM_SIZE" real,
    "TUNING_MAXIMUM_SIZE" integer,
    "TUNING_MINIMUM_FAULTS" integer,
    "TUNING_MAXIMUM_FAULTS" integer,
    "TUNING_THREAD_FAULTS" integer,
    "TUNING_MINIMUM_ACTIVITY" integer,
    "TUNING_MAXIMUM_ACTIVITY" integer
);


ALTER TABLE qsys2.memory_pool_info OWNER TO netdataservice;

--
-- TOC entry 4349 (class 0 OID 16395)
-- Dependencies: 215
-- Data for Name: memory_pool_info; Type: TABLE DATA; Schema: qsys2; Owner: netdataservice
--

COPY qsys2.memory_pool_info ("SYSTEM_POOL_ID", "POOL_NAME", "CURRENT_SIZE", "RESERVED_SIZE", "DEFINED_SIZE", "MAXIMUM_ACTIVE_THREADS", "CURRENT_THREADS", "CURRENT_INELIGIBLE_THREADS", "SUBSYSTEM_LIBRARY_NAME", "SUBSYSTEM_NAME", "DESCRIPTION", "PAGING_OPTION", "ELAPSED_TIME", "ELAPSED_DATABASE_FAULTS", "ELAPSED_NON_DATABASE_FAULTS", "ELAPSED_TOTAL_FAULTS", "ELAPSED_DATABASE_PAGES", "ELAPSED_NON_DATABASE_PAGES", "ELAPSED_ACTIVE_TO_WAIT", "ELAPSED_WAIT_TO_INELIGIBLE", "ELAPSED_ACTIVE_TO_INELIGIBLE", "TUNING_PRIORITY", "TUNING_MINIMUM_SIZE", "TUNING_MAXIMUM_SIZE", "TUNING_MINIMUM_FAULTS", "TUNING_MAXIMUM_FAULTS", "TUNING_THREAD_FAULTS", "TUNING_MINIMUM_ACTIVITY", "TUNING_MAXIMUM_ACTIVITY") FROM stdin;
1	*MACHINE	44270.21	23075.28	44270.21	32767	791	0			Used by internal machine functions	*FIXED	1	0	0	0	0	0	3222.2	0	0	1	3.8	100	10	10	0	0	0
2	*BASE	712158.56	14.72	\N	14917	2411	0			Default system pool	*CALC	1	21	12	34	3225	12	6944.4	0	0	1	5	100	12	200	1	5	32767
3	*INTERACT	84991.99	0	84991.99	256	9	0			Used for interactive work	*CALC	1	0	0	0	0	0	0	0	0	1	10	100	12	200	1	5	32767
4	*SPOOL	8499.19	0	8499.19	20	1	0			Used for printing	*CALC	1	0	0	0	0	0	0	0	0	2	1	100	5	100	1	5	32767
\.


-- Completed on 2023-11-14 12:55:39 GMT

--
-- PostgreSQL database dump complete
--

