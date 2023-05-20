CREATE TABLE IF NOT EXISTS public.query
(
    id serial,
    query_string character varying NOT NULL,
    start bigint NOT NULL,
    "end" bigint NOT NULL,
    start_date date DEFAULT now(),
    CONSTRAINT query_pkey PRIMARY KEY (id)
)


CREATE TABLE IF NOT EXISTS public.result
(
    id bigserial NOT NULL,
    query_id bigint NOT NULL,
    url character varying,
    site character varying,
    title character varying,
    description text,
    content text,
    "number" bigint,
    date_str character varying,
    encoding character varying,
    content_type character varying,
    intensity_1 integer,
    intensity_2 integer,
    intensity_3 integer,
    intensity_composite integer,
    intensity bigint,
    CONSTRAINT result_pkey PRIMARY KEY (id),
    CONSTRAINT query_id_fk FOREIGN KEY (query_id)
        REFERENCES public.query (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);
