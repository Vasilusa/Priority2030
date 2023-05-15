CREATE TABLE IF NOT EXISTS public.query
(
    id integer NOT NULL DEFAULT nextval('query_id_seq'::regclass),
    query_string character varying COLLATE pg_catalog."default" NOT NULL,
    start bigint NOT NULL,
    "end" bigint NOT NULL,
    CONSTRAINT query_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.query
    OWNER to scan;

-- Table: public.result

-- DROP TABLE IF EXISTS public.result;

CREATE TABLE IF NOT EXISTS public.result
(
    id bigint NOT NULL DEFAULT nextval('result_id_seq'::regclass),
    query_id bigint NOT NULL DEFAULT nextval('result_query_id_seq'::regclass),
    url character varying COLLATE pg_catalog."default",
    site character varying COLLATE pg_catalog."default",
    title character varying COLLATE pg_catalog."default",
    description text COLLATE pg_catalog."default",
    content text COLLATE pg_catalog."default",
    "number" bigint,
    date_str character varying COLLATE pg_catalog."default",
    encoding character varying COLLATE pg_catalog."default",
    intensity bigint,
    CONSTRAINT result_pkey PRIMARY KEY (id),
    CONSTRAINT query_id_fk FOREIGN KEY (query_id)
        REFERENCES public.query (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.result
    OWNER to scan;
