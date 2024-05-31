CREATE TABLE IF NOT EXISTS public.query
(
    id serial,
    query_string character varying NOT NULL,
    start bigint NOT NULL,
    "end" bigint NOT NULL,
    start_date date DEFAULT now(),
    CONSTRAINT query_pkey PRIMARY KEY (id)
);


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

ALTER TABLE public.result ADD "when" date;

ALTER TABLE "result" ADD score1 INTEGER, ADD score2 INTEGER, ADD score3 INTEGER;

CREATE TABLE IF NOT EXISTS public.analysis
(
    id serial NOT NULL,
    model character varying COLLATE pg_catalog."default" NOT NULL,
    version integer,
    comment text COLLATE pg_catalog."default",
    start_date date DEFAULT now(),
    query_id integer NOT NULL DEFAULT nextval('analysis_query_id_seq'::regclass),
    CONSTRAINT analysis_pkey PRIMARY KEY (id),
    CONSTRAINT analysis_query_fk FOREIGN KEY (query_id)
        REFERENCES public.query (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS public.analysis_result
(
    id bigserial NOT NULL,
    analysis_id integer NOT NULL,
    score_1 double precision,
    score_2 double precision,
    score_3 double precision,
    result_id bigint NOT NULL,
    CONSTRAINT analysis_result_pkey PRIMARY KEY (id),
    CONSTRAINT analysis_result_analysis_fk FOREIGN KEY (analysis_id)
        REFERENCES public.analysis (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT analysis_result_result_fk FOREIGN KEY (result_id)
        REFERENCES public.result (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
);
