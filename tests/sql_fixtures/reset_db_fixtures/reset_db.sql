--
-- PostgreSQL database dump
--

-- Dumped from database version 15.5 (Debian 15.5-1.pgdg120+1)
-- Dumped by pg_dump version 15.5 (Debian 15.5-1.pgdg120+1)

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
-- Name: auth_cache; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_cache (
    cache_key character varying(255) NOT NULL,
    value text NOT NULL,
    expires timestamp with time zone NOT NULL
);


ALTER TABLE public.auth_cache OWNER TO postgres;

--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO postgres;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auth_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_id_seq OWNER TO postgres;

--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auth_group_id_seq OWNED BY public.auth_group.id;


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO postgres;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auth_group_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_permissions_id_seq OWNER TO postgres;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auth_group_permissions_id_seq OWNED BY public.auth_group_permissions.id;


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO postgres;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auth_permission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_permission_id_seq OWNER TO postgres;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auth_permission_id_seq OWNED BY public.auth_permission.id;


--
-- Name: auth_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_tokens (
    id integer NOT NULL,
    refresh_token text NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.auth_tokens OWNER TO postgres;

--
-- Name: bank_transaction_lineitems; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bank_transaction_lineitems (
    id integer NOT NULL,
    account_id character varying(255) NOT NULL,
    item_code character varying(255),
    tracking_categories jsonb,
    amount double precision NOT NULL,
    description text,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    bank_transaction_id integer NOT NULL,
    expense_id integer NOT NULL,
    tax_amount double precision,
    tax_code character varying(255),
    customer_id character varying(255),
    line_item_id character varying(255)
);


ALTER TABLE public.bank_transaction_lineitems OWNER TO postgres;

--
-- Name: bank_transaction_lineitems_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bank_transaction_lineitems_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bank_transaction_lineitems_id_seq OWNER TO postgres;

--
-- Name: bank_transaction_lineitems_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bank_transaction_lineitems_id_seq OWNED BY public.bank_transaction_lineitems.id;


--
-- Name: bank_transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bank_transactions (
    id integer NOT NULL,
    contact_id character varying(255) NOT NULL,
    bank_account_code character varying(255) NOT NULL,
    currency character varying(255) NOT NULL,
    reference character varying(255) NOT NULL,
    transaction_date date NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    expense_group_id integer NOT NULL,
    export_id character varying(255)
);


ALTER TABLE public.bank_transactions OWNER TO postgres;

--
-- Name: bank_transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bank_transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bank_transactions_id_seq OWNER TO postgres;

--
-- Name: bank_transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bank_transactions_id_seq OWNED BY public.bank_transactions.id;


--
-- Name: bill_lineitems; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bill_lineitems (
    id integer NOT NULL,
    tracking_categories jsonb,
    item_code character varying(255),
    account_id character varying(255) NOT NULL,
    description text NOT NULL,
    amount double precision NOT NULL,
    bill_id integer NOT NULL,
    expense_id integer NOT NULL,
    tax_amount double precision,
    tax_code character varying(255),
    customer_id character varying(255),
    line_item_id character varying(255)
);


ALTER TABLE public.bill_lineitems OWNER TO postgres;

--
-- Name: bill_lineitems_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bill_lineitems_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bill_lineitems_id_seq OWNER TO postgres;

--
-- Name: bill_lineitems_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bill_lineitems_id_seq OWNED BY public.bill_lineitems.id;


--
-- Name: bills; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bills (
    id integer NOT NULL,
    currency character varying(255) NOT NULL,
    contact_id character varying(255) NOT NULL,
    reference character varying(255) NOT NULL,
    date timestamp with time zone NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    expense_group_id integer NOT NULL,
    paid_on_xero boolean NOT NULL,
    payment_synced boolean NOT NULL,
    export_id character varying(255)
);


ALTER TABLE public.bills OWNER TO postgres;

--
-- Name: bills_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bills_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bills_id_seq OWNER TO postgres;

--
-- Name: bills_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bills_id_seq OWNED BY public.bills.id;


--
-- Name: category_mappings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.category_mappings (
    id integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    destination_account_id integer,
    destination_expense_head_id integer,
    source_category_id integer NOT NULL,
    workspace_id integer NOT NULL
);


ALTER TABLE public.category_mappings OWNER TO postgres;

--
-- Name: category_mappings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.category_mappings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.category_mappings_id_seq OWNER TO postgres;

--
-- Name: category_mappings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.category_mappings_id_seq OWNED BY public.category_mappings.id;


--
-- Name: destination_attributes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.destination_attributes (
    id integer NOT NULL,
    attribute_type character varying(255) NOT NULL,
    display_name character varying(255) NOT NULL,
    value character varying(255) NOT NULL,
    destination_id character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    workspace_id integer NOT NULL,
    active boolean,
    detail jsonb,
    auto_created boolean NOT NULL
);


ALTER TABLE public.destination_attributes OWNER TO postgres;

--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE public.django_admin_log OWNER TO postgres;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.django_admin_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_admin_log_id_seq OWNER TO postgres;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.django_admin_log_id_seq OWNED BY public.django_admin_log.id;


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO postgres;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.django_content_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_content_type_id_seq OWNER TO postgres;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.django_content_type_id_seq OWNED BY public.django_content_type.id;


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_migrations (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE public.django_migrations OWNER TO postgres;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.django_migrations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_migrations_id_seq OWNER TO postgres;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.django_migrations_id_seq OWNED BY public.django_migrations.id;


--
-- Name: django_q_ormq; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_q_ormq (
    id integer NOT NULL,
    key character varying(100) NOT NULL,
    payload text NOT NULL,
    lock timestamp with time zone
);


ALTER TABLE public.django_q_ormq OWNER TO postgres;

--
-- Name: django_q_ormq_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.django_q_ormq_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_q_ormq_id_seq OWNER TO postgres;

--
-- Name: django_q_ormq_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.django_q_ormq_id_seq OWNED BY public.django_q_ormq.id;


--
-- Name: django_q_schedule; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_q_schedule (
    id integer NOT NULL,
    func character varying(256) NOT NULL,
    hook character varying(256),
    args text,
    kwargs text,
    schedule_type character varying(2) NOT NULL,
    repeats integer NOT NULL,
    next_run timestamp with time zone,
    task character varying(100),
    name character varying(100),
    minutes smallint,
    cron character varying(100),
    cluster character varying(100),
    intended_date_kwarg character varying(100),
    CONSTRAINT django_q_schedule_minutes_check CHECK ((minutes >= 0))
);


ALTER TABLE public.django_q_schedule OWNER TO postgres;

--
-- Name: django_q_schedule_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.django_q_schedule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_q_schedule_id_seq OWNER TO postgres;

--
-- Name: django_q_schedule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.django_q_schedule_id_seq OWNED BY public.django_q_schedule.id;


--
-- Name: django_q_task; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_q_task (
    name character varying(100) NOT NULL,
    func character varying(256) NOT NULL,
    hook character varying(256),
    args text,
    kwargs text,
    result text,
    started timestamp with time zone NOT NULL,
    stopped timestamp with time zone NOT NULL,
    success boolean NOT NULL,
    id character varying(32) NOT NULL,
    "group" character varying(100),
    attempt_count integer NOT NULL,
    cluster character varying(100)
);


ALTER TABLE public.django_q_task OWNER TO postgres;

--
-- Name: django_session; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO postgres;

--
-- Name: employee_mappings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.employee_mappings (
    id integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    destination_card_account_id integer,
    destination_employee_id integer,
    destination_vendor_id integer,
    source_employee_id integer NOT NULL,
    workspace_id integer NOT NULL
);


ALTER TABLE public.employee_mappings OWNER TO postgres;

--
-- Name: employee_mappings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.employee_mappings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.employee_mappings_id_seq OWNER TO postgres;

--
-- Name: employee_mappings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.employee_mappings_id_seq OWNED BY public.employee_mappings.id;


--
-- Name: errors; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.errors (
    id integer NOT NULL,
    type character varying(50) NOT NULL,
    is_resolved boolean NOT NULL,
    error_title character varying(255) NOT NULL,
    error_detail text NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    expense_attribute_id integer,
    expense_group_id integer,
    workspace_id integer NOT NULL
);


ALTER TABLE public.errors OWNER TO postgres;

--
-- Name: errors_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.errors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.errors_id_seq OWNER TO postgres;

--
-- Name: errors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.errors_id_seq OWNED BY public.errors.id;


--
-- Name: expense_attributes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expense_attributes (
    id integer NOT NULL,
    attribute_type character varying(255) NOT NULL,
    display_name character varying(255) NOT NULL,
    value character varying(1000) NOT NULL,
    source_id character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    workspace_id integer NOT NULL,
    active boolean,
    detail jsonb,
    auto_mapped boolean NOT NULL,
    auto_created boolean NOT NULL
);


ALTER TABLE public.expense_attributes OWNER TO postgres;

--
-- Name: expense_fields; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expense_fields (
    id integer NOT NULL,
    attribute_type character varying(255) NOT NULL,
    source_field_id integer NOT NULL,
    is_enabled boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    workspace_id integer NOT NULL
);


ALTER TABLE public.expense_fields OWNER TO postgres;

--
-- Name: expense_fields_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.expense_fields_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.expense_fields_id_seq OWNER TO postgres;

--
-- Name: expense_fields_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.expense_fields_id_seq OWNED BY public.expense_fields.id;


--
-- Name: expense_group_settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expense_group_settings (
    id integer NOT NULL,
    reimbursable_expense_group_fields character varying(100)[] NOT NULL,
    corporate_credit_card_expense_group_fields character varying(100)[] NOT NULL,
    expense_state character varying(100) NOT NULL,
    reimbursable_export_date_type character varying(100) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    workspace_id integer NOT NULL,
    ccc_export_date_type character varying(100) NOT NULL,
    ccc_expense_state character varying(100),
    reimbursable_expense_state character varying(100),
    import_card_credits boolean NOT NULL
);


ALTER TABLE public.expense_group_settings OWNER TO postgres;

--
-- Name: expense_groups; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expense_groups (
    id integer NOT NULL,
    fund_source character varying(255) NOT NULL,
    description jsonb,
    created_at timestamp with time zone NOT NULL,
    exported_at timestamp with time zone,
    updated_at timestamp with time zone NOT NULL,
    workspace_id integer NOT NULL,
    response_logs jsonb,
    employee_name character varying(100)
);


ALTER TABLE public.expense_groups OWNER TO postgres;

--
-- Name: expense_groups_expenses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expense_groups_expenses (
    id integer NOT NULL,
    expensegroup_id integer NOT NULL,
    expense_id integer NOT NULL
);


ALTER TABLE public.expense_groups_expenses OWNER TO postgres;

--
-- Name: expense_groups_expenses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.expense_groups_expenses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.expense_groups_expenses_id_seq OWNER TO postgres;

--
-- Name: expense_groups_expenses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.expense_groups_expenses_id_seq OWNED BY public.expense_groups_expenses.id;


--
-- Name: expense_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.expense_groups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.expense_groups_id_seq OWNER TO postgres;

--
-- Name: expense_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.expense_groups_id_seq OWNED BY public.expense_groups.id;


--
-- Name: expenses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expenses (
    id integer NOT NULL,
    employee_email character varying(255) NOT NULL,
    category character varying(255),
    sub_category character varying(255),
    project character varying(255),
    expense_id character varying(255) NOT NULL,
    expense_number character varying(255) NOT NULL,
    claim_number character varying(255),
    amount double precision NOT NULL,
    currency character varying(5) NOT NULL,
    foreign_amount double precision,
    foreign_currency character varying(5),
    settlement_id character varying(255),
    reimbursable boolean NOT NULL,
    state character varying(255) NOT NULL,
    vendor character varying(255),
    cost_center character varying(255),
    purpose text,
    report_id character varying(255) NOT NULL,
    spent_at timestamp with time zone,
    approved_at timestamp with time zone,
    expense_created_at timestamp with time zone NOT NULL,
    expense_updated_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    fund_source character varying(255) NOT NULL,
    verified_at timestamp with time zone,
    custom_properties jsonb,
    paid_on_xero boolean NOT NULL,
    org_id character varying(255),
    file_ids character varying(255)[],
    corporate_card_id character varying(255),
    tax_amount double precision,
    tax_group_id character varying(255),
    billable boolean NOT NULL,
    employee_name character varying(255),
    posted_at timestamp with time zone
);


ALTER TABLE public.expenses OWNER TO postgres;

--
-- Name: expenses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.expenses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.expenses_id_seq OWNER TO postgres;

--
-- Name: expenses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.expenses_id_seq OWNED BY public.expenses.id;


--
-- Name: fyle_accounting_mappings_destinationattribute_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fyle_accounting_mappings_destinationattribute_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fyle_accounting_mappings_destinationattribute_id_seq OWNER TO postgres;

--
-- Name: fyle_accounting_mappings_destinationattribute_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fyle_accounting_mappings_destinationattribute_id_seq OWNED BY public.destination_attributes.id;


--
-- Name: fyle_accounting_mappings_expenseattribute_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fyle_accounting_mappings_expenseattribute_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fyle_accounting_mappings_expenseattribute_id_seq OWNER TO postgres;

--
-- Name: fyle_accounting_mappings_expenseattribute_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fyle_accounting_mappings_expenseattribute_id_seq OWNED BY public.expense_attributes.id;


--
-- Name: mappings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mappings (
    id integer NOT NULL,
    source_type character varying(255) NOT NULL,
    destination_type character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    destination_id integer NOT NULL,
    source_id integer NOT NULL,
    workspace_id integer NOT NULL
);


ALTER TABLE public.mappings OWNER TO postgres;

--
-- Name: fyle_accounting_mappings_mapping_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fyle_accounting_mappings_mapping_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fyle_accounting_mappings_mapping_id_seq OWNER TO postgres;

--
-- Name: fyle_accounting_mappings_mapping_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fyle_accounting_mappings_mapping_id_seq OWNED BY public.mappings.id;


--
-- Name: mapping_settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mapping_settings (
    id integer NOT NULL,
    source_field character varying(255) NOT NULL,
    destination_field character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    workspace_id integer NOT NULL,
    import_to_fyle boolean NOT NULL,
    is_custom boolean NOT NULL,
    source_placeholder text,
    expense_field_id integer
);


ALTER TABLE public.mapping_settings OWNER TO postgres;

--
-- Name: fyle_accounting_mappings_mappingsetting_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fyle_accounting_mappings_mappingsetting_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fyle_accounting_mappings_mappingsetting_id_seq OWNER TO postgres;

--
-- Name: fyle_accounting_mappings_mappingsetting_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fyle_accounting_mappings_mappingsetting_id_seq OWNED BY public.mapping_settings.id;


--
-- Name: fyle_credentials; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fyle_credentials (
    id integer NOT NULL,
    refresh_token text NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    workspace_id integer NOT NULL,
    cluster_domain character varying(255)
);


ALTER TABLE public.fyle_credentials OWNER TO postgres;

--
-- Name: fyle_credentials_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fyle_credentials_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fyle_credentials_id_seq OWNER TO postgres;

--
-- Name: fyle_credentials_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fyle_credentials_id_seq OWNED BY public.fyle_credentials.id;


--
-- Name: fyle_expensegroupsettings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fyle_expensegroupsettings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fyle_expensegroupsettings_id_seq OWNER TO postgres;

--
-- Name: fyle_expensegroupsettings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fyle_expensegroupsettings_id_seq OWNED BY public.expense_group_settings.id;


--
-- Name: fyle_rest_auth_authtokens_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fyle_rest_auth_authtokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fyle_rest_auth_authtokens_id_seq OWNER TO postgres;

--
-- Name: fyle_rest_auth_authtokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fyle_rest_auth_authtokens_id_seq OWNED BY public.auth_tokens.id;


--
-- Name: general_mappings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.general_mappings (
    id integer NOT NULL,
    bank_account_name character varying(255),
    bank_account_id character varying(255),
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    workspace_id integer NOT NULL,
    payment_account_id character varying(255),
    payment_account_name character varying(255),
    default_tax_code_id character varying(255),
    default_tax_code_name character varying(255)
);


ALTER TABLE public.general_mappings OWNER TO postgres;

--
-- Name: general_mappings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.general_mappings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.general_mappings_id_seq OWNER TO postgres;

--
-- Name: general_mappings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.general_mappings_id_seq OWNED BY public.general_mappings.id;


--
-- Name: last_export_details; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.last_export_details (
    id integer NOT NULL,
    last_exported_at timestamp with time zone,
    export_mode character varying(50),
    total_expense_groups_count integer,
    successful_expense_groups_count integer,
    failed_expense_groups_count integer,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    workspace_id integer NOT NULL
);


ALTER TABLE public.last_export_details OWNER TO postgres;

--
-- Name: last_export_details_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.last_export_details_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.last_export_details_id_seq OWNER TO postgres;

--
-- Name: last_export_details_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.last_export_details_id_seq OWNED BY public.last_export_details.id;


--
-- Name: payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payments (
    id integer NOT NULL,
    invoice_id character varying(255) NOT NULL,
    account_id character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    expense_group_id integer NOT NULL,
    workspace_id integer NOT NULL,
    amount double precision NOT NULL
);


ALTER TABLE public.payments OWNER TO postgres;

--
-- Name: payments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.payments_id_seq OWNER TO postgres;

--
-- Name: payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.payments_id_seq OWNED BY public.payments.id;


--
-- Name: reimbursements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reimbursements (
    id integer NOT NULL,
    settlement_id character varying(255) NOT NULL,
    reimbursement_id character varying(255) NOT NULL,
    state character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    workspace_id integer NOT NULL
);


ALTER TABLE public.reimbursements OWNER TO postgres;

--
-- Name: reimbursements_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reimbursements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.reimbursements_id_seq OWNER TO postgres;

--
-- Name: reimbursements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reimbursements_id_seq OWNED BY public.reimbursements.id;


--
-- Name: task_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.task_logs (
    id integer NOT NULL,
    type character varying(50) NOT NULL,
    task_id character varying(255),
    status character varying(255) NOT NULL,
    detail jsonb,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    expense_group_id integer,
    workspace_id integer NOT NULL,
    bank_transaction_id integer,
    bill_id integer,
    xero_errors jsonb,
    payment_id integer
);


ALTER TABLE public.task_logs OWNER TO postgres;

--
-- Name: task_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.task_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.task_log_id_seq OWNER TO postgres;

--
-- Name: task_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.task_log_id_seq OWNED BY public.task_logs.id;


--
-- Name: tenant_mappings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tenant_mappings (
    id integer NOT NULL,
    tenant_name character varying(255),
    tenant_id character varying(255),
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    workspace_id integer NOT NULL,
    connection_id character varying(255)
);


ALTER TABLE public.tenant_mappings OWNER TO postgres;

--
-- Name: tenant_mappings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tenant_mappings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tenant_mappings_id_seq OWNER TO postgres;

--
-- Name: tenant_mappings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tenant_mappings_id_seq OWNED BY public.tenant_mappings.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    user_id character varying(255) NOT NULL,
    full_name character varying(255) NOT NULL,
    active boolean NOT NULL,
    staff boolean NOT NULL,
    admin boolean NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_user_id_seq OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.id;


--
-- Name: workspace_general_settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workspace_general_settings (
    id integer NOT NULL,
    reimbursable_expenses_object character varying(50),
    corporate_credit_card_expenses_object character varying(50),
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    workspace_id integer NOT NULL,
    sync_fyle_to_xero_payments boolean NOT NULL,
    sync_xero_to_fyle_payments boolean NOT NULL,
    import_categories boolean NOT NULL,
    auto_map_employees character varying(50),
    auto_create_destination_entity boolean NOT NULL,
    map_merchant_to_contact boolean NOT NULL,
    skip_cards_mapping boolean NOT NULL,
    import_tax_codes boolean,
    charts_of_accounts character varying(100)[] NOT NULL,
    import_customers boolean NOT NULL,
    change_accounting_period boolean NOT NULL,
    auto_create_merchant_destination_entity boolean NOT NULL,
    is_simplify_report_closure_enabled boolean NOT NULL,
    import_suppliers_as_merchants boolean NOT NULL
);


ALTER TABLE public.workspace_general_settings OWNER TO postgres;

--
-- Name: workspace_schedules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workspace_schedules (
    id integer NOT NULL,
    enabled boolean NOT NULL,
    start_datetime timestamp with time zone,
    interval_hours integer,
    schedule_id integer,
    workspace_id integer NOT NULL,
    additional_email_options jsonb,
    emails_selected character varying(255)[],
    error_count integer
);


ALTER TABLE public.workspace_schedules OWNER TO postgres;

--
-- Name: workspaces; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workspaces (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    fyle_org_id character varying(255) NOT NULL,
    last_synced_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    destination_synced_at timestamp with time zone,
    source_synced_at timestamp with time zone,
    xero_short_code character varying(30),
    xero_accounts_last_synced_at timestamp with time zone,
    onboarding_state character varying(50),
    app_version character varying(2) NOT NULL,
    fyle_currency character varying(5),
    xero_currency character varying(5),
    ccc_last_synced_at timestamp with time zone
);


ALTER TABLE public.workspaces OWNER TO postgres;

--
-- Name: workspaces_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workspaces_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workspaces_id_seq OWNER TO postgres;

--
-- Name: workspaces_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workspaces_id_seq OWNED BY public.workspaces.id;


--
-- Name: workspaces_user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workspaces_user (
    id integer NOT NULL,
    workspace_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.workspaces_user OWNER TO postgres;

--
-- Name: workspaces_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workspaces_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workspaces_user_id_seq OWNER TO postgres;

--
-- Name: workspaces_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workspaces_user_id_seq OWNED BY public.workspaces_user.id;


--
-- Name: workspaces_workspacegeneralsettings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workspaces_workspacegeneralsettings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workspaces_workspacegeneralsettings_id_seq OWNER TO postgres;

--
-- Name: workspaces_workspacegeneralsettings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workspaces_workspacegeneralsettings_id_seq OWNED BY public.workspace_general_settings.id;


--
-- Name: workspaces_workspaceschedule_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workspaces_workspaceschedule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workspaces_workspaceschedule_id_seq OWNER TO postgres;

--
-- Name: workspaces_workspaceschedule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workspaces_workspaceschedule_id_seq OWNED BY public.workspace_schedules.id;


--
-- Name: xero_credentials; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.xero_credentials (
    id integer NOT NULL,
    refresh_token text,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    workspace_id integer NOT NULL,
    country character varying(255),
    is_expired boolean NOT NULL
);


ALTER TABLE public.xero_credentials OWNER TO postgres;

--
-- Name: xero_credentials_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.xero_credentials_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.xero_credentials_id_seq OWNER TO postgres;

--
-- Name: xero_credentials_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.xero_credentials_id_seq OWNED BY public.xero_credentials.id;


--
-- Name: auth_group id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group ALTER COLUMN id SET DEFAULT nextval('public.auth_group_id_seq'::regclass);


--
-- Name: auth_group_permissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('public.auth_group_permissions_id_seq'::regclass);


--
-- Name: auth_permission id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_permission ALTER COLUMN id SET DEFAULT nextval('public.auth_permission_id_seq'::regclass);


--
-- Name: auth_tokens id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_tokens ALTER COLUMN id SET DEFAULT nextval('public.fyle_rest_auth_authtokens_id_seq'::regclass);


--
-- Name: bank_transaction_lineitems id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_transaction_lineitems ALTER COLUMN id SET DEFAULT nextval('public.bank_transaction_lineitems_id_seq'::regclass);


--
-- Name: bank_transactions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_transactions ALTER COLUMN id SET DEFAULT nextval('public.bank_transactions_id_seq'::regclass);


--
-- Name: bill_lineitems id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bill_lineitems ALTER COLUMN id SET DEFAULT nextval('public.bill_lineitems_id_seq'::regclass);


--
-- Name: bills id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bills ALTER COLUMN id SET DEFAULT nextval('public.bills_id_seq'::regclass);


--
-- Name: category_mappings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.category_mappings ALTER COLUMN id SET DEFAULT nextval('public.category_mappings_id_seq'::regclass);


--
-- Name: destination_attributes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.destination_attributes ALTER COLUMN id SET DEFAULT nextval('public.fyle_accounting_mappings_destinationattribute_id_seq'::regclass);


--
-- Name: django_admin_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_admin_log ALTER COLUMN id SET DEFAULT nextval('public.django_admin_log_id_seq'::regclass);


--
-- Name: django_content_type id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_content_type ALTER COLUMN id SET DEFAULT nextval('public.django_content_type_id_seq'::regclass);


--
-- Name: django_migrations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_migrations ALTER COLUMN id SET DEFAULT nextval('public.django_migrations_id_seq'::regclass);


--
-- Name: django_q_ormq id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_q_ormq ALTER COLUMN id SET DEFAULT nextval('public.django_q_ormq_id_seq'::regclass);


--
-- Name: django_q_schedule id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_q_schedule ALTER COLUMN id SET DEFAULT nextval('public.django_q_schedule_id_seq'::regclass);


--
-- Name: employee_mappings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_mappings ALTER COLUMN id SET DEFAULT nextval('public.employee_mappings_id_seq'::regclass);


--
-- Name: errors id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.errors ALTER COLUMN id SET DEFAULT nextval('public.errors_id_seq'::regclass);


--
-- Name: expense_attributes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_attributes ALTER COLUMN id SET DEFAULT nextval('public.fyle_accounting_mappings_expenseattribute_id_seq'::regclass);


--
-- Name: expense_fields id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_fields ALTER COLUMN id SET DEFAULT nextval('public.expense_fields_id_seq'::regclass);


--
-- Name: expense_group_settings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_group_settings ALTER COLUMN id SET DEFAULT nextval('public.fyle_expensegroupsettings_id_seq'::regclass);


--
-- Name: expense_groups id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_groups ALTER COLUMN id SET DEFAULT nextval('public.expense_groups_id_seq'::regclass);


--
-- Name: expense_groups_expenses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_groups_expenses ALTER COLUMN id SET DEFAULT nextval('public.expense_groups_expenses_id_seq'::regclass);


--
-- Name: expenses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses ALTER COLUMN id SET DEFAULT nextval('public.expenses_id_seq'::regclass);


--
-- Name: fyle_credentials id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fyle_credentials ALTER COLUMN id SET DEFAULT nextval('public.fyle_credentials_id_seq'::regclass);


--
-- Name: general_mappings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.general_mappings ALTER COLUMN id SET DEFAULT nextval('public.general_mappings_id_seq'::regclass);


--
-- Name: last_export_details id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.last_export_details ALTER COLUMN id SET DEFAULT nextval('public.last_export_details_id_seq'::regclass);


--
-- Name: mapping_settings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mapping_settings ALTER COLUMN id SET DEFAULT nextval('public.fyle_accounting_mappings_mappingsetting_id_seq'::regclass);


--
-- Name: mappings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mappings ALTER COLUMN id SET DEFAULT nextval('public.fyle_accounting_mappings_mapping_id_seq'::regclass);


--
-- Name: payments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments ALTER COLUMN id SET DEFAULT nextval('public.payments_id_seq'::regclass);


--
-- Name: reimbursements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reimbursements ALTER COLUMN id SET DEFAULT nextval('public.reimbursements_id_seq'::regclass);


--
-- Name: task_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_logs ALTER COLUMN id SET DEFAULT nextval('public.task_log_id_seq'::regclass);


--
-- Name: tenant_mappings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_mappings ALTER COLUMN id SET DEFAULT nextval('public.tenant_mappings_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Name: workspace_general_settings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspace_general_settings ALTER COLUMN id SET DEFAULT nextval('public.workspaces_workspacegeneralsettings_id_seq'::regclass);


--
-- Name: workspace_schedules id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspace_schedules ALTER COLUMN id SET DEFAULT nextval('public.workspaces_workspaceschedule_id_seq'::regclass);


--
-- Name: workspaces id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspaces ALTER COLUMN id SET DEFAULT nextval('public.workspaces_id_seq'::regclass);


--
-- Name: workspaces_user id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspaces_user ALTER COLUMN id SET DEFAULT nextval('public.workspaces_user_id_seq'::regclass);


--
-- Name: xero_credentials id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.xero_credentials ALTER COLUMN id SET DEFAULT nextval('public.xero_credentials_id_seq'::regclass);


--
-- Data for Name: auth_cache; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_cache (cache_key, value, expires) FROM stdin;
\.


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	2	add_permission
6	Can change permission	2	change_permission
7	Can delete permission	2	delete_permission
8	Can view permission	2	view_permission
9	Can add group	3	add_group
10	Can change group	3	change_group
11	Can delete group	3	delete_group
12	Can view group	3	view_group
13	Can add content type	4	add_contenttype
14	Can change content type	4	change_contenttype
15	Can delete content type	4	delete_contenttype
16	Can view content type	4	view_contenttype
17	Can add session	5	add_session
18	Can change session	5	change_session
19	Can delete session	5	delete_session
20	Can view session	5	view_session
21	Can add auth token	6	add_authtoken
22	Can change auth token	6	change_authtoken
23	Can delete auth token	6	delete_authtoken
24	Can view auth token	6	view_authtoken
25	Can add destination attribute	7	add_destinationattribute
26	Can change destination attribute	7	change_destinationattribute
27	Can delete destination attribute	7	delete_destinationattribute
28	Can view destination attribute	7	view_destinationattribute
29	Can add expense attribute	8	add_expenseattribute
30	Can change expense attribute	8	change_expenseattribute
31	Can delete expense attribute	8	delete_expenseattribute
32	Can view expense attribute	8	view_expenseattribute
33	Can add mapping setting	9	add_mappingsetting
34	Can change mapping setting	9	change_mappingsetting
35	Can delete mapping setting	9	delete_mappingsetting
36	Can view mapping setting	9	view_mappingsetting
37	Can add mapping	10	add_mapping
38	Can change mapping	10	change_mapping
39	Can delete mapping	10	delete_mapping
40	Can view mapping	10	view_mapping
41	Can add employee mapping	11	add_employeemapping
42	Can change employee mapping	11	change_employeemapping
43	Can delete employee mapping	11	delete_employeemapping
44	Can view employee mapping	11	view_employeemapping
45	Can add category mapping	12	add_categorymapping
46	Can change category mapping	12	change_categorymapping
47	Can delete category mapping	12	delete_categorymapping
48	Can view category mapping	12	view_categorymapping
49	Can add user	13	add_user
50	Can change user	13	change_user
51	Can delete user	13	delete_user
52	Can view user	13	view_user
53	Can add workspace	14	add_workspace
54	Can change workspace	14	change_workspace
55	Can delete workspace	14	delete_workspace
56	Can view workspace	14	view_workspace
57	Can add xero credentials	15	add_xerocredentials
58	Can change xero credentials	15	change_xerocredentials
59	Can delete xero credentials	15	delete_xerocredentials
60	Can view xero credentials	15	view_xerocredentials
61	Can add workspace general settings	16	add_workspacegeneralsettings
62	Can change workspace general settings	16	change_workspacegeneralsettings
63	Can delete workspace general settings	16	delete_workspacegeneralsettings
64	Can view workspace general settings	16	view_workspacegeneralsettings
65	Can add fyle credential	17	add_fylecredential
66	Can change fyle credential	17	change_fylecredential
67	Can delete fyle credential	17	delete_fylecredential
68	Can view fyle credential	17	view_fylecredential
69	Can add workspace schedule	18	add_workspaceschedule
70	Can change workspace schedule	18	change_workspaceschedule
71	Can delete workspace schedule	18	delete_workspaceschedule
72	Can view workspace schedule	18	view_workspaceschedule
73	Can add expense	19	add_expense
74	Can change expense	19	change_expense
75	Can delete expense	19	delete_expense
76	Can view expense	19	view_expense
77	Can add expense group settings	20	add_expensegroupsettings
78	Can change expense group settings	20	change_expensegroupsettings
79	Can delete expense group settings	20	delete_expensegroupsettings
80	Can view expense group settings	20	view_expensegroupsettings
81	Can add expense group	21	add_expensegroup
82	Can change expense group	21	change_expensegroup
83	Can delete expense group	21	delete_expensegroup
84	Can view expense group	21	view_expensegroup
85	Can add reimbursement	22	add_reimbursement
86	Can change reimbursement	22	change_reimbursement
87	Can delete reimbursement	22	delete_reimbursement
88	Can view reimbursement	22	view_reimbursement
89	Can add task log	23	add_tasklog
90	Can change task log	23	change_tasklog
91	Can delete task log	23	delete_tasklog
92	Can view task log	23	view_tasklog
93	Can add tenant mapping	24	add_tenantmapping
94	Can change tenant mapping	24	change_tenantmapping
95	Can delete tenant mapping	24	delete_tenantmapping
96	Can view tenant mapping	24	view_tenantmapping
97	Can add general mapping	25	add_generalmapping
98	Can change general mapping	25	change_generalmapping
99	Can delete general mapping	25	delete_generalmapping
100	Can view general mapping	25	view_generalmapping
101	Can add bill	26	add_bill
102	Can change bill	26	change_bill
103	Can delete bill	26	delete_bill
104	Can view bill	26	view_bill
105	Can add bill line item	27	add_billlineitem
106	Can change bill line item	27	change_billlineitem
107	Can delete bill line item	27	delete_billlineitem
108	Can view bill line item	27	view_billlineitem
109	Can add bank transaction	28	add_banktransaction
110	Can change bank transaction	28	change_banktransaction
111	Can delete bank transaction	28	delete_banktransaction
112	Can view bank transaction	28	view_banktransaction
113	Can add bank transaction line item	29	add_banktransactionlineitem
114	Can change bank transaction line item	29	change_banktransactionlineitem
115	Can delete bank transaction line item	29	delete_banktransactionlineitem
116	Can view bank transaction line item	29	view_banktransactionlineitem
117	Can add payment	30	add_payment
118	Can change payment	30	change_payment
119	Can delete payment	30	delete_payment
120	Can view payment	30	view_payment
121	Can add Scheduled task	31	add_schedule
122	Can change Scheduled task	31	change_schedule
123	Can delete Scheduled task	31	delete_schedule
124	Can view Scheduled task	31	view_schedule
125	Can add task	32	add_task
126	Can change task	32	change_task
127	Can delete task	32	delete_task
128	Can view task	32	view_task
129	Can add Failed task	33	add_failure
130	Can change Failed task	33	change_failure
131	Can delete Failed task	33	delete_failure
132	Can view Failed task	33	view_failure
133	Can add Successful task	34	add_success
134	Can change Successful task	34	change_success
135	Can delete Successful task	34	delete_success
136	Can view Successful task	34	view_success
137	Can add Queued task	35	add_ormq
138	Can change Queued task	35	change_ormq
139	Can delete Queued task	35	delete_ormq
140	Can view Queued task	35	view_ormq
141	Can add error	36	add_error
142	Can change error	36	change_error
143	Can delete error	36	delete_error
144	Can view error	36	view_error
145	Can add last export detail	37	add_lastexportdetail
146	Can change last export detail	37	change_lastexportdetail
147	Can delete last export detail	37	delete_lastexportdetail
148	Can view last export detail	37	view_lastexportdetail
149	Can add expense field	38	add_expensefield
150	Can change expense field	38	change_expensefield
151	Can delete expense field	38	delete_expensefield
152	Can view expense field	38	view_expensefield
\.


--
-- Data for Name: auth_tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_tokens (id, refresh_token, user_id) FROM stdin;
1	eyJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2NTk0NzE4NzgsImlzcyI6IkZ5bGVBcHAiLCJvcmdfdXNlcl9pZCI6Ilwib3VXRk5QNDlUWHlQXCIiLCJ0cGFfaWQiOiJcInRwYW9Ua2VFYWlGZWdcIiIsInRwYV9uYW1lIjoiXCJGeWxlIFhlcm8gSW50ZWcuLlwiIiwiY2x1c3Rlcl9kb21haW4iOiJcImh0dHBzOi8vc3RhZ2luZy5meWxlLnRlY2hcIiIsImV4cCI6MTk3NDgzMTg3OH0.mOHEigQMVW9MO1SQaKMjIzZ1kD79lYrhGXo_-zSmD04	1
\.


--
-- Data for Name: bank_transaction_lineitems; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bank_transaction_lineitems (id, account_id, item_code, tracking_categories, amount, description, created_at, updated_at, bank_transaction_id, expense_id, tax_amount, tax_code, customer_id, line_item_id) FROM stdin;
1	429	\N	\N	10	sravan.kumar@fyle.in, category - WIP spent on 2022-05-25, report number - C/2022/05/R/13  - https://staging.fyle.tech/app/admin/#/enterprise/view_expense/txBMQRkBQciI?org_id=orPJvXuoLqvJ	2022-08-02 20:27:58.697679+00	2022-08-02 20:27:59.403964+00	1	9	\N	\N	\N	c6608618-f41c-4496-8fad-e057433313e9
2	429	\N	\N	101	sravan.kumar@fyle.in, category - WIP spent on 2022-05-24, report number - C/2022/05/R/12  - https://staging.fyle.tech/app/admin/#/enterprise/view_expense/txkw3dt3umkN?org_id=orPJvXuoLqvJ	2022-08-02 20:28:02.731907+00	2022-08-02 20:28:03.689727+00	2	10	\N	\N	\N	e683b297-e13a-4cd5-9c0e-33eabe20b9b1
3	429	\N	\N	151	sravan.kumar@fyle.in, category - WIP spent on 2022-05-25, report number - C/2022/05/R/15  - https://staging.fyle.tech/app/admin/#/enterprise/view_expense/tx1FW3uxYZG6?org_id=orPJvXuoLqvJ	2022-08-02 20:28:07.102842+00	2022-08-02 20:28:07.661616+00	3	7	\N	\N	\N	813ee68f-0f2f-4a5d-b50a-cc5da5167bfc
4	429	\N	\N	100	sravan.kumar@fyle.in, category - Food spent on 2022-05-25, report number - C/2022/05/R/18  - https://staging.fyle.tech/app/admin/#/enterprise/view_expense/txjIqTCtkkC8?org_id=orPJvXuoLqvJ	2022-08-02 20:28:11.19761+00	2022-08-02 20:28:11.755289+00	4	4	\N	\N	\N	1dcc3c7c-02a5-4b26-b913-8f7d4af3a2b5
5	429	\N	\N	101	sravan.kumar@fyle.in, category - WIP spent on 2021-01-01, report number - C/2022/05/R/17  - https://staging.fyle.tech/app/admin/#/enterprise/view_expense/txUPRc3VwxOP?org_id=orPJvXuoLqvJ	2022-08-02 20:28:15.494549+00	2022-08-02 20:28:16.120904+00	5	5	\N	\N	\N	d04728ba-27b2-411a-9110-26061ca3342a
6	429	\N	\N	45	sravan.kumar@fyle.in, category - WIP spent on 2022-05-25, report number - C/2022/05/R/14  - https://staging.fyle.tech/app/admin/#/enterprise/view_expense/txVXhyVB8mgK?org_id=orPJvXuoLqvJ	2022-08-02 20:28:19.536148+00	2022-08-02 20:28:20.034073+00	6	8	\N	\N	\N	b6256803-f91d-458b-88a5-3fc1d860aa62
\.


--
-- Data for Name: bank_transactions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bank_transactions (id, contact_id, bank_account_code, currency, reference, transaction_date, created_at, updated_at, expense_group_id, export_id) FROM stdin;
1	3aaf24ba-6d35-455f-b92a-9e0dc20d3d9a	562555f2-8cde-4ce9-8203-0363922537a4	USD	10 - sravan.kumar@fyle.in	2022-05-25	2022-08-02 20:27:58.615801+00	2022-08-02 20:27:59.401764+00	10	a66a279c-f510-4723-a1ef-7fc9488aa3cb
2	3aaf24ba-6d35-455f-b92a-9e0dc20d3d9a	562555f2-8cde-4ce9-8203-0363922537a4	USD	5 - sravan.kumar@fyle.in	2022-05-24	2022-08-02 20:28:02.689921+00	2022-08-02 20:28:03.686902+00	5	a00e1785-4aac-404c-80a5-f80a1a7f58cc
3	3aaf24ba-6d35-455f-b92a-9e0dc20d3d9a	562555f2-8cde-4ce9-8203-0363922537a4	USD	8 - sravan.kumar@fyle.in	2022-05-25	2022-08-02 20:28:07.028819+00	2022-08-02 20:28:07.660028+00	8	3539faf8-19bf-4737-a218-90705824fa97
4	3aaf24ba-6d35-455f-b92a-9e0dc20d3d9a	562555f2-8cde-4ce9-8203-0363922537a4	USD	6 - sravan.kumar@fyle.in	2022-05-25	2022-08-02 20:28:11.155638+00	2022-08-02 20:28:11.753165+00	6	bbd472ed-d366-4695-a32b-f170b15eeb1b
5	3aaf24ba-6d35-455f-b92a-9e0dc20d3d9a	562555f2-8cde-4ce9-8203-0363922537a4	USD	9 - sravan.kumar@fyle.in	2021-01-01	2022-08-02 20:28:15.443594+00	2022-08-02 20:28:16.118977+00	9	7311b70a-e270-46e9-a182-84031e99b222
6	3aaf24ba-6d35-455f-b92a-9e0dc20d3d9a	562555f2-8cde-4ce9-8203-0363922537a4	USD	7 - sravan.kumar@fyle.in	2022-05-25	2022-08-02 20:28:19.484476+00	2022-08-02 20:28:20.032035+00	7	7cad7d4b-b62f-4265-bdbb-b0e40da46df3
\.


--
-- Data for Name: bill_lineitems; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bill_lineitems (id, tracking_categories, item_code, account_id, description, amount, bill_id, expense_id, tax_amount, tax_code, customer_id, line_item_id) FROM stdin;
1	\N	\N	429	ashwin.t@fyle.in, category - Food spent on 2020-05-25, report number - C/2022/05/R/16  - https://staging.fyle.tech/app/admin/#/enterprise/view_expense/txUDvDmEV4ep?org_id=orPJvXuoLqvJ	5	1	6	\N	\N	\N	51cca2e7-5bef-452c-83fb-2ca8c0865f37
2	\N	\N	429	sravan.kumar@fyle.in, category - Food spent on 2020-01-01, report number - C/2022/06/R/1  - https://staging.fyle.tech/app/admin/#/enterprise/view_expense/txGilVGolf60?org_id=orPJvXuoLqvJ	10	2	3	\N	\N	\N	dd9fa5fc-11f7-4113-b67a-e799220811e7
3	\N	\N	429	ashwin.t@fyle.in, category - Food spent on 2022-06-27, report number - C/2022/06/R/2  - https://staging.fyle.tech/app/admin/#/enterprise/view_expense/txaaVBj3yKGW?org_id=orPJvXuoLqvJ	1	3	1	\N	\N	\N	bd0a73f3-16bf-44fa-ad49-302692bbff14
4	\N	\N	429	ashwin.t@fyle.in, category - Food spent on 2022-06-27, report number - C/2022/06/R/3  - https://staging.fyle.tech/app/admin/#/enterprise/view_expense/txB6D8k0Ws8a?org_id=orPJvXuoLqvJ	4	4	2	\N	\N	\N	913aa7a1-fc6f-4156-a263-46a85b7cfbc9
\.


--
-- Data for Name: bills; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bills (id, currency, contact_id, reference, date, created_at, updated_at, expense_group_id, paid_on_xero, payment_synced, export_id) FROM stdin;
1	USD	9eecdd86-78bb-47c9-95df-986369748151	2 - ashwin.t@fyle.in	2022-08-02 00:00:00+00	2022-08-02 20:27:44.058777+00	2022-08-02 20:27:44.877194+00	2	f	f	c35cf4b3-784a-408b-9ddf-df111dd2e073
2	USD	229b7701-21a2-4539-b39e-5c34f56e1711	4 - sravan.kumar@fyle.in	2022-08-02 00:00:00+00	2022-08-02 20:27:48.290698+00	2022-08-02 20:27:48.932223+00	4	f	f	2780aebc-2f8c-4b47-a7e2-64b920c5e7c1
3	USD	9eecdd86-78bb-47c9-95df-986369748151	1 - ashwin.t@fyle.in	2022-08-02 00:00:00+00	2022-08-02 20:27:51.443082+00	2022-08-02 20:27:52.020404+00	1	f	f	c70ce61b-5157-4e11-97c7-6d1f843b2a5f
4	USD	9eecdd86-78bb-47c9-95df-986369748151	3 - ashwin.t@fyle.in	2022-08-02 00:00:00+00	2022-08-02 20:27:54.558597+00	2022-08-02 20:27:55.12968+00	3	f	f	9520557e-c20c-4fa4-b4b4-702102866beb
\.


--
-- Data for Name: category_mappings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.category_mappings (id, created_at, updated_at, destination_account_id, destination_expense_head_id, source_category_id, workspace_id) FROM stdin;
\.


--
-- Data for Name: destination_attributes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.destination_attributes (id, attribute_type, display_name, value, destination_id, created_at, updated_at, workspace_id, active, detail, auto_created) FROM stdin;
1	TENANT	Tenant	Demo Company (Global)	36ab1910-11b3-4325-b545-8d1170668ab3	2022-08-02 20:24:57.176235+00	2022-08-02 20:24:57.176295+00	1	\N	\N	f
2	BANK_ACCOUNT	Bank Account	Business Bank Account	562555f2-8cde-4ce9-8203-0363922537a4	2022-08-02 20:25:06.834102+00	2022-08-02 20:25:06.8342+00	1	\N	{"active": true, "account_type": "ASSET", "enable_payments_to_account": false}	f
3	BANK_ACCOUNT	Bank Account	Business Savings Account	72f1dcfe-5d7d-4239-bf9d-e12469309716	2022-08-02 20:25:06.834588+00	2022-08-02 20:25:06.834631+00	1	\N	{"active": true, "account_type": "ASSET", "enable_payments_to_account": false}	f
4	ACCOUNT	Account	Sales	200	2022-08-02 20:25:06.849237+00	2022-08-02 20:25:06.849281+00	1	\N	{"active": true, "account_type": "REVENUE", "enable_payments_to_account": false}	f
5	ACCOUNT	Account	Other Revenue	260	2022-08-02 20:25:06.849477+00	2022-08-02 20:25:06.849508+00	1	\N	{"active": true, "account_type": "REVENUE", "enable_payments_to_account": false}	f
6	ACCOUNT	Account	Interest Income	270	2022-08-02 20:25:06.849634+00	2022-08-02 20:25:06.849665+00	1	\N	{"active": true, "account_type": "REVENUE", "enable_payments_to_account": false}	f
7	ACCOUNT	Account	Purchases	300	2022-08-02 20:25:06.849734+00	2022-08-02 20:25:06.849763+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
8	ACCOUNT	Account	Cost of Goods Sold	310	2022-08-02 20:25:06.849831+00	2022-08-02 20:25:06.849861+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
9	ACCOUNT	Account	Advertising	400	2022-08-02 20:25:06.849929+00	2022-08-02 20:25:06.850065+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
10	ACCOUNT	Account	Bank Fees	404	2022-08-02 20:25:06.850152+00	2022-08-02 20:25:06.8502+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
11	ACCOUNT	Account	Cleaning	408	2022-08-02 20:25:06.850582+00	2022-08-02 20:25:06.850621+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
12	ACCOUNT	Account	Consulting & Accounting	412	2022-08-02 20:25:06.850725+00	2022-08-02 20:25:06.850767+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
13	ACCOUNT	Account	Depreciation	416	2022-08-02 20:25:06.85094+00	2022-08-02 20:25:06.851022+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
14	ACCOUNT	Account	Entertainment	420	2022-08-02 20:25:06.851564+00	2022-08-02 20:25:06.851622+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
15	ACCOUNT	Account	Freight & Courier	425	2022-08-02 20:25:06.851818+00	2022-08-02 20:25:06.851871+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
16	ACCOUNT	Account	General Expenses	429	2022-08-02 20:25:06.851943+00	2022-08-02 20:25:06.851971+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
17	ACCOUNT	Account	Insurance	433	2022-08-02 20:25:06.852035+00	2022-08-02 20:25:06.852063+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
18	ACCOUNT	Account	Interest Expense	437	2022-08-02 20:25:06.852232+00	2022-08-02 20:25:06.852261+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
19	ACCOUNT	Account	Legal expenses	441	2022-08-02 20:25:06.852325+00	2022-08-02 20:25:06.852352+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
20	ACCOUNT	Account	Light, Power, Heating	445	2022-08-02 20:25:06.852416+00	2022-08-02 20:25:06.852444+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
21	ACCOUNT	Account	Motor Vehicle Expenses	449	2022-08-02 20:25:06.852507+00	2022-08-02 20:25:06.852535+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
22	ACCOUNT	Account	Office Expenses	453	2022-08-02 20:25:06.852597+00	2022-08-02 20:25:06.852625+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
23	ACCOUNT	Account	Printing & Stationery	461	2022-08-02 20:25:06.852687+00	2022-08-02 20:25:06.852714+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
24	ACCOUNT	Account	Rent	469	2022-08-02 20:25:06.852777+00	2022-08-02 20:25:06.852805+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
25	ACCOUNT	Account	Repairs and Maintenance	473	2022-08-02 20:25:06.852868+00	2022-08-02 20:25:06.852895+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
26	ACCOUNT	Account	Wages and Salaries	477	2022-08-02 20:25:06.852958+00	2022-08-02 20:25:06.852986+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
27	ACCOUNT	Account	Superannuation	478	2022-08-02 20:25:06.853048+00	2022-08-02 20:25:06.853076+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
28	ACCOUNT	Account	Subscriptions	485	2022-08-02 20:25:06.853138+00	2022-08-02 20:25:06.853165+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
29	ACCOUNT	Account	Telephone & Internet	489	2022-08-02 20:25:06.853228+00	2022-08-02 20:25:06.853257+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
30	ACCOUNT	Account	Travel - National	493	2022-08-02 20:25:06.853438+00	2022-08-02 20:25:06.853466+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
31	ACCOUNT	Account	Travel - International	494	2022-08-02 20:25:06.853528+00	2022-08-02 20:25:06.853556+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
32	ACCOUNT	Account	Bank Revaluations	497	2022-08-02 20:25:06.853618+00	2022-08-02 20:25:06.853646+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
33	ACCOUNT	Account	Unrealised Currency Gains	498	2022-08-02 20:25:06.853707+00	2022-08-02 20:25:06.853735+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
34	ACCOUNT	Account	Realised Currency Gains	499	2022-08-02 20:25:06.853797+00	2022-08-02 20:25:06.853825+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
35	ACCOUNT	Account	Income Tax Expense	505	2022-08-02 20:25:06.853887+00	2022-08-02 20:25:06.853915+00	1	\N	{"active": true, "account_type": "EXPENSE", "enable_payments_to_account": false}	f
36	ACCOUNT	Account	Accounts Receivable	610	2022-08-02 20:25:06.853977+00	2022-08-02 20:25:06.854005+00	1	\N	{"active": true, "account_type": "ASSET", "enable_payments_to_account": false}	f
37	ACCOUNT	Account	Prepayments	620	2022-08-02 20:25:06.854066+00	2022-08-02 20:25:06.854094+00	1	\N	{"active": true, "account_type": "ASSET", "enable_payments_to_account": false}	f
38	ACCOUNT	Account	Inventory	630	2022-08-02 20:25:06.854156+00	2022-08-02 20:25:06.854184+00	1	\N	{"active": true, "account_type": "ASSET", "enable_payments_to_account": false}	f
39	ACCOUNT	Account	Office Equipment	710	2022-08-02 20:25:06.854344+00	2022-08-02 20:25:06.854508+00	1	\N	{"active": true, "account_type": "ASSET", "enable_payments_to_account": false}	f
40	ACCOUNT	Account	Less Accumulated Depreciation on Office Equipment	711	2022-08-02 20:25:06.854693+00	2022-08-02 20:25:06.855219+00	1	\N	{"active": true, "account_type": "ASSET", "enable_payments_to_account": false}	f
41	ACCOUNT	Account	Computer Equipment	720	2022-08-02 20:25:06.855554+00	2022-08-02 20:25:06.855586+00	1	\N	{"active": true, "account_type": "ASSET", "enable_payments_to_account": false}	f
42	ACCOUNT	Account	Less Accumulated Depreciation on Computer Equipment	721	2022-08-02 20:25:06.855657+00	2022-08-02 20:25:06.855685+00	1	\N	{"active": true, "account_type": "ASSET", "enable_payments_to_account": false}	f
43	ACCOUNT	Account	Accounts Payable	800	2022-08-02 20:25:06.855751+00	2022-08-02 20:25:06.855779+00	1	\N	{"active": true, "account_type": "LIABILITY", "enable_payments_to_account": false}	f
44	ACCOUNT	Account	Unpaid Expense Claims	801	2022-08-02 20:25:06.855844+00	2022-08-02 20:25:06.855872+00	1	\N	{"active": true, "account_type": "LIABILITY", "enable_payments_to_account": false}	f
45	ACCOUNT	Account	Sales Tax	820	2022-08-02 20:25:06.855935+00	2022-08-02 20:25:06.855963+00	1	\N	{"active": true, "account_type": "LIABILITY", "enable_payments_to_account": false}	f
46	ACCOUNT	Account	Employee Tax Payable	825	2022-08-02 20:25:06.856026+00	2022-08-02 20:25:06.856054+00	1	\N	{"active": true, "account_type": "LIABILITY", "enable_payments_to_account": false}	f
47	ACCOUNT	Account	Superannuation Payable	826	2022-08-02 20:25:06.856116+00	2022-08-02 20:25:06.856144+00	1	\N	{"active": true, "account_type": "LIABILITY", "enable_payments_to_account": false}	f
48	ACCOUNT	Account	Income Tax Payable	830	2022-08-02 20:25:06.856207+00	2022-08-02 20:25:06.856235+00	1	\N	{"active": true, "account_type": "LIABILITY", "enable_payments_to_account": false}	f
49	ACCOUNT	Account	Revenue Received in Advance	835	2022-08-02 20:25:06.856451+00	2022-08-02 20:25:06.85648+00	1	\N	{"active": true, "account_type": "LIABILITY", "enable_payments_to_account": false}	f
50	ACCOUNT	Account	Historical Adjustment	840	2022-08-02 20:25:06.856543+00	2022-08-02 20:25:06.856572+00	1	\N	{"active": true, "account_type": "LIABILITY", "enable_payments_to_account": false}	f
51	ACCOUNT	Account	Suspense	850	2022-08-02 20:25:06.856635+00	2022-08-02 20:25:06.856663+00	1	\N	{"active": true, "account_type": "LIABILITY", "enable_payments_to_account": false}	f
52	ACCOUNT	Account	Clearing Account	855	2022-08-02 20:25:06.856725+00	2022-08-02 20:25:06.856754+00	1	\N	{"active": true, "account_type": "LIABILITY", "enable_payments_to_account": true}	f
53	ACCOUNT	Account	Rounding	860	2022-08-02 20:25:06.856816+00	2022-08-02 20:25:06.856844+00	1	\N	{"active": true, "account_type": "LIABILITY", "enable_payments_to_account": false}	f
54	ACCOUNT	Account	Tracking Transfers	877	2022-08-02 20:25:06.873717+00	2022-08-02 20:25:06.873766+00	1	\N	{"active": true, "account_type": "LIABILITY", "enable_payments_to_account": false}	f
55	ACCOUNT	Account	Owner A Drawings	880	2022-08-02 20:25:06.87384+00	2022-08-02 20:25:06.873918+00	1	\N	{"active": true, "account_type": "LIABILITY", "enable_payments_to_account": true}	f
56	ACCOUNT	Account	Owner A Funds Introduced	881	2022-08-02 20:25:06.874055+00	2022-08-02 20:25:06.874095+00	1	\N	{"active": true, "account_type": "LIABILITY", "enable_payments_to_account": true}	f
57	ACCOUNT	Account	Loan	900	2022-08-02 20:25:06.874187+00	2022-08-02 20:25:06.874228+00	1	\N	{"active": true, "account_type": "LIABILITY", "enable_payments_to_account": false}	f
58	ACCOUNT	Account	Retained Earnings	960	2022-08-02 20:25:06.874322+00	2022-08-02 20:25:06.874362+00	1	\N	{"active": true, "account_type": "EQUITY", "enable_payments_to_account": false}	f
59	ACCOUNT	Account	Owner A Share Capital	970	2022-08-02 20:25:06.874566+00	2022-08-02 20:25:06.874609+00	1	\N	{"active": true, "account_type": "EQUITY", "enable_payments_to_account": true}	f
60	CONTACT	Contact	Harshitha P	fbf56259-0a62-4582-8bc5-024f57f659f5	2022-08-02 20:25:07.631648+00	2022-08-02 20:25:07.631688+00	1	\N	{"email": "harshitha.p@fyle.in"}	f
61	CONTACT	Contact	Coco Cafe	9a777d01-2bfb-4623-807d-129d3f077e21	2022-08-02 20:25:07.631754+00	2022-08-02 20:25:07.631782+00	1	\N	{"email": null}	f
62	CONTACT	Contact	Ridgeway Bank	43d1337e-4360-4589-9a76-1d0538c4ce6f	2022-08-02 20:25:07.631845+00	2022-08-02 20:25:07.631872+00	1	\N	{"email": null}	f
63	CONTACT	Contact	Office Supplies Company	cb906ad4-b1d7-44bf-b25a-4862c7059a43	2022-08-02 20:25:07.631933+00	2022-08-02 20:25:07.631961+00	1	\N	{"email": null}	f
64	CONTACT	Contact	7-Eleven	f41cbe7c-de57-4927-b8a0-49fb0151be77	2022-08-02 20:25:07.632022+00	2022-08-02 20:25:07.63205+00	1	\N	{"email": ""}	f
65	CONTACT	Contact	Woolworths Market	be4cfc19-c55a-4f19-817b-4eee4ccf2c01	2022-08-02 20:25:07.632111+00	2022-08-02 20:25:07.632138+00	1	\N	{"email": null}	f
66	CONTACT	Contact	Gable Print	406e9eba-9939-48de-a300-57853bb1a6a4	2022-08-02 20:25:07.632199+00	2022-08-02 20:25:07.632239+00	1	\N	{"email": null}	f
67	CONTACT	Contact	Orlena Greenville	940f1da6-6d14-46e5-a692-77de93732f96	2022-08-02 20:25:07.632451+00	2022-08-02 20:25:07.63248+00	1	\N	{"email": ""}	f
68	CONTACT	Contact	Dimples Warehouse	733b5108-96cb-4d43-bc5b-7f37a2f77c26	2022-08-02 20:25:07.632542+00	2022-08-02 20:25:07.632569+00	1	\N	{"email": null}	f
69	CONTACT	Contact	Fulton Airport Parking	d8ce2ea5-d312-4c34-9656-8554b8071a81	2022-08-02 20:25:07.63263+00	2022-08-02 20:25:07.632658+00	1	\N	{"email": null}	f
70	CONTACT	Contact	Espresso 31	f5cb9bf0-7aa2-473e-8115-87863dee95f3	2022-08-02 20:25:07.632719+00	2022-08-02 20:25:07.632747+00	1	\N	{"email": ""}	f
71	CONTACT	Contact	24 Locks	2e68080d-b3bd-4051-b33c-9f031550b958	2022-08-02 20:25:07.632808+00	2022-08-02 20:25:07.632835+00	1	\N	{"email": null}	f
72	CONTACT	Contact	Epicenter Cafe	f6ecf9a4-ee5a-4e9c-b52b-bec4737e8623	2022-08-02 20:25:07.632896+00	2022-08-02 20:25:07.632923+00	1	\N	{"email": ""}	f
73	CONTACT	Contact	Melrose Parking	b6c2d5e5-94f2-4df5-a7c2-f1de0bff034f	2022-08-02 20:25:07.632984+00	2022-08-02 20:25:07.633012+00	1	\N	{"email": null}	f
74	CONTACT	Contact	Berry Brew	16cf5671-54a8-4d4e-9a55-f2be8ec3dcf4	2022-08-02 20:25:07.633072+00	2022-08-02 20:25:07.6331+00	1	\N	{"email": null}	f
75	CONTACT	Contact	Brunswick Petals	162c177a-3391-4742-890f-f3ebfe0df1f3	2022-08-02 20:25:07.633161+00	2022-08-02 20:25:07.633189+00	1	\N	{"email": null}	f
76	CONTACT	Contact	PC Complete	aacecb74-ef1e-44e0-ba52-0bc521639697	2022-08-02 20:25:07.633379+00	2022-08-02 20:25:07.633407+00	1	\N	{"email": null}	f
77	CONTACT	Contact	Bayside Wholesale	c01292e3-1a1a-4a70-b120-1218f8f71096	2022-08-02 20:25:07.633469+00	2022-08-02 20:25:07.633496+00	1	\N	{"email": ""}	f
78	CONTACT	Contact	SMART Agency	3f58af86-b4d9-4ac9-950c-2e4cdd94d5be	2022-08-02 20:25:07.633557+00	2022-08-02 20:25:07.633585+00	1	\N	{"email": null}	f
79	CONTACT	Contact	Central Copiers	cade9142-f5fe-4970-b39e-2f388b8740c0	2022-08-02 20:25:07.633646+00	2022-08-02 20:25:07.633673+00	1	\N	{"email": null}	f
80	CONTACT	Contact	Xero	3b30a108-9156-4a42-a893-3bbbe7af1ef8	2022-08-02 20:25:07.633734+00	2022-08-02 20:25:07.633761+00	1	\N	{"email": null}	f
81	CONTACT	Contact	Truxton Property Management	f4af0a9b-e710-4611-8618-4360944ce1f3	2022-08-02 20:25:07.633822+00	2022-08-02 20:25:07.63385+00	1	\N	{"email": null}	f
82	CONTACT	Contact	Swanston Security	78b7299c-4f1f-46d2-acc3-44a46bd361b1	2022-08-02 20:25:07.63391+00	2022-08-02 20:25:07.633938+00	1	\N	{"email": null}	f
83	CONTACT	Contact	MCO Cleaning Services	537d4d64-2fc1-4521-89c3-489d20fae20d	2022-08-02 20:25:07.633999+00	2022-08-02 20:25:07.634027+00	1	\N	{"email": null}	f
84	CONTACT	Contact	Carlton Functions	4ad99fdf-a0cc-4aaa-a1a6-6a1549b9df40	2022-08-02 20:25:07.634088+00	2022-08-02 20:25:07.634115+00	1	\N	{"email": null}	f
85	CONTACT	Contact	Net Connect	b553bc60-5fb9-4d5e-b604-71aaf657cd3d	2022-08-02 20:25:07.634177+00	2022-08-02 20:25:07.634204+00	1	\N	{"email": ""}	f
86	CONTACT	Contact	ABC Furniture	39efa556-8dda-4c81-83d3-a631e59eb6d3	2022-08-02 20:25:07.634399+00	2022-08-02 20:25:07.634428+00	1	\N	{"email": "info@abfl.com"}	f
87	CONTACT	Contact	Capital Cab Co	f93cd75c-9412-4a8c-91a3-b41fe751aa01	2022-08-02 20:25:07.634488+00	2022-08-02 20:25:07.634516+00	1	\N	{"email": ""}	f
88	CONTACT	Contact	Hoyt Productions	1d80716b-427e-4cad-80c6-c4b3a18eb23d	2022-08-02 20:25:07.634577+00	2022-08-02 20:25:07.634604+00	1	\N	{"email": null}	f
89	CONTACT	Contact	PowerDirect	8f48b066-e047-459d-80dd-d495b36608d0	2022-08-02 20:25:07.634665+00	2022-08-02 20:25:07.634692+00	1	\N	{"email": ""}	f
90	CONTACT	Contact	Gateway Motors	ddd4ba65-9b7e-4adf-be7a-e91efbb6c082	2022-08-02 20:25:07.634753+00	2022-08-02 20:25:07.63478+00	1	\N	{"email": null}	f
91	CONTACT	Contact	Hamilton Smith Ltd	fd89489e-699c-4d77-a881-10c127bfbeb3	2022-08-02 20:25:07.634841+00	2022-08-02 20:25:07.634868+00	1	\N	{"email": "info@hsg.co"}	f
92	CONTACT	Contact	Ridgeway University	65a44264-dea0-481a-b49d-18a334a72334	2022-08-02 20:25:07.634929+00	2022-08-02 20:25:07.634957+00	1	\N	{"email": ""}	f
93	CONTACT	Contact	Boom FM	37918a06-92f6-4edb-bfe0-1fc041c90f8b	2022-08-02 20:25:07.635017+00	2022-08-02 20:25:07.635044+00	1	\N	{"email": null}	f
94	CONTACT	Contact	Bayside Club	b68deed5-49c8-416a-9f35-2ab14bb1fb6b	2022-08-02 20:25:07.635105+00	2022-08-02 20:25:07.635132+00	1	\N	{"email": "secretarybob@bsclub.co"}	f
95	CONTACT	Contact	Marine Systems	5b96e86b-418e-48e8-8949-308c14aec278	2022-08-02 20:25:07.635193+00	2022-08-02 20:25:07.635232+00	1	\N	{"email": ""}	f
96	CONTACT	Contact	City Agency	fa52f698-1244-47cd-8fb9-5f32b6490a55	2022-08-02 20:25:07.635407+00	2022-08-02 20:25:07.635435+00	1	\N	{"email": null}	f
97	CONTACT	Contact	DIISR - Small Business Services	a3cf95c5-9d26-42e1-80c0-69e5f24886d3	2022-08-02 20:25:07.635507+00	2022-08-02 20:25:07.635536+00	1	\N	{"email": ""}	f
98	CONTACT	Contact	Young Bros Transport	021b18f8-b62f-4d8a-889e-71fd5427892a	2022-08-02 20:25:07.635601+00	2022-08-02 20:25:07.63563+00	1	\N	{"email": "rog@ybt.co"}	f
99	CONTACT	Contact	Port & Philip Freight	378f211a-64c2-4327-bab3-9b057f4f51d9	2022-08-02 20:25:07.635695+00	2022-08-02 20:25:07.635724+00	1	\N	{"email": ""}	f
100	CONTACT	Contact	Bank West	47f61ab1-5245-40a2-a3a5-bc224c850c8d	2022-08-02 20:25:07.635789+00	2022-08-02 20:25:07.63592+00	1	\N	{"email": ""}	f
101	CONTACT	Contact	Rex Media Group	3cbd5263-0965-4c4e-932c-bf50e3297610	2022-08-02 20:25:07.636488+00	2022-08-02 20:25:07.636554+00	1	\N	{"email": "info@rexmedia.co"}	f
102	CONTACT	Contact	Basket Case	85d15bf3-207f-4278-8449-e12dade98c66	2022-08-02 20:25:07.636769+00	2022-08-02 20:25:07.637245+00	1	\N	{"email": ""}	f
103	CONTACT	Contact	Petrie McLoud Watson & Associates	2aaaeb6b-b519-4698-9b0a-f74ba1d39be6	2022-08-02 20:25:07.637625+00	2022-08-02 20:25:07.637678+00	1	\N	{"email": null}	f
104	CONTACT	Contact	City Limousines	7c913d33-39d5-4a1c-b8b1-e23f5fc999e0	2022-08-02 20:25:07.637762+00	2022-08-02 20:25:07.638441+00	1	\N	{"email": ""}	f
105	CONTACT	Contact	Joanna	9eecdd86-78bb-47c9-95df-986369748151	2022-08-02 20:25:07.638561+00	2022-08-02 20:25:07.638592+00	1	\N	{"email": "ashwin.t@fyle.in"}	f
106	CONTACT	Contact	Sravan K	229b7701-21a2-4539-b39e-5c34f56e1711	2022-08-02 20:25:07.638661+00	2022-08-02 20:25:07.638691+00	1	\N	{"email": "sravan.kumar@fyle.in"}	f
108	CUSTOMER	Customer	Hamilton Smith Ltd	fd89489e-699c-4d77-a881-10c127bfbeb3	2022-08-02 20:25:09.006121+00	2022-08-02 20:25:09.006197+00	1	\N	{"email": "info@hsg.co"}	f
109	CUSTOMER	Customer	Ridgeway University	65a44264-dea0-481a-b49d-18a334a72334	2022-08-02 20:25:09.008587+00	2022-08-02 20:25:09.008686+00	1	\N	{"email": ""}	f
110	CUSTOMER	Customer	Boom FM	37918a06-92f6-4edb-bfe0-1fc041c90f8b	2022-08-02 20:25:09.008782+00	2022-08-02 20:25:09.008819+00	1	\N	{"email": null}	f
111	CUSTOMER	Customer	Bayside Club	b68deed5-49c8-416a-9f35-2ab14bb1fb6b	2022-08-02 20:25:09.008894+00	2022-08-02 20:25:09.008924+00	1	\N	{"email": "secretarybob@bsclub.co"}	f
112	CUSTOMER	Customer	Marine Systems	5b96e86b-418e-48e8-8949-308c14aec278	2022-08-02 20:25:09.008994+00	2022-08-02 20:25:09.009596+00	1	\N	{"email": ""}	f
113	CUSTOMER	Customer	City Agency	fa52f698-1244-47cd-8fb9-5f32b6490a55	2022-08-02 20:25:09.009978+00	2022-08-02 20:25:09.010133+00	1	\N	{"email": null}	f
114	CUSTOMER	Customer	DIISR - Small Business Services	a3cf95c5-9d26-42e1-80c0-69e5f24886d3	2022-08-02 20:25:09.016791+00	2022-08-02 20:25:09.01684+00	1	\N	{"email": ""}	f
115	CUSTOMER	Customer	Young Bros Transport	021b18f8-b62f-4d8a-889e-71fd5427892a	2022-08-02 20:25:09.016952+00	2022-08-02 20:25:09.017387+00	1	\N	{"email": "rog@ybt.co"}	f
116	CUSTOMER	Customer	Port & Philip Freight	378f211a-64c2-4327-bab3-9b057f4f51d9	2022-08-02 20:25:09.01756+00	2022-08-02 20:25:09.017586+00	1	\N	{"email": ""}	f
117	CUSTOMER	Customer	Bank West	47f61ab1-5245-40a2-a3a5-bc224c850c8d	2022-08-02 20:25:09.017657+00	2022-08-02 20:25:09.017668+00	1	\N	{"email": ""}	f
118	CUSTOMER	Customer	Rex Media Group	3cbd5263-0965-4c4e-932c-bf50e3297610	2022-08-02 20:25:09.018006+00	2022-08-02 20:25:09.018037+00	1	\N	{"email": "info@rexmedia.co"}	f
119	CUSTOMER	Customer	Basket Case	85d15bf3-207f-4278-8449-e12dade98c66	2022-08-02 20:25:09.018113+00	2022-08-02 20:25:09.018141+00	1	\N	{"email": ""}	f
120	CUSTOMER	Customer	Petrie McLoud Watson & Associates	2aaaeb6b-b519-4698-9b0a-f74ba1d39be6	2022-08-02 20:25:09.018216+00	2022-08-02 20:25:09.018458+00	1	\N	{"email": null}	f
121	CUSTOMER	Customer	City Limousines	7c913d33-39d5-4a1c-b8b1-e23f5fc999e0	2022-08-02 20:25:09.018579+00	2022-08-02 20:25:09.018635+00	1	\N	{"email": ""}	f
122	ITEM	Item	BOOK	8bbaf73c-5a32-4458-addf-bd30a36c8551	2022-08-02 20:25:10.084723+00	2022-08-02 20:25:10.084913+00	1	\N	\N	f
123	ITEM	Item	DevD	6cba12ac-e300-4745-838a-f57dfdb88e11	2022-08-02 20:25:10.085169+00	2022-08-02 20:25:10.085391+00	1	\N	\N	f
124	ITEM	Item	DevH	b36131d5-f37e-4cb1-bb9c-320446c7b004	2022-08-02 20:25:10.085522+00	2022-08-02 20:25:10.085571+00	1	\N	\N	f
125	ITEM	Item	GB1-White	3644c19f-7c46-4e18-93fa-5550c307bcdd	2022-08-02 20:25:10.085664+00	2022-08-02 20:25:10.085696+00	1	\N	\N	f
126	ITEM	Item	GB3-White	53c1d46d-cf8e-45d2-8dc1-9bd73b0ca9e2	2022-08-02 20:25:10.085758+00	2022-08-02 20:25:10.085788+00	1	\N	\N	f
127	ITEM	Item	GB6-White	9ce48e6a-118b-40a5-ae43-2e7dea8b18ad	2022-08-02 20:25:10.085861+00	2022-08-02 20:25:10.085892+00	1	\N	\N	f
128	ITEM	Item	GB9-White	baaba2cb-9abf-4bd4-af24-9429a7e79cec	2022-08-02 20:25:10.085952+00	2022-08-02 20:25:10.085983+00	1	\N	\N	f
129	ITEM	Item	PMBr	ec4362af-a038-4984-ab93-1bba3b6bd402	2022-08-02 20:25:10.086039+00	2022-08-02 20:25:10.086069+00	1	\N	\N	f
130	ITEM	Item	PMD	ffb8b59d-17d8-4245-af16-cdf7a689dcb9	2022-08-02 20:25:10.086126+00	2022-08-02 20:25:10.086156+00	1	\N	\N	f
131	ITEM	Item	PMDD	c8151f6e-09bd-43a4-8726-d9c9122d8200	2022-08-02 20:25:10.086212+00	2022-08-02 20:25:10.086255+00	1	\N	\N	f
132	ITEM	Item	PMWe	3add2df0-f436-431e-a59b-0e76fb4d6720	2022-08-02 20:25:10.086577+00	2022-08-02 20:25:10.086711+00	1	\N	\N	f
133	ITEM	Item	Support-M	e82eaa5c-3c5f-47ed-b2a9-7de266ab1eaf	2022-08-02 20:25:10.086816+00	2022-08-02 20:25:10.086859+00	1	\N	\N	f
134	ITEM	Item	Train-MS	e5cc8904-5865-4846-ad0c-5d9b695b8af9	2022-08-02 20:25:10.086947+00	2022-08-02 20:25:10.086988+00	1	\N	\N	f
135	ITEM	Item	TSL - Black	dc63985f-7e32-4669-b60b-8b550417ddbb	2022-08-02 20:25:10.087074+00	2022-08-02 20:25:10.087116+00	1	\N	\N	f
136	ITEM	Item	TSM - Black	56268ecd-d722-4f39-ac6b-1f34b639393a	2022-08-02 20:25:10.087354+00	2022-08-02 20:25:10.087393+00	1	\N	\N	f
137	ITEM	Item	TSS - Black	d3687dce-a3c2-4d07-9364-0c540f73c4f8	2022-08-02 20:25:10.087455+00	2022-08-02 20:25:10.087485+00	1	\N	\N	f
138	REGION	Region	Eastside	7b354c1c-cf59-42fc-9449-a65c51988335	2022-08-02 20:25:10.478532+00	2022-08-02 20:25:10.478581+00	1	\N	\N	f
139	REGION	Region	North	5e2974a2-097d-4f3b-bfd5-605d78c4a282	2022-08-02 20:25:10.478655+00	2022-08-02 20:25:10.478687+00	1	\N	\N	f
140	REGION	Region	South	e83ea9f2-de2c-44d8-b4f8-a5065bed339e	2022-08-02 20:25:10.478751+00	2022-08-02 20:25:10.478773+00	1	\N	\N	f
141	REGION	Region	West Coast	fc96efd9-b832-4b31-a93e-61f56158adad	2022-08-02 20:25:10.478833+00	2022-08-02 20:25:10.478862+00	1	\N	\N	f
142	TAX_CODE	Tax Code	Exempt Sales @0.0%	CAN030	2022-08-02 20:25:10.961315+00	2022-08-02 20:25:10.961376+00	1	\N	{"tax_rate": 0.0, "tax_refs": [{"Name": "No Tax", "Rate": 0.0, "IsCompound": false, "IsNonRecoverable": false}]}	f
143	TAX_CODE	Tax Code	MB - GST/RST on Purchases @12.0%	CAN029	2022-08-02 20:25:10.961472+00	2022-08-02 20:25:10.961502+00	1	\N	{"tax_rate": 12.0, "tax_refs": [{"Name": "RST", "Rate": 7.0, "IsCompound": false, "IsNonRecoverable": false}, {"Name": "GST", "Rate": 5.0, "IsCompound": false, "IsNonRecoverable": false}]}	f
144	TAX_CODE	Tax Code	MB - GST/RST on Sales @12.0%	CAN028	2022-08-02 20:25:10.961576+00	2022-08-02 20:25:10.961606+00	1	\N	{"tax_rate": 12.0, "tax_refs": [{"Name": "RST", "Rate": 7.0, "IsCompound": false, "IsNonRecoverable": false}, {"Name": "GST", "Rate": 5.0, "IsCompound": false, "IsNonRecoverable": false}]}	f
145	TAX_CODE	Tax Code	Sales Tax on Imports @0.0%	GSTONIMPORTS	2022-08-02 20:25:10.961764+00	2022-08-02 20:25:10.961798+00	1	\N	{"tax_rate": 0.0, "tax_refs": [{"Name": "TAX", "Rate": 0.0, "IsCompound": false, "IsNonRecoverable": false}]}	f
146	TAX_CODE	Tax Code	Tax Exempt @0.0%	NONE	2022-08-02 20:25:10.961914+00	2022-08-02 20:25:10.961973+00	1	\N	{"tax_rate": 0.0, "tax_refs": [{"Name": "No Tax", "Rate": 0.0, "IsCompound": false, "IsNonRecoverable": false}]}	f
147	TAX_CODE	Tax Code	Tax on Consulting @8.25%	OUTPUT	2022-08-02 20:25:10.962769+00	2022-08-02 20:25:10.962801+00	1	\N	{"tax_rate": 8.25, "tax_refs": [{"Name": "City Tax", "Rate": 4.0, "IsCompound": false, "IsNonRecoverable": false}, {"Name": "State Tax", "Rate": 4.25, "IsCompound": false, "IsNonRecoverable": false}]}	f
148	TAX_CODE	Tax Code	Tax on Goods @8.75%	TAX001	2022-08-02 20:25:10.962877+00	2022-08-02 20:25:10.962905+00	1	\N	{"tax_rate": 8.75, "tax_refs": [{"Name": "State Tax", "Rate": 4.5, "IsCompound": false, "IsNonRecoverable": false}, {"Name": "City Tax", "Rate": 4.25, "IsCompound": false, "IsNonRecoverable": false}]}	f
149	TAX_CODE	Tax Code	Tax on Purchases @8.25%	INPUT	2022-08-02 20:25:10.962973+00	2022-08-02 20:25:10.963001+00	1	\N	{"tax_rate": 8.25, "tax_refs": [{"Name": "State Tax", "Rate": 4.25, "IsCompound": false, "IsNonRecoverable": false}, {"Name": "City Tax", "Rate": 4.0, "IsCompound": false, "IsNonRecoverable": false}]}	f
107	CONTACT	Contact	Credit Card Misc	3aaf24ba-6d35-455f-b92a-9e0dc20d3d9a	2022-08-02 20:25:07.638758+00	2022-08-02 20:28:19.432122+00	1	\N	{"email": ""}	f
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	permission
3	auth	group
4	contenttypes	contenttype
5	sessions	session
6	fyle_rest_auth	authtoken
7	fyle_accounting_mappings	destinationattribute
8	fyle_accounting_mappings	expenseattribute
9	fyle_accounting_mappings	mappingsetting
10	fyle_accounting_mappings	mapping
11	fyle_accounting_mappings	employeemapping
12	fyle_accounting_mappings	categorymapping
13	users	user
14	workspaces	workspace
15	workspaces	xerocredentials
16	workspaces	workspacegeneralsettings
17	workspaces	fylecredential
18	workspaces	workspaceschedule
19	fyle	expense
20	fyle	expensegroupsettings
21	fyle	expensegroup
22	fyle	reimbursement
23	tasks	tasklog
24	mappings	tenantmapping
25	mappings	generalmapping
26	xero	bill
27	xero	billlineitem
28	xero	banktransaction
29	xero	banktransactionlineitem
30	xero	payment
31	django_q	schedule
32	django_q	task
33	django_q	failure
34	django_q	success
35	django_q	ormq
36	tasks	error
37	workspaces	lastexportdetail
38	fyle_accounting_mappings	expensefield
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	users	0001_initial	2022-08-02 20:14:41.710095+00
2	contenttypes	0001_initial	2022-08-02 20:14:41.752294+00
3	admin	0001_initial	2022-08-02 20:14:41.780828+00
4	admin	0002_logentry_remove_auto_add	2022-08-02 20:14:41.830254+00
5	admin	0003_logentry_add_action_flag_choices	2022-08-02 20:14:41.851492+00
6	contenttypes	0002_remove_content_type_name	2022-08-02 20:14:41.920355+00
7	auth	0001_initial	2022-08-02 20:14:41.989694+00
8	auth	0002_alter_permission_name_max_length	2022-08-02 20:14:42.060237+00
9	auth	0003_alter_user_email_max_length	2022-08-02 20:14:42.073708+00
10	auth	0004_alter_user_username_opts	2022-08-02 20:14:42.093699+00
11	auth	0005_alter_user_last_login_null	2022-08-02 20:14:42.119327+00
12	auth	0006_require_contenttypes_0002	2022-08-02 20:14:42.130588+00
13	auth	0007_alter_validators_add_error_messages	2022-08-02 20:14:42.145566+00
14	auth	0008_alter_user_username_max_length	2022-08-02 20:14:42.158769+00
15	auth	0009_alter_user_last_name_max_length	2022-08-02 20:14:42.174898+00
16	auth	0010_alter_group_name_max_length	2022-08-02 20:14:42.191516+00
17	auth	0011_update_proxy_permissions	2022-08-02 20:14:42.216437+00
18	auth	0012_alter_user_first_name_max_length	2022-08-02 20:14:42.234784+00
19	django_q	0001_initial	2022-08-02 20:14:42.344506+00
20	django_q	0002_auto_20150630_1624	2022-08-02 20:14:42.36702+00
21	django_q	0003_auto_20150708_1326	2022-08-02 20:14:42.395592+00
22	django_q	0004_auto_20150710_1043	2022-08-02 20:14:42.417438+00
23	django_q	0005_auto_20150718_1506	2022-08-02 20:14:42.432003+00
24	django_q	0006_auto_20150805_1817	2022-08-02 20:14:42.474077+00
25	django_q	0007_ormq	2022-08-02 20:14:42.515018+00
26	django_q	0008_auto_20160224_1026	2022-08-02 20:14:42.539095+00
27	django_q	0009_auto_20171009_0915	2022-08-02 20:14:42.587641+00
28	django_q	0010_auto_20200610_0856	2022-08-02 20:14:42.681069+00
29	django_q	0011_auto_20200628_1055	2022-08-02 20:14:42.702734+00
30	django_q	0012_auto_20200702_1608	2022-08-02 20:14:42.714272+00
31	django_q	0013_task_attempt_count	2022-08-02 20:14:42.748869+00
32	workspaces	0001_initial	2022-08-02 20:14:42.930621+00
33	workspaces	0002_auto_20201101_0710	2022-08-02 20:14:42.998648+00
34	workspaces	0003_workspaceschedule	2022-08-02 20:14:43.048293+00
35	workspaces	0004_auto_20201228_0813	2022-08-02 20:14:43.084219+00
36	workspaces	0005_auto_20210201_1145	2022-08-02 20:14:43.126731+00
37	fyle	0001_initial	2022-08-02 20:14:43.340828+00
38	fyle	0002_auto_20201221_0814	2022-08-02 20:14:43.404955+00
39	fyle	0003_auto_20210201_1145	2022-08-02 20:14:43.467379+00
40	fyle	0004_expense_org_id	2022-08-02 20:14:43.508641+00
41	fyle	0005_remove_expense_exported	2022-08-02 20:14:43.543005+00
42	fyle	0006_expense_file_ids	2022-08-02 20:14:43.587056+00
43	fyle	0007_expense_corporate_card_id	2022-08-02 20:14:43.621859+00
44	fyle	0008_auto_20211206_0733	2022-08-02 20:14:43.674176+00
45	fyle	0009_auto_20211220_0611	2022-08-02 20:14:43.711313+00
46	fyle	0010_auto_20220329_0837	2022-08-02 20:14:43.741621+00
47	fyle	0011_expense_billable	2022-08-02 20:14:43.759709+00
48	fyle_accounting_mappings	0001_initial	2022-08-02 20:14:44.026031+00
49	fyle_accounting_mappings	0002_auto_20201117_0655	2022-08-02 20:14:44.176151+00
50	fyle_accounting_mappings	0003_auto_20201221_1244	2022-08-02 20:14:44.32588+00
51	fyle_accounting_mappings	0004_auto_20210127_1241	2022-08-02 20:14:44.38288+00
52	fyle_accounting_mappings	0005_expenseattribute_auto_mapped	2022-08-02 20:14:44.415652+00
53	fyle_accounting_mappings	0006_auto_20210305_0827	2022-08-02 20:14:44.502671+00
54	fyle_accounting_mappings	0007_auto_20210409_1931	2022-08-02 20:14:44.600383+00
55	fyle_accounting_mappings	0008_auto_20210604_0713	2022-08-02 20:14:44.702773+00
56	fyle_accounting_mappings	0009_auto_20210618_1004	2022-08-02 20:14:44.736208+00
57	fyle_accounting_mappings	0010_remove_mappingsetting_expense_field_id	2022-08-02 20:14:44.763051+00
58	fyle_accounting_mappings	0011_categorymapping_employeemapping	2022-08-02 20:14:45.070008+00
59	fyle_accounting_mappings	0012_auto_20211206_0600	2022-08-02 20:14:45.271079+00
60	fyle_rest_auth	0001_initial	2022-08-02 20:14:45.32894+00
61	fyle_rest_auth	0002_auto_20200101_1205	2022-08-02 20:14:45.459258+00
62	fyle_rest_auth	0003_auto_20200107_0921	2022-08-02 20:14:45.567351+00
63	fyle_rest_auth	0004_auto_20200107_1345	2022-08-02 20:14:45.622613+00
64	fyle_rest_auth	0005_remove_authtoken_access_token	2022-08-02 20:14:45.641525+00
65	fyle_rest_auth	0006_auto_20201221_0849	2022-08-02 20:14:45.658087+00
66	mappings	0001_initial	2022-08-02 20:14:45.722661+00
67	mappings	0002_generalmapping	2022-08-02 20:14:45.865566+00
68	mappings	0003_auto_20210201_1145	2022-08-02 20:14:45.967911+00
69	mappings	0004_tenantmapping_connection_id	2022-08-02 20:14:46.091918+00
70	mappings	0005_auto_20220329_0837	2022-08-02 20:14:46.193277+00
71	sessions	0001_initial	2022-08-02 20:14:46.216851+00
72	xero	0001_initial	2022-08-02 20:14:46.3524+00
73	xero	0002_banktransaction_banktransactionlineitem	2022-08-02 20:14:46.561847+00
74	xero	0003_auto_20210201_1145	2022-08-02 20:14:46.693228+00
75	tasks	0001_initial	2022-08-02 20:14:46.830112+00
76	tasks	0002_auto_20201102_1720	2022-08-02 20:14:46.957691+00
77	tasks	0003_tasklog_xero_errors	2022-08-02 20:14:47.178952+00
78	tasks	0004_auto_20201221_0814	2022-08-02 20:14:47.220797+00
79	tasks	0005_tasklog_payment	2022-08-02 20:14:47.277667+00
80	tasks	0006_auto_20211123_0843	2022-08-02 20:14:47.359552+00
81	tasks	0007_auto_20211206_0733	2022-08-02 20:14:47.499839+00
82	users	0002_auto_20201228_0813	2022-08-02 20:14:47.515924+00
83	workspaces	0006_workspacegeneralsettings_import_categories	2022-08-02 20:14:47.550359+00
84	workspaces	0007_workspacegeneralsettings_auto_map_employees	2022-08-02 20:14:47.587725+00
85	workspaces	0008_workspacegeneralsettings_auto_create_destination_entity	2022-08-02 20:14:47.630132+00
86	workspaces	0009_workspacegeneralsettings_map_merchant_to_contact	2022-08-02 20:14:47.673415+00
87	workspaces	0010_auto_20210414_1118	2022-08-02 20:14:47.835754+00
88	workspaces	0011_auto_20211005_0726	2022-08-02 20:14:47.873298+00
89	workspaces	0012_workspacegeneralsettings_map_fyle_cards_xero_bank_account	2022-08-02 20:14:47.911771+00
90	workspaces	0013_workspace_xero_short_code	2022-08-02 20:14:47.988911+00
91	workspaces	0014_auto_20211217_0947	2022-08-02 20:14:48.09385+00
92	workspaces	0015_auto_20220329_0837	2022-08-02 20:14:48.256014+00
93	workspaces	0016_auto_20220329_1251	2022-08-02 20:14:48.370508+00
94	workspaces	0017_remove_workspace_cluster_domain	2022-08-02 20:14:48.478555+00
95	workspaces	0018_xerocredentials_country	2022-08-02 20:14:48.660221+00
96	workspaces	0019_workspacegeneralsettings_charts_of_accounts	2022-08-02 20:14:48.701989+00
97	workspaces	0020_workspace_xero_accounts_last_synced_at	2022-08-02 20:14:48.744921+00
98	workspaces	0021_workspacegeneralsettings_import_customers	2022-08-02 20:14:48.789959+00
99	workspaces	0022_workspacegeneralsettings_change_accounting_period	2022-08-02 20:14:48.836936+00
100	xero	0004_payment_amount	2022-08-02 20:14:48.89288+00
101	xero	0005_auto_20210308_0707	2022-08-02 20:14:48.919163+00
102	xero	0006_auto_20211206_0733	2022-08-02 20:14:48.962265+00
103	xero	0007_auto_20220329_0837	2022-08-02 20:14:49.014705+00
104	xero	0008_auto_20220331_0504	2022-08-02 20:14:49.120136+00
105	xero	0009_auto_20220614_1320	2022-08-02 20:14:49.359825+00
106	workspaces	0023_workspacegeneralsettings_auto_create_merchant_destination_entity	2022-08-29 11:29:34.137291+00
107	fyle_accounting_mappings	0013_auto_20220323_1133	2022-09-08 08:50:25.699837+00
108	fyle_accounting_mappings	0014_mappingsetting_source_placeholder	2022-09-08 08:50:25.741+00
109	fyle_accounting_mappings	0015_auto_20220412_0614	2022-09-08 08:50:25.770543+00
110	fyle_accounting_mappings	0016_auto_20220413_1624	2022-09-08 08:50:25.793733+00
111	fyle_accounting_mappings	0017_auto_20220419_0649	2022-09-08 08:50:25.811911+00
112	fyle_accounting_mappings	0018_auto_20220419_0709	2022-09-08 08:50:25.834243+00
113	workspaces	0024_auto_20220909_1206	2022-09-23 08:56:07.83287+00
114	workspaces	0025_auto_20220920_1111	2022-09-23 08:56:07.842453+00
115	fyle	0012_auto_20220923_0613	2022-09-23 08:56:07.90403+00
116	mappings	0006_auto_20220909_1206	2022-09-23 08:56:07.919911+00
117	fyle	0013_expensegroupsettings_import_card_credits	2022-10-17 08:00:24.739834+00
118	workspaces	0026_auto_20221004_1922	2022-10-17 08:00:25.224871+00
119	tasks	0008_error	2022-10-17 08:00:25.413763+00
120	fyle	0014_expensegroup_response_logs	2022-10-17 09:59:59.938388+00
121	workspaces	0027_auto_20221014_0741	2022-10-17 11:17:16.229906+00
122	workspaces	0028_lastexportdetail	2022-10-25 10:08:34.248947+00
123	workspaces	0029_workspace_ccc_last_synced_at	2022-10-28 06:48:09.644137+00
124	mappings	0007_auto_20221102_0630	2022-11-03 06:28:39.216754+00
125	workspaces	0030_auto_20221102_1924	2022-11-03 06:28:39.245951+00
126	fyle	0015_auto_20221104_1049	2022-11-04 11:04:25.882513+00
127	workspaces	0031_auto_20221116_0649	2023-01-11 06:28:22.8634+00
128	fyle	0016_auto_20230117_0616	2023-01-18 09:08:24.092416+00
129	workspaces	0032_workspacegeneralsettings_is_simplify_report_closure_enabled	2023-03-14 08:52:43.983448+00
130	workspaces	0033_auto_20230315_1034	2023-03-16 10:30:47.143545+00
131	workspaces	0034_auto_20230320_0805	2023-03-20 08:06:40.679962+00
132	workspaces	0033_auto_20230321_0736	2023-03-21 07:52:39.767433+00
133	workspaces	0035_merge_20230321_0751	2023-03-21 07:52:39.77092+00
134	workspaces	0036_auto_20230323_0846	2023-03-23 08:48:08.362718+00
135	fyle_accounting_mappings	0019_auto_20230105_1104	2023-04-10 08:19:53.587731+00
136	fyle_accounting_mappings	0020_auto_20230302_0519	2023-04-10 08:19:53.615283+00
137	fyle_accounting_mappings	0021_auto_20230323_0557	2023-04-10 08:19:53.627683+00
138	fyle	0017_expense_posted_at	2023-06-22 06:52:23.798799+00
139	fyle_accounting_mappings	0022_auto_20230411_1118	2023-06-22 06:52:23.813446+00
140	workspaces	0037_workspacegeneralsettings_import_suppliers_as_merchants	2023-08-29 13:13:53.212703+00
141	django_q	0014_schedule_cluster	2024-02-07 11:26:26.03684+00
142	django_q	0015_alter_schedule_schedule_type	2024-02-07 11:26:26.042653+00
143	django_q	0016_schedule_intended_date_kwarg	2024-02-07 11:26:26.046856+00
144	django_q	0017_task_cluster_alter	2024-02-07 11:26:26.055692+00
\.


--
-- Data for Name: django_q_ormq; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_q_ormq (id, key, payload, lock) FROM stdin;
\.


--
-- Data for Name: django_q_schedule; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_q_schedule (id, func, hook, args, kwargs, schedule_type, repeats, next_run, task, name, minutes, cron, cluster, intended_date_kwarg) FROM stdin;
3	apps.xero.tasks.process_reimbursements	\N	1	\N	I	-1	2022-08-03 08:25:24.720773+00	\N	\N	1440	\N	\N	\N
1	apps.mappings.tasks.auto_create_project_mappings	\N	1	\N	I	-2	2022-08-03 20:25:24.662662+00	e921600a45634f628a9bc2d15688db65	\N	1440	\N	\N	\N
2	apps.xero.tasks.check_xero_object_status	\N	1	\N	I	-2	2022-08-03 20:25:24.701039+00	efc402091b134261bf5fd2e6beebb9e1	\N	1440	\N	\N	\N
4	apps.mappings.tasks.auto_create_category_mappings	\N	1	\N	I	-2	2022-08-03 20:25:24.736446+00	47d62492face4ec7a30d0e7b4e1f65fd	\N	1440	\N	\N	\N
\.


--
-- Data for Name: django_q_task; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_q_task (name, func, hook, args, kwargs, result, started, stopped, success, id, "group", attempt_count, cluster) FROM stdin;
mockingbird-pennsylvania-table-bakerloo	apps.xero.tasks.update_xero_short_code	\N	gASVBQAAAAAAAABLAYWULg==	gAR9lC4=	\N	2022-08-02 20:25:03.713821+00	2022-08-02 20:25:06.307361+00	t	4f7b40e491ac43d09c2e315bb8c51d71	\N	1	\N
bluebird-diet-march-kansas	apps.xero.tasks.create_missing_currency	\N	gASVBQAAAAAAAABLAYWULg==	gAR9lC4=	\N	2022-08-02 20:25:03.709737+00	2022-08-02 20:25:06.693096+00	t	4dc71e8d54be4a938756b3e13164a09a	\N	1	\N
cardinal-comet-steak-august	apps.xero.tasks.check_xero_object_status	\N	gASVBQAAAAAAAABLAYWULg==	gAR9lC4=	\N	2022-08-02 20:25:29.972306+00	2022-08-02 20:25:31.161165+00	t	efc402091b134261bf5fd2e6beebb9e1	2	1	\N
ohio-asparagus-alanine-hydrogen	apps.mappings.tasks.auto_create_project_mappings	\N	gASVBQAAAAAAAABLAYWULg==	gAR9lC4=	\N	2022-08-02 20:25:29.962566+00	2022-08-02 20:25:32.185191+00	t	e921600a45634f628a9bc2d15688db65	1	1	\N
alanine-artist-muppet-friend	apps.mappings.tasks.auto_create_tax_codes_mappings	\N	gASVBQAAAAAAAABLAYWULg==	gAR9lC4=	\N	2022-08-02 20:25:30.006579+00	2022-08-02 20:25:32.740485+00	t	de3bae4949a84aa1ab69cc9b8d3d6f8f	6	1	\N
oregon-pluto-papa-emma	apps.mappings.tasks.async_auto_map_employees	\N	gASVBQAAAAAAAABLAYWULg==	gAR9lC4=	\N	2022-08-02 20:25:29.985349+00	2022-08-02 20:25:32.878313+00	t	98d3a04c90a647c0a63083be4624227e	5	1	\N
coffee-rugby-tennessee-sixteen	apps.mappings.tasks.auto_create_category_mappings	\N	gASVBQAAAAAAAABLAYWULg==	gAR9lC4=	gARdlC4=	2022-08-02 20:25:29.978504+00	2022-08-02 20:25:59.169036+00	t	47d62492face4ec7a30d0e7b4e1f65fd	4	1	\N
bakerloo-table-table-fruit	apps.fyle.tasks.create_expense_groups	\N	gASVCQIAAAAAAABLAV2UKIwIUEVSU09OQUyUjANDQ0OUZYwVZGphbmdvLmRiLm1vZGVscy5iYXNllIwObW9kZWxfdW5waWNrbGWUk5SMBXRhc2tzlIwHVGFza0xvZ5SGlIWUUpR9lCiMBl9zdGF0ZZRoA4wKTW9kZWxTdGF0ZZSTlCmBlH2UKIwMZmllbGRzX2NhY2hllH2UjAJkYpSMB2RlZmF1bHSUjAZhZGRpbmeUiXVijAJpZJRLAYwMd29ya3NwYWNlX2lklEsBjAR0eXBllIwRRkVUQ0hJTkdfRVhQRU5TRVOUjAd0YXNrX2lklE6MEGV4cGVuc2VfZ3JvdXBfaWSUTowKcGF5bWVudF9pZJROjAdiaWxsX2lklE6ME2JhbmtfdHJhbnNhY3Rpb25faWSUTowGc3RhdHVzlIwIQ09NUExFVEWUjAZkZXRhaWyUfZSMB21lc3NhZ2WUjBdDcmVhdGluZyBleHBlbnNlIGdyb3Vwc5RzjAt4ZXJvX2Vycm9yc5ROjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YIAhQaFQ0lxZSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwKdXBkYXRlZF9hdJRoKUMKB+YIAhQaFg8OiJRoLoaUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xNJR1YoeULg==	gAR9lC4=	gASVKQIAAAAAAACMEnBpY2tsZWZpZWxkLmZpZWxkc5SMDl9PYmplY3RXcmFwcGVylJOUKYGUTn2UjARfb2JqlIwVZGphbmdvLmRiLm1vZGVscy5iYXNllIwObW9kZWxfdW5waWNrbGWUk5SMBXRhc2tzlIwHVGFza0xvZ5SGlIWUUpR9lCiMBl9zdGF0ZZRoBowKTW9kZWxTdGF0ZZSTlCmBlH2UKIwMZmllbGRzX2NhY2hllH2UjAJkYpSMB2RlZmF1bHSUjAZhZGRpbmeUiXVijAJpZJRLAYwMd29ya3NwYWNlX2lklEsBjAR0eXBllIwRRkVUQ0hJTkdfRVhQRU5TRVOUjAd0YXNrX2lklE6MEGV4cGVuc2VfZ3JvdXBfaWSUTowKcGF5bWVudF9pZJROjAdiaWxsX2lklE6ME2JhbmtfdHJhbnNhY3Rpb25faWSUTowGc3RhdHVzlIwIQ09NUExFVEWUjAZkZXRhaWyUfZSMB21lc3NhZ2WUjBdDcmVhdGluZyBleHBlbnNlIGdyb3Vwc5RzjAt4ZXJvX2Vycm9yc5ROjApjcmVhdGVkX2F0lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+YIAhQaFQ0lxZSMBHB5dHqUjARfVVRDlJOUKVKUhpRSlIwKdXBkYXRlZF9hdJRoLEMKB+YIAhQaFg8OiJRoMYaUUpSMD19kamFuZ29fdmVyc2lvbpSMBjMuMS4xNJR1YnOGlGIu	2022-08-02 20:26:21.876363+00	2022-08-02 20:26:22.990709+00	t	17c29e5ae1ae4cdb8dcbc6580f8426fc	\N	1	\N
steak-massachusetts-beryllium-fifteen	apps.xero.tasks.create_bill	\N	gASVzgoAAAAAAABLAksCjA9hcHBzLnhlcm8udXRpbHOUjA1YZXJvQ29ubmVjdG9ylJOUKYGUfZQojApjb25uZWN0aW9ulIwPeGVyb3Nkay54ZXJvc2RrlIwHWGVyb1NES5STlCmBlH2UKIwSX1hlcm9TREtfX2Jhc2VfdXJslIwUaHR0cHM6Ly9hcGkueGVyby5jb22UjBNfWGVyb1NES19fY2xpZW50X2lklIwgQkIxMzk0NjdENTQyNEIxNEJFM0RCRjkyODk1RUI2Q0aUjBdfWGVyb1NES19fY2xpZW50X3NlY3JldJSMMDAzTzhiQ0hkQWFfWW56RGhPelVneThNSXo5VGpyRFRQSlVaRzRycVFpYklRWVJncZSMDl9yZWZyZXNoX3Rva2VulIxAZTk1YTI0NjMwMGI4YzQzNzkwNTEzNTU3MDRhYTdkNWRkNGFhMmRlNzBkNGI3N2JlNDM4ODZmNzhiYTdjMGQwOZSMCGludm9pY2VzlIwVeGVyb3Nkay5hcGlzLmludm9pY2VzlIwISW52b2ljZXOUk5QpgZR9lCiMFl9BcGlCYXNlX19hY2Nlc3NfdG9rZW6UWOwEAABleUpoYkdjaU9pSlNVekkxTmlJc0ltdHBaQ0k2SWpGRFFVWTRSVFkyTnpjeVJEWkVRekF5T0VRMk56STJSa1F3TWpZeE5UZ3hOVGN3UlVaRE1Ua2lMQ0owZVhBaU9pSktWMVFpTENKNE5YUWlPaUpJU3kxUFdtNWpkR0pqUVc4eGJrcDJNRU5aVm1kV1kwOWZRbXNpZlEuZXlKdVltWWlPakUyTlRrME56RTVPRGtzSW1WNGNDSTZNVFkxT1RRM016YzRPU3dpYVhOeklqb2lhSFIwY0hNNkx5OXBaR1Z1ZEdsMGVTNTRaWEp2TG1OdmJTSXNJbUYxWkNJNkltaDBkSEJ6T2k4dmFXUmxiblJwZEhrdWVHVnlieTVqYjIwdmNtVnpiM1Z5WTJWeklpd2lZMnhwWlc1MFgybGtJam9pUWtJeE16azBOamRFTlRReU5FSXhORUpGTTBSQ1Jqa3lPRGsxUlVJMlEwWWlMQ0p6ZFdJaU9pSTVPVEV6WmpaaVpqUXlNVEkxTmpreU9USmlNemczWW1RelpEWXpaalJrWXlJc0ltRjFkR2hmZEdsdFpTSTZNVFkxT1RRM01UZzROaXdpZUdWeWIxOTFjMlZ5YVdRaU9pSXhOMlU1Tmpsak1DMHpaVFV5TFRSa1pUa3RZV1ZsTVMweU5XWTVNR0ptTkRjME1XUWlMQ0puYkc5aVlXeGZjMlZ6YzJsdmJsOXBaQ0k2SWpNeU1EZGxObUppTXpRNU16UmpZV1k1TUdKbFlqQmtNREU0T1RoaU9HTmpJaXdpYW5ScElqb2lPVFU1TkRoaFlUTTNNRFkwWTJJM01qa3paVEppT1RNNE4yRXlNakppWTJZaUxDSmhkWFJvWlc1MGFXTmhkR2x2Ymw5bGRtVnVkRjlwWkNJNkltSTRZV1V4WTJRMUxUWTVNall0TkRGaU1TMWhaVFF6TFdGaE1UUXdOemc1TkRBM01pSXNJbk5qYjNCbElqcGJJbUZqWTI5MWJuUnBibWN1YzJWMGRHbHVaM01pTENKaFkyTnZkVzUwYVc1bkxtRjBkR0ZqYUcxbGJuUnpJaXdpWVdOamIzVnVkR2x1Wnk1MGNtRnVjMkZqZEdsdmJuTWlMQ0poWTJOdmRXNTBhVzVuTG1OdmJuUmhZM1J6SWl3aWIyWm1iR2x1WlY5aFkyTmxjM01pWFN3aVlXMXlJanBiSW5OemJ5SmRmUS5aY1FSVmE1cklCcmZvcmxWeUtETHpfcVotTF9TbWVTNmxGMFd5YnZwMWtTclExRWVZWVpWTXNRWS1oa205NEdrWnV6U0NVRXNwTE9ZNjFXV29KTkltekNLbWplbDF1WFdFZlF0LV9RRG0yR3hNU1l5VGxKaDdXbzVsTnpqSno4NkltbVhiV1ptQmtVSVZnMUwyRnBGZVpmbGYxd0dpc240c1RTeTctQnZtWGhhZ0o3Vy11UWZUdG1POUNFOGJNSVFicnVfSG02VGtpRHQ0R2RZbGxOUkZfeWhhd1Z0TV9SX2JwMFVIY21UeGMzZVg0RVZ0dVdlRzdWVUE4eGM0YTZnTzViT1lVVEZiUzk3alFmbFZtMmxsMzJHbWN2SWpzUjE1NUhJUU9zSy1KdVJsZlFPQ25MRk1JcEJhRXpld2EzdDVTeFR0M3hxTzVPZkFFRDBKVHlSbEGUjBNfQXBpQmFzZV9fdGVuYW50X2lklE6MFF9BcGlCYXNlX19zZXJ2ZXJfdXJslGgMdWKMCGFjY291bnRzlIwVeGVyb3Nkay5hcGlzLmFjY291bnRzlIwIQWNjb3VudHOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAhjb250YWN0c5SMFXhlcm9zZGsuYXBpcy5jb250YWN0c5SMCENvbnRhY3RzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowTdHJhY2tpbmdfY2F0ZWdvcmllc5SMIHhlcm9zZGsuYXBpcy50cmFja2luZ19jYXRlZ29yaWVzlIwSVHJhY2tpbmdDYXRlZ29yaWVzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowIcGF5bWVudHOUjBV4ZXJvc2RrLmFwaXMucGF5bWVudHOUjAhQYXltZW50c5STlCmBlH2UKGgZaBpoG05oHGgMdWKMBWl0ZW1zlIwSeGVyb3Nkay5hcGlzLml0ZW1zlIwFSXRlbXOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAd0ZW5hbnRzlIwUeGVyb3Nkay5hcGlzLnRlbmFudHOUjAdUZW5hbnRzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowRYmFua190cmFuc2FjdGlvbnOUjB54ZXJvc2RrLmFwaXMuYmFua190cmFuc2FjdGlvbnOUjBBCYW5rVHJhbnNhY3Rpb25zlJOUKYGUfZQoaBloGmgbTmgcaAx1YowLYXR0YWNobWVudHOUjBh4ZXJvc2RrLmFwaXMuYXR0YWNobWVudHOUjAtBdHRhY2htZW50c5STlCmBlH2UKGgZaBpoG05oHGgMdWKMDW9yZ2FuaXNhdGlvbnOUjBp4ZXJvc2RrLmFwaXMub3JnYW5pc2F0aW9uc5SMDU9yZ2FuaXNhdGlvbnOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAtjb25uZWN0aW9uc5SMGHhlcm9zZGsuYXBpcy5jb25uZWN0aW9uc5SMC0Nvbm5lY3Rpb25zlJOUKYGUfZQoaBloGmgbTmgcaAx1YowKY3VycmVuY2llc5SMF3hlcm9zZGsuYXBpcy5jdXJyZW5jaWVzlIwKQ3VycmVuY2llc5STlCmBlH2UKGgZaBpoG05oHGgMdWKMCXRheF9yYXRlc5SMFnhlcm9zZGsuYXBpcy50YXhfcmF0ZXOUjAhUYXhSYXRlc5STlCmBlH2UKGgZaBpoG05oHGgMdWKME2xpbmtlZF90cmFuc2FjdGlvbnOUjCB4ZXJvc2RrLmFwaXMubGlua2VkX3RyYW5zYWN0aW9uc5SMEkxpbmtlZFRyYW5zYWN0aW9uc5STlCmBlH2UKGgZaBpoG05oHGgMdWJ1YowMd29ya3NwYWNlX2lklEsBdWKHlC4=	gAR9lC4=	\N	2022-08-02 20:26:29.722507+00	2022-08-02 20:26:32.646684+00	t	b4d9dc65136441b0aba8dacc1955afa0	84bf34f853d9421a98bd1412c960a134	1	\N
stream-sink-hydrogen-ceiling	apps.xero.tasks.create_bill	\N	gASVzgoAAAAAAABLBEsDjA9hcHBzLnhlcm8udXRpbHOUjA1YZXJvQ29ubmVjdG9ylJOUKYGUfZQojApjb25uZWN0aW9ulIwPeGVyb3Nkay54ZXJvc2RrlIwHWGVyb1NES5STlCmBlH2UKIwSX1hlcm9TREtfX2Jhc2VfdXJslIwUaHR0cHM6Ly9hcGkueGVyby5jb22UjBNfWGVyb1NES19fY2xpZW50X2lklIwgQkIxMzk0NjdENTQyNEIxNEJFM0RCRjkyODk1RUI2Q0aUjBdfWGVyb1NES19fY2xpZW50X3NlY3JldJSMMDAzTzhiQ0hkQWFfWW56RGhPelVneThNSXo5VGpyRFRQSlVaRzRycVFpYklRWVJncZSMDl9yZWZyZXNoX3Rva2VulIxAZTk1YTI0NjMwMGI4YzQzNzkwNTEzNTU3MDRhYTdkNWRkNGFhMmRlNzBkNGI3N2JlNDM4ODZmNzhiYTdjMGQwOZSMCGludm9pY2VzlIwVeGVyb3Nkay5hcGlzLmludm9pY2VzlIwISW52b2ljZXOUk5QpgZR9lCiMFl9BcGlCYXNlX19hY2Nlc3NfdG9rZW6UWOwEAABleUpoYkdjaU9pSlNVekkxTmlJc0ltdHBaQ0k2SWpGRFFVWTRSVFkyTnpjeVJEWkVRekF5T0VRMk56STJSa1F3TWpZeE5UZ3hOVGN3UlVaRE1Ua2lMQ0owZVhBaU9pSktWMVFpTENKNE5YUWlPaUpJU3kxUFdtNWpkR0pqUVc4eGJrcDJNRU5aVm1kV1kwOWZRbXNpZlEuZXlKdVltWWlPakUyTlRrME56RTVPRGtzSW1WNGNDSTZNVFkxT1RRM016YzRPU3dpYVhOeklqb2lhSFIwY0hNNkx5OXBaR1Z1ZEdsMGVTNTRaWEp2TG1OdmJTSXNJbUYxWkNJNkltaDBkSEJ6T2k4dmFXUmxiblJwZEhrdWVHVnlieTVqYjIwdmNtVnpiM1Z5WTJWeklpd2lZMnhwWlc1MFgybGtJam9pUWtJeE16azBOamRFTlRReU5FSXhORUpGTTBSQ1Jqa3lPRGsxUlVJMlEwWWlMQ0p6ZFdJaU9pSTVPVEV6WmpaaVpqUXlNVEkxTmpreU9USmlNemczWW1RelpEWXpaalJrWXlJc0ltRjFkR2hmZEdsdFpTSTZNVFkxT1RRM01UZzROaXdpZUdWeWIxOTFjMlZ5YVdRaU9pSXhOMlU1Tmpsak1DMHpaVFV5TFRSa1pUa3RZV1ZsTVMweU5XWTVNR0ptTkRjME1XUWlMQ0puYkc5aVlXeGZjMlZ6YzJsdmJsOXBaQ0k2SWpNeU1EZGxObUppTXpRNU16UmpZV1k1TUdKbFlqQmtNREU0T1RoaU9HTmpJaXdpYW5ScElqb2lPVFU1TkRoaFlUTTNNRFkwWTJJM01qa3paVEppT1RNNE4yRXlNakppWTJZaUxDSmhkWFJvWlc1MGFXTmhkR2x2Ymw5bGRtVnVkRjlwWkNJNkltSTRZV1V4WTJRMUxUWTVNall0TkRGaU1TMWhaVFF6TFdGaE1UUXdOemc1TkRBM01pSXNJbk5qYjNCbElqcGJJbUZqWTI5MWJuUnBibWN1YzJWMGRHbHVaM01pTENKaFkyTnZkVzUwYVc1bkxtRjBkR0ZqYUcxbGJuUnpJaXdpWVdOamIzVnVkR2x1Wnk1MGNtRnVjMkZqZEdsdmJuTWlMQ0poWTJOdmRXNTBhVzVuTG1OdmJuUmhZM1J6SWl3aWIyWm1iR2x1WlY5aFkyTmxjM01pWFN3aVlXMXlJanBiSW5OemJ5SmRmUS5aY1FSVmE1cklCcmZvcmxWeUtETHpfcVotTF9TbWVTNmxGMFd5YnZwMWtTclExRWVZWVpWTXNRWS1oa205NEdrWnV6U0NVRXNwTE9ZNjFXV29KTkltekNLbWplbDF1WFdFZlF0LV9RRG0yR3hNU1l5VGxKaDdXbzVsTnpqSno4NkltbVhiV1ptQmtVSVZnMUwyRnBGZVpmbGYxd0dpc240c1RTeTctQnZtWGhhZ0o3Vy11UWZUdG1POUNFOGJNSVFicnVfSG02VGtpRHQ0R2RZbGxOUkZfeWhhd1Z0TV9SX2JwMFVIY21UeGMzZVg0RVZ0dVdlRzdWVUE4eGM0YTZnTzViT1lVVEZiUzk3alFmbFZtMmxsMzJHbWN2SWpzUjE1NUhJUU9zSy1KdVJsZlFPQ25MRk1JcEJhRXpld2EzdDVTeFR0M3hxTzVPZkFFRDBKVHlSbEGUjBNfQXBpQmFzZV9fdGVuYW50X2lklE6MFF9BcGlCYXNlX19zZXJ2ZXJfdXJslGgMdWKMCGFjY291bnRzlIwVeGVyb3Nkay5hcGlzLmFjY291bnRzlIwIQWNjb3VudHOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAhjb250YWN0c5SMFXhlcm9zZGsuYXBpcy5jb250YWN0c5SMCENvbnRhY3RzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowTdHJhY2tpbmdfY2F0ZWdvcmllc5SMIHhlcm9zZGsuYXBpcy50cmFja2luZ19jYXRlZ29yaWVzlIwSVHJhY2tpbmdDYXRlZ29yaWVzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowIcGF5bWVudHOUjBV4ZXJvc2RrLmFwaXMucGF5bWVudHOUjAhQYXltZW50c5STlCmBlH2UKGgZaBpoG05oHGgMdWKMBWl0ZW1zlIwSeGVyb3Nkay5hcGlzLml0ZW1zlIwFSXRlbXOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAd0ZW5hbnRzlIwUeGVyb3Nkay5hcGlzLnRlbmFudHOUjAdUZW5hbnRzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowRYmFua190cmFuc2FjdGlvbnOUjB54ZXJvc2RrLmFwaXMuYmFua190cmFuc2FjdGlvbnOUjBBCYW5rVHJhbnNhY3Rpb25zlJOUKYGUfZQoaBloGmgbTmgcaAx1YowLYXR0YWNobWVudHOUjBh4ZXJvc2RrLmFwaXMuYXR0YWNobWVudHOUjAtBdHRhY2htZW50c5STlCmBlH2UKGgZaBpoG05oHGgMdWKMDW9yZ2FuaXNhdGlvbnOUjBp4ZXJvc2RrLmFwaXMub3JnYW5pc2F0aW9uc5SMDU9yZ2FuaXNhdGlvbnOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAtjb25uZWN0aW9uc5SMGHhlcm9zZGsuYXBpcy5jb25uZWN0aW9uc5SMC0Nvbm5lY3Rpb25zlJOUKYGUfZQoaBloGmgbTmgcaAx1YowKY3VycmVuY2llc5SMF3hlcm9zZGsuYXBpcy5jdXJyZW5jaWVzlIwKQ3VycmVuY2llc5STlCmBlH2UKGgZaBpoG05oHGgMdWKMCXRheF9yYXRlc5SMFnhlcm9zZGsuYXBpcy50YXhfcmF0ZXOUjAhUYXhSYXRlc5STlCmBlH2UKGgZaBpoG05oHGgMdWKME2xpbmtlZF90cmFuc2FjdGlvbnOUjCB4ZXJvc2RrLmFwaXMubGlua2VkX3RyYW5zYWN0aW9uc5SMEkxpbmtlZFRyYW5zYWN0aW9uc5STlCmBlH2UKGgZaBpoG05oHGgMdWJ1YowMd29ya3NwYWNlX2lklEsBdWKHlC4=	gAR9lC4=	\N	2022-08-02 20:26:32.649939+00	2022-08-02 20:26:35.789498+00	t	8e42e2fb94ac4cb3b36a42fb4d835ab0	84bf34f853d9421a98bd1412c960a134	1	\N
beryllium-michigan-paris-vegan	apps.xero.tasks.create_bill	\N	gASVzgoAAAAAAABLAUsEjA9hcHBzLnhlcm8udXRpbHOUjA1YZXJvQ29ubmVjdG9ylJOUKYGUfZQojApjb25uZWN0aW9ulIwPeGVyb3Nkay54ZXJvc2RrlIwHWGVyb1NES5STlCmBlH2UKIwSX1hlcm9TREtfX2Jhc2VfdXJslIwUaHR0cHM6Ly9hcGkueGVyby5jb22UjBNfWGVyb1NES19fY2xpZW50X2lklIwgQkIxMzk0NjdENTQyNEIxNEJFM0RCRjkyODk1RUI2Q0aUjBdfWGVyb1NES19fY2xpZW50X3NlY3JldJSMMDAzTzhiQ0hkQWFfWW56RGhPelVneThNSXo5VGpyRFRQSlVaRzRycVFpYklRWVJncZSMDl9yZWZyZXNoX3Rva2VulIxAZTk1YTI0NjMwMGI4YzQzNzkwNTEzNTU3MDRhYTdkNWRkNGFhMmRlNzBkNGI3N2JlNDM4ODZmNzhiYTdjMGQwOZSMCGludm9pY2VzlIwVeGVyb3Nkay5hcGlzLmludm9pY2VzlIwISW52b2ljZXOUk5QpgZR9lCiMFl9BcGlCYXNlX19hY2Nlc3NfdG9rZW6UWOwEAABleUpoYkdjaU9pSlNVekkxTmlJc0ltdHBaQ0k2SWpGRFFVWTRSVFkyTnpjeVJEWkVRekF5T0VRMk56STJSa1F3TWpZeE5UZ3hOVGN3UlVaRE1Ua2lMQ0owZVhBaU9pSktWMVFpTENKNE5YUWlPaUpJU3kxUFdtNWpkR0pqUVc4eGJrcDJNRU5aVm1kV1kwOWZRbXNpZlEuZXlKdVltWWlPakUyTlRrME56RTVPRGtzSW1WNGNDSTZNVFkxT1RRM016YzRPU3dpYVhOeklqb2lhSFIwY0hNNkx5OXBaR1Z1ZEdsMGVTNTRaWEp2TG1OdmJTSXNJbUYxWkNJNkltaDBkSEJ6T2k4dmFXUmxiblJwZEhrdWVHVnlieTVqYjIwdmNtVnpiM1Z5WTJWeklpd2lZMnhwWlc1MFgybGtJam9pUWtJeE16azBOamRFTlRReU5FSXhORUpGTTBSQ1Jqa3lPRGsxUlVJMlEwWWlMQ0p6ZFdJaU9pSTVPVEV6WmpaaVpqUXlNVEkxTmpreU9USmlNemczWW1RelpEWXpaalJrWXlJc0ltRjFkR2hmZEdsdFpTSTZNVFkxT1RRM01UZzROaXdpZUdWeWIxOTFjMlZ5YVdRaU9pSXhOMlU1Tmpsak1DMHpaVFV5TFRSa1pUa3RZV1ZsTVMweU5XWTVNR0ptTkRjME1XUWlMQ0puYkc5aVlXeGZjMlZ6YzJsdmJsOXBaQ0k2SWpNeU1EZGxObUppTXpRNU16UmpZV1k1TUdKbFlqQmtNREU0T1RoaU9HTmpJaXdpYW5ScElqb2lPVFU1TkRoaFlUTTNNRFkwWTJJM01qa3paVEppT1RNNE4yRXlNakppWTJZaUxDSmhkWFJvWlc1MGFXTmhkR2x2Ymw5bGRtVnVkRjlwWkNJNkltSTRZV1V4WTJRMUxUWTVNall0TkRGaU1TMWhaVFF6TFdGaE1UUXdOemc1TkRBM01pSXNJbk5qYjNCbElqcGJJbUZqWTI5MWJuUnBibWN1YzJWMGRHbHVaM01pTENKaFkyTnZkVzUwYVc1bkxtRjBkR0ZqYUcxbGJuUnpJaXdpWVdOamIzVnVkR2x1Wnk1MGNtRnVjMkZqZEdsdmJuTWlMQ0poWTJOdmRXNTBhVzVuTG1OdmJuUmhZM1J6SWl3aWIyWm1iR2x1WlY5aFkyTmxjM01pWFN3aVlXMXlJanBiSW5OemJ5SmRmUS5aY1FSVmE1cklCcmZvcmxWeUtETHpfcVotTF9TbWVTNmxGMFd5YnZwMWtTclExRWVZWVpWTXNRWS1oa205NEdrWnV6U0NVRXNwTE9ZNjFXV29KTkltekNLbWplbDF1WFdFZlF0LV9RRG0yR3hNU1l5VGxKaDdXbzVsTnpqSno4NkltbVhiV1ptQmtVSVZnMUwyRnBGZVpmbGYxd0dpc240c1RTeTctQnZtWGhhZ0o3Vy11UWZUdG1POUNFOGJNSVFicnVfSG02VGtpRHQ0R2RZbGxOUkZfeWhhd1Z0TV9SX2JwMFVIY21UeGMzZVg0RVZ0dVdlRzdWVUE4eGM0YTZnTzViT1lVVEZiUzk3alFmbFZtMmxsMzJHbWN2SWpzUjE1NUhJUU9zSy1KdVJsZlFPQ25MRk1JcEJhRXpld2EzdDVTeFR0M3hxTzVPZkFFRDBKVHlSbEGUjBNfQXBpQmFzZV9fdGVuYW50X2lklE6MFF9BcGlCYXNlX19zZXJ2ZXJfdXJslGgMdWKMCGFjY291bnRzlIwVeGVyb3Nkay5hcGlzLmFjY291bnRzlIwIQWNjb3VudHOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAhjb250YWN0c5SMFXhlcm9zZGsuYXBpcy5jb250YWN0c5SMCENvbnRhY3RzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowTdHJhY2tpbmdfY2F0ZWdvcmllc5SMIHhlcm9zZGsuYXBpcy50cmFja2luZ19jYXRlZ29yaWVzlIwSVHJhY2tpbmdDYXRlZ29yaWVzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowIcGF5bWVudHOUjBV4ZXJvc2RrLmFwaXMucGF5bWVudHOUjAhQYXltZW50c5STlCmBlH2UKGgZaBpoG05oHGgMdWKMBWl0ZW1zlIwSeGVyb3Nkay5hcGlzLml0ZW1zlIwFSXRlbXOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAd0ZW5hbnRzlIwUeGVyb3Nkay5hcGlzLnRlbmFudHOUjAdUZW5hbnRzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowRYmFua190cmFuc2FjdGlvbnOUjB54ZXJvc2RrLmFwaXMuYmFua190cmFuc2FjdGlvbnOUjBBCYW5rVHJhbnNhY3Rpb25zlJOUKYGUfZQoaBloGmgbTmgcaAx1YowLYXR0YWNobWVudHOUjBh4ZXJvc2RrLmFwaXMuYXR0YWNobWVudHOUjAtBdHRhY2htZW50c5STlCmBlH2UKGgZaBpoG05oHGgMdWKMDW9yZ2FuaXNhdGlvbnOUjBp4ZXJvc2RrLmFwaXMub3JnYW5pc2F0aW9uc5SMDU9yZ2FuaXNhdGlvbnOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAtjb25uZWN0aW9uc5SMGHhlcm9zZGsuYXBpcy5jb25uZWN0aW9uc5SMC0Nvbm5lY3Rpb25zlJOUKYGUfZQoaBloGmgbTmgcaAx1YowKY3VycmVuY2llc5SMF3hlcm9zZGsuYXBpcy5jdXJyZW5jaWVzlIwKQ3VycmVuY2llc5STlCmBlH2UKGgZaBpoG05oHGgMdWKMCXRheF9yYXRlc5SMFnhlcm9zZGsuYXBpcy50YXhfcmF0ZXOUjAhUYXhSYXRlc5STlCmBlH2UKGgZaBpoG05oHGgMdWKME2xpbmtlZF90cmFuc2FjdGlvbnOUjCB4ZXJvc2RrLmFwaXMubGlua2VkX3RyYW5zYWN0aW9uc5SMEkxpbmtlZFRyYW5zYWN0aW9uc5STlCmBlH2UKGgZaBpoG05oHGgMdWJ1YowMd29ya3NwYWNlX2lklEsBdWKHlC4=	gAR9lC4=	\N	2022-08-02 20:26:35.791546+00	2022-08-02 20:26:38.930019+00	t	eec57d4324ec4e0f85f25d86a160406b	84bf34f853d9421a98bd1412c960a134	1	\N
leopard-nitrogen-thirteen-solar	apps.xero.tasks.create_bill	\N	gASVzgoAAAAAAABLA0sFjA9hcHBzLnhlcm8udXRpbHOUjA1YZXJvQ29ubmVjdG9ylJOUKYGUfZQojApjb25uZWN0aW9ulIwPeGVyb3Nkay54ZXJvc2RrlIwHWGVyb1NES5STlCmBlH2UKIwSX1hlcm9TREtfX2Jhc2VfdXJslIwUaHR0cHM6Ly9hcGkueGVyby5jb22UjBNfWGVyb1NES19fY2xpZW50X2lklIwgQkIxMzk0NjdENTQyNEIxNEJFM0RCRjkyODk1RUI2Q0aUjBdfWGVyb1NES19fY2xpZW50X3NlY3JldJSMMDAzTzhiQ0hkQWFfWW56RGhPelVneThNSXo5VGpyRFRQSlVaRzRycVFpYklRWVJncZSMDl9yZWZyZXNoX3Rva2VulIxAZTk1YTI0NjMwMGI4YzQzNzkwNTEzNTU3MDRhYTdkNWRkNGFhMmRlNzBkNGI3N2JlNDM4ODZmNzhiYTdjMGQwOZSMCGludm9pY2VzlIwVeGVyb3Nkay5hcGlzLmludm9pY2VzlIwISW52b2ljZXOUk5QpgZR9lCiMFl9BcGlCYXNlX19hY2Nlc3NfdG9rZW6UWOwEAABleUpoYkdjaU9pSlNVekkxTmlJc0ltdHBaQ0k2SWpGRFFVWTRSVFkyTnpjeVJEWkVRekF5T0VRMk56STJSa1F3TWpZeE5UZ3hOVGN3UlVaRE1Ua2lMQ0owZVhBaU9pSktWMVFpTENKNE5YUWlPaUpJU3kxUFdtNWpkR0pqUVc4eGJrcDJNRU5aVm1kV1kwOWZRbXNpZlEuZXlKdVltWWlPakUyTlRrME56RTVPRGtzSW1WNGNDSTZNVFkxT1RRM016YzRPU3dpYVhOeklqb2lhSFIwY0hNNkx5OXBaR1Z1ZEdsMGVTNTRaWEp2TG1OdmJTSXNJbUYxWkNJNkltaDBkSEJ6T2k4dmFXUmxiblJwZEhrdWVHVnlieTVqYjIwdmNtVnpiM1Z5WTJWeklpd2lZMnhwWlc1MFgybGtJam9pUWtJeE16azBOamRFTlRReU5FSXhORUpGTTBSQ1Jqa3lPRGsxUlVJMlEwWWlMQ0p6ZFdJaU9pSTVPVEV6WmpaaVpqUXlNVEkxTmpreU9USmlNemczWW1RelpEWXpaalJrWXlJc0ltRjFkR2hmZEdsdFpTSTZNVFkxT1RRM01UZzROaXdpZUdWeWIxOTFjMlZ5YVdRaU9pSXhOMlU1Tmpsak1DMHpaVFV5TFRSa1pUa3RZV1ZsTVMweU5XWTVNR0ptTkRjME1XUWlMQ0puYkc5aVlXeGZjMlZ6YzJsdmJsOXBaQ0k2SWpNeU1EZGxObUppTXpRNU16UmpZV1k1TUdKbFlqQmtNREU0T1RoaU9HTmpJaXdpYW5ScElqb2lPVFU1TkRoaFlUTTNNRFkwWTJJM01qa3paVEppT1RNNE4yRXlNakppWTJZaUxDSmhkWFJvWlc1MGFXTmhkR2x2Ymw5bGRtVnVkRjlwWkNJNkltSTRZV1V4WTJRMUxUWTVNall0TkRGaU1TMWhaVFF6TFdGaE1UUXdOemc1TkRBM01pSXNJbk5qYjNCbElqcGJJbUZqWTI5MWJuUnBibWN1YzJWMGRHbHVaM01pTENKaFkyTnZkVzUwYVc1bkxtRjBkR0ZqYUcxbGJuUnpJaXdpWVdOamIzVnVkR2x1Wnk1MGNtRnVjMkZqZEdsdmJuTWlMQ0poWTJOdmRXNTBhVzVuTG1OdmJuUmhZM1J6SWl3aWIyWm1iR2x1WlY5aFkyTmxjM01pWFN3aVlXMXlJanBiSW5OemJ5SmRmUS5aY1FSVmE1cklCcmZvcmxWeUtETHpfcVotTF9TbWVTNmxGMFd5YnZwMWtTclExRWVZWVpWTXNRWS1oa205NEdrWnV6U0NVRXNwTE9ZNjFXV29KTkltekNLbWplbDF1WFdFZlF0LV9RRG0yR3hNU1l5VGxKaDdXbzVsTnpqSno4NkltbVhiV1ptQmtVSVZnMUwyRnBGZVpmbGYxd0dpc240c1RTeTctQnZtWGhhZ0o3Vy11UWZUdG1POUNFOGJNSVFicnVfSG02VGtpRHQ0R2RZbGxOUkZfeWhhd1Z0TV9SX2JwMFVIY21UeGMzZVg0RVZ0dVdlRzdWVUE4eGM0YTZnTzViT1lVVEZiUzk3alFmbFZtMmxsMzJHbWN2SWpzUjE1NUhJUU9zSy1KdVJsZlFPQ25MRk1JcEJhRXpld2EzdDVTeFR0M3hxTzVPZkFFRDBKVHlSbEGUjBNfQXBpQmFzZV9fdGVuYW50X2lklE6MFF9BcGlCYXNlX19zZXJ2ZXJfdXJslGgMdWKMCGFjY291bnRzlIwVeGVyb3Nkay5hcGlzLmFjY291bnRzlIwIQWNjb3VudHOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAhjb250YWN0c5SMFXhlcm9zZGsuYXBpcy5jb250YWN0c5SMCENvbnRhY3RzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowTdHJhY2tpbmdfY2F0ZWdvcmllc5SMIHhlcm9zZGsuYXBpcy50cmFja2luZ19jYXRlZ29yaWVzlIwSVHJhY2tpbmdDYXRlZ29yaWVzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowIcGF5bWVudHOUjBV4ZXJvc2RrLmFwaXMucGF5bWVudHOUjAhQYXltZW50c5STlCmBlH2UKGgZaBpoG05oHGgMdWKMBWl0ZW1zlIwSeGVyb3Nkay5hcGlzLml0ZW1zlIwFSXRlbXOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAd0ZW5hbnRzlIwUeGVyb3Nkay5hcGlzLnRlbmFudHOUjAdUZW5hbnRzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowRYmFua190cmFuc2FjdGlvbnOUjB54ZXJvc2RrLmFwaXMuYmFua190cmFuc2FjdGlvbnOUjBBCYW5rVHJhbnNhY3Rpb25zlJOUKYGUfZQoaBloGmgbTmgcaAx1YowLYXR0YWNobWVudHOUjBh4ZXJvc2RrLmFwaXMuYXR0YWNobWVudHOUjAtBdHRhY2htZW50c5STlCmBlH2UKGgZaBpoG05oHGgMdWKMDW9yZ2FuaXNhdGlvbnOUjBp4ZXJvc2RrLmFwaXMub3JnYW5pc2F0aW9uc5SMDU9yZ2FuaXNhdGlvbnOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAtjb25uZWN0aW9uc5SMGHhlcm9zZGsuYXBpcy5jb25uZWN0aW9uc5SMC0Nvbm5lY3Rpb25zlJOUKYGUfZQoaBloGmgbTmgcaAx1YowKY3VycmVuY2llc5SMF3hlcm9zZGsuYXBpcy5jdXJyZW5jaWVzlIwKQ3VycmVuY2llc5STlCmBlH2UKGgZaBpoG05oHGgMdWKMCXRheF9yYXRlc5SMFnhlcm9zZGsuYXBpcy50YXhfcmF0ZXOUjAhUYXhSYXRlc5STlCmBlH2UKGgZaBpoG05oHGgMdWKME2xpbmtlZF90cmFuc2FjdGlvbnOUjCB4ZXJvc2RrLmFwaXMubGlua2VkX3RyYW5zYWN0aW9uc5SMEkxpbmtlZFRyYW5zYWN0aW9uc5STlCmBlH2UKGgZaBpoG05oHGgMdWJ1YowMd29ya3NwYWNlX2lklEsBdWKHlC4=	gAR9lC4=	\N	2022-08-02 20:26:38.931823+00	2022-08-02 20:26:42.055962+00	t	409b8a295592411bb5ec94138c05094e	84bf34f853d9421a98bd1412c960a134	1	\N
don-emma-california-fix	apps.xero.tasks.create_bank_transaction	\N	gASVzgoAAAAAAABLCksGjA9hcHBzLnhlcm8udXRpbHOUjA1YZXJvQ29ubmVjdG9ylJOUKYGUfZQojApjb25uZWN0aW9ulIwPeGVyb3Nkay54ZXJvc2RrlIwHWGVyb1NES5STlCmBlH2UKIwSX1hlcm9TREtfX2Jhc2VfdXJslIwUaHR0cHM6Ly9hcGkueGVyby5jb22UjBNfWGVyb1NES19fY2xpZW50X2lklIwgQkIxMzk0NjdENTQyNEIxNEJFM0RCRjkyODk1RUI2Q0aUjBdfWGVyb1NES19fY2xpZW50X3NlY3JldJSMMDAzTzhiQ0hkQWFfWW56RGhPelVneThNSXo5VGpyRFRQSlVaRzRycVFpYklRWVJncZSMDl9yZWZyZXNoX3Rva2VulIxAZTk1YTI0NjMwMGI4YzQzNzkwNTEzNTU3MDRhYTdkNWRkNGFhMmRlNzBkNGI3N2JlNDM4ODZmNzhiYTdjMGQwOZSMCGludm9pY2VzlIwVeGVyb3Nkay5hcGlzLmludm9pY2VzlIwISW52b2ljZXOUk5QpgZR9lCiMFl9BcGlCYXNlX19hY2Nlc3NfdG9rZW6UWOwEAABleUpoYkdjaU9pSlNVekkxTmlJc0ltdHBaQ0k2SWpGRFFVWTRSVFkyTnpjeVJEWkVRekF5T0VRMk56STJSa1F3TWpZeE5UZ3hOVGN3UlVaRE1Ua2lMQ0owZVhBaU9pSktWMVFpTENKNE5YUWlPaUpJU3kxUFdtNWpkR0pqUVc4eGJrcDJNRU5aVm1kV1kwOWZRbXNpZlEuZXlKdVltWWlPakUyTlRrME56RTVPRGtzSW1WNGNDSTZNVFkxT1RRM016YzRPU3dpYVhOeklqb2lhSFIwY0hNNkx5OXBaR1Z1ZEdsMGVTNTRaWEp2TG1OdmJTSXNJbUYxWkNJNkltaDBkSEJ6T2k4dmFXUmxiblJwZEhrdWVHVnlieTVqYjIwdmNtVnpiM1Z5WTJWeklpd2lZMnhwWlc1MFgybGtJam9pUWtJeE16azBOamRFTlRReU5FSXhORUpGTTBSQ1Jqa3lPRGsxUlVJMlEwWWlMQ0p6ZFdJaU9pSTVPVEV6WmpaaVpqUXlNVEkxTmpreU9USmlNemczWW1RelpEWXpaalJrWXlJc0ltRjFkR2hmZEdsdFpTSTZNVFkxT1RRM01UZzROaXdpZUdWeWIxOTFjMlZ5YVdRaU9pSXhOMlU1Tmpsak1DMHpaVFV5TFRSa1pUa3RZV1ZsTVMweU5XWTVNR0ptTkRjME1XUWlMQ0puYkc5aVlXeGZjMlZ6YzJsdmJsOXBaQ0k2SWpNeU1EZGxObUppTXpRNU16UmpZV1k1TUdKbFlqQmtNREU0T1RoaU9HTmpJaXdpYW5ScElqb2lPVFU1TkRoaFlUTTNNRFkwWTJJM01qa3paVEppT1RNNE4yRXlNakppWTJZaUxDSmhkWFJvWlc1MGFXTmhkR2x2Ymw5bGRtVnVkRjlwWkNJNkltSTRZV1V4WTJRMUxUWTVNall0TkRGaU1TMWhaVFF6TFdGaE1UUXdOemc1TkRBM01pSXNJbk5qYjNCbElqcGJJbUZqWTI5MWJuUnBibWN1YzJWMGRHbHVaM01pTENKaFkyTnZkVzUwYVc1bkxtRjBkR0ZqYUcxbGJuUnpJaXdpWVdOamIzVnVkR2x1Wnk1MGNtRnVjMkZqZEdsdmJuTWlMQ0poWTJOdmRXNTBhVzVuTG1OdmJuUmhZM1J6SWl3aWIyWm1iR2x1WlY5aFkyTmxjM01pWFN3aVlXMXlJanBiSW5OemJ5SmRmUS5aY1FSVmE1cklCcmZvcmxWeUtETHpfcVotTF9TbWVTNmxGMFd5YnZwMWtTclExRWVZWVpWTXNRWS1oa205NEdrWnV6U0NVRXNwTE9ZNjFXV29KTkltekNLbWplbDF1WFdFZlF0LV9RRG0yR3hNU1l5VGxKaDdXbzVsTnpqSno4NkltbVhiV1ptQmtVSVZnMUwyRnBGZVpmbGYxd0dpc240c1RTeTctQnZtWGhhZ0o3Vy11UWZUdG1POUNFOGJNSVFicnVfSG02VGtpRHQ0R2RZbGxOUkZfeWhhd1Z0TV9SX2JwMFVIY21UeGMzZVg0RVZ0dVdlRzdWVUE4eGM0YTZnTzViT1lVVEZiUzk3alFmbFZtMmxsMzJHbWN2SWpzUjE1NUhJUU9zSy1KdVJsZlFPQ25MRk1JcEJhRXpld2EzdDVTeFR0M3hxTzVPZkFFRDBKVHlSbEGUjBNfQXBpQmFzZV9fdGVuYW50X2lklE6MFF9BcGlCYXNlX19zZXJ2ZXJfdXJslGgMdWKMCGFjY291bnRzlIwVeGVyb3Nkay5hcGlzLmFjY291bnRzlIwIQWNjb3VudHOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAhjb250YWN0c5SMFXhlcm9zZGsuYXBpcy5jb250YWN0c5SMCENvbnRhY3RzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowTdHJhY2tpbmdfY2F0ZWdvcmllc5SMIHhlcm9zZGsuYXBpcy50cmFja2luZ19jYXRlZ29yaWVzlIwSVHJhY2tpbmdDYXRlZ29yaWVzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowIcGF5bWVudHOUjBV4ZXJvc2RrLmFwaXMucGF5bWVudHOUjAhQYXltZW50c5STlCmBlH2UKGgZaBpoG05oHGgMdWKMBWl0ZW1zlIwSeGVyb3Nkay5hcGlzLml0ZW1zlIwFSXRlbXOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAd0ZW5hbnRzlIwUeGVyb3Nkay5hcGlzLnRlbmFudHOUjAdUZW5hbnRzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowRYmFua190cmFuc2FjdGlvbnOUjB54ZXJvc2RrLmFwaXMuYmFua190cmFuc2FjdGlvbnOUjBBCYW5rVHJhbnNhY3Rpb25zlJOUKYGUfZQoaBloGmgbTmgcaAx1YowLYXR0YWNobWVudHOUjBh4ZXJvc2RrLmFwaXMuYXR0YWNobWVudHOUjAtBdHRhY2htZW50c5STlCmBlH2UKGgZaBpoG05oHGgMdWKMDW9yZ2FuaXNhdGlvbnOUjBp4ZXJvc2RrLmFwaXMub3JnYW5pc2F0aW9uc5SMDU9yZ2FuaXNhdGlvbnOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAtjb25uZWN0aW9uc5SMGHhlcm9zZGsuYXBpcy5jb25uZWN0aW9uc5SMC0Nvbm5lY3Rpb25zlJOUKYGUfZQoaBloGmgbTmgcaAx1YowKY3VycmVuY2llc5SMF3hlcm9zZGsuYXBpcy5jdXJyZW5jaWVzlIwKQ3VycmVuY2llc5STlCmBlH2UKGgZaBpoG05oHGgMdWKMCXRheF9yYXRlc5SMFnhlcm9zZGsuYXBpcy50YXhfcmF0ZXOUjAhUYXhSYXRlc5STlCmBlH2UKGgZaBpoG05oHGgMdWKME2xpbmtlZF90cmFuc2FjdGlvbnOUjCB4ZXJvc2RrLmFwaXMubGlua2VkX3RyYW5zYWN0aW9uc5SMEkxpbmtlZFRyYW5zYWN0aW9uc5STlCmBlH2UKGgZaBpoG05oHGgMdWJ1YowMd29ya3NwYWNlX2lklEsBdWKHlC4=	gAR9lC4=	\N	2022-08-02 20:26:42.057577+00	2022-08-02 20:26:46.342917+00	t	7b0c24677b104217bd8ce7c881a61778	84bf34f853d9421a98bd1412c960a134	1	\N
fish-sierra-south-vermont	apps.xero.tasks.create_bank_transaction	\N	gASVzgoAAAAAAABLBUsHjA9hcHBzLnhlcm8udXRpbHOUjA1YZXJvQ29ubmVjdG9ylJOUKYGUfZQojApjb25uZWN0aW9ulIwPeGVyb3Nkay54ZXJvc2RrlIwHWGVyb1NES5STlCmBlH2UKIwSX1hlcm9TREtfX2Jhc2VfdXJslIwUaHR0cHM6Ly9hcGkueGVyby5jb22UjBNfWGVyb1NES19fY2xpZW50X2lklIwgQkIxMzk0NjdENTQyNEIxNEJFM0RCRjkyODk1RUI2Q0aUjBdfWGVyb1NES19fY2xpZW50X3NlY3JldJSMMDAzTzhiQ0hkQWFfWW56RGhPelVneThNSXo5VGpyRFRQSlVaRzRycVFpYklRWVJncZSMDl9yZWZyZXNoX3Rva2VulIxAZTk1YTI0NjMwMGI4YzQzNzkwNTEzNTU3MDRhYTdkNWRkNGFhMmRlNzBkNGI3N2JlNDM4ODZmNzhiYTdjMGQwOZSMCGludm9pY2VzlIwVeGVyb3Nkay5hcGlzLmludm9pY2VzlIwISW52b2ljZXOUk5QpgZR9lCiMFl9BcGlCYXNlX19hY2Nlc3NfdG9rZW6UWOwEAABleUpoYkdjaU9pSlNVekkxTmlJc0ltdHBaQ0k2SWpGRFFVWTRSVFkyTnpjeVJEWkVRekF5T0VRMk56STJSa1F3TWpZeE5UZ3hOVGN3UlVaRE1Ua2lMQ0owZVhBaU9pSktWMVFpTENKNE5YUWlPaUpJU3kxUFdtNWpkR0pqUVc4eGJrcDJNRU5aVm1kV1kwOWZRbXNpZlEuZXlKdVltWWlPakUyTlRrME56RTVPRGtzSW1WNGNDSTZNVFkxT1RRM016YzRPU3dpYVhOeklqb2lhSFIwY0hNNkx5OXBaR1Z1ZEdsMGVTNTRaWEp2TG1OdmJTSXNJbUYxWkNJNkltaDBkSEJ6T2k4dmFXUmxiblJwZEhrdWVHVnlieTVqYjIwdmNtVnpiM1Z5WTJWeklpd2lZMnhwWlc1MFgybGtJam9pUWtJeE16azBOamRFTlRReU5FSXhORUpGTTBSQ1Jqa3lPRGsxUlVJMlEwWWlMQ0p6ZFdJaU9pSTVPVEV6WmpaaVpqUXlNVEkxTmpreU9USmlNemczWW1RelpEWXpaalJrWXlJc0ltRjFkR2hmZEdsdFpTSTZNVFkxT1RRM01UZzROaXdpZUdWeWIxOTFjMlZ5YVdRaU9pSXhOMlU1Tmpsak1DMHpaVFV5TFRSa1pUa3RZV1ZsTVMweU5XWTVNR0ptTkRjME1XUWlMQ0puYkc5aVlXeGZjMlZ6YzJsdmJsOXBaQ0k2SWpNeU1EZGxObUppTXpRNU16UmpZV1k1TUdKbFlqQmtNREU0T1RoaU9HTmpJaXdpYW5ScElqb2lPVFU1TkRoaFlUTTNNRFkwWTJJM01qa3paVEppT1RNNE4yRXlNakppWTJZaUxDSmhkWFJvWlc1MGFXTmhkR2x2Ymw5bGRtVnVkRjlwWkNJNkltSTRZV1V4WTJRMUxUWTVNall0TkRGaU1TMWhaVFF6TFdGaE1UUXdOemc1TkRBM01pSXNJbk5qYjNCbElqcGJJbUZqWTI5MWJuUnBibWN1YzJWMGRHbHVaM01pTENKaFkyTnZkVzUwYVc1bkxtRjBkR0ZqYUcxbGJuUnpJaXdpWVdOamIzVnVkR2x1Wnk1MGNtRnVjMkZqZEdsdmJuTWlMQ0poWTJOdmRXNTBhVzVuTG1OdmJuUmhZM1J6SWl3aWIyWm1iR2x1WlY5aFkyTmxjM01pWFN3aVlXMXlJanBiSW5OemJ5SmRmUS5aY1FSVmE1cklCcmZvcmxWeUtETHpfcVotTF9TbWVTNmxGMFd5YnZwMWtTclExRWVZWVpWTXNRWS1oa205NEdrWnV6U0NVRXNwTE9ZNjFXV29KTkltekNLbWplbDF1WFdFZlF0LV9RRG0yR3hNU1l5VGxKaDdXbzVsTnpqSno4NkltbVhiV1ptQmtVSVZnMUwyRnBGZVpmbGYxd0dpc240c1RTeTctQnZtWGhhZ0o3Vy11UWZUdG1POUNFOGJNSVFicnVfSG02VGtpRHQ0R2RZbGxOUkZfeWhhd1Z0TV9SX2JwMFVIY21UeGMzZVg0RVZ0dVdlRzdWVUE4eGM0YTZnTzViT1lVVEZiUzk3alFmbFZtMmxsMzJHbWN2SWpzUjE1NUhJUU9zSy1KdVJsZlFPQ25MRk1JcEJhRXpld2EzdDVTeFR0M3hxTzVPZkFFRDBKVHlSbEGUjBNfQXBpQmFzZV9fdGVuYW50X2lklE6MFF9BcGlCYXNlX19zZXJ2ZXJfdXJslGgMdWKMCGFjY291bnRzlIwVeGVyb3Nkay5hcGlzLmFjY291bnRzlIwIQWNjb3VudHOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAhjb250YWN0c5SMFXhlcm9zZGsuYXBpcy5jb250YWN0c5SMCENvbnRhY3RzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowTdHJhY2tpbmdfY2F0ZWdvcmllc5SMIHhlcm9zZGsuYXBpcy50cmFja2luZ19jYXRlZ29yaWVzlIwSVHJhY2tpbmdDYXRlZ29yaWVzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowIcGF5bWVudHOUjBV4ZXJvc2RrLmFwaXMucGF5bWVudHOUjAhQYXltZW50c5STlCmBlH2UKGgZaBpoG05oHGgMdWKMBWl0ZW1zlIwSeGVyb3Nkay5hcGlzLml0ZW1zlIwFSXRlbXOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAd0ZW5hbnRzlIwUeGVyb3Nkay5hcGlzLnRlbmFudHOUjAdUZW5hbnRzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowRYmFua190cmFuc2FjdGlvbnOUjB54ZXJvc2RrLmFwaXMuYmFua190cmFuc2FjdGlvbnOUjBBCYW5rVHJhbnNhY3Rpb25zlJOUKYGUfZQoaBloGmgbTmgcaAx1YowLYXR0YWNobWVudHOUjBh4ZXJvc2RrLmFwaXMuYXR0YWNobWVudHOUjAtBdHRhY2htZW50c5STlCmBlH2UKGgZaBpoG05oHGgMdWKMDW9yZ2FuaXNhdGlvbnOUjBp4ZXJvc2RrLmFwaXMub3JnYW5pc2F0aW9uc5SMDU9yZ2FuaXNhdGlvbnOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAtjb25uZWN0aW9uc5SMGHhlcm9zZGsuYXBpcy5jb25uZWN0aW9uc5SMC0Nvbm5lY3Rpb25zlJOUKYGUfZQoaBloGmgbTmgcaAx1YowKY3VycmVuY2llc5SMF3hlcm9zZGsuYXBpcy5jdXJyZW5jaWVzlIwKQ3VycmVuY2llc5STlCmBlH2UKGgZaBpoG05oHGgMdWKMCXRheF9yYXRlc5SMFnhlcm9zZGsuYXBpcy50YXhfcmF0ZXOUjAhUYXhSYXRlc5STlCmBlH2UKGgZaBpoG05oHGgMdWKME2xpbmtlZF90cmFuc2FjdGlvbnOUjCB4ZXJvc2RrLmFwaXMubGlua2VkX3RyYW5zYWN0aW9uc5SMEkxpbmtlZFRyYW5zYWN0aW9uc5STlCmBlH2UKGgZaBpoG05oHGgMdWJ1YowMd29ya3NwYWNlX2lklEsBdWKHlC4=	gAR9lC4=	\N	2022-08-02 20:26:46.346757+00	2022-08-02 20:26:50.549518+00	t	389f9475232a4985a7b6c6181c954a2f	84bf34f853d9421a98bd1412c960a134	1	\N
kansas-jupiter-alanine-gee	apps.xero.tasks.create_bank_transaction	\N	gASVzgoAAAAAAABLCEsIjA9hcHBzLnhlcm8udXRpbHOUjA1YZXJvQ29ubmVjdG9ylJOUKYGUfZQojApjb25uZWN0aW9ulIwPeGVyb3Nkay54ZXJvc2RrlIwHWGVyb1NES5STlCmBlH2UKIwSX1hlcm9TREtfX2Jhc2VfdXJslIwUaHR0cHM6Ly9hcGkueGVyby5jb22UjBNfWGVyb1NES19fY2xpZW50X2lklIwgQkIxMzk0NjdENTQyNEIxNEJFM0RCRjkyODk1RUI2Q0aUjBdfWGVyb1NES19fY2xpZW50X3NlY3JldJSMMDAzTzhiQ0hkQWFfWW56RGhPelVneThNSXo5VGpyRFRQSlVaRzRycVFpYklRWVJncZSMDl9yZWZyZXNoX3Rva2VulIxAZTk1YTI0NjMwMGI4YzQzNzkwNTEzNTU3MDRhYTdkNWRkNGFhMmRlNzBkNGI3N2JlNDM4ODZmNzhiYTdjMGQwOZSMCGludm9pY2VzlIwVeGVyb3Nkay5hcGlzLmludm9pY2VzlIwISW52b2ljZXOUk5QpgZR9lCiMFl9BcGlCYXNlX19hY2Nlc3NfdG9rZW6UWOwEAABleUpoYkdjaU9pSlNVekkxTmlJc0ltdHBaQ0k2SWpGRFFVWTRSVFkyTnpjeVJEWkVRekF5T0VRMk56STJSa1F3TWpZeE5UZ3hOVGN3UlVaRE1Ua2lMQ0owZVhBaU9pSktWMVFpTENKNE5YUWlPaUpJU3kxUFdtNWpkR0pqUVc4eGJrcDJNRU5aVm1kV1kwOWZRbXNpZlEuZXlKdVltWWlPakUyTlRrME56RTVPRGtzSW1WNGNDSTZNVFkxT1RRM016YzRPU3dpYVhOeklqb2lhSFIwY0hNNkx5OXBaR1Z1ZEdsMGVTNTRaWEp2TG1OdmJTSXNJbUYxWkNJNkltaDBkSEJ6T2k4dmFXUmxiblJwZEhrdWVHVnlieTVqYjIwdmNtVnpiM1Z5WTJWeklpd2lZMnhwWlc1MFgybGtJam9pUWtJeE16azBOamRFTlRReU5FSXhORUpGTTBSQ1Jqa3lPRGsxUlVJMlEwWWlMQ0p6ZFdJaU9pSTVPVEV6WmpaaVpqUXlNVEkxTmpreU9USmlNemczWW1RelpEWXpaalJrWXlJc0ltRjFkR2hmZEdsdFpTSTZNVFkxT1RRM01UZzROaXdpZUdWeWIxOTFjMlZ5YVdRaU9pSXhOMlU1Tmpsak1DMHpaVFV5TFRSa1pUa3RZV1ZsTVMweU5XWTVNR0ptTkRjME1XUWlMQ0puYkc5aVlXeGZjMlZ6YzJsdmJsOXBaQ0k2SWpNeU1EZGxObUppTXpRNU16UmpZV1k1TUdKbFlqQmtNREU0T1RoaU9HTmpJaXdpYW5ScElqb2lPVFU1TkRoaFlUTTNNRFkwWTJJM01qa3paVEppT1RNNE4yRXlNakppWTJZaUxDSmhkWFJvWlc1MGFXTmhkR2x2Ymw5bGRtVnVkRjlwWkNJNkltSTRZV1V4WTJRMUxUWTVNall0TkRGaU1TMWhaVFF6TFdGaE1UUXdOemc1TkRBM01pSXNJbk5qYjNCbElqcGJJbUZqWTI5MWJuUnBibWN1YzJWMGRHbHVaM01pTENKaFkyTnZkVzUwYVc1bkxtRjBkR0ZqYUcxbGJuUnpJaXdpWVdOamIzVnVkR2x1Wnk1MGNtRnVjMkZqZEdsdmJuTWlMQ0poWTJOdmRXNTBhVzVuTG1OdmJuUmhZM1J6SWl3aWIyWm1iR2x1WlY5aFkyTmxjM01pWFN3aVlXMXlJanBiSW5OemJ5SmRmUS5aY1FSVmE1cklCcmZvcmxWeUtETHpfcVotTF9TbWVTNmxGMFd5YnZwMWtTclExRWVZWVpWTXNRWS1oa205NEdrWnV6U0NVRXNwTE9ZNjFXV29KTkltekNLbWplbDF1WFdFZlF0LV9RRG0yR3hNU1l5VGxKaDdXbzVsTnpqSno4NkltbVhiV1ptQmtVSVZnMUwyRnBGZVpmbGYxd0dpc240c1RTeTctQnZtWGhhZ0o3Vy11UWZUdG1POUNFOGJNSVFicnVfSG02VGtpRHQ0R2RZbGxOUkZfeWhhd1Z0TV9SX2JwMFVIY21UeGMzZVg0RVZ0dVdlRzdWVUE4eGM0YTZnTzViT1lVVEZiUzk3alFmbFZtMmxsMzJHbWN2SWpzUjE1NUhJUU9zSy1KdVJsZlFPQ25MRk1JcEJhRXpld2EzdDVTeFR0M3hxTzVPZkFFRDBKVHlSbEGUjBNfQXBpQmFzZV9fdGVuYW50X2lklE6MFF9BcGlCYXNlX19zZXJ2ZXJfdXJslGgMdWKMCGFjY291bnRzlIwVeGVyb3Nkay5hcGlzLmFjY291bnRzlIwIQWNjb3VudHOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAhjb250YWN0c5SMFXhlcm9zZGsuYXBpcy5jb250YWN0c5SMCENvbnRhY3RzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowTdHJhY2tpbmdfY2F0ZWdvcmllc5SMIHhlcm9zZGsuYXBpcy50cmFja2luZ19jYXRlZ29yaWVzlIwSVHJhY2tpbmdDYXRlZ29yaWVzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowIcGF5bWVudHOUjBV4ZXJvc2RrLmFwaXMucGF5bWVudHOUjAhQYXltZW50c5STlCmBlH2UKGgZaBpoG05oHGgMdWKMBWl0ZW1zlIwSeGVyb3Nkay5hcGlzLml0ZW1zlIwFSXRlbXOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAd0ZW5hbnRzlIwUeGVyb3Nkay5hcGlzLnRlbmFudHOUjAdUZW5hbnRzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowRYmFua190cmFuc2FjdGlvbnOUjB54ZXJvc2RrLmFwaXMuYmFua190cmFuc2FjdGlvbnOUjBBCYW5rVHJhbnNhY3Rpb25zlJOUKYGUfZQoaBloGmgbTmgcaAx1YowLYXR0YWNobWVudHOUjBh4ZXJvc2RrLmFwaXMuYXR0YWNobWVudHOUjAtBdHRhY2htZW50c5STlCmBlH2UKGgZaBpoG05oHGgMdWKMDW9yZ2FuaXNhdGlvbnOUjBp4ZXJvc2RrLmFwaXMub3JnYW5pc2F0aW9uc5SMDU9yZ2FuaXNhdGlvbnOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAtjb25uZWN0aW9uc5SMGHhlcm9zZGsuYXBpcy5jb25uZWN0aW9uc5SMC0Nvbm5lY3Rpb25zlJOUKYGUfZQoaBloGmgbTmgcaAx1YowKY3VycmVuY2llc5SMF3hlcm9zZGsuYXBpcy5jdXJyZW5jaWVzlIwKQ3VycmVuY2llc5STlCmBlH2UKGgZaBpoG05oHGgMdWKMCXRheF9yYXRlc5SMFnhlcm9zZGsuYXBpcy50YXhfcmF0ZXOUjAhUYXhSYXRlc5STlCmBlH2UKGgZaBpoG05oHGgMdWKME2xpbmtlZF90cmFuc2FjdGlvbnOUjCB4ZXJvc2RrLmFwaXMubGlua2VkX3RyYW5zYWN0aW9uc5SMEkxpbmtlZFRyYW5zYWN0aW9uc5STlCmBlH2UKGgZaBpoG05oHGgMdWJ1YowMd29ya3NwYWNlX2lklEsBdWKHlC4=	gAR9lC4=	\N	2022-08-02 20:26:50.552262+00	2022-08-02 20:26:53.92776+00	t	e727953a6b7844399e3edc7e3e52d6e8	84bf34f853d9421a98bd1412c960a134	1	\N
winner-vermont-ten-bacon	apps.xero.tasks.create_bank_transaction	\N	gASVzgoAAAAAAABLBksJjA9hcHBzLnhlcm8udXRpbHOUjA1YZXJvQ29ubmVjdG9ylJOUKYGUfZQojApjb25uZWN0aW9ulIwPeGVyb3Nkay54ZXJvc2RrlIwHWGVyb1NES5STlCmBlH2UKIwSX1hlcm9TREtfX2Jhc2VfdXJslIwUaHR0cHM6Ly9hcGkueGVyby5jb22UjBNfWGVyb1NES19fY2xpZW50X2lklIwgQkIxMzk0NjdENTQyNEIxNEJFM0RCRjkyODk1RUI2Q0aUjBdfWGVyb1NES19fY2xpZW50X3NlY3JldJSMMDAzTzhiQ0hkQWFfWW56RGhPelVneThNSXo5VGpyRFRQSlVaRzRycVFpYklRWVJncZSMDl9yZWZyZXNoX3Rva2VulIxAZTk1YTI0NjMwMGI4YzQzNzkwNTEzNTU3MDRhYTdkNWRkNGFhMmRlNzBkNGI3N2JlNDM4ODZmNzhiYTdjMGQwOZSMCGludm9pY2VzlIwVeGVyb3Nkay5hcGlzLmludm9pY2VzlIwISW52b2ljZXOUk5QpgZR9lCiMFl9BcGlCYXNlX19hY2Nlc3NfdG9rZW6UWOwEAABleUpoYkdjaU9pSlNVekkxTmlJc0ltdHBaQ0k2SWpGRFFVWTRSVFkyTnpjeVJEWkVRekF5T0VRMk56STJSa1F3TWpZeE5UZ3hOVGN3UlVaRE1Ua2lMQ0owZVhBaU9pSktWMVFpTENKNE5YUWlPaUpJU3kxUFdtNWpkR0pqUVc4eGJrcDJNRU5aVm1kV1kwOWZRbXNpZlEuZXlKdVltWWlPakUyTlRrME56RTVPRGtzSW1WNGNDSTZNVFkxT1RRM016YzRPU3dpYVhOeklqb2lhSFIwY0hNNkx5OXBaR1Z1ZEdsMGVTNTRaWEp2TG1OdmJTSXNJbUYxWkNJNkltaDBkSEJ6T2k4dmFXUmxiblJwZEhrdWVHVnlieTVqYjIwdmNtVnpiM1Z5WTJWeklpd2lZMnhwWlc1MFgybGtJam9pUWtJeE16azBOamRFTlRReU5FSXhORUpGTTBSQ1Jqa3lPRGsxUlVJMlEwWWlMQ0p6ZFdJaU9pSTVPVEV6WmpaaVpqUXlNVEkxTmpreU9USmlNemczWW1RelpEWXpaalJrWXlJc0ltRjFkR2hmZEdsdFpTSTZNVFkxT1RRM01UZzROaXdpZUdWeWIxOTFjMlZ5YVdRaU9pSXhOMlU1Tmpsak1DMHpaVFV5TFRSa1pUa3RZV1ZsTVMweU5XWTVNR0ptTkRjME1XUWlMQ0puYkc5aVlXeGZjMlZ6YzJsdmJsOXBaQ0k2SWpNeU1EZGxObUppTXpRNU16UmpZV1k1TUdKbFlqQmtNREU0T1RoaU9HTmpJaXdpYW5ScElqb2lPVFU1TkRoaFlUTTNNRFkwWTJJM01qa3paVEppT1RNNE4yRXlNakppWTJZaUxDSmhkWFJvWlc1MGFXTmhkR2x2Ymw5bGRtVnVkRjlwWkNJNkltSTRZV1V4WTJRMUxUWTVNall0TkRGaU1TMWhaVFF6TFdGaE1UUXdOemc1TkRBM01pSXNJbk5qYjNCbElqcGJJbUZqWTI5MWJuUnBibWN1YzJWMGRHbHVaM01pTENKaFkyTnZkVzUwYVc1bkxtRjBkR0ZqYUcxbGJuUnpJaXdpWVdOamIzVnVkR2x1Wnk1MGNtRnVjMkZqZEdsdmJuTWlMQ0poWTJOdmRXNTBhVzVuTG1OdmJuUmhZM1J6SWl3aWIyWm1iR2x1WlY5aFkyTmxjM01pWFN3aVlXMXlJanBiSW5OemJ5SmRmUS5aY1FSVmE1cklCcmZvcmxWeUtETHpfcVotTF9TbWVTNmxGMFd5YnZwMWtTclExRWVZWVpWTXNRWS1oa205NEdrWnV6U0NVRXNwTE9ZNjFXV29KTkltekNLbWplbDF1WFdFZlF0LV9RRG0yR3hNU1l5VGxKaDdXbzVsTnpqSno4NkltbVhiV1ptQmtVSVZnMUwyRnBGZVpmbGYxd0dpc240c1RTeTctQnZtWGhhZ0o3Vy11UWZUdG1POUNFOGJNSVFicnVfSG02VGtpRHQ0R2RZbGxOUkZfeWhhd1Z0TV9SX2JwMFVIY21UeGMzZVg0RVZ0dVdlRzdWVUE4eGM0YTZnTzViT1lVVEZiUzk3alFmbFZtMmxsMzJHbWN2SWpzUjE1NUhJUU9zSy1KdVJsZlFPQ25MRk1JcEJhRXpld2EzdDVTeFR0M3hxTzVPZkFFRDBKVHlSbEGUjBNfQXBpQmFzZV9fdGVuYW50X2lklE6MFF9BcGlCYXNlX19zZXJ2ZXJfdXJslGgMdWKMCGFjY291bnRzlIwVeGVyb3Nkay5hcGlzLmFjY291bnRzlIwIQWNjb3VudHOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAhjb250YWN0c5SMFXhlcm9zZGsuYXBpcy5jb250YWN0c5SMCENvbnRhY3RzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowTdHJhY2tpbmdfY2F0ZWdvcmllc5SMIHhlcm9zZGsuYXBpcy50cmFja2luZ19jYXRlZ29yaWVzlIwSVHJhY2tpbmdDYXRlZ29yaWVzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowIcGF5bWVudHOUjBV4ZXJvc2RrLmFwaXMucGF5bWVudHOUjAhQYXltZW50c5STlCmBlH2UKGgZaBpoG05oHGgMdWKMBWl0ZW1zlIwSeGVyb3Nkay5hcGlzLml0ZW1zlIwFSXRlbXOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAd0ZW5hbnRzlIwUeGVyb3Nkay5hcGlzLnRlbmFudHOUjAdUZW5hbnRzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowRYmFua190cmFuc2FjdGlvbnOUjB54ZXJvc2RrLmFwaXMuYmFua190cmFuc2FjdGlvbnOUjBBCYW5rVHJhbnNhY3Rpb25zlJOUKYGUfZQoaBloGmgbTmgcaAx1YowLYXR0YWNobWVudHOUjBh4ZXJvc2RrLmFwaXMuYXR0YWNobWVudHOUjAtBdHRhY2htZW50c5STlCmBlH2UKGgZaBpoG05oHGgMdWKMDW9yZ2FuaXNhdGlvbnOUjBp4ZXJvc2RrLmFwaXMub3JnYW5pc2F0aW9uc5SMDU9yZ2FuaXNhdGlvbnOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAtjb25uZWN0aW9uc5SMGHhlcm9zZGsuYXBpcy5jb25uZWN0aW9uc5SMC0Nvbm5lY3Rpb25zlJOUKYGUfZQoaBloGmgbTmgcaAx1YowKY3VycmVuY2llc5SMF3hlcm9zZGsuYXBpcy5jdXJyZW5jaWVzlIwKQ3VycmVuY2llc5STlCmBlH2UKGgZaBpoG05oHGgMdWKMCXRheF9yYXRlc5SMFnhlcm9zZGsuYXBpcy50YXhfcmF0ZXOUjAhUYXhSYXRlc5STlCmBlH2UKGgZaBpoG05oHGgMdWKME2xpbmtlZF90cmFuc2FjdGlvbnOUjCB4ZXJvc2RrLmFwaXMubGlua2VkX3RyYW5zYWN0aW9uc5SMEkxpbmtlZFRyYW5zYWN0aW9uc5STlCmBlH2UKGgZaBpoG05oHGgMdWJ1YowMd29ya3NwYWNlX2lklEsBdWKHlC4=	gAR9lC4=	\N	2022-08-02 20:26:53.930537+00	2022-08-02 20:26:57.882719+00	t	fbd9e93d6c0d41cc8023f8818223ce7f	84bf34f853d9421a98bd1412c960a134	1	\N
alpha-utah-fix-massachusetts	apps.xero.tasks.create_bank_transaction	\N	gASVzgoAAAAAAABLCUsKjA9hcHBzLnhlcm8udXRpbHOUjA1YZXJvQ29ubmVjdG9ylJOUKYGUfZQojApjb25uZWN0aW9ulIwPeGVyb3Nkay54ZXJvc2RrlIwHWGVyb1NES5STlCmBlH2UKIwSX1hlcm9TREtfX2Jhc2VfdXJslIwUaHR0cHM6Ly9hcGkueGVyby5jb22UjBNfWGVyb1NES19fY2xpZW50X2lklIwgQkIxMzk0NjdENTQyNEIxNEJFM0RCRjkyODk1RUI2Q0aUjBdfWGVyb1NES19fY2xpZW50X3NlY3JldJSMMDAzTzhiQ0hkQWFfWW56RGhPelVneThNSXo5VGpyRFRQSlVaRzRycVFpYklRWVJncZSMDl9yZWZyZXNoX3Rva2VulIxAZTk1YTI0NjMwMGI4YzQzNzkwNTEzNTU3MDRhYTdkNWRkNGFhMmRlNzBkNGI3N2JlNDM4ODZmNzhiYTdjMGQwOZSMCGludm9pY2VzlIwVeGVyb3Nkay5hcGlzLmludm9pY2VzlIwISW52b2ljZXOUk5QpgZR9lCiMFl9BcGlCYXNlX19hY2Nlc3NfdG9rZW6UWOwEAABleUpoYkdjaU9pSlNVekkxTmlJc0ltdHBaQ0k2SWpGRFFVWTRSVFkyTnpjeVJEWkVRekF5T0VRMk56STJSa1F3TWpZeE5UZ3hOVGN3UlVaRE1Ua2lMQ0owZVhBaU9pSktWMVFpTENKNE5YUWlPaUpJU3kxUFdtNWpkR0pqUVc4eGJrcDJNRU5aVm1kV1kwOWZRbXNpZlEuZXlKdVltWWlPakUyTlRrME56RTVPRGtzSW1WNGNDSTZNVFkxT1RRM016YzRPU3dpYVhOeklqb2lhSFIwY0hNNkx5OXBaR1Z1ZEdsMGVTNTRaWEp2TG1OdmJTSXNJbUYxWkNJNkltaDBkSEJ6T2k4dmFXUmxiblJwZEhrdWVHVnlieTVqYjIwdmNtVnpiM1Z5WTJWeklpd2lZMnhwWlc1MFgybGtJam9pUWtJeE16azBOamRFTlRReU5FSXhORUpGTTBSQ1Jqa3lPRGsxUlVJMlEwWWlMQ0p6ZFdJaU9pSTVPVEV6WmpaaVpqUXlNVEkxTmpreU9USmlNemczWW1RelpEWXpaalJrWXlJc0ltRjFkR2hmZEdsdFpTSTZNVFkxT1RRM01UZzROaXdpZUdWeWIxOTFjMlZ5YVdRaU9pSXhOMlU1Tmpsak1DMHpaVFV5TFRSa1pUa3RZV1ZsTVMweU5XWTVNR0ptTkRjME1XUWlMQ0puYkc5aVlXeGZjMlZ6YzJsdmJsOXBaQ0k2SWpNeU1EZGxObUppTXpRNU16UmpZV1k1TUdKbFlqQmtNREU0T1RoaU9HTmpJaXdpYW5ScElqb2lPVFU1TkRoaFlUTTNNRFkwWTJJM01qa3paVEppT1RNNE4yRXlNakppWTJZaUxDSmhkWFJvWlc1MGFXTmhkR2x2Ymw5bGRtVnVkRjlwWkNJNkltSTRZV1V4WTJRMUxUWTVNall0TkRGaU1TMWhaVFF6TFdGaE1UUXdOemc1TkRBM01pSXNJbk5qYjNCbElqcGJJbUZqWTI5MWJuUnBibWN1YzJWMGRHbHVaM01pTENKaFkyTnZkVzUwYVc1bkxtRjBkR0ZqYUcxbGJuUnpJaXdpWVdOamIzVnVkR2x1Wnk1MGNtRnVjMkZqZEdsdmJuTWlMQ0poWTJOdmRXNTBhVzVuTG1OdmJuUmhZM1J6SWl3aWIyWm1iR2x1WlY5aFkyTmxjM01pWFN3aVlXMXlJanBiSW5OemJ5SmRmUS5aY1FSVmE1cklCcmZvcmxWeUtETHpfcVotTF9TbWVTNmxGMFd5YnZwMWtTclExRWVZWVpWTXNRWS1oa205NEdrWnV6U0NVRXNwTE9ZNjFXV29KTkltekNLbWplbDF1WFdFZlF0LV9RRG0yR3hNU1l5VGxKaDdXbzVsTnpqSno4NkltbVhiV1ptQmtVSVZnMUwyRnBGZVpmbGYxd0dpc240c1RTeTctQnZtWGhhZ0o3Vy11UWZUdG1POUNFOGJNSVFicnVfSG02VGtpRHQ0R2RZbGxOUkZfeWhhd1Z0TV9SX2JwMFVIY21UeGMzZVg0RVZ0dVdlRzdWVUE4eGM0YTZnTzViT1lVVEZiUzk3alFmbFZtMmxsMzJHbWN2SWpzUjE1NUhJUU9zSy1KdVJsZlFPQ25MRk1JcEJhRXpld2EzdDVTeFR0M3hxTzVPZkFFRDBKVHlSbEGUjBNfQXBpQmFzZV9fdGVuYW50X2lklE6MFF9BcGlCYXNlX19zZXJ2ZXJfdXJslGgMdWKMCGFjY291bnRzlIwVeGVyb3Nkay5hcGlzLmFjY291bnRzlIwIQWNjb3VudHOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAhjb250YWN0c5SMFXhlcm9zZGsuYXBpcy5jb250YWN0c5SMCENvbnRhY3RzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowTdHJhY2tpbmdfY2F0ZWdvcmllc5SMIHhlcm9zZGsuYXBpcy50cmFja2luZ19jYXRlZ29yaWVzlIwSVHJhY2tpbmdDYXRlZ29yaWVzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowIcGF5bWVudHOUjBV4ZXJvc2RrLmFwaXMucGF5bWVudHOUjAhQYXltZW50c5STlCmBlH2UKGgZaBpoG05oHGgMdWKMBWl0ZW1zlIwSeGVyb3Nkay5hcGlzLml0ZW1zlIwFSXRlbXOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAd0ZW5hbnRzlIwUeGVyb3Nkay5hcGlzLnRlbmFudHOUjAdUZW5hbnRzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowRYmFua190cmFuc2FjdGlvbnOUjB54ZXJvc2RrLmFwaXMuYmFua190cmFuc2FjdGlvbnOUjBBCYW5rVHJhbnNhY3Rpb25zlJOUKYGUfZQoaBloGmgbTmgcaAx1YowLYXR0YWNobWVudHOUjBh4ZXJvc2RrLmFwaXMuYXR0YWNobWVudHOUjAtBdHRhY2htZW50c5STlCmBlH2UKGgZaBpoG05oHGgMdWKMDW9yZ2FuaXNhdGlvbnOUjBp4ZXJvc2RrLmFwaXMub3JnYW5pc2F0aW9uc5SMDU9yZ2FuaXNhdGlvbnOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAtjb25uZWN0aW9uc5SMGHhlcm9zZGsuYXBpcy5jb25uZWN0aW9uc5SMC0Nvbm5lY3Rpb25zlJOUKYGUfZQoaBloGmgbTmgcaAx1YowKY3VycmVuY2llc5SMF3hlcm9zZGsuYXBpcy5jdXJyZW5jaWVzlIwKQ3VycmVuY2llc5STlCmBlH2UKGgZaBpoG05oHGgMdWKMCXRheF9yYXRlc5SMFnhlcm9zZGsuYXBpcy50YXhfcmF0ZXOUjAhUYXhSYXRlc5STlCmBlH2UKGgZaBpoG05oHGgMdWKME2xpbmtlZF90cmFuc2FjdGlvbnOUjCB4ZXJvc2RrLmFwaXMubGlua2VkX3RyYW5zYWN0aW9uc5SMEkxpbmtlZFRyYW5zYWN0aW9uc5STlCmBlH2UKGgZaBpoG05oHGgMdWJ1YowMd29ya3NwYWNlX2lklEsBdWKHlC4=	gAR9lC4=	\N	2022-08-02 20:26:57.885765+00	2022-08-02 20:27:00.819913+00	t	0cadb11489564e78be9595f6b549ff85	84bf34f853d9421a98bd1412c960a134	1	\N
enemy-may-london-lion	apps.xero.tasks.create_bank_transaction	\N	gASVzgoAAAAAAABLB0sLjA9hcHBzLnhlcm8udXRpbHOUjA1YZXJvQ29ubmVjdG9ylJOUKYGUfZQojApjb25uZWN0aW9ulIwPeGVyb3Nkay54ZXJvc2RrlIwHWGVyb1NES5STlCmBlH2UKIwSX1hlcm9TREtfX2Jhc2VfdXJslIwUaHR0cHM6Ly9hcGkueGVyby5jb22UjBNfWGVyb1NES19fY2xpZW50X2lklIwgQkIxMzk0NjdENTQyNEIxNEJFM0RCRjkyODk1RUI2Q0aUjBdfWGVyb1NES19fY2xpZW50X3NlY3JldJSMMDAzTzhiQ0hkQWFfWW56RGhPelVneThNSXo5VGpyRFRQSlVaRzRycVFpYklRWVJncZSMDl9yZWZyZXNoX3Rva2VulIxAZTk1YTI0NjMwMGI4YzQzNzkwNTEzNTU3MDRhYTdkNWRkNGFhMmRlNzBkNGI3N2JlNDM4ODZmNzhiYTdjMGQwOZSMCGludm9pY2VzlIwVeGVyb3Nkay5hcGlzLmludm9pY2VzlIwISW52b2ljZXOUk5QpgZR9lCiMFl9BcGlCYXNlX19hY2Nlc3NfdG9rZW6UWOwEAABleUpoYkdjaU9pSlNVekkxTmlJc0ltdHBaQ0k2SWpGRFFVWTRSVFkyTnpjeVJEWkVRekF5T0VRMk56STJSa1F3TWpZeE5UZ3hOVGN3UlVaRE1Ua2lMQ0owZVhBaU9pSktWMVFpTENKNE5YUWlPaUpJU3kxUFdtNWpkR0pqUVc4eGJrcDJNRU5aVm1kV1kwOWZRbXNpZlEuZXlKdVltWWlPakUyTlRrME56RTVPRGtzSW1WNGNDSTZNVFkxT1RRM016YzRPU3dpYVhOeklqb2lhSFIwY0hNNkx5OXBaR1Z1ZEdsMGVTNTRaWEp2TG1OdmJTSXNJbUYxWkNJNkltaDBkSEJ6T2k4dmFXUmxiblJwZEhrdWVHVnlieTVqYjIwdmNtVnpiM1Z5WTJWeklpd2lZMnhwWlc1MFgybGtJam9pUWtJeE16azBOamRFTlRReU5FSXhORUpGTTBSQ1Jqa3lPRGsxUlVJMlEwWWlMQ0p6ZFdJaU9pSTVPVEV6WmpaaVpqUXlNVEkxTmpreU9USmlNemczWW1RelpEWXpaalJrWXlJc0ltRjFkR2hmZEdsdFpTSTZNVFkxT1RRM01UZzROaXdpZUdWeWIxOTFjMlZ5YVdRaU9pSXhOMlU1Tmpsak1DMHpaVFV5TFRSa1pUa3RZV1ZsTVMweU5XWTVNR0ptTkRjME1XUWlMQ0puYkc5aVlXeGZjMlZ6YzJsdmJsOXBaQ0k2SWpNeU1EZGxObUppTXpRNU16UmpZV1k1TUdKbFlqQmtNREU0T1RoaU9HTmpJaXdpYW5ScElqb2lPVFU1TkRoaFlUTTNNRFkwWTJJM01qa3paVEppT1RNNE4yRXlNakppWTJZaUxDSmhkWFJvWlc1MGFXTmhkR2x2Ymw5bGRtVnVkRjlwWkNJNkltSTRZV1V4WTJRMUxUWTVNall0TkRGaU1TMWhaVFF6TFdGaE1UUXdOemc1TkRBM01pSXNJbk5qYjNCbElqcGJJbUZqWTI5MWJuUnBibWN1YzJWMGRHbHVaM01pTENKaFkyTnZkVzUwYVc1bkxtRjBkR0ZqYUcxbGJuUnpJaXdpWVdOamIzVnVkR2x1Wnk1MGNtRnVjMkZqZEdsdmJuTWlMQ0poWTJOdmRXNTBhVzVuTG1OdmJuUmhZM1J6SWl3aWIyWm1iR2x1WlY5aFkyTmxjM01pWFN3aVlXMXlJanBiSW5OemJ5SmRmUS5aY1FSVmE1cklCcmZvcmxWeUtETHpfcVotTF9TbWVTNmxGMFd5YnZwMWtTclExRWVZWVpWTXNRWS1oa205NEdrWnV6U0NVRXNwTE9ZNjFXV29KTkltekNLbWplbDF1WFdFZlF0LV9RRG0yR3hNU1l5VGxKaDdXbzVsTnpqSno4NkltbVhiV1ptQmtVSVZnMUwyRnBGZVpmbGYxd0dpc240c1RTeTctQnZtWGhhZ0o3Vy11UWZUdG1POUNFOGJNSVFicnVfSG02VGtpRHQ0R2RZbGxOUkZfeWhhd1Z0TV9SX2JwMFVIY21UeGMzZVg0RVZ0dVdlRzdWVUE4eGM0YTZnTzViT1lVVEZiUzk3alFmbFZtMmxsMzJHbWN2SWpzUjE1NUhJUU9zSy1KdVJsZlFPQ25MRk1JcEJhRXpld2EzdDVTeFR0M3hxTzVPZkFFRDBKVHlSbEGUjBNfQXBpQmFzZV9fdGVuYW50X2lklE6MFF9BcGlCYXNlX19zZXJ2ZXJfdXJslGgMdWKMCGFjY291bnRzlIwVeGVyb3Nkay5hcGlzLmFjY291bnRzlIwIQWNjb3VudHOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAhjb250YWN0c5SMFXhlcm9zZGsuYXBpcy5jb250YWN0c5SMCENvbnRhY3RzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowTdHJhY2tpbmdfY2F0ZWdvcmllc5SMIHhlcm9zZGsuYXBpcy50cmFja2luZ19jYXRlZ29yaWVzlIwSVHJhY2tpbmdDYXRlZ29yaWVzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowIcGF5bWVudHOUjBV4ZXJvc2RrLmFwaXMucGF5bWVudHOUjAhQYXltZW50c5STlCmBlH2UKGgZaBpoG05oHGgMdWKMBWl0ZW1zlIwSeGVyb3Nkay5hcGlzLml0ZW1zlIwFSXRlbXOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAd0ZW5hbnRzlIwUeGVyb3Nkay5hcGlzLnRlbmFudHOUjAdUZW5hbnRzlJOUKYGUfZQoaBloGmgbTmgcaAx1YowRYmFua190cmFuc2FjdGlvbnOUjB54ZXJvc2RrLmFwaXMuYmFua190cmFuc2FjdGlvbnOUjBBCYW5rVHJhbnNhY3Rpb25zlJOUKYGUfZQoaBloGmgbTmgcaAx1YowLYXR0YWNobWVudHOUjBh4ZXJvc2RrLmFwaXMuYXR0YWNobWVudHOUjAtBdHRhY2htZW50c5STlCmBlH2UKGgZaBpoG05oHGgMdWKMDW9yZ2FuaXNhdGlvbnOUjBp4ZXJvc2RrLmFwaXMub3JnYW5pc2F0aW9uc5SMDU9yZ2FuaXNhdGlvbnOUk5QpgZR9lChoGWgaaBtOaBxoDHVijAtjb25uZWN0aW9uc5SMGHhlcm9zZGsuYXBpcy5jb25uZWN0aW9uc5SMC0Nvbm5lY3Rpb25zlJOUKYGUfZQoaBloGmgbTmgcaAx1YowKY3VycmVuY2llc5SMF3hlcm9zZGsuYXBpcy5jdXJyZW5jaWVzlIwKQ3VycmVuY2llc5STlCmBlH2UKGgZaBpoG05oHGgMdWKMCXRheF9yYXRlc5SMFnhlcm9zZGsuYXBpcy50YXhfcmF0ZXOUjAhUYXhSYXRlc5STlCmBlH2UKGgZaBpoG05oHGgMdWKME2xpbmtlZF90cmFuc2FjdGlvbnOUjCB4ZXJvc2RrLmFwaXMubGlua2VkX3RyYW5zYWN0aW9uc5SMEkxpbmtlZFRyYW5zYWN0aW9uc5STlCmBlH2UKGgZaBpoG05oHGgMdWJ1YowMd29ya3NwYWNlX2lklEsBdWKHlC4=	gAR9lC4=	\N	2022-08-02 20:27:00.821958+00	2022-08-02 20:27:04.042171+00	t	a2af211320e74707879d7f195fb8a538	84bf34f853d9421a98bd1412c960a134	1	\N
gee-lemon-ink-river	apps.xero.tasks.create_bill	\N	gASVAQsAAAAAAABLAksCjA9hcHBzLnhlcm8udXRpbHOUjA1YZXJvQ29ubmVjdG9ylJOUKYGUfZQojApjb25uZWN0aW9ulIwPeGVyb3Nkay54ZXJvc2RrlIwHWGVyb1NES5STlCmBlH2UKIwSX1hlcm9TREtfX2Jhc2VfdXJslIwUaHR0cHM6Ly9hcGkueGVyby5jb22UjBNfWGVyb1NES19fY2xpZW50X2lklIwgQkIxMzk0NjdENTQyNEIxNEJFM0RCRjkyODk1RUI2Q0aUjBdfWGVyb1NES19fY2xpZW50X3NlY3JldJSMMDAzTzhiQ0hkQWFfWW56RGhPelVneThNSXo5VGpyRFRQSlVaRzRycVFpYklRWVJncZSMDl9yZWZyZXNoX3Rva2VulIxANDYxMDUwY2NlNDBkMmVlOGM4NzI4NjhlNzNhZWQ1NWRmZTQ2Nzc1N2JkMTZkMGUyMmU4M2Q0YTNlYWQ2Mjg3OJSMCGludm9pY2VzlIwVeGVyb3Nkay5hcGlzLmludm9pY2VzlIwISW52b2ljZXOUk5QpgZR9lCiMFl9BcGlCYXNlX19hY2Nlc3NfdG9rZW6UWOwEAABleUpoYkdjaU9pSlNVekkxTmlJc0ltdHBaQ0k2SWpGRFFVWTRSVFkyTnpjeVJEWkVRekF5T0VRMk56STJSa1F3TWpZeE5UZ3hOVGN3UlVaRE1Ua2lMQ0owZVhBaU9pSktWMVFpTENKNE5YUWlPaUpJU3kxUFdtNWpkR0pqUVc4eGJrcDJNRU5aVm1kV1kwOWZRbXNpZlEuZXlKdVltWWlPakUyTlRrME56SXdOakVzSW1WNGNDSTZNVFkxT1RRM016ZzJNU3dpYVhOeklqb2lhSFIwY0hNNkx5OXBaR1Z1ZEdsMGVTNTRaWEp2TG1OdmJTSXNJbUYxWkNJNkltaDBkSEJ6T2k4dmFXUmxiblJwZEhrdWVHVnlieTVqYjIwdmNtVnpiM1Z5WTJWeklpd2lZMnhwWlc1MFgybGtJam9pUWtJeE16azBOamRFTlRReU5FSXhORUpGTTBSQ1Jqa3lPRGsxUlVJMlEwWWlMQ0p6ZFdJaU9pSTVPVEV6WmpaaVpqUXlNVEkxTmpreU9USmlNemczWW1RelpEWXpaalJrWXlJc0ltRjFkR2hmZEdsdFpTSTZNVFkxT1RRM01UZzROaXdpZUdWeWIxOTFjMlZ5YVdRaU9pSXhOMlU1Tmpsak1DMHpaVFV5TFRSa1pUa3RZV1ZsTVMweU5XWTVNR0ptTkRjME1XUWlMQ0puYkc5aVlXeGZjMlZ6YzJsdmJsOXBaQ0k2SWpNeU1EZGxObUppTXpRNU16UmpZV1k1TUdKbFlqQmtNREU0T1RoaU9HTmpJaXdpYW5ScElqb2lPVFU1TkRoaFlUTTNNRFkwWTJJM01qa3paVEppT1RNNE4yRXlNakppWTJZaUxDSmhkWFJvWlc1MGFXTmhkR2x2Ymw5bGRtVnVkRjlwWkNJNkltSTRZV1V4WTJRMUxUWTVNall0TkRGaU1TMWhaVFF6TFdGaE1UUXdOemc1TkRBM01pSXNJbk5qYjNCbElqcGJJbUZqWTI5MWJuUnBibWN1YzJWMGRHbHVaM01pTENKaFkyTnZkVzUwYVc1bkxtRjBkR0ZqYUcxbGJuUnpJaXdpWVdOamIzVnVkR2x1Wnk1MGNtRnVjMkZqZEdsdmJuTWlMQ0poWTJOdmRXNTBhVzVuTG1OdmJuUmhZM1J6SWl3aWIyWm1iR2x1WlY5aFkyTmxjM01pWFN3aVlXMXlJanBiSW5OemJ5SmRmUS5PNlozdmR5Q0VuZThFQ1I0ZHhxZ0pXbHY1NHVNQ01VNlBEMkNyU0k5Y3Ria25kaXNCMm9fRGxXbHNtNGlJS1lEeU9oTldsbGt0NTFfdTBNMWxvZHNGVDZBZ25TVjZpYmZRWGxjSTkyT0lmZXhIczVIaEFxbVQ5aGpoeF96VElpM0JQbzhQc1FUMEVRdTk4Ym9SNlRUQnJldnMyTjVscFBYcUJ2VVFXSXdGNTVWMEJ6Z0RlYzZHQzhLWG5fOFNudFlpWHB4TWpkOU9yRnlwdjdVVy13TUdkcVYybmtrdmZRSTMzenJnZjU0MVF2NmZoQnVoV2N5NnNvc0F6Yk5yV2luX1pIRU1WcHd2bGRQa2ZOcGxpWXpJNlgyeldzSVA1NjJqX0c3OWZOOGg1ajRzT05kSnczUmJYZ01CMEY4R3ZRS2RXaDNBS21QX0g4bmFTY04taml2WEGUjBNfQXBpQmFzZV9fdGVuYW50X2lklIwkMzZhYjE5MTAtMTFiMy00MzI1LWI1NDUtOGQxMTcwNjY4YWIzlIwUX0FwaUJhc2VfX3NlcnZlcl91cmyUaAx1YowIYWNjb3VudHOUjBV4ZXJvc2RrLmFwaXMuYWNjb3VudHOUjAhBY2NvdW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAhjb250YWN0c5SMFXhlcm9zZGsuYXBpcy5jb250YWN0c5SMCENvbnRhY3RzlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKME3RyYWNraW5nX2NhdGVnb3JpZXOUjCB4ZXJvc2RrLmFwaXMudHJhY2tpbmdfY2F0ZWdvcmllc5SMElRyYWNraW5nQ2F0ZWdvcmllc5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAhwYXltZW50c5SMFXhlcm9zZGsuYXBpcy5wYXltZW50c5SMCFBheW1lbnRzlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKMBWl0ZW1zlIwSeGVyb3Nkay5hcGlzLml0ZW1zlIwFSXRlbXOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowHdGVuYW50c5SMFHhlcm9zZGsuYXBpcy50ZW5hbnRzlIwHVGVuYW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijBFiYW5rX3RyYW5zYWN0aW9uc5SMHnhlcm9zZGsuYXBpcy5iYW5rX3RyYW5zYWN0aW9uc5SMEEJhbmtUcmFuc2FjdGlvbnOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowLYXR0YWNobWVudHOUjBh4ZXJvc2RrLmFwaXMuYXR0YWNobWVudHOUjAtBdHRhY2htZW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijA1vcmdhbmlzYXRpb25zlIwaeGVyb3Nkay5hcGlzLm9yZ2FuaXNhdGlvbnOUjA1PcmdhbmlzYXRpb25zlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKMC2Nvbm5lY3Rpb25zlIwYeGVyb3Nkay5hcGlzLmNvbm5lY3Rpb25zlIwLQ29ubmVjdGlvbnOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowKY3VycmVuY2llc5SMF3hlcm9zZGsuYXBpcy5jdXJyZW5jaWVzlIwKQ3VycmVuY2llc5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAl0YXhfcmF0ZXOUjBZ4ZXJvc2RrLmFwaXMudGF4X3JhdGVzlIwIVGF4UmF0ZXOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowTbGlua2VkX3RyYW5zYWN0aW9uc5SMIHhlcm9zZGsuYXBpcy5saW5rZWRfdHJhbnNhY3Rpb25zlIwSTGlua2VkVHJhbnNhY3Rpb25zlJOUKYGUfZQoaBloGmgbaBxoHWgMdWJ1YowMd29ya3NwYWNlX2lklEsBdWKHlC4=	gAR9lC4=	\N	2022-08-02 20:27:41.523038+00	2022-08-02 20:27:45.125792+00	t	e26417c3fd094bc88547a80f5c2809c4	0afd912e17ff4bb2816bd9dc8349ba01	1	\N
zebra-jig-happy-december	apps.xero.tasks.create_bill	\N	gASVAQsAAAAAAABLBEsDjA9hcHBzLnhlcm8udXRpbHOUjA1YZXJvQ29ubmVjdG9ylJOUKYGUfZQojApjb25uZWN0aW9ulIwPeGVyb3Nkay54ZXJvc2RrlIwHWGVyb1NES5STlCmBlH2UKIwSX1hlcm9TREtfX2Jhc2VfdXJslIwUaHR0cHM6Ly9hcGkueGVyby5jb22UjBNfWGVyb1NES19fY2xpZW50X2lklIwgQkIxMzk0NjdENTQyNEIxNEJFM0RCRjkyODk1RUI2Q0aUjBdfWGVyb1NES19fY2xpZW50X3NlY3JldJSMMDAzTzhiQ0hkQWFfWW56RGhPelVneThNSXo5VGpyRFRQSlVaRzRycVFpYklRWVJncZSMDl9yZWZyZXNoX3Rva2VulIxANDYxMDUwY2NlNDBkMmVlOGM4NzI4NjhlNzNhZWQ1NWRmZTQ2Nzc1N2JkMTZkMGUyMmU4M2Q0YTNlYWQ2Mjg3OJSMCGludm9pY2VzlIwVeGVyb3Nkay5hcGlzLmludm9pY2VzlIwISW52b2ljZXOUk5QpgZR9lCiMFl9BcGlCYXNlX19hY2Nlc3NfdG9rZW6UWOwEAABleUpoYkdjaU9pSlNVekkxTmlJc0ltdHBaQ0k2SWpGRFFVWTRSVFkyTnpjeVJEWkVRekF5T0VRMk56STJSa1F3TWpZeE5UZ3hOVGN3UlVaRE1Ua2lMQ0owZVhBaU9pSktWMVFpTENKNE5YUWlPaUpJU3kxUFdtNWpkR0pqUVc4eGJrcDJNRU5aVm1kV1kwOWZRbXNpZlEuZXlKdVltWWlPakUyTlRrME56SXdOakVzSW1WNGNDSTZNVFkxT1RRM016ZzJNU3dpYVhOeklqb2lhSFIwY0hNNkx5OXBaR1Z1ZEdsMGVTNTRaWEp2TG1OdmJTSXNJbUYxWkNJNkltaDBkSEJ6T2k4dmFXUmxiblJwZEhrdWVHVnlieTVqYjIwdmNtVnpiM1Z5WTJWeklpd2lZMnhwWlc1MFgybGtJam9pUWtJeE16azBOamRFTlRReU5FSXhORUpGTTBSQ1Jqa3lPRGsxUlVJMlEwWWlMQ0p6ZFdJaU9pSTVPVEV6WmpaaVpqUXlNVEkxTmpreU9USmlNemczWW1RelpEWXpaalJrWXlJc0ltRjFkR2hmZEdsdFpTSTZNVFkxT1RRM01UZzROaXdpZUdWeWIxOTFjMlZ5YVdRaU9pSXhOMlU1Tmpsak1DMHpaVFV5TFRSa1pUa3RZV1ZsTVMweU5XWTVNR0ptTkRjME1XUWlMQ0puYkc5aVlXeGZjMlZ6YzJsdmJsOXBaQ0k2SWpNeU1EZGxObUppTXpRNU16UmpZV1k1TUdKbFlqQmtNREU0T1RoaU9HTmpJaXdpYW5ScElqb2lPVFU1TkRoaFlUTTNNRFkwWTJJM01qa3paVEppT1RNNE4yRXlNakppWTJZaUxDSmhkWFJvWlc1MGFXTmhkR2x2Ymw5bGRtVnVkRjlwWkNJNkltSTRZV1V4WTJRMUxUWTVNall0TkRGaU1TMWhaVFF6TFdGaE1UUXdOemc1TkRBM01pSXNJbk5qYjNCbElqcGJJbUZqWTI5MWJuUnBibWN1YzJWMGRHbHVaM01pTENKaFkyTnZkVzUwYVc1bkxtRjBkR0ZqYUcxbGJuUnpJaXdpWVdOamIzVnVkR2x1Wnk1MGNtRnVjMkZqZEdsdmJuTWlMQ0poWTJOdmRXNTBhVzVuTG1OdmJuUmhZM1J6SWl3aWIyWm1iR2x1WlY5aFkyTmxjM01pWFN3aVlXMXlJanBiSW5OemJ5SmRmUS5PNlozdmR5Q0VuZThFQ1I0ZHhxZ0pXbHY1NHVNQ01VNlBEMkNyU0k5Y3Ria25kaXNCMm9fRGxXbHNtNGlJS1lEeU9oTldsbGt0NTFfdTBNMWxvZHNGVDZBZ25TVjZpYmZRWGxjSTkyT0lmZXhIczVIaEFxbVQ5aGpoeF96VElpM0JQbzhQc1FUMEVRdTk4Ym9SNlRUQnJldnMyTjVscFBYcUJ2VVFXSXdGNTVWMEJ6Z0RlYzZHQzhLWG5fOFNudFlpWHB4TWpkOU9yRnlwdjdVVy13TUdkcVYybmtrdmZRSTMzenJnZjU0MVF2NmZoQnVoV2N5NnNvc0F6Yk5yV2luX1pIRU1WcHd2bGRQa2ZOcGxpWXpJNlgyeldzSVA1NjJqX0c3OWZOOGg1ajRzT05kSnczUmJYZ01CMEY4R3ZRS2RXaDNBS21QX0g4bmFTY04taml2WEGUjBNfQXBpQmFzZV9fdGVuYW50X2lklIwkMzZhYjE5MTAtMTFiMy00MzI1LWI1NDUtOGQxMTcwNjY4YWIzlIwUX0FwaUJhc2VfX3NlcnZlcl91cmyUaAx1YowIYWNjb3VudHOUjBV4ZXJvc2RrLmFwaXMuYWNjb3VudHOUjAhBY2NvdW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAhjb250YWN0c5SMFXhlcm9zZGsuYXBpcy5jb250YWN0c5SMCENvbnRhY3RzlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKME3RyYWNraW5nX2NhdGVnb3JpZXOUjCB4ZXJvc2RrLmFwaXMudHJhY2tpbmdfY2F0ZWdvcmllc5SMElRyYWNraW5nQ2F0ZWdvcmllc5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAhwYXltZW50c5SMFXhlcm9zZGsuYXBpcy5wYXltZW50c5SMCFBheW1lbnRzlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKMBWl0ZW1zlIwSeGVyb3Nkay5hcGlzLml0ZW1zlIwFSXRlbXOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowHdGVuYW50c5SMFHhlcm9zZGsuYXBpcy50ZW5hbnRzlIwHVGVuYW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijBFiYW5rX3RyYW5zYWN0aW9uc5SMHnhlcm9zZGsuYXBpcy5iYW5rX3RyYW5zYWN0aW9uc5SMEEJhbmtUcmFuc2FjdGlvbnOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowLYXR0YWNobWVudHOUjBh4ZXJvc2RrLmFwaXMuYXR0YWNobWVudHOUjAtBdHRhY2htZW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijA1vcmdhbmlzYXRpb25zlIwaeGVyb3Nkay5hcGlzLm9yZ2FuaXNhdGlvbnOUjA1PcmdhbmlzYXRpb25zlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKMC2Nvbm5lY3Rpb25zlIwYeGVyb3Nkay5hcGlzLmNvbm5lY3Rpb25zlIwLQ29ubmVjdGlvbnOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowKY3VycmVuY2llc5SMF3hlcm9zZGsuYXBpcy5jdXJyZW5jaWVzlIwKQ3VycmVuY2llc5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAl0YXhfcmF0ZXOUjBZ4ZXJvc2RrLmFwaXMudGF4X3JhdGVzlIwIVGF4UmF0ZXOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowTbGlua2VkX3RyYW5zYWN0aW9uc5SMIHhlcm9zZGsuYXBpcy5saW5rZWRfdHJhbnNhY3Rpb25zlIwSTGlua2VkVHJhbnNhY3Rpb25zlJOUKYGUfZQoaBloGmgbaBxoHWgMdWJ1YowMd29ya3NwYWNlX2lklEsBdWKHlC4=	gAR9lC4=	\N	2022-08-02 20:27:45.127997+00	2022-08-02 20:27:49.119182+00	t	a69119d0d8cb4138b8d392a041f641c6	0afd912e17ff4bb2816bd9dc8349ba01	1	\N
enemy-johnny-rugby-papa	apps.xero.tasks.create_bill	\N	gASVAQsAAAAAAABLAUsEjA9hcHBzLnhlcm8udXRpbHOUjA1YZXJvQ29ubmVjdG9ylJOUKYGUfZQojApjb25uZWN0aW9ulIwPeGVyb3Nkay54ZXJvc2RrlIwHWGVyb1NES5STlCmBlH2UKIwSX1hlcm9TREtfX2Jhc2VfdXJslIwUaHR0cHM6Ly9hcGkueGVyby5jb22UjBNfWGVyb1NES19fY2xpZW50X2lklIwgQkIxMzk0NjdENTQyNEIxNEJFM0RCRjkyODk1RUI2Q0aUjBdfWGVyb1NES19fY2xpZW50X3NlY3JldJSMMDAzTzhiQ0hkQWFfWW56RGhPelVneThNSXo5VGpyRFRQSlVaRzRycVFpYklRWVJncZSMDl9yZWZyZXNoX3Rva2VulIxANDYxMDUwY2NlNDBkMmVlOGM4NzI4NjhlNzNhZWQ1NWRmZTQ2Nzc1N2JkMTZkMGUyMmU4M2Q0YTNlYWQ2Mjg3OJSMCGludm9pY2VzlIwVeGVyb3Nkay5hcGlzLmludm9pY2VzlIwISW52b2ljZXOUk5QpgZR9lCiMFl9BcGlCYXNlX19hY2Nlc3NfdG9rZW6UWOwEAABleUpoYkdjaU9pSlNVekkxTmlJc0ltdHBaQ0k2SWpGRFFVWTRSVFkyTnpjeVJEWkVRekF5T0VRMk56STJSa1F3TWpZeE5UZ3hOVGN3UlVaRE1Ua2lMQ0owZVhBaU9pSktWMVFpTENKNE5YUWlPaUpJU3kxUFdtNWpkR0pqUVc4eGJrcDJNRU5aVm1kV1kwOWZRbXNpZlEuZXlKdVltWWlPakUyTlRrME56SXdOakVzSW1WNGNDSTZNVFkxT1RRM016ZzJNU3dpYVhOeklqb2lhSFIwY0hNNkx5OXBaR1Z1ZEdsMGVTNTRaWEp2TG1OdmJTSXNJbUYxWkNJNkltaDBkSEJ6T2k4dmFXUmxiblJwZEhrdWVHVnlieTVqYjIwdmNtVnpiM1Z5WTJWeklpd2lZMnhwWlc1MFgybGtJam9pUWtJeE16azBOamRFTlRReU5FSXhORUpGTTBSQ1Jqa3lPRGsxUlVJMlEwWWlMQ0p6ZFdJaU9pSTVPVEV6WmpaaVpqUXlNVEkxTmpreU9USmlNemczWW1RelpEWXpaalJrWXlJc0ltRjFkR2hmZEdsdFpTSTZNVFkxT1RRM01UZzROaXdpZUdWeWIxOTFjMlZ5YVdRaU9pSXhOMlU1Tmpsak1DMHpaVFV5TFRSa1pUa3RZV1ZsTVMweU5XWTVNR0ptTkRjME1XUWlMQ0puYkc5aVlXeGZjMlZ6YzJsdmJsOXBaQ0k2SWpNeU1EZGxObUppTXpRNU16UmpZV1k1TUdKbFlqQmtNREU0T1RoaU9HTmpJaXdpYW5ScElqb2lPVFU1TkRoaFlUTTNNRFkwWTJJM01qa3paVEppT1RNNE4yRXlNakppWTJZaUxDSmhkWFJvWlc1MGFXTmhkR2x2Ymw5bGRtVnVkRjlwWkNJNkltSTRZV1V4WTJRMUxUWTVNall0TkRGaU1TMWhaVFF6TFdGaE1UUXdOemc1TkRBM01pSXNJbk5qYjNCbElqcGJJbUZqWTI5MWJuUnBibWN1YzJWMGRHbHVaM01pTENKaFkyTnZkVzUwYVc1bkxtRjBkR0ZqYUcxbGJuUnpJaXdpWVdOamIzVnVkR2x1Wnk1MGNtRnVjMkZqZEdsdmJuTWlMQ0poWTJOdmRXNTBhVzVuTG1OdmJuUmhZM1J6SWl3aWIyWm1iR2x1WlY5aFkyTmxjM01pWFN3aVlXMXlJanBiSW5OemJ5SmRmUS5PNlozdmR5Q0VuZThFQ1I0ZHhxZ0pXbHY1NHVNQ01VNlBEMkNyU0k5Y3Ria25kaXNCMm9fRGxXbHNtNGlJS1lEeU9oTldsbGt0NTFfdTBNMWxvZHNGVDZBZ25TVjZpYmZRWGxjSTkyT0lmZXhIczVIaEFxbVQ5aGpoeF96VElpM0JQbzhQc1FUMEVRdTk4Ym9SNlRUQnJldnMyTjVscFBYcUJ2VVFXSXdGNTVWMEJ6Z0RlYzZHQzhLWG5fOFNudFlpWHB4TWpkOU9yRnlwdjdVVy13TUdkcVYybmtrdmZRSTMzenJnZjU0MVF2NmZoQnVoV2N5NnNvc0F6Yk5yV2luX1pIRU1WcHd2bGRQa2ZOcGxpWXpJNlgyeldzSVA1NjJqX0c3OWZOOGg1ajRzT05kSnczUmJYZ01CMEY4R3ZRS2RXaDNBS21QX0g4bmFTY04taml2WEGUjBNfQXBpQmFzZV9fdGVuYW50X2lklIwkMzZhYjE5MTAtMTFiMy00MzI1LWI1NDUtOGQxMTcwNjY4YWIzlIwUX0FwaUJhc2VfX3NlcnZlcl91cmyUaAx1YowIYWNjb3VudHOUjBV4ZXJvc2RrLmFwaXMuYWNjb3VudHOUjAhBY2NvdW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAhjb250YWN0c5SMFXhlcm9zZGsuYXBpcy5jb250YWN0c5SMCENvbnRhY3RzlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKME3RyYWNraW5nX2NhdGVnb3JpZXOUjCB4ZXJvc2RrLmFwaXMudHJhY2tpbmdfY2F0ZWdvcmllc5SMElRyYWNraW5nQ2F0ZWdvcmllc5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAhwYXltZW50c5SMFXhlcm9zZGsuYXBpcy5wYXltZW50c5SMCFBheW1lbnRzlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKMBWl0ZW1zlIwSeGVyb3Nkay5hcGlzLml0ZW1zlIwFSXRlbXOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowHdGVuYW50c5SMFHhlcm9zZGsuYXBpcy50ZW5hbnRzlIwHVGVuYW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijBFiYW5rX3RyYW5zYWN0aW9uc5SMHnhlcm9zZGsuYXBpcy5iYW5rX3RyYW5zYWN0aW9uc5SMEEJhbmtUcmFuc2FjdGlvbnOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowLYXR0YWNobWVudHOUjBh4ZXJvc2RrLmFwaXMuYXR0YWNobWVudHOUjAtBdHRhY2htZW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijA1vcmdhbmlzYXRpb25zlIwaeGVyb3Nkay5hcGlzLm9yZ2FuaXNhdGlvbnOUjA1PcmdhbmlzYXRpb25zlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKMC2Nvbm5lY3Rpb25zlIwYeGVyb3Nkay5hcGlzLmNvbm5lY3Rpb25zlIwLQ29ubmVjdGlvbnOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowKY3VycmVuY2llc5SMF3hlcm9zZGsuYXBpcy5jdXJyZW5jaWVzlIwKQ3VycmVuY2llc5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAl0YXhfcmF0ZXOUjBZ4ZXJvc2RrLmFwaXMudGF4X3JhdGVzlIwIVGF4UmF0ZXOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowTbGlua2VkX3RyYW5zYWN0aW9uc5SMIHhlcm9zZGsuYXBpcy5saW5rZWRfdHJhbnNhY3Rpb25zlIwSTGlua2VkVHJhbnNhY3Rpb25zlJOUKYGUfZQoaBloGmgbaBxoHWgMdWJ1YowMd29ya3NwYWNlX2lklEsBdWKHlC4=	gAR9lC4=	\N	2022-08-02 20:27:49.123994+00	2022-08-02 20:27:52.195975+00	t	6a42d5c2309c47809fdd2cd3c2a3f933	0afd912e17ff4bb2816bd9dc8349ba01	1	\N
south-stairway-cup-don	apps.xero.tasks.create_bill	\N	gASVAQsAAAAAAABLA0sFjA9hcHBzLnhlcm8udXRpbHOUjA1YZXJvQ29ubmVjdG9ylJOUKYGUfZQojApjb25uZWN0aW9ulIwPeGVyb3Nkay54ZXJvc2RrlIwHWGVyb1NES5STlCmBlH2UKIwSX1hlcm9TREtfX2Jhc2VfdXJslIwUaHR0cHM6Ly9hcGkueGVyby5jb22UjBNfWGVyb1NES19fY2xpZW50X2lklIwgQkIxMzk0NjdENTQyNEIxNEJFM0RCRjkyODk1RUI2Q0aUjBdfWGVyb1NES19fY2xpZW50X3NlY3JldJSMMDAzTzhiQ0hkQWFfWW56RGhPelVneThNSXo5VGpyRFRQSlVaRzRycVFpYklRWVJncZSMDl9yZWZyZXNoX3Rva2VulIxANDYxMDUwY2NlNDBkMmVlOGM4NzI4NjhlNzNhZWQ1NWRmZTQ2Nzc1N2JkMTZkMGUyMmU4M2Q0YTNlYWQ2Mjg3OJSMCGludm9pY2VzlIwVeGVyb3Nkay5hcGlzLmludm9pY2VzlIwISW52b2ljZXOUk5QpgZR9lCiMFl9BcGlCYXNlX19hY2Nlc3NfdG9rZW6UWOwEAABleUpoYkdjaU9pSlNVekkxTmlJc0ltdHBaQ0k2SWpGRFFVWTRSVFkyTnpjeVJEWkVRekF5T0VRMk56STJSa1F3TWpZeE5UZ3hOVGN3UlVaRE1Ua2lMQ0owZVhBaU9pSktWMVFpTENKNE5YUWlPaUpJU3kxUFdtNWpkR0pqUVc4eGJrcDJNRU5aVm1kV1kwOWZRbXNpZlEuZXlKdVltWWlPakUyTlRrME56SXdOakVzSW1WNGNDSTZNVFkxT1RRM016ZzJNU3dpYVhOeklqb2lhSFIwY0hNNkx5OXBaR1Z1ZEdsMGVTNTRaWEp2TG1OdmJTSXNJbUYxWkNJNkltaDBkSEJ6T2k4dmFXUmxiblJwZEhrdWVHVnlieTVqYjIwdmNtVnpiM1Z5WTJWeklpd2lZMnhwWlc1MFgybGtJam9pUWtJeE16azBOamRFTlRReU5FSXhORUpGTTBSQ1Jqa3lPRGsxUlVJMlEwWWlMQ0p6ZFdJaU9pSTVPVEV6WmpaaVpqUXlNVEkxTmpreU9USmlNemczWW1RelpEWXpaalJrWXlJc0ltRjFkR2hmZEdsdFpTSTZNVFkxT1RRM01UZzROaXdpZUdWeWIxOTFjMlZ5YVdRaU9pSXhOMlU1Tmpsak1DMHpaVFV5TFRSa1pUa3RZV1ZsTVMweU5XWTVNR0ptTkRjME1XUWlMQ0puYkc5aVlXeGZjMlZ6YzJsdmJsOXBaQ0k2SWpNeU1EZGxObUppTXpRNU16UmpZV1k1TUdKbFlqQmtNREU0T1RoaU9HTmpJaXdpYW5ScElqb2lPVFU1TkRoaFlUTTNNRFkwWTJJM01qa3paVEppT1RNNE4yRXlNakppWTJZaUxDSmhkWFJvWlc1MGFXTmhkR2x2Ymw5bGRtVnVkRjlwWkNJNkltSTRZV1V4WTJRMUxUWTVNall0TkRGaU1TMWhaVFF6TFdGaE1UUXdOemc1TkRBM01pSXNJbk5qYjNCbElqcGJJbUZqWTI5MWJuUnBibWN1YzJWMGRHbHVaM01pTENKaFkyTnZkVzUwYVc1bkxtRjBkR0ZqYUcxbGJuUnpJaXdpWVdOamIzVnVkR2x1Wnk1MGNtRnVjMkZqZEdsdmJuTWlMQ0poWTJOdmRXNTBhVzVuTG1OdmJuUmhZM1J6SWl3aWIyWm1iR2x1WlY5aFkyTmxjM01pWFN3aVlXMXlJanBiSW5OemJ5SmRmUS5PNlozdmR5Q0VuZThFQ1I0ZHhxZ0pXbHY1NHVNQ01VNlBEMkNyU0k5Y3Ria25kaXNCMm9fRGxXbHNtNGlJS1lEeU9oTldsbGt0NTFfdTBNMWxvZHNGVDZBZ25TVjZpYmZRWGxjSTkyT0lmZXhIczVIaEFxbVQ5aGpoeF96VElpM0JQbzhQc1FUMEVRdTk4Ym9SNlRUQnJldnMyTjVscFBYcUJ2VVFXSXdGNTVWMEJ6Z0RlYzZHQzhLWG5fOFNudFlpWHB4TWpkOU9yRnlwdjdVVy13TUdkcVYybmtrdmZRSTMzenJnZjU0MVF2NmZoQnVoV2N5NnNvc0F6Yk5yV2luX1pIRU1WcHd2bGRQa2ZOcGxpWXpJNlgyeldzSVA1NjJqX0c3OWZOOGg1ajRzT05kSnczUmJYZ01CMEY4R3ZRS2RXaDNBS21QX0g4bmFTY04taml2WEGUjBNfQXBpQmFzZV9fdGVuYW50X2lklIwkMzZhYjE5MTAtMTFiMy00MzI1LWI1NDUtOGQxMTcwNjY4YWIzlIwUX0FwaUJhc2VfX3NlcnZlcl91cmyUaAx1YowIYWNjb3VudHOUjBV4ZXJvc2RrLmFwaXMuYWNjb3VudHOUjAhBY2NvdW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAhjb250YWN0c5SMFXhlcm9zZGsuYXBpcy5jb250YWN0c5SMCENvbnRhY3RzlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKME3RyYWNraW5nX2NhdGVnb3JpZXOUjCB4ZXJvc2RrLmFwaXMudHJhY2tpbmdfY2F0ZWdvcmllc5SMElRyYWNraW5nQ2F0ZWdvcmllc5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAhwYXltZW50c5SMFXhlcm9zZGsuYXBpcy5wYXltZW50c5SMCFBheW1lbnRzlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKMBWl0ZW1zlIwSeGVyb3Nkay5hcGlzLml0ZW1zlIwFSXRlbXOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowHdGVuYW50c5SMFHhlcm9zZGsuYXBpcy50ZW5hbnRzlIwHVGVuYW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijBFiYW5rX3RyYW5zYWN0aW9uc5SMHnhlcm9zZGsuYXBpcy5iYW5rX3RyYW5zYWN0aW9uc5SMEEJhbmtUcmFuc2FjdGlvbnOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowLYXR0YWNobWVudHOUjBh4ZXJvc2RrLmFwaXMuYXR0YWNobWVudHOUjAtBdHRhY2htZW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijA1vcmdhbmlzYXRpb25zlIwaeGVyb3Nkay5hcGlzLm9yZ2FuaXNhdGlvbnOUjA1PcmdhbmlzYXRpb25zlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKMC2Nvbm5lY3Rpb25zlIwYeGVyb3Nkay5hcGlzLmNvbm5lY3Rpb25zlIwLQ29ubmVjdGlvbnOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowKY3VycmVuY2llc5SMF3hlcm9zZGsuYXBpcy5jdXJyZW5jaWVzlIwKQ3VycmVuY2llc5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAl0YXhfcmF0ZXOUjBZ4ZXJvc2RrLmFwaXMudGF4X3JhdGVzlIwIVGF4UmF0ZXOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowTbGlua2VkX3RyYW5zYWN0aW9uc5SMIHhlcm9zZGsuYXBpcy5saW5rZWRfdHJhbnNhY3Rpb25zlIwSTGlua2VkVHJhbnNhY3Rpb25zlJOUKYGUfZQoaBloGmgbaBxoHWgMdWJ1YowMd29ya3NwYWNlX2lklEsBdWKHlC4=	gAR9lC4=	\N	2022-08-02 20:27:52.200721+00	2022-08-02 20:27:55.326271+00	t	db6553221c7c43f09c39109b63f29732	0afd912e17ff4bb2816bd9dc8349ba01	1	\N
network-burger-mountain-paris	apps.xero.tasks.create_bank_transaction	\N	gASVAQsAAAAAAABLCksGjA9hcHBzLnhlcm8udXRpbHOUjA1YZXJvQ29ubmVjdG9ylJOUKYGUfZQojApjb25uZWN0aW9ulIwPeGVyb3Nkay54ZXJvc2RrlIwHWGVyb1NES5STlCmBlH2UKIwSX1hlcm9TREtfX2Jhc2VfdXJslIwUaHR0cHM6Ly9hcGkueGVyby5jb22UjBNfWGVyb1NES19fY2xpZW50X2lklIwgQkIxMzk0NjdENTQyNEIxNEJFM0RCRjkyODk1RUI2Q0aUjBdfWGVyb1NES19fY2xpZW50X3NlY3JldJSMMDAzTzhiQ0hkQWFfWW56RGhPelVneThNSXo5VGpyRFRQSlVaRzRycVFpYklRWVJncZSMDl9yZWZyZXNoX3Rva2VulIxANDYxMDUwY2NlNDBkMmVlOGM4NzI4NjhlNzNhZWQ1NWRmZTQ2Nzc1N2JkMTZkMGUyMmU4M2Q0YTNlYWQ2Mjg3OJSMCGludm9pY2VzlIwVeGVyb3Nkay5hcGlzLmludm9pY2VzlIwISW52b2ljZXOUk5QpgZR9lCiMFl9BcGlCYXNlX19hY2Nlc3NfdG9rZW6UWOwEAABleUpoYkdjaU9pSlNVekkxTmlJc0ltdHBaQ0k2SWpGRFFVWTRSVFkyTnpjeVJEWkVRekF5T0VRMk56STJSa1F3TWpZeE5UZ3hOVGN3UlVaRE1Ua2lMQ0owZVhBaU9pSktWMVFpTENKNE5YUWlPaUpJU3kxUFdtNWpkR0pqUVc4eGJrcDJNRU5aVm1kV1kwOWZRbXNpZlEuZXlKdVltWWlPakUyTlRrME56SXdOakVzSW1WNGNDSTZNVFkxT1RRM016ZzJNU3dpYVhOeklqb2lhSFIwY0hNNkx5OXBaR1Z1ZEdsMGVTNTRaWEp2TG1OdmJTSXNJbUYxWkNJNkltaDBkSEJ6T2k4dmFXUmxiblJwZEhrdWVHVnlieTVqYjIwdmNtVnpiM1Z5WTJWeklpd2lZMnhwWlc1MFgybGtJam9pUWtJeE16azBOamRFTlRReU5FSXhORUpGTTBSQ1Jqa3lPRGsxUlVJMlEwWWlMQ0p6ZFdJaU9pSTVPVEV6WmpaaVpqUXlNVEkxTmpreU9USmlNemczWW1RelpEWXpaalJrWXlJc0ltRjFkR2hmZEdsdFpTSTZNVFkxT1RRM01UZzROaXdpZUdWeWIxOTFjMlZ5YVdRaU9pSXhOMlU1Tmpsak1DMHpaVFV5TFRSa1pUa3RZV1ZsTVMweU5XWTVNR0ptTkRjME1XUWlMQ0puYkc5aVlXeGZjMlZ6YzJsdmJsOXBaQ0k2SWpNeU1EZGxObUppTXpRNU16UmpZV1k1TUdKbFlqQmtNREU0T1RoaU9HTmpJaXdpYW5ScElqb2lPVFU1TkRoaFlUTTNNRFkwWTJJM01qa3paVEppT1RNNE4yRXlNakppWTJZaUxDSmhkWFJvWlc1MGFXTmhkR2x2Ymw5bGRtVnVkRjlwWkNJNkltSTRZV1V4WTJRMUxUWTVNall0TkRGaU1TMWhaVFF6TFdGaE1UUXdOemc1TkRBM01pSXNJbk5qYjNCbElqcGJJbUZqWTI5MWJuUnBibWN1YzJWMGRHbHVaM01pTENKaFkyTnZkVzUwYVc1bkxtRjBkR0ZqYUcxbGJuUnpJaXdpWVdOamIzVnVkR2x1Wnk1MGNtRnVjMkZqZEdsdmJuTWlMQ0poWTJOdmRXNTBhVzVuTG1OdmJuUmhZM1J6SWl3aWIyWm1iR2x1WlY5aFkyTmxjM01pWFN3aVlXMXlJanBiSW5OemJ5SmRmUS5PNlozdmR5Q0VuZThFQ1I0ZHhxZ0pXbHY1NHVNQ01VNlBEMkNyU0k5Y3Ria25kaXNCMm9fRGxXbHNtNGlJS1lEeU9oTldsbGt0NTFfdTBNMWxvZHNGVDZBZ25TVjZpYmZRWGxjSTkyT0lmZXhIczVIaEFxbVQ5aGpoeF96VElpM0JQbzhQc1FUMEVRdTk4Ym9SNlRUQnJldnMyTjVscFBYcUJ2VVFXSXdGNTVWMEJ6Z0RlYzZHQzhLWG5fOFNudFlpWHB4TWpkOU9yRnlwdjdVVy13TUdkcVYybmtrdmZRSTMzenJnZjU0MVF2NmZoQnVoV2N5NnNvc0F6Yk5yV2luX1pIRU1WcHd2bGRQa2ZOcGxpWXpJNlgyeldzSVA1NjJqX0c3OWZOOGg1ajRzT05kSnczUmJYZ01CMEY4R3ZRS2RXaDNBS21QX0g4bmFTY04taml2WEGUjBNfQXBpQmFzZV9fdGVuYW50X2lklIwkMzZhYjE5MTAtMTFiMy00MzI1LWI1NDUtOGQxMTcwNjY4YWIzlIwUX0FwaUJhc2VfX3NlcnZlcl91cmyUaAx1YowIYWNjb3VudHOUjBV4ZXJvc2RrLmFwaXMuYWNjb3VudHOUjAhBY2NvdW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAhjb250YWN0c5SMFXhlcm9zZGsuYXBpcy5jb250YWN0c5SMCENvbnRhY3RzlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKME3RyYWNraW5nX2NhdGVnb3JpZXOUjCB4ZXJvc2RrLmFwaXMudHJhY2tpbmdfY2F0ZWdvcmllc5SMElRyYWNraW5nQ2F0ZWdvcmllc5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAhwYXltZW50c5SMFXhlcm9zZGsuYXBpcy5wYXltZW50c5SMCFBheW1lbnRzlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKMBWl0ZW1zlIwSeGVyb3Nkay5hcGlzLml0ZW1zlIwFSXRlbXOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowHdGVuYW50c5SMFHhlcm9zZGsuYXBpcy50ZW5hbnRzlIwHVGVuYW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijBFiYW5rX3RyYW5zYWN0aW9uc5SMHnhlcm9zZGsuYXBpcy5iYW5rX3RyYW5zYWN0aW9uc5SMEEJhbmtUcmFuc2FjdGlvbnOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowLYXR0YWNobWVudHOUjBh4ZXJvc2RrLmFwaXMuYXR0YWNobWVudHOUjAtBdHRhY2htZW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijA1vcmdhbmlzYXRpb25zlIwaeGVyb3Nkay5hcGlzLm9yZ2FuaXNhdGlvbnOUjA1PcmdhbmlzYXRpb25zlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKMC2Nvbm5lY3Rpb25zlIwYeGVyb3Nkay5hcGlzLmNvbm5lY3Rpb25zlIwLQ29ubmVjdGlvbnOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowKY3VycmVuY2llc5SMF3hlcm9zZGsuYXBpcy5jdXJyZW5jaWVzlIwKQ3VycmVuY2llc5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAl0YXhfcmF0ZXOUjBZ4ZXJvc2RrLmFwaXMudGF4X3JhdGVzlIwIVGF4UmF0ZXOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowTbGlua2VkX3RyYW5zYWN0aW9uc5SMIHhlcm9zZGsuYXBpcy5saW5rZWRfdHJhbnNhY3Rpb25zlIwSTGlua2VkVHJhbnNhY3Rpb25zlJOUKYGUfZQoaBloGmgbaBxoHWgMdWJ1YowMd29ya3NwYWNlX2lklEsBdWKHlC4=	gAR9lC4=	\N	2022-08-02 20:27:55.328159+00	2022-08-02 20:27:59.584045+00	t	c6b542a805f742ac9028bb97bd28f3ca	0afd912e17ff4bb2816bd9dc8349ba01	1	\N
low-carolina-wolfram-nine	apps.xero.tasks.create_bank_transaction	\N	gASVAQsAAAAAAABLBUsHjA9hcHBzLnhlcm8udXRpbHOUjA1YZXJvQ29ubmVjdG9ylJOUKYGUfZQojApjb25uZWN0aW9ulIwPeGVyb3Nkay54ZXJvc2RrlIwHWGVyb1NES5STlCmBlH2UKIwSX1hlcm9TREtfX2Jhc2VfdXJslIwUaHR0cHM6Ly9hcGkueGVyby5jb22UjBNfWGVyb1NES19fY2xpZW50X2lklIwgQkIxMzk0NjdENTQyNEIxNEJFM0RCRjkyODk1RUI2Q0aUjBdfWGVyb1NES19fY2xpZW50X3NlY3JldJSMMDAzTzhiQ0hkQWFfWW56RGhPelVneThNSXo5VGpyRFRQSlVaRzRycVFpYklRWVJncZSMDl9yZWZyZXNoX3Rva2VulIxANDYxMDUwY2NlNDBkMmVlOGM4NzI4NjhlNzNhZWQ1NWRmZTQ2Nzc1N2JkMTZkMGUyMmU4M2Q0YTNlYWQ2Mjg3OJSMCGludm9pY2VzlIwVeGVyb3Nkay5hcGlzLmludm9pY2VzlIwISW52b2ljZXOUk5QpgZR9lCiMFl9BcGlCYXNlX19hY2Nlc3NfdG9rZW6UWOwEAABleUpoYkdjaU9pSlNVekkxTmlJc0ltdHBaQ0k2SWpGRFFVWTRSVFkyTnpjeVJEWkVRekF5T0VRMk56STJSa1F3TWpZeE5UZ3hOVGN3UlVaRE1Ua2lMQ0owZVhBaU9pSktWMVFpTENKNE5YUWlPaUpJU3kxUFdtNWpkR0pqUVc4eGJrcDJNRU5aVm1kV1kwOWZRbXNpZlEuZXlKdVltWWlPakUyTlRrME56SXdOakVzSW1WNGNDSTZNVFkxT1RRM016ZzJNU3dpYVhOeklqb2lhSFIwY0hNNkx5OXBaR1Z1ZEdsMGVTNTRaWEp2TG1OdmJTSXNJbUYxWkNJNkltaDBkSEJ6T2k4dmFXUmxiblJwZEhrdWVHVnlieTVqYjIwdmNtVnpiM1Z5WTJWeklpd2lZMnhwWlc1MFgybGtJam9pUWtJeE16azBOamRFTlRReU5FSXhORUpGTTBSQ1Jqa3lPRGsxUlVJMlEwWWlMQ0p6ZFdJaU9pSTVPVEV6WmpaaVpqUXlNVEkxTmpreU9USmlNemczWW1RelpEWXpaalJrWXlJc0ltRjFkR2hmZEdsdFpTSTZNVFkxT1RRM01UZzROaXdpZUdWeWIxOTFjMlZ5YVdRaU9pSXhOMlU1Tmpsak1DMHpaVFV5TFRSa1pUa3RZV1ZsTVMweU5XWTVNR0ptTkRjME1XUWlMQ0puYkc5aVlXeGZjMlZ6YzJsdmJsOXBaQ0k2SWpNeU1EZGxObUppTXpRNU16UmpZV1k1TUdKbFlqQmtNREU0T1RoaU9HTmpJaXdpYW5ScElqb2lPVFU1TkRoaFlUTTNNRFkwWTJJM01qa3paVEppT1RNNE4yRXlNakppWTJZaUxDSmhkWFJvWlc1MGFXTmhkR2x2Ymw5bGRtVnVkRjlwWkNJNkltSTRZV1V4WTJRMUxUWTVNall0TkRGaU1TMWhaVFF6TFdGaE1UUXdOemc1TkRBM01pSXNJbk5qYjNCbElqcGJJbUZqWTI5MWJuUnBibWN1YzJWMGRHbHVaM01pTENKaFkyTnZkVzUwYVc1bkxtRjBkR0ZqYUcxbGJuUnpJaXdpWVdOamIzVnVkR2x1Wnk1MGNtRnVjMkZqZEdsdmJuTWlMQ0poWTJOdmRXNTBhVzVuTG1OdmJuUmhZM1J6SWl3aWIyWm1iR2x1WlY5aFkyTmxjM01pWFN3aVlXMXlJanBiSW5OemJ5SmRmUS5PNlozdmR5Q0VuZThFQ1I0ZHhxZ0pXbHY1NHVNQ01VNlBEMkNyU0k5Y3Ria25kaXNCMm9fRGxXbHNtNGlJS1lEeU9oTldsbGt0NTFfdTBNMWxvZHNGVDZBZ25TVjZpYmZRWGxjSTkyT0lmZXhIczVIaEFxbVQ5aGpoeF96VElpM0JQbzhQc1FUMEVRdTk4Ym9SNlRUQnJldnMyTjVscFBYcUJ2VVFXSXdGNTVWMEJ6Z0RlYzZHQzhLWG5fOFNudFlpWHB4TWpkOU9yRnlwdjdVVy13TUdkcVYybmtrdmZRSTMzenJnZjU0MVF2NmZoQnVoV2N5NnNvc0F6Yk5yV2luX1pIRU1WcHd2bGRQa2ZOcGxpWXpJNlgyeldzSVA1NjJqX0c3OWZOOGg1ajRzT05kSnczUmJYZ01CMEY4R3ZRS2RXaDNBS21QX0g4bmFTY04taml2WEGUjBNfQXBpQmFzZV9fdGVuYW50X2lklIwkMzZhYjE5MTAtMTFiMy00MzI1LWI1NDUtOGQxMTcwNjY4YWIzlIwUX0FwaUJhc2VfX3NlcnZlcl91cmyUaAx1YowIYWNjb3VudHOUjBV4ZXJvc2RrLmFwaXMuYWNjb3VudHOUjAhBY2NvdW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAhjb250YWN0c5SMFXhlcm9zZGsuYXBpcy5jb250YWN0c5SMCENvbnRhY3RzlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKME3RyYWNraW5nX2NhdGVnb3JpZXOUjCB4ZXJvc2RrLmFwaXMudHJhY2tpbmdfY2F0ZWdvcmllc5SMElRyYWNraW5nQ2F0ZWdvcmllc5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAhwYXltZW50c5SMFXhlcm9zZGsuYXBpcy5wYXltZW50c5SMCFBheW1lbnRzlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKMBWl0ZW1zlIwSeGVyb3Nkay5hcGlzLml0ZW1zlIwFSXRlbXOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowHdGVuYW50c5SMFHhlcm9zZGsuYXBpcy50ZW5hbnRzlIwHVGVuYW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijBFiYW5rX3RyYW5zYWN0aW9uc5SMHnhlcm9zZGsuYXBpcy5iYW5rX3RyYW5zYWN0aW9uc5SMEEJhbmtUcmFuc2FjdGlvbnOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowLYXR0YWNobWVudHOUjBh4ZXJvc2RrLmFwaXMuYXR0YWNobWVudHOUjAtBdHRhY2htZW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijA1vcmdhbmlzYXRpb25zlIwaeGVyb3Nkay5hcGlzLm9yZ2FuaXNhdGlvbnOUjA1PcmdhbmlzYXRpb25zlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKMC2Nvbm5lY3Rpb25zlIwYeGVyb3Nkay5hcGlzLmNvbm5lY3Rpb25zlIwLQ29ubmVjdGlvbnOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowKY3VycmVuY2llc5SMF3hlcm9zZGsuYXBpcy5jdXJyZW5jaWVzlIwKQ3VycmVuY2llc5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAl0YXhfcmF0ZXOUjBZ4ZXJvc2RrLmFwaXMudGF4X3JhdGVzlIwIVGF4UmF0ZXOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowTbGlua2VkX3RyYW5zYWN0aW9uc5SMIHhlcm9zZGsuYXBpcy5saW5rZWRfdHJhbnNhY3Rpb25zlIwSTGlua2VkVHJhbnNhY3Rpb25zlJOUKYGUfZQoaBloGmgbaBxoHWgMdWJ1YowMd29ya3NwYWNlX2lklEsBdWKHlC4=	gAR9lC4=	\N	2022-08-02 20:27:59.590393+00	2022-08-02 20:28:03.880287+00	t	76d1ba630263490991d5cc71a825495f	0afd912e17ff4bb2816bd9dc8349ba01	1	\N
skylark-massachusetts-romeo-virginia	apps.xero.tasks.create_bank_transaction	\N	gASVAQsAAAAAAABLCEsIjA9hcHBzLnhlcm8udXRpbHOUjA1YZXJvQ29ubmVjdG9ylJOUKYGUfZQojApjb25uZWN0aW9ulIwPeGVyb3Nkay54ZXJvc2RrlIwHWGVyb1NES5STlCmBlH2UKIwSX1hlcm9TREtfX2Jhc2VfdXJslIwUaHR0cHM6Ly9hcGkueGVyby5jb22UjBNfWGVyb1NES19fY2xpZW50X2lklIwgQkIxMzk0NjdENTQyNEIxNEJFM0RCRjkyODk1RUI2Q0aUjBdfWGVyb1NES19fY2xpZW50X3NlY3JldJSMMDAzTzhiQ0hkQWFfWW56RGhPelVneThNSXo5VGpyRFRQSlVaRzRycVFpYklRWVJncZSMDl9yZWZyZXNoX3Rva2VulIxANDYxMDUwY2NlNDBkMmVlOGM4NzI4NjhlNzNhZWQ1NWRmZTQ2Nzc1N2JkMTZkMGUyMmU4M2Q0YTNlYWQ2Mjg3OJSMCGludm9pY2VzlIwVeGVyb3Nkay5hcGlzLmludm9pY2VzlIwISW52b2ljZXOUk5QpgZR9lCiMFl9BcGlCYXNlX19hY2Nlc3NfdG9rZW6UWOwEAABleUpoYkdjaU9pSlNVekkxTmlJc0ltdHBaQ0k2SWpGRFFVWTRSVFkyTnpjeVJEWkVRekF5T0VRMk56STJSa1F3TWpZeE5UZ3hOVGN3UlVaRE1Ua2lMQ0owZVhBaU9pSktWMVFpTENKNE5YUWlPaUpJU3kxUFdtNWpkR0pqUVc4eGJrcDJNRU5aVm1kV1kwOWZRbXNpZlEuZXlKdVltWWlPakUyTlRrME56SXdOakVzSW1WNGNDSTZNVFkxT1RRM016ZzJNU3dpYVhOeklqb2lhSFIwY0hNNkx5OXBaR1Z1ZEdsMGVTNTRaWEp2TG1OdmJTSXNJbUYxWkNJNkltaDBkSEJ6T2k4dmFXUmxiblJwZEhrdWVHVnlieTVqYjIwdmNtVnpiM1Z5WTJWeklpd2lZMnhwWlc1MFgybGtJam9pUWtJeE16azBOamRFTlRReU5FSXhORUpGTTBSQ1Jqa3lPRGsxUlVJMlEwWWlMQ0p6ZFdJaU9pSTVPVEV6WmpaaVpqUXlNVEkxTmpreU9USmlNemczWW1RelpEWXpaalJrWXlJc0ltRjFkR2hmZEdsdFpTSTZNVFkxT1RRM01UZzROaXdpZUdWeWIxOTFjMlZ5YVdRaU9pSXhOMlU1Tmpsak1DMHpaVFV5TFRSa1pUa3RZV1ZsTVMweU5XWTVNR0ptTkRjME1XUWlMQ0puYkc5aVlXeGZjMlZ6YzJsdmJsOXBaQ0k2SWpNeU1EZGxObUppTXpRNU16UmpZV1k1TUdKbFlqQmtNREU0T1RoaU9HTmpJaXdpYW5ScElqb2lPVFU1TkRoaFlUTTNNRFkwWTJJM01qa3paVEppT1RNNE4yRXlNakppWTJZaUxDSmhkWFJvWlc1MGFXTmhkR2x2Ymw5bGRtVnVkRjlwWkNJNkltSTRZV1V4WTJRMUxUWTVNall0TkRGaU1TMWhaVFF6TFdGaE1UUXdOemc1TkRBM01pSXNJbk5qYjNCbElqcGJJbUZqWTI5MWJuUnBibWN1YzJWMGRHbHVaM01pTENKaFkyTnZkVzUwYVc1bkxtRjBkR0ZqYUcxbGJuUnpJaXdpWVdOamIzVnVkR2x1Wnk1MGNtRnVjMkZqZEdsdmJuTWlMQ0poWTJOdmRXNTBhVzVuTG1OdmJuUmhZM1J6SWl3aWIyWm1iR2x1WlY5aFkyTmxjM01pWFN3aVlXMXlJanBiSW5OemJ5SmRmUS5PNlozdmR5Q0VuZThFQ1I0ZHhxZ0pXbHY1NHVNQ01VNlBEMkNyU0k5Y3Ria25kaXNCMm9fRGxXbHNtNGlJS1lEeU9oTldsbGt0NTFfdTBNMWxvZHNGVDZBZ25TVjZpYmZRWGxjSTkyT0lmZXhIczVIaEFxbVQ5aGpoeF96VElpM0JQbzhQc1FUMEVRdTk4Ym9SNlRUQnJldnMyTjVscFBYcUJ2VVFXSXdGNTVWMEJ6Z0RlYzZHQzhLWG5fOFNudFlpWHB4TWpkOU9yRnlwdjdVVy13TUdkcVYybmtrdmZRSTMzenJnZjU0MVF2NmZoQnVoV2N5NnNvc0F6Yk5yV2luX1pIRU1WcHd2bGRQa2ZOcGxpWXpJNlgyeldzSVA1NjJqX0c3OWZOOGg1ajRzT05kSnczUmJYZ01CMEY4R3ZRS2RXaDNBS21QX0g4bmFTY04taml2WEGUjBNfQXBpQmFzZV9fdGVuYW50X2lklIwkMzZhYjE5MTAtMTFiMy00MzI1LWI1NDUtOGQxMTcwNjY4YWIzlIwUX0FwaUJhc2VfX3NlcnZlcl91cmyUaAx1YowIYWNjb3VudHOUjBV4ZXJvc2RrLmFwaXMuYWNjb3VudHOUjAhBY2NvdW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAhjb250YWN0c5SMFXhlcm9zZGsuYXBpcy5jb250YWN0c5SMCENvbnRhY3RzlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKME3RyYWNraW5nX2NhdGVnb3JpZXOUjCB4ZXJvc2RrLmFwaXMudHJhY2tpbmdfY2F0ZWdvcmllc5SMElRyYWNraW5nQ2F0ZWdvcmllc5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAhwYXltZW50c5SMFXhlcm9zZGsuYXBpcy5wYXltZW50c5SMCFBheW1lbnRzlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKMBWl0ZW1zlIwSeGVyb3Nkay5hcGlzLml0ZW1zlIwFSXRlbXOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowHdGVuYW50c5SMFHhlcm9zZGsuYXBpcy50ZW5hbnRzlIwHVGVuYW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijBFiYW5rX3RyYW5zYWN0aW9uc5SMHnhlcm9zZGsuYXBpcy5iYW5rX3RyYW5zYWN0aW9uc5SMEEJhbmtUcmFuc2FjdGlvbnOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowLYXR0YWNobWVudHOUjBh4ZXJvc2RrLmFwaXMuYXR0YWNobWVudHOUjAtBdHRhY2htZW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijA1vcmdhbmlzYXRpb25zlIwaeGVyb3Nkay5hcGlzLm9yZ2FuaXNhdGlvbnOUjA1PcmdhbmlzYXRpb25zlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKMC2Nvbm5lY3Rpb25zlIwYeGVyb3Nkay5hcGlzLmNvbm5lY3Rpb25zlIwLQ29ubmVjdGlvbnOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowKY3VycmVuY2llc5SMF3hlcm9zZGsuYXBpcy5jdXJyZW5jaWVzlIwKQ3VycmVuY2llc5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAl0YXhfcmF0ZXOUjBZ4ZXJvc2RrLmFwaXMudGF4X3JhdGVzlIwIVGF4UmF0ZXOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowTbGlua2VkX3RyYW5zYWN0aW9uc5SMIHhlcm9zZGsuYXBpcy5saW5rZWRfdHJhbnNhY3Rpb25zlIwSTGlua2VkVHJhbnNhY3Rpb25zlJOUKYGUfZQoaBloGmgbaBxoHWgMdWJ1YowMd29ya3NwYWNlX2lklEsBdWKHlC4=	gAR9lC4=	\N	2022-08-02 20:28:03.883389+00	2022-08-02 20:28:07.845553+00	t	bc064333d4044a1cbe86f47011bb1842	0afd912e17ff4bb2816bd9dc8349ba01	1	\N
eight-nineteen-fourteen-vegan	apps.xero.tasks.create_bank_transaction	\N	gASVAQsAAAAAAABLBksJjA9hcHBzLnhlcm8udXRpbHOUjA1YZXJvQ29ubmVjdG9ylJOUKYGUfZQojApjb25uZWN0aW9ulIwPeGVyb3Nkay54ZXJvc2RrlIwHWGVyb1NES5STlCmBlH2UKIwSX1hlcm9TREtfX2Jhc2VfdXJslIwUaHR0cHM6Ly9hcGkueGVyby5jb22UjBNfWGVyb1NES19fY2xpZW50X2lklIwgQkIxMzk0NjdENTQyNEIxNEJFM0RCRjkyODk1RUI2Q0aUjBdfWGVyb1NES19fY2xpZW50X3NlY3JldJSMMDAzTzhiQ0hkQWFfWW56RGhPelVneThNSXo5VGpyRFRQSlVaRzRycVFpYklRWVJncZSMDl9yZWZyZXNoX3Rva2VulIxANDYxMDUwY2NlNDBkMmVlOGM4NzI4NjhlNzNhZWQ1NWRmZTQ2Nzc1N2JkMTZkMGUyMmU4M2Q0YTNlYWQ2Mjg3OJSMCGludm9pY2VzlIwVeGVyb3Nkay5hcGlzLmludm9pY2VzlIwISW52b2ljZXOUk5QpgZR9lCiMFl9BcGlCYXNlX19hY2Nlc3NfdG9rZW6UWOwEAABleUpoYkdjaU9pSlNVekkxTmlJc0ltdHBaQ0k2SWpGRFFVWTRSVFkyTnpjeVJEWkVRekF5T0VRMk56STJSa1F3TWpZeE5UZ3hOVGN3UlVaRE1Ua2lMQ0owZVhBaU9pSktWMVFpTENKNE5YUWlPaUpJU3kxUFdtNWpkR0pqUVc4eGJrcDJNRU5aVm1kV1kwOWZRbXNpZlEuZXlKdVltWWlPakUyTlRrME56SXdOakVzSW1WNGNDSTZNVFkxT1RRM016ZzJNU3dpYVhOeklqb2lhSFIwY0hNNkx5OXBaR1Z1ZEdsMGVTNTRaWEp2TG1OdmJTSXNJbUYxWkNJNkltaDBkSEJ6T2k4dmFXUmxiblJwZEhrdWVHVnlieTVqYjIwdmNtVnpiM1Z5WTJWeklpd2lZMnhwWlc1MFgybGtJam9pUWtJeE16azBOamRFTlRReU5FSXhORUpGTTBSQ1Jqa3lPRGsxUlVJMlEwWWlMQ0p6ZFdJaU9pSTVPVEV6WmpaaVpqUXlNVEkxTmpreU9USmlNemczWW1RelpEWXpaalJrWXlJc0ltRjFkR2hmZEdsdFpTSTZNVFkxT1RRM01UZzROaXdpZUdWeWIxOTFjMlZ5YVdRaU9pSXhOMlU1Tmpsak1DMHpaVFV5TFRSa1pUa3RZV1ZsTVMweU5XWTVNR0ptTkRjME1XUWlMQ0puYkc5aVlXeGZjMlZ6YzJsdmJsOXBaQ0k2SWpNeU1EZGxObUppTXpRNU16UmpZV1k1TUdKbFlqQmtNREU0T1RoaU9HTmpJaXdpYW5ScElqb2lPVFU1TkRoaFlUTTNNRFkwWTJJM01qa3paVEppT1RNNE4yRXlNakppWTJZaUxDSmhkWFJvWlc1MGFXTmhkR2x2Ymw5bGRtVnVkRjlwWkNJNkltSTRZV1V4WTJRMUxUWTVNall0TkRGaU1TMWhaVFF6TFdGaE1UUXdOemc1TkRBM01pSXNJbk5qYjNCbElqcGJJbUZqWTI5MWJuUnBibWN1YzJWMGRHbHVaM01pTENKaFkyTnZkVzUwYVc1bkxtRjBkR0ZqYUcxbGJuUnpJaXdpWVdOamIzVnVkR2x1Wnk1MGNtRnVjMkZqZEdsdmJuTWlMQ0poWTJOdmRXNTBhVzVuTG1OdmJuUmhZM1J6SWl3aWIyWm1iR2x1WlY5aFkyTmxjM01pWFN3aVlXMXlJanBiSW5OemJ5SmRmUS5PNlozdmR5Q0VuZThFQ1I0ZHhxZ0pXbHY1NHVNQ01VNlBEMkNyU0k5Y3Ria25kaXNCMm9fRGxXbHNtNGlJS1lEeU9oTldsbGt0NTFfdTBNMWxvZHNGVDZBZ25TVjZpYmZRWGxjSTkyT0lmZXhIczVIaEFxbVQ5aGpoeF96VElpM0JQbzhQc1FUMEVRdTk4Ym9SNlRUQnJldnMyTjVscFBYcUJ2VVFXSXdGNTVWMEJ6Z0RlYzZHQzhLWG5fOFNudFlpWHB4TWpkOU9yRnlwdjdVVy13TUdkcVYybmtrdmZRSTMzenJnZjU0MVF2NmZoQnVoV2N5NnNvc0F6Yk5yV2luX1pIRU1WcHd2bGRQa2ZOcGxpWXpJNlgyeldzSVA1NjJqX0c3OWZOOGg1ajRzT05kSnczUmJYZ01CMEY4R3ZRS2RXaDNBS21QX0g4bmFTY04taml2WEGUjBNfQXBpQmFzZV9fdGVuYW50X2lklIwkMzZhYjE5MTAtMTFiMy00MzI1LWI1NDUtOGQxMTcwNjY4YWIzlIwUX0FwaUJhc2VfX3NlcnZlcl91cmyUaAx1YowIYWNjb3VudHOUjBV4ZXJvc2RrLmFwaXMuYWNjb3VudHOUjAhBY2NvdW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAhjb250YWN0c5SMFXhlcm9zZGsuYXBpcy5jb250YWN0c5SMCENvbnRhY3RzlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKME3RyYWNraW5nX2NhdGVnb3JpZXOUjCB4ZXJvc2RrLmFwaXMudHJhY2tpbmdfY2F0ZWdvcmllc5SMElRyYWNraW5nQ2F0ZWdvcmllc5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAhwYXltZW50c5SMFXhlcm9zZGsuYXBpcy5wYXltZW50c5SMCFBheW1lbnRzlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKMBWl0ZW1zlIwSeGVyb3Nkay5hcGlzLml0ZW1zlIwFSXRlbXOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowHdGVuYW50c5SMFHhlcm9zZGsuYXBpcy50ZW5hbnRzlIwHVGVuYW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijBFiYW5rX3RyYW5zYWN0aW9uc5SMHnhlcm9zZGsuYXBpcy5iYW5rX3RyYW5zYWN0aW9uc5SMEEJhbmtUcmFuc2FjdGlvbnOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowLYXR0YWNobWVudHOUjBh4ZXJvc2RrLmFwaXMuYXR0YWNobWVudHOUjAtBdHRhY2htZW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijA1vcmdhbmlzYXRpb25zlIwaeGVyb3Nkay5hcGlzLm9yZ2FuaXNhdGlvbnOUjA1PcmdhbmlzYXRpb25zlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKMC2Nvbm5lY3Rpb25zlIwYeGVyb3Nkay5hcGlzLmNvbm5lY3Rpb25zlIwLQ29ubmVjdGlvbnOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowKY3VycmVuY2llc5SMF3hlcm9zZGsuYXBpcy5jdXJyZW5jaWVzlIwKQ3VycmVuY2llc5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAl0YXhfcmF0ZXOUjBZ4ZXJvc2RrLmFwaXMudGF4X3JhdGVzlIwIVGF4UmF0ZXOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowTbGlua2VkX3RyYW5zYWN0aW9uc5SMIHhlcm9zZGsuYXBpcy5saW5rZWRfdHJhbnNhY3Rpb25zlIwSTGlua2VkVHJhbnNhY3Rpb25zlJOUKYGUfZQoaBloGmgbaBxoHWgMdWJ1YowMd29ya3NwYWNlX2lklEsBdWKHlC4=	gAR9lC4=	\N	2022-08-02 20:28:07.848471+00	2022-08-02 20:28:11.942022+00	t	7888478cdd724370805a6cfb41619953	0afd912e17ff4bb2816bd9dc8349ba01	1	\N
summer-diet-oxygen-undress	apps.xero.tasks.create_bank_transaction	\N	gASVAQsAAAAAAABLCUsKjA9hcHBzLnhlcm8udXRpbHOUjA1YZXJvQ29ubmVjdG9ylJOUKYGUfZQojApjb25uZWN0aW9ulIwPeGVyb3Nkay54ZXJvc2RrlIwHWGVyb1NES5STlCmBlH2UKIwSX1hlcm9TREtfX2Jhc2VfdXJslIwUaHR0cHM6Ly9hcGkueGVyby5jb22UjBNfWGVyb1NES19fY2xpZW50X2lklIwgQkIxMzk0NjdENTQyNEIxNEJFM0RCRjkyODk1RUI2Q0aUjBdfWGVyb1NES19fY2xpZW50X3NlY3JldJSMMDAzTzhiQ0hkQWFfWW56RGhPelVneThNSXo5VGpyRFRQSlVaRzRycVFpYklRWVJncZSMDl9yZWZyZXNoX3Rva2VulIxANDYxMDUwY2NlNDBkMmVlOGM4NzI4NjhlNzNhZWQ1NWRmZTQ2Nzc1N2JkMTZkMGUyMmU4M2Q0YTNlYWQ2Mjg3OJSMCGludm9pY2VzlIwVeGVyb3Nkay5hcGlzLmludm9pY2VzlIwISW52b2ljZXOUk5QpgZR9lCiMFl9BcGlCYXNlX19hY2Nlc3NfdG9rZW6UWOwEAABleUpoYkdjaU9pSlNVekkxTmlJc0ltdHBaQ0k2SWpGRFFVWTRSVFkyTnpjeVJEWkVRekF5T0VRMk56STJSa1F3TWpZeE5UZ3hOVGN3UlVaRE1Ua2lMQ0owZVhBaU9pSktWMVFpTENKNE5YUWlPaUpJU3kxUFdtNWpkR0pqUVc4eGJrcDJNRU5aVm1kV1kwOWZRbXNpZlEuZXlKdVltWWlPakUyTlRrME56SXdOakVzSW1WNGNDSTZNVFkxT1RRM016ZzJNU3dpYVhOeklqb2lhSFIwY0hNNkx5OXBaR1Z1ZEdsMGVTNTRaWEp2TG1OdmJTSXNJbUYxWkNJNkltaDBkSEJ6T2k4dmFXUmxiblJwZEhrdWVHVnlieTVqYjIwdmNtVnpiM1Z5WTJWeklpd2lZMnhwWlc1MFgybGtJam9pUWtJeE16azBOamRFTlRReU5FSXhORUpGTTBSQ1Jqa3lPRGsxUlVJMlEwWWlMQ0p6ZFdJaU9pSTVPVEV6WmpaaVpqUXlNVEkxTmpreU9USmlNemczWW1RelpEWXpaalJrWXlJc0ltRjFkR2hmZEdsdFpTSTZNVFkxT1RRM01UZzROaXdpZUdWeWIxOTFjMlZ5YVdRaU9pSXhOMlU1Tmpsak1DMHpaVFV5TFRSa1pUa3RZV1ZsTVMweU5XWTVNR0ptTkRjME1XUWlMQ0puYkc5aVlXeGZjMlZ6YzJsdmJsOXBaQ0k2SWpNeU1EZGxObUppTXpRNU16UmpZV1k1TUdKbFlqQmtNREU0T1RoaU9HTmpJaXdpYW5ScElqb2lPVFU1TkRoaFlUTTNNRFkwWTJJM01qa3paVEppT1RNNE4yRXlNakppWTJZaUxDSmhkWFJvWlc1MGFXTmhkR2x2Ymw5bGRtVnVkRjlwWkNJNkltSTRZV1V4WTJRMUxUWTVNall0TkRGaU1TMWhaVFF6TFdGaE1UUXdOemc1TkRBM01pSXNJbk5qYjNCbElqcGJJbUZqWTI5MWJuUnBibWN1YzJWMGRHbHVaM01pTENKaFkyTnZkVzUwYVc1bkxtRjBkR0ZqYUcxbGJuUnpJaXdpWVdOamIzVnVkR2x1Wnk1MGNtRnVjMkZqZEdsdmJuTWlMQ0poWTJOdmRXNTBhVzVuTG1OdmJuUmhZM1J6SWl3aWIyWm1iR2x1WlY5aFkyTmxjM01pWFN3aVlXMXlJanBiSW5OemJ5SmRmUS5PNlozdmR5Q0VuZThFQ1I0ZHhxZ0pXbHY1NHVNQ01VNlBEMkNyU0k5Y3Ria25kaXNCMm9fRGxXbHNtNGlJS1lEeU9oTldsbGt0NTFfdTBNMWxvZHNGVDZBZ25TVjZpYmZRWGxjSTkyT0lmZXhIczVIaEFxbVQ5aGpoeF96VElpM0JQbzhQc1FUMEVRdTk4Ym9SNlRUQnJldnMyTjVscFBYcUJ2VVFXSXdGNTVWMEJ6Z0RlYzZHQzhLWG5fOFNudFlpWHB4TWpkOU9yRnlwdjdVVy13TUdkcVYybmtrdmZRSTMzenJnZjU0MVF2NmZoQnVoV2N5NnNvc0F6Yk5yV2luX1pIRU1WcHd2bGRQa2ZOcGxpWXpJNlgyeldzSVA1NjJqX0c3OWZOOGg1ajRzT05kSnczUmJYZ01CMEY4R3ZRS2RXaDNBS21QX0g4bmFTY04taml2WEGUjBNfQXBpQmFzZV9fdGVuYW50X2lklIwkMzZhYjE5MTAtMTFiMy00MzI1LWI1NDUtOGQxMTcwNjY4YWIzlIwUX0FwaUJhc2VfX3NlcnZlcl91cmyUaAx1YowIYWNjb3VudHOUjBV4ZXJvc2RrLmFwaXMuYWNjb3VudHOUjAhBY2NvdW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAhjb250YWN0c5SMFXhlcm9zZGsuYXBpcy5jb250YWN0c5SMCENvbnRhY3RzlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKME3RyYWNraW5nX2NhdGVnb3JpZXOUjCB4ZXJvc2RrLmFwaXMudHJhY2tpbmdfY2F0ZWdvcmllc5SMElRyYWNraW5nQ2F0ZWdvcmllc5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAhwYXltZW50c5SMFXhlcm9zZGsuYXBpcy5wYXltZW50c5SMCFBheW1lbnRzlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKMBWl0ZW1zlIwSeGVyb3Nkay5hcGlzLml0ZW1zlIwFSXRlbXOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowHdGVuYW50c5SMFHhlcm9zZGsuYXBpcy50ZW5hbnRzlIwHVGVuYW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijBFiYW5rX3RyYW5zYWN0aW9uc5SMHnhlcm9zZGsuYXBpcy5iYW5rX3RyYW5zYWN0aW9uc5SMEEJhbmtUcmFuc2FjdGlvbnOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowLYXR0YWNobWVudHOUjBh4ZXJvc2RrLmFwaXMuYXR0YWNobWVudHOUjAtBdHRhY2htZW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijA1vcmdhbmlzYXRpb25zlIwaeGVyb3Nkay5hcGlzLm9yZ2FuaXNhdGlvbnOUjA1PcmdhbmlzYXRpb25zlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKMC2Nvbm5lY3Rpb25zlIwYeGVyb3Nkay5hcGlzLmNvbm5lY3Rpb25zlIwLQ29ubmVjdGlvbnOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowKY3VycmVuY2llc5SMF3hlcm9zZGsuYXBpcy5jdXJyZW5jaWVzlIwKQ3VycmVuY2llc5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAl0YXhfcmF0ZXOUjBZ4ZXJvc2RrLmFwaXMudGF4X3JhdGVzlIwIVGF4UmF0ZXOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowTbGlua2VkX3RyYW5zYWN0aW9uc5SMIHhlcm9zZGsuYXBpcy5saW5rZWRfdHJhbnNhY3Rpb25zlIwSTGlua2VkVHJhbnNhY3Rpb25zlJOUKYGUfZQoaBloGmgbaBxoHWgMdWJ1YowMd29ya3NwYWNlX2lklEsBdWKHlC4=	gAR9lC4=	\N	2022-08-02 20:28:11.9439+00	2022-08-02 20:28:16.30644+00	t	71f26c39521e453aa6210e2397bc428f	0afd912e17ff4bb2816bd9dc8349ba01	1	\N
rugby-kansas-berlin-moon	apps.xero.tasks.create_bank_transaction	\N	gASVAQsAAAAAAABLB0sLjA9hcHBzLnhlcm8udXRpbHOUjA1YZXJvQ29ubmVjdG9ylJOUKYGUfZQojApjb25uZWN0aW9ulIwPeGVyb3Nkay54ZXJvc2RrlIwHWGVyb1NES5STlCmBlH2UKIwSX1hlcm9TREtfX2Jhc2VfdXJslIwUaHR0cHM6Ly9hcGkueGVyby5jb22UjBNfWGVyb1NES19fY2xpZW50X2lklIwgQkIxMzk0NjdENTQyNEIxNEJFM0RCRjkyODk1RUI2Q0aUjBdfWGVyb1NES19fY2xpZW50X3NlY3JldJSMMDAzTzhiQ0hkQWFfWW56RGhPelVneThNSXo5VGpyRFRQSlVaRzRycVFpYklRWVJncZSMDl9yZWZyZXNoX3Rva2VulIxANDYxMDUwY2NlNDBkMmVlOGM4NzI4NjhlNzNhZWQ1NWRmZTQ2Nzc1N2JkMTZkMGUyMmU4M2Q0YTNlYWQ2Mjg3OJSMCGludm9pY2VzlIwVeGVyb3Nkay5hcGlzLmludm9pY2VzlIwISW52b2ljZXOUk5QpgZR9lCiMFl9BcGlCYXNlX19hY2Nlc3NfdG9rZW6UWOwEAABleUpoYkdjaU9pSlNVekkxTmlJc0ltdHBaQ0k2SWpGRFFVWTRSVFkyTnpjeVJEWkVRekF5T0VRMk56STJSa1F3TWpZeE5UZ3hOVGN3UlVaRE1Ua2lMQ0owZVhBaU9pSktWMVFpTENKNE5YUWlPaUpJU3kxUFdtNWpkR0pqUVc4eGJrcDJNRU5aVm1kV1kwOWZRbXNpZlEuZXlKdVltWWlPakUyTlRrME56SXdOakVzSW1WNGNDSTZNVFkxT1RRM016ZzJNU3dpYVhOeklqb2lhSFIwY0hNNkx5OXBaR1Z1ZEdsMGVTNTRaWEp2TG1OdmJTSXNJbUYxWkNJNkltaDBkSEJ6T2k4dmFXUmxiblJwZEhrdWVHVnlieTVqYjIwdmNtVnpiM1Z5WTJWeklpd2lZMnhwWlc1MFgybGtJam9pUWtJeE16azBOamRFTlRReU5FSXhORUpGTTBSQ1Jqa3lPRGsxUlVJMlEwWWlMQ0p6ZFdJaU9pSTVPVEV6WmpaaVpqUXlNVEkxTmpreU9USmlNemczWW1RelpEWXpaalJrWXlJc0ltRjFkR2hmZEdsdFpTSTZNVFkxT1RRM01UZzROaXdpZUdWeWIxOTFjMlZ5YVdRaU9pSXhOMlU1Tmpsak1DMHpaVFV5TFRSa1pUa3RZV1ZsTVMweU5XWTVNR0ptTkRjME1XUWlMQ0puYkc5aVlXeGZjMlZ6YzJsdmJsOXBaQ0k2SWpNeU1EZGxObUppTXpRNU16UmpZV1k1TUdKbFlqQmtNREU0T1RoaU9HTmpJaXdpYW5ScElqb2lPVFU1TkRoaFlUTTNNRFkwWTJJM01qa3paVEppT1RNNE4yRXlNakppWTJZaUxDSmhkWFJvWlc1MGFXTmhkR2x2Ymw5bGRtVnVkRjlwWkNJNkltSTRZV1V4WTJRMUxUWTVNall0TkRGaU1TMWhaVFF6TFdGaE1UUXdOemc1TkRBM01pSXNJbk5qYjNCbElqcGJJbUZqWTI5MWJuUnBibWN1YzJWMGRHbHVaM01pTENKaFkyTnZkVzUwYVc1bkxtRjBkR0ZqYUcxbGJuUnpJaXdpWVdOamIzVnVkR2x1Wnk1MGNtRnVjMkZqZEdsdmJuTWlMQ0poWTJOdmRXNTBhVzVuTG1OdmJuUmhZM1J6SWl3aWIyWm1iR2x1WlY5aFkyTmxjM01pWFN3aVlXMXlJanBiSW5OemJ5SmRmUS5PNlozdmR5Q0VuZThFQ1I0ZHhxZ0pXbHY1NHVNQ01VNlBEMkNyU0k5Y3Ria25kaXNCMm9fRGxXbHNtNGlJS1lEeU9oTldsbGt0NTFfdTBNMWxvZHNGVDZBZ25TVjZpYmZRWGxjSTkyT0lmZXhIczVIaEFxbVQ5aGpoeF96VElpM0JQbzhQc1FUMEVRdTk4Ym9SNlRUQnJldnMyTjVscFBYcUJ2VVFXSXdGNTVWMEJ6Z0RlYzZHQzhLWG5fOFNudFlpWHB4TWpkOU9yRnlwdjdVVy13TUdkcVYybmtrdmZRSTMzenJnZjU0MVF2NmZoQnVoV2N5NnNvc0F6Yk5yV2luX1pIRU1WcHd2bGRQa2ZOcGxpWXpJNlgyeldzSVA1NjJqX0c3OWZOOGg1ajRzT05kSnczUmJYZ01CMEY4R3ZRS2RXaDNBS21QX0g4bmFTY04taml2WEGUjBNfQXBpQmFzZV9fdGVuYW50X2lklIwkMzZhYjE5MTAtMTFiMy00MzI1LWI1NDUtOGQxMTcwNjY4YWIzlIwUX0FwaUJhc2VfX3NlcnZlcl91cmyUaAx1YowIYWNjb3VudHOUjBV4ZXJvc2RrLmFwaXMuYWNjb3VudHOUjAhBY2NvdW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAhjb250YWN0c5SMFXhlcm9zZGsuYXBpcy5jb250YWN0c5SMCENvbnRhY3RzlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKME3RyYWNraW5nX2NhdGVnb3JpZXOUjCB4ZXJvc2RrLmFwaXMudHJhY2tpbmdfY2F0ZWdvcmllc5SMElRyYWNraW5nQ2F0ZWdvcmllc5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAhwYXltZW50c5SMFXhlcm9zZGsuYXBpcy5wYXltZW50c5SMCFBheW1lbnRzlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKMBWl0ZW1zlIwSeGVyb3Nkay5hcGlzLml0ZW1zlIwFSXRlbXOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowHdGVuYW50c5SMFHhlcm9zZGsuYXBpcy50ZW5hbnRzlIwHVGVuYW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijBFiYW5rX3RyYW5zYWN0aW9uc5SMHnhlcm9zZGsuYXBpcy5iYW5rX3RyYW5zYWN0aW9uc5SMEEJhbmtUcmFuc2FjdGlvbnOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowLYXR0YWNobWVudHOUjBh4ZXJvc2RrLmFwaXMuYXR0YWNobWVudHOUjAtBdHRhY2htZW50c5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijA1vcmdhbmlzYXRpb25zlIwaeGVyb3Nkay5hcGlzLm9yZ2FuaXNhdGlvbnOUjA1PcmdhbmlzYXRpb25zlJOUKYGUfZQoaBloGmgbaBxoHWgMdWKMC2Nvbm5lY3Rpb25zlIwYeGVyb3Nkay5hcGlzLmNvbm5lY3Rpb25zlIwLQ29ubmVjdGlvbnOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowKY3VycmVuY2llc5SMF3hlcm9zZGsuYXBpcy5jdXJyZW5jaWVzlIwKQ3VycmVuY2llc5STlCmBlH2UKGgZaBpoG2gcaB1oDHVijAl0YXhfcmF0ZXOUjBZ4ZXJvc2RrLmFwaXMudGF4X3JhdGVzlIwIVGF4UmF0ZXOUk5QpgZR9lChoGWgaaBtoHGgdaAx1YowTbGlua2VkX3RyYW5zYWN0aW9uc5SMIHhlcm9zZGsuYXBpcy5saW5rZWRfdHJhbnNhY3Rpb25zlIwSTGlua2VkVHJhbnNhY3Rpb25zlJOUKYGUfZQoaBloGmgbaBxoHWgMdWJ1YowMd29ya3NwYWNlX2lklEsBdWKHlC4=	gAR9lC4=	\N	2022-08-02 20:28:16.309321+00	2022-08-02 20:28:20.223386+00	t	a0c67ca76f8a4ac08fb05c77ad7e0747	0afd912e17ff4bb2816bd9dc8349ba01	1	\N
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
\.


--
-- Data for Name: employee_mappings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.employee_mappings (id, created_at, updated_at, destination_card_account_id, destination_employee_id, destination_vendor_id, source_employee_id, workspace_id) FROM stdin;
\.


--
-- Data for Name: errors; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.errors (id, type, is_resolved, error_title, error_detail, created_at, updated_at, expense_attribute_id, expense_group_id, workspace_id) FROM stdin;
18	CATEGORY_MAPPING	t	Software	Category mapping is missing	2022-05-23 13:01:02.210349+00	2022-05-23 13:01:59.787365+00	112	\N	1
\.


--
-- Data for Name: expense_attributes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expense_attributes (id, attribute_type, display_name, value, source_id, created_at, updated_at, workspace_id, active, detail, auto_mapped, auto_created) FROM stdin;
22	CATEGORY	Category	Entertainment	46633	2022-08-02 20:25:06.616442+00	2022-08-02 20:25:06.616486+00	1	\N	\N	t	f
2	EMPLOYEE	Employee	shwetabh.kumar@fyle.in	ouIed37iMcs8	2022-08-02 20:25:06.273541+00	2022-08-02 20:25:06.273637+00	1	\N	{"user_id": "usLwhr0RljRQ", "location": null, "full_name": "Shwetabh Kumar", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
3	EMPLOYEE	Employee	shekhar.c@fylehq.com	ouM3r6PNVIOU	2022-08-02 20:25:06.273747+00	2022-08-02 20:25:06.273778+00	1	\N	{"user_id": "usyXTHFwpO3a", "location": null, "full_name": "Shekhar Chatterjee", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
4	EMPLOYEE	Employee	shekhar.c@fyle.in	ouqGj35zUG8K	2022-08-02 20:25:06.273852+00	2022-08-02 20:25:06.273874+00	1	\N	{"user_id": "usw44tkoKUte", "location": null, "full_name": "Shekhar", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
5	EMPLOYEE	Employee	ashwin.t+4@fyle.in	ouYexI2bk7yN	2022-08-02 20:25:06.273952+00	2022-08-02 20:25:06.273981+00	1	\N	{"user_id": "uswAZ4ET3tpk", "location": null, "full_name": "ash4", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
6	EMPLOYEE	Employee	ashwin.t+3@fyle.in	ou20iqY6vwWh	2022-08-02 20:25:06.274058+00	2022-08-02 20:25:06.274087+00	1	\N	{"user_id": "ushWdvf4s39k", "location": null, "full_name": "ashwin3", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
7	EMPLOYEE	Employee	ashwin.t+1@fyle.in	ouRrASCp53an	2022-08-02 20:25:06.274161+00	2022-08-02 20:25:06.27419+00	1	\N	{"user_id": "usn8BEPzrzWl", "location": null, "full_name": "Bahubali", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
23	CATEGORY	Category	Interest Expense	121904	2022-08-02 20:25:06.616559+00	2022-08-02 20:25:06.616589+00	1	\N	\N	t	f
9	EMPLOYEE	Employee	vikas.prasad@fyle.in	oulKrC1lPwUa	2022-08-02 20:25:06.27438+00	2022-08-02 20:25:06.274409+00	1	\N	{"user_id": "us1oIx15QhHE", "location": null, "full_name": "vikas prasad", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
10	EMPLOYEE	Employee	arun.tvs@fyle.in	ouyf10hfUkrB	2022-08-02 20:25:06.274482+00	2022-08-02 20:25:06.274511+00	1	\N	{"user_id": "usEyHSLj6aHw", "location": null, "full_name": "kk", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
11	EMPLOYEE	Employee	vishal.soni@fyle.in	ouxbvvn08v3j	2022-08-02 20:25:06.274583+00	2022-08-02 20:25:06.274612+00	1	\N	{"user_id": "us2KlecXw6Yv", "location": null, "full_name": "Vishal Soni", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
12	EMPLOYEE	Employee	suhas.s@fyle.in	ouJymhJAj1pP	2022-08-02 20:25:06.274684+00	2022-08-02 20:25:06.274713+00	1	\N	{"user_id": "usBptJrudTJK", "location": null, "full_name": "u2", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
13	EMPLOYEE	Employee	suhas.s+323@fyle.in	ouoxULQNa50M	2022-08-02 20:25:06.274785+00	2022-08-02 20:25:06.274814+00	1	\N	{"user_id": "usKZ1egF4j9t", "location": null, "full_name": "u1", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
14	EMPLOYEE	Employee	rum_pel_stilt_skin@fyle.in	ouYrnCH2A9ov	2022-08-02 20:25:06.274886+00	2022-08-02 20:25:06.274915+00	1	\N	{"user_id": "usb4kCXRoWWV", "location": null, "full_name": "Vikas Prasad", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
15	EMPLOYEE	Employee	namrata.khandelwal@fyle.in	ouwzfXPsXZL5	2022-08-02 20:25:06.274986+00	2022-08-02 20:25:06.275016+00	1	\N	{"user_id": "usHMAxZPKcvU", "location": null, "full_name": "Namrata", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
16	EMPLOYEE	Employee	chetanya.shrimalie@fyle.in	oukes8HPOm0r	2022-08-02 20:25:06.275087+00	2022-08-02 20:25:06.275117+00	1	\N	{"user_id": "usDYUlKsY3TQ", "location": null, "full_name": "Chetanya Shrimalie - long name text here, very long name, some name. can you still l see this name?", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
17	EMPLOYEE	Employee	priyanka.shishodia@fyle.in	ouUmpzDJhbnz	2022-08-02 20:25:06.275187+00	2022-08-02 20:25:06.275217+00	1	\N	{"user_id": "usd8u4WZ3o0w", "location": null, "full_name": "P S", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
18	EMPLOYEE	Employee	shreyas.kashyap@fyle.in	ou4mg1ZJhFmj	2022-08-02 20:25:06.275288+00	2022-08-02 20:25:06.275317+00	1	\N	{"user_id": "us5MFRanyObO", "location": null, "full_name": "Shrey", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
19	EMPLOYEE	Employee	ironman@fyle.in	oukceqsSZCgw	2022-08-02 20:25:06.275387+00	2022-08-02 20:25:06.275416+00	1	\N	{"user_id": "ussmkbBFTmvb", "location": null, "full_name": "Tony Stark", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
20	EMPLOYEE	Employee	jasmine@fyle.in	ouyevF66s7P3	2022-08-02 20:25:06.275486+00	2022-08-02 20:25:06.275515+00	1	\N	{"user_id": "useuTXEBAeop", "location": null, "full_name": "Jamine", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
21	EMPLOYEE	Employee	keith@fyle.in	oudvKqt9DnJX	2022-08-02 20:25:06.275586+00	2022-08-02 20:25:06.275615+00	1	\N	{"user_id": "ushRaRjU4eFM", "location": null, "full_name": "Keith", "department": null, "department_id": null, "employee_code": null, "department_code": null}	f	f
24	CATEGORY	Category	Purchases	121905	2022-08-02 20:25:06.616653+00	2022-08-02 20:25:06.616682+00	1	\N	\N	t	f
25	CATEGORY	Category	Advertising	123385	2022-08-02 20:25:06.616745+00	2022-08-02 20:25:06.616774+00	1	\N	\N	t	f
26	CATEGORY	Category	Insurance	123393	2022-08-02 20:25:06.616937+00	2022-08-02 20:25:06.616975+00	1	\N	\N	t	f
29	CATEGORY	Category	Rent	124273	2022-08-02 20:25:06.617228+00	2022-08-02 20:25:06.617258+00	1	\N	\N	t	f
51	CATEGORY	Category	Activity	46627	2022-08-02 20:25:06.620628+00	2022-08-02 20:25:06.620656+00	1	\N	\N	f	f
52	CATEGORY	Category	Train	46628	2022-08-02 20:25:06.620713+00	2022-08-02 20:25:06.620741+00	1	\N	\N	f	f
53	CATEGORY	Category	Fuel	46629	2022-08-02 20:25:06.620798+00	2022-08-02 20:25:06.620825+00	1	\N	\N	f	f
54	CATEGORY	Category	Snacks	46630	2022-08-02 20:25:06.620882+00	2022-08-02 20:25:06.620909+00	1	\N	\N	f	f
55	CATEGORY	Category	Office Supplies	46631	2022-08-02 20:25:06.620966+00	2022-08-02 20:25:06.620993+00	1	\N	\N	f	f
56	CATEGORY	Category	Utility	46632	2022-08-02 20:25:06.62105+00	2022-08-02 20:25:06.621077+00	1	\N	\N	f	f
57	CATEGORY	Category	Others	46634	2022-08-02 20:25:06.621134+00	2022-08-02 20:25:06.621161+00	1	\N	\N	f	f
58	CATEGORY	Category	Mileage	46635	2022-08-02 20:25:06.621319+00	2022-08-02 20:25:06.621348+00	1	\N	\N	f	f
59	CATEGORY	Category	Food	46636	2022-08-02 20:25:06.621417+00	2022-08-02 20:25:06.621438+00	1	\N	\N	f	f
60	CATEGORY	Category	Per Diem	46637	2022-08-02 20:25:06.621642+00	2022-08-02 20:25:06.621838+00	1	\N	\N	f	f
61	CATEGORY	Category	Bus	46638	2022-08-02 20:25:06.621896+00	2022-08-02 20:25:06.621923+00	1	\N	\N	f	f
62	CATEGORY	Category	Internet	46639	2022-08-02 20:25:06.621979+00	2022-08-02 20:25:06.622006+00	1	\N	\N	f	f
63	CATEGORY	Category	Courier	46641	2022-08-02 20:25:06.622063+00	2022-08-02 20:25:06.62209+00	1	\N	\N	f	f
64	CATEGORY	Category	Hotel	46642	2022-08-02 20:25:06.622157+00	2022-08-02 20:25:06.622287+00	1	\N	\N	f	f
65	CATEGORY	Category	Professional Services	46643	2022-08-02 20:25:06.622406+00	2022-08-02 20:25:06.622439+00	1	\N	\N	f	f
66	CATEGORY	Category	Phone	46644	2022-08-02 20:25:06.622503+00	2022-08-02 20:25:06.622532+00	1	\N	\N	f	f
67	CATEGORY	Category	Office Party	46645	2022-08-02 20:25:06.622596+00	2022-08-02 20:25:06.622628+00	1	\N	\N	f	f
68	CATEGORY	Category	Flight	46646	2022-08-02 20:25:06.622693+00	2022-08-02 20:25:06.622723+00	1	\N	\N	f	f
69	CATEGORY	Category	Software	46647	2022-08-02 20:25:06.622787+00	2022-08-02 20:25:06.622816+00	1	\N	\N	f	f
70	CATEGORY	Category	Parking	46648	2022-08-02 20:25:06.622877+00	2022-08-02 20:25:06.622906+00	1	\N	\N	f	f
71	CATEGORY	Category	Toll Charge	46649	2022-08-02 20:25:06.622967+00	2022-08-02 20:25:06.622996+00	1	\N	\N	f	f
72	CATEGORY	Category	Tax	46650	2022-08-02 20:25:06.63579+00	2022-08-02 20:25:06.635833+00	1	\N	\N	f	f
73	CATEGORY	Category	Training	46651	2022-08-02 20:25:06.635903+00	2022-08-02 20:25:06.635932+00	1	\N	\N	f	f
74	CATEGORY	Category	Unspecified	46652	2022-08-02 20:25:06.636026+00	2022-08-02 20:25:06.636056+00	1	\N	\N	f	f
75	CATEGORY	Category	Meals	123414	2022-08-02 20:25:06.63612+00	2022-08-02 20:25:06.636149+00	1	\N	\N	f	f
76	CATEGORY	Category	Airfare	124118	2022-08-02 20:25:06.63621+00	2022-08-02 20:25:06.636364+00	1	\N	\N	f	f
77	CATEGORY	Category	Equipment	124119	2022-08-02 20:25:06.636485+00	2022-08-02 20:25:06.636514+00	1	\N	\N	f	f
78	CATEGORY	Category	Cell phone	124120	2022-08-02 20:25:06.636572+00	2022-08-02 20:25:06.636599+00	1	\N	\N	f	f
79	CATEGORY	Category	Description about 00	124121	2022-08-02 20:25:06.636656+00	2022-08-02 20:25:06.636684+00	1	\N	\N	f	f
80	CATEGORY	Category	Description about ASHWIN MANUALLY ADDED THIS	124131	2022-08-02 20:25:06.636741+00	2022-08-02 20:25:06.636768+00	1	\N	\N	f	f
81	CATEGORY	Category	Description about ASHWIN MANUALLY ADDED THIS2	124132	2022-08-02 20:25:06.636825+00	2022-08-02 20:25:06.636852+00	1	\N	\N	f	f
82	CATEGORY	Category	Travel Expenses	124158	2022-08-02 20:25:06.636909+00	2022-08-02 20:25:06.636936+00	1	\N	\N	f	f
83	CATEGORY	Category	Travel Expenses which supports National - International	124169	2022-08-02 20:25:06.636992+00	2022-08-02 20:25:06.63702+00	1	\N	\N	f	f
84	CATEGORY	Category	Accounts Receivable	124337	2022-08-02 20:25:06.637076+00	2022-08-02 20:25:06.637103+00	1	\N	\N	f	f
85	CATEGORY	Category	Accounts Payable	124340	2022-08-02 20:25:06.63716+00	2022-08-02 20:25:06.637187+00	1	\N	\N	f	f
86	CATEGORY	Category	Accounts Payable - Employees	124341	2022-08-02 20:25:06.637366+00	2022-08-02 20:25:06.637392+00	1	\N	\N	f	f
87	CATEGORY	Category	Furniture for the department	141037	2022-08-02 20:25:06.63747+00	2022-08-02 20:25:06.637498+00	1	\N	\N	f	f
88	CATEGORY	Category	test	141038	2022-08-02 20:25:06.637555+00	2022-08-02 20:25:06.637582+00	1	\N	\N	f	f
89	CATEGORY	Category	Netflix	148767	2022-08-02 20:25:06.637638+00	2022-08-02 20:25:06.637665+00	1	\N	\N	f	f
90	CATEGORY	Category	Emma	148768	2022-08-02 20:25:06.637722+00	2022-08-02 20:25:06.63775+00	1	\N	\N	f	f
91	CATEGORY	Category	Depreciation Expense	121901	2022-08-02 20:25:06.637806+00	2022-08-02 20:25:06.637833+00	1	\N	\N	f	f
92	CATEGORY	Category	Dues and Subscriptions	121902	2022-08-02 20:25:06.63789+00	2022-08-02 20:25:06.637917+00	1	\N	\N	f	f
93	CATEGORY	Category	Rent Expense	121906	2022-08-02 20:25:06.637973+00	2022-08-02 20:25:06.638001+00	1	\N	\N	f	f
94	CATEGORY	Category	Equipment Rental	123391	2022-08-02 20:25:06.638057+00	2022-08-02 20:25:06.638084+00	1	\N	\N	f	f
95	CATEGORY	Category	Utilities	123426	2022-08-02 20:25:06.638141+00	2022-08-02 20:25:06.638168+00	1	\N	\N	f	f
96	CATEGORY	Category	Business	123964	2022-08-02 20:25:06.638362+00	2022-08-02 20:25:06.638463+00	1	\N	\N	f	f
97	CATEGORY	Category	Exchange Rate Variance	123965	2022-08-02 20:25:06.638523+00	2022-08-02 20:25:06.63855+00	1	\N	\N	f	f
98	CATEGORY	Category	Other Receivables	123966	2022-08-02 20:25:06.638607+00	2022-08-02 20:25:06.638634+00	1	\N	\N	f	f
99	CATEGORY	Category	Miscellaneous Expense	123967	2022-08-02 20:25:06.638691+00	2022-08-02 20:25:06.638733+00	1	\N	\N	f	f
100	CATEGORY	Category	Labor	123968	2022-08-02 20:25:06.638817+00	2022-08-02 20:25:06.638835+00	1	\N	\N	f	f
101	CATEGORY	Category	Note Receivable-Current	123969	2022-08-02 20:25:06.638877+00	2022-08-02 20:25:06.638895+00	1	\N	\N	f	f
102	CATEGORY	Category	Office Expense	123970	2022-08-02 20:25:06.638951+00	2022-08-02 20:25:06.638981+00	1	\N	\N	f	f
103	CATEGORY	Category	Outside Services	123971	2022-08-02 20:25:06.639068+00	2022-08-02 20:25:06.639213+00	1	\N	\N	f	f
104	CATEGORY	Category	Postage & Delivery	123972	2022-08-02 20:25:06.639279+00	2022-08-02 20:25:06.639314+00	1	\N	\N	f	f
105	CATEGORY	Category	Vehicle Registration	123973	2022-08-02 20:25:06.639401+00	2022-08-02 20:25:06.639453+00	1	\N	\N	f	f
106	CATEGORY	Category	Telephone Expense	123974	2022-08-02 20:25:06.639516+00	2022-08-02 20:25:06.639845+00	1	\N	\N	f	f
107	CATEGORY	Category	Professional Fees	123975	2022-08-02 20:25:06.639903+00	2022-08-02 20:25:06.639926+00	1	\N	\N	f	f
108	CATEGORY	Category	Repairs & Maintenance	123976	2022-08-02 20:25:06.639984+00	2022-08-02 20:25:06.639995+00	1	\N	\N	f	f
109	CATEGORY	Category	Supplies Expense	123977	2022-08-02 20:25:06.640053+00	2022-08-02 20:25:06.640081+00	1	\N	\N	f	f
110	CATEGORY	Category	Payroll Expenses	123978	2022-08-02 20:25:06.640285+00	2022-08-02 20:25:06.640313+00	1	\N	\N	f	f
111	CATEGORY	Category	Taxes & Licenses-Other	123979	2022-08-02 20:25:06.640371+00	2022-08-02 20:25:06.640398+00	1	\N	\N	f	f
112	CATEGORY	Category	WIP	123980	2022-08-02 20:25:06.640455+00	2022-08-02 20:25:06.640535+00	1	\N	\N	f	f
113	CATEGORY	Category	Property	123981	2022-08-02 20:25:06.640597+00	2022-08-02 20:25:06.640626+00	1	\N	\N	f	f
114	CATEGORY	Category	Vendor Return Variance	123982	2022-08-02 20:25:06.640686+00	2022-08-02 20:25:06.640715+00	1	\N	\N	f	f
115	CATEGORY	Category	Mfg Scrap	123983	2022-08-02 20:25:06.640775+00	2022-08-02 20:25:06.640804+00	1	\N	\N	f	f
116	CATEGORY	Category	Cellular	123984	2022-08-02 20:25:06.640864+00	2022-08-02 20:25:06.640912+00	1	\N	\N	f	f
404	CATEGORY	Category	COGS-Other	124287	2022-08-02 20:25:06.985588+00	2022-08-02 20:25:06.985615+00	1	\N	\N	f	f
117	CATEGORY	Category	Online Fees	123985	2022-08-02 20:25:06.641019+00	2022-08-02 20:25:06.641049+00	1	\N	\N	f	f
118	CATEGORY	Category	Manufacturing Expenses	123986	2022-08-02 20:25:06.64112+00	2022-08-02 20:25:06.641148+00	1	\N	\N	f	f
119	CATEGORY	Category	Labor Burden	123987	2022-08-02 20:25:06.641206+00	2022-08-02 20:25:06.641233+00	1	\N	\N	f	f
120	CATEGORY	Category	WIP Variance	123988	2022-08-02 20:25:06.641432+00	2022-08-02 20:25:06.64146+00	1	\N	\N	f	f
121	CATEGORY	Category	Inventory Asset	123989	2022-08-02 20:25:06.641517+00	2022-08-02 20:25:06.641544+00	1	\N	\N	f	f
122	CATEGORY	Category	Furniture & Fixtures Expense	123990	2022-08-02 20:25:06.646763+00	2022-08-02 20:25:06.646804+00	1	\N	\N	f	f
123	CATEGORY	Category	Legal	123991	2022-08-02 20:25:06.646871+00	2022-08-02 20:25:06.646899+00	1	\N	\N	f	f
124	CATEGORY	Category	Inventory Returned Not Credited	123992	2022-08-02 20:25:06.646959+00	2022-08-02 20:25:06.646986+00	1	\N	\N	f	f
125	CATEGORY	Category	Undeposited Funds	123993	2022-08-02 20:25:06.647045+00	2022-08-02 20:25:06.647073+00	1	\N	\N	f	f
126	CATEGORY	Category	Allowance for Doubtful Accounts	123994	2022-08-02 20:25:06.64713+00	2022-08-02 20:25:06.647157+00	1	\N	\N	f	f
127	CATEGORY	Category	Pager	123995	2022-08-02 20:25:06.647215+00	2022-08-02 20:25:06.647254+00	1	\N	\N	f	f
128	CATEGORY	Category	Purchase Price Variance	123996	2022-08-02 20:25:06.647415+00	2022-08-02 20:25:06.647443+00	1	\N	\N	f	f
129	CATEGORY	Category	Build Price Variance	123997	2022-08-02 20:25:06.647501+00	2022-08-02 20:25:06.647528+00	1	\N	\N	f	f
130	CATEGORY	Category	Build Quantity Variance	123998	2022-08-02 20:25:06.647585+00	2022-08-02 20:25:06.647612+00	1	\N	\N	f	f
131	CATEGORY	Category	Employee Advances	123999	2022-08-02 20:25:06.647669+00	2022-08-02 20:25:06.647696+00	1	\N	\N	f	f
132	CATEGORY	Category	Prepaid Expenses	124000	2022-08-02 20:25:06.647753+00	2022-08-02 20:25:06.64778+00	1	\N	\N	f	f
133	CATEGORY	Category	Prepaid Income Taxes	124001	2022-08-02 20:25:06.647837+00	2022-08-02 20:25:06.647864+00	1	\N	\N	f	f
134	CATEGORY	Category	Merchandise	124002	2022-08-02 20:25:06.647921+00	2022-08-02 20:25:06.647948+00	1	\N	\N	f	f
135	CATEGORY	Category	Service	124003	2022-08-02 20:25:06.648005+00	2022-08-02 20:25:06.648032+00	1	\N	\N	f	f
136	CATEGORY	Category	Salaries & Wages	124004	2022-08-02 20:25:06.648089+00	2022-08-02 20:25:06.648116+00	1	\N	\N	f	f
137	CATEGORY	Category	Other Direct Costs	124005	2022-08-02 20:25:06.648172+00	2022-08-02 20:25:06.648322+00	1	\N	\N	f	f
138	CATEGORY	Category	Inventory Variance	124006	2022-08-02 20:25:06.648397+00	2022-08-02 20:25:06.648429+00	1	\N	\N	f	f
139	CATEGORY	Category	Amortization Expense	124007	2022-08-02 20:25:06.648859+00	2022-08-02 20:25:06.648892+00	1	\N	\N	f	f
140	CATEGORY	Category	Automobile Expense	124008	2022-08-02 20:25:06.648943+00	2022-08-02 20:25:06.648967+00	1	\N	\N	f	f
141	CATEGORY	Category	Gas & Oil	124009	2022-08-02 20:25:06.649036+00	2022-08-02 20:25:06.649066+00	1	\N	\N	f	f
142	CATEGORY	Category	Repairs	124010	2022-08-02 20:25:06.64924+00	2022-08-02 20:25:06.649268+00	1	\N	\N	f	f
143	CATEGORY	Category	Bad Debt Expense	124011	2022-08-02 20:25:06.649325+00	2022-08-02 20:25:06.649352+00	1	\N	\N	f	f
144	CATEGORY	Category	Bank Service Charges	124012	2022-08-02 20:25:06.649408+00	2022-08-02 20:25:06.649435+00	1	\N	\N	f	f
145	CATEGORY	Category	Contributions	124013	2022-08-02 20:25:06.649492+00	2022-08-02 20:25:06.649519+00	1	\N	\N	f	f
146	CATEGORY	Category	Freight & Delivery	124014	2022-08-02 20:25:06.649575+00	2022-08-02 20:25:06.649602+00	1	\N	\N	f	f
147	CATEGORY	Category	Insurance Expense	124015	2022-08-02 20:25:06.649658+00	2022-08-02 20:25:06.649685+00	1	\N	\N	f	f
148	CATEGORY	Category	Liability	124016	2022-08-02 20:25:06.649742+00	2022-08-02 20:25:06.649769+00	1	\N	\N	f	f
149	CATEGORY	Category	Workers' compensation	124017	2022-08-02 20:25:06.649825+00	2022-08-02 20:25:06.649852+00	1	\N	\N	f	f
150	CATEGORY	Category	Disability	124018	2022-08-02 20:25:06.649909+00	2022-08-02 20:25:06.649936+00	1	\N	\N	f	f
151	CATEGORY	Category	Meals & Entertainment	124019	2022-08-02 20:25:06.649992+00	2022-08-02 20:25:06.650019+00	1	\N	\N	f	f
152	CATEGORY	Category	Regular Service	124020	2022-08-02 20:25:06.650075+00	2022-08-02 20:25:06.650102+00	1	\N	\N	f	f
153	CATEGORY	Category	Gain (loss) on Sale of Assets	124021	2022-08-02 20:25:06.650158+00	2022-08-02 20:25:06.650185+00	1	\N	\N	f	f
154	CATEGORY	Category	Salaries & Wages Expense	124022	2022-08-02 20:25:06.650242+00	2022-08-02 20:25:06.650369+00	1	\N	\N	f	f
155	CATEGORY	Category	Advances Paid	124023	2022-08-02 20:25:06.650442+00	2022-08-02 20:25:06.65047+00	1	\N	\N	f	f
156	CATEGORY	Category	Duty Expense	124025	2022-08-02 20:25:06.650526+00	2022-08-02 20:25:06.650554+00	1	\N	\N	f	f
157	CATEGORY	Category	Freight Expense	124026	2022-08-02 20:25:06.65061+00	2022-08-02 20:25:06.650637+00	1	\N	\N	f	f
158	CATEGORY	Category	Damaged Goods	124027	2022-08-02 20:25:06.650694+00	2022-08-02 20:25:06.65072+00	1	\N	\N	f	f
159	CATEGORY	Category	Inventory Write Offs	124028	2022-08-02 20:25:06.650777+00	2022-08-02 20:25:06.650804+00	1	\N	\N	f	f
160	CATEGORY	Category	Inventory In Transit	124029	2022-08-02 20:25:06.65086+00	2022-08-02 20:25:06.650888+00	1	\N	\N	f	f
161	CATEGORY	Category	Bill Quantity Variance	124030	2022-08-02 20:25:06.650944+00	2022-08-02 20:25:06.650971+00	1	\N	\N	f	f
162	CATEGORY	Category	Bill Price Variance	124031	2022-08-02 20:25:06.651027+00	2022-08-02 20:25:06.651054+00	1	\N	\N	f	f
163	CATEGORY	Category	Bill Exchange Rate Variance	124032	2022-08-02 20:25:06.65111+00	2022-08-02 20:25:06.651137+00	1	\N	\N	f	f
164	CATEGORY	Category	Inventory Transfer Price Gain - Loss	124033	2022-08-02 20:25:06.651193+00	2022-08-02 20:25:06.651222+00	1	\N	\N	f	f
165	CATEGORY	Category	Unbuild Variance	124034	2022-08-02 20:25:06.651369+00	2022-08-02 20:25:06.651397+00	1	\N	\N	f	f
166	CATEGORY	Category	Rounding Gain-Loss	124035	2022-08-02 20:25:06.651454+00	2022-08-02 20:25:06.651481+00	1	\N	\N	f	f
167	CATEGORY	Category	Realized Gain-Loss	124036	2022-08-02 20:25:06.651537+00	2022-08-02 20:25:06.651564+00	1	\N	\N	f	f
168	CATEGORY	Category	Unrealized Gain-Loss	124037	2022-08-02 20:25:06.651622+00	2022-08-02 20:25:06.651649+00	1	\N	\N	f	f
169	CATEGORY	Category	WIP Revenue	124038	2022-08-02 20:25:06.651706+00	2022-08-02 20:25:06.651733+00	1	\N	\N	f	f
170	CATEGORY	Category	WIP COGS	124039	2022-08-02 20:25:06.651789+00	2022-08-02 20:25:06.651817+00	1	\N	\N	f	f
171	CATEGORY	Category	Mfg WIP	124040	2022-08-02 20:25:06.651874+00	2022-08-02 20:25:06.651901+00	1	\N	\N	f	f
172	CATEGORY	Category	Vendor Rebates	124041	2022-08-02 20:25:06.659141+00	2022-08-02 20:25:06.659329+00	1	\N	\N	f	f
173	CATEGORY	Category	Customer Return Variance	124042	2022-08-02 20:25:06.659401+00	2022-08-02 20:25:06.65943+00	1	\N	\N	f	f
174	CATEGORY	Category	Machine	124043	2022-08-02 20:25:06.65949+00	2022-08-02 20:25:06.659518+00	1	\N	\N	f	f
175	CATEGORY	Category	Machine Burden	124044	2022-08-02 20:25:06.659576+00	2022-08-02 20:25:06.659603+00	1	\N	\N	f	f
176	CATEGORY	Category	ash	124045	2022-08-02 20:25:06.659662+00	2022-08-02 20:25:06.659689+00	1	\N	\N	f	f
177	CATEGORY	Category	sub ash	124046	2022-08-02 20:25:06.659746+00	2022-08-02 20:25:06.659773+00	1	\N	\N	f	f
178	CATEGORY	Category	Machinery & Equipment	124326	2022-08-02 20:25:06.65983+00	2022-08-02 20:25:06.659857+00	1	\N	\N	f	f
179	CATEGORY	Category	Furniture & Fixtures	124328	2022-08-02 20:25:06.659914+00	2022-08-02 20:25:06.659942+00	1	\N	\N	f	f
180	CATEGORY	Category	GST Paid	147727	2022-08-02 20:25:06.659998+00	2022-08-02 20:25:06.660026+00	1	\N	\N	f	f
181	CATEGORY	Category	LCT Paid	147728	2022-08-02 20:25:06.660083+00	2022-08-02 20:25:06.66011+00	1	\N	\N	f	f
182	CATEGORY	Category	WET Paid	147729	2022-08-02 20:25:06.660167+00	2022-08-02 20:25:06.660194+00	1	\N	\N	f	f
183	CATEGORY	Category	ABN Withholding	147730	2022-08-02 20:25:06.660371+00	2022-08-02 20:25:06.660412+00	1	\N	\N	f	f
184	CATEGORY	Category	Pay As You Go Withholding	147731	2022-08-02 20:25:06.66047+00	2022-08-02 20:25:06.660498+00	1	\N	\N	f	f
185	CATEGORY	Category	VAT on Purchases	196395	2022-08-02 20:25:06.660554+00	2022-08-02 20:25:06.660581+00	1	\N	\N	f	f
186	CATEGORY	Category	UK Expense Acct	196396	2022-08-02 20:25:06.660637+00	2022-08-02 20:25:06.660664+00	1	\N	\N	f	f
187	CATEGORY	Category	UK EXP Account	196397	2022-08-02 20:25:06.660721+00	2022-08-02 20:25:06.660748+00	1	\N	\N	f	f
188	CATEGORY	Category	IT Equipment	196398	2022-08-02 20:25:06.660804+00	2022-08-02 20:25:06.660831+00	1	\N	\N	f	f
189	CATEGORY	Category	Leasehold Improvements	196399	2022-08-02 20:25:06.660887+00	2022-08-02 20:25:06.660914+00	1	\N	\N	f	f
190	CATEGORY	Category	Acc. Dep-Furniture & Fixtures	196400	2022-08-02 20:25:06.66097+00	2022-08-02 20:25:06.660997+00	1	\N	\N	f	f
191	CATEGORY	Category	Acc. Dep-Machinery & Equipment	196401	2022-08-02 20:25:06.661053+00	2022-08-02 20:25:06.66108+00	1	\N	\N	f	f
192	CATEGORY	Category	Acc. Dep-Building	196402	2022-08-02 20:25:06.661136+00	2022-08-02 20:25:06.661163+00	1	\N	\N	f	f
193	CATEGORY	Category	Acc. Dep-Leasehold Improvements	196403	2022-08-02 20:25:06.661231+00	2022-08-02 20:25:06.661359+00	1	\N	\N	f	f
194	CATEGORY	Category	Accrued Expenses	196404	2022-08-02 20:25:06.661427+00	2022-08-02 20:25:06.661455+00	1	\N	\N	f	f
195	CATEGORY	Category	Accrued Wages	196405	2022-08-02 20:25:06.661512+00	2022-08-02 20:25:06.661539+00	1	\N	\N	f	f
196	CATEGORY	Category	Accrued Vacation & Sick Pay	196406	2022-08-02 20:25:06.661596+00	2022-08-02 20:25:06.661623+00	1	\N	\N	f	f
197	CATEGORY	Category	Credit Card Payable	196407	2022-08-02 20:25:06.66168+00	2022-08-02 20:25:06.661707+00	1	\N	\N	f	f
198	CATEGORY	Category	Payroll Liabilities	196408	2022-08-02 20:25:06.661764+00	2022-08-02 20:25:06.661791+00	1	\N	\N	f	f
199	CATEGORY	Category	Sales Taxes Payable	196409	2022-08-02 20:25:06.661847+00	2022-08-02 20:25:06.661874+00	1	\N	\N	f	f
200	CATEGORY	Category	Income Taxes Payable	196410	2022-08-02 20:25:06.66193+00	2022-08-02 20:25:06.661957+00	1	\N	\N	f	f
201	CATEGORY	Category	Line of Credit Payable	196411	2022-08-02 20:25:06.662013+00	2022-08-02 20:25:06.662041+00	1	\N	\N	f	f
202	CATEGORY	Category	Loan Payable-Short-Term	196412	2022-08-02 20:25:06.662097+00	2022-08-02 20:25:06.662124+00	1	\N	\N	f	f
203	CATEGORY	Category	Retirement Contribution Payable	196413	2022-08-02 20:25:06.66218+00	2022-08-02 20:25:06.662207+00	1	\N	\N	f	f
204	CATEGORY	Category	Current Portion Long-Term Debt	196414	2022-08-02 20:25:06.662395+00	2022-08-02 20:25:06.662423+00	1	\N	\N	f	f
205	CATEGORY	Category	Inventory Received Not Billed	196415	2022-08-02 20:25:06.66248+00	2022-08-02 20:25:06.662507+00	1	\N	\N	f	f
206	CATEGORY	Category	Refunds Payable	196416	2022-08-02 20:25:06.662563+00	2022-08-02 20:25:06.66259+00	1	\N	\N	f	f
207	CATEGORY	Category	Commissions Payable	196417	2022-08-02 20:25:06.662646+00	2022-08-02 20:25:06.662673+00	1	\N	\N	f	f
208	CATEGORY	Category	Gift Certificates	196418	2022-08-02 20:25:06.66273+00	2022-08-02 20:25:06.662758+00	1	\N	\N	f	f
209	CATEGORY	Category	Deferred Expense	196419	2022-08-02 20:25:06.662814+00	2022-08-02 20:25:06.662842+00	1	\N	\N	f	f
210	CATEGORY	Category	Accumulated Depreciation	196420	2022-08-02 20:25:06.662898+00	2022-08-02 20:25:06.662926+00	1	\N	\N	f	f
211	CATEGORY	Category	Acc. Dep - IT Equipment	196421	2022-08-02 20:25:06.663282+00	2022-08-02 20:25:06.663311+00	1	\N	\N	f	f
212	CATEGORY	Category	Customer Deposits	196422	2022-08-02 20:25:06.663368+00	2022-08-02 20:25:06.663395+00	1	\N	\N	f	f
213	CATEGORY	Category	Building	196423	2022-08-02 20:25:06.663452+00	2022-08-02 20:25:06.663491+00	1	\N	\N	f	f
214	CATEGORY	Category	Failed ACH Transactions	196424	2022-08-02 20:25:06.663543+00	2022-08-02 20:25:06.663557+00	1	\N	\N	f	f
215	CATEGORY	Category	Sales Taxes Payable AK	196425	2022-08-02 20:25:06.663606+00	2022-08-02 20:25:06.663633+00	1	\N	\N	f	f
216	CATEGORY	Category	Fyle Tax	196426	2022-08-02 20:25:06.663685+00	2022-08-02 20:25:06.663714+00	1	\N	\N	f	f
217	CATEGORY	Category	Tax Liability	196427	2022-08-02 20:25:06.663774+00	2022-08-02 20:25:06.663803+00	1	\N	\N	f	f
218	CATEGORY	Category	GST Collected	196428	2022-08-02 20:25:06.66386+00	2022-08-02 20:25:06.66388+00	1	\N	\N	f	f
219	CATEGORY	Category	LCT Collected	196429	2022-08-02 20:25:06.663941+00	2022-08-02 20:25:06.66397+00	1	\N	\N	f	f
220	CATEGORY	Category	WET Collected	196430	2022-08-02 20:25:06.664025+00	2022-08-02 20:25:06.664046+00	1	\N	\N	f	f
221	CATEGORY	Category	ABN	196431	2022-08-02 20:25:06.664182+00	2022-08-02 20:25:06.664205+00	1	\N	\N	f	f
222	CATEGORY	Category	PAYG	196432	2022-08-02 20:25:06.910797+00	2022-08-02 20:25:06.910836+00	1	\N	\N	f	f
223	CATEGORY	Category	Sales Taxes Payable NY	196433	2022-08-02 20:25:06.910896+00	2022-08-02 20:25:06.910924+00	1	\N	\N	f	f
224	CATEGORY	Category	VAT on Sales	196434	2022-08-02 20:25:06.910981+00	2022-08-02 20:25:06.911008+00	1	\N	\N	f	f
225	CATEGORY	Category	VAT Liability	196435	2022-08-02 20:25:06.911065+00	2022-08-02 20:25:06.911092+00	1	\N	\N	f	f
226	CATEGORY	Category	Deposits	196974	2022-08-02 20:25:06.911149+00	2022-08-02 20:25:06.911176+00	1	\N	\N	f	f
227	CATEGORY	Category	Organization Expense	196975	2022-08-02 20:25:06.911233+00	2022-08-02 20:25:06.911516+00	1	\N	\N	f	f
228	CATEGORY	Category	Sales	196976	2022-08-02 20:25:06.9116+00	2022-08-02 20:25:06.911629+00	1	\N	\N	f	f
229	CATEGORY	Category	Sales - Merchandise	196977	2022-08-02 20:25:06.911687+00	2022-08-02 20:25:06.911714+00	1	\N	\N	f	f
230	CATEGORY	Category	Sales - Service	196978	2022-08-02 20:25:06.911771+00	2022-08-02 20:25:06.911798+00	1	\N	\N	f	f
231	CATEGORY	Category	Sales - Clearance	196979	2022-08-02 20:25:06.911855+00	2022-08-02 20:25:06.911882+00	1	\N	\N	f	f
232	CATEGORY	Category	Sales - Warranty	196980	2022-08-02 20:25:06.911938+00	2022-08-02 20:25:06.911966+00	1	\N	\N	f	f
233	CATEGORY	Category	Uncategorized Income	196981	2022-08-02 20:25:06.912022+00	2022-08-02 20:25:06.912049+00	1	\N	\N	f	f
234	CATEGORY	Category	WIP eRev	196982	2022-08-02 20:25:06.912106+00	2022-08-02 20:25:06.912133+00	1	\N	\N	f	f
235	CATEGORY	Category	XERO-123	196350	2022-08-02 20:25:06.912189+00	2022-08-02 20:25:06.912227+00	1	\N	\N	f	f
236	CATEGORY	Category	Miscellaneous Income	196351	2022-08-02 20:25:06.912405+00	2022-08-02 20:25:06.912433+00	1	\N	\N	f	f
237	CATEGORY	Category	Other Revenue	198231	2022-08-02 20:25:06.91249+00	2022-08-02 20:25:06.912517+00	1	\N	\N	f	f
238	CATEGORY	Category	Sravan Category	198232	2022-08-02 20:25:06.912596+00	2022-08-02 20:25:06.912624+00	1	\N	\N	f	f
239	CATEGORY	Category	G0ZVX1015G / Turbo charged	194278	2022-08-02 20:25:06.91268+00	2022-08-02 20:25:06.912708+00	1	\N	\N	f	f
240	CATEGORY	Category	KGF	192782	2022-08-02 20:25:06.912764+00	2022-08-02 20:25:06.912792+00	1	\N	\N	f	f
241	CATEGORY	Category	Sample	192784	2022-08-02 20:25:06.912849+00	2022-08-02 20:25:06.912876+00	1	\N	\N	f	f
242	CATEGORY	Category	Truck	192785	2022-08-02 20:25:06.912933+00	2022-08-02 20:25:06.91296+00	1	\N	\N	f	f
243	CATEGORY	Category	Original Cost	192786	2022-08-02 20:25:06.913016+00	2022-08-02 20:25:06.913043+00	1	\N	\N	f	f
244	CATEGORY	Category	Arizona Dept. of Revenue Payable	164924	2022-08-02 20:25:06.9131+00	2022-08-02 20:25:06.913127+00	1	\N	\N	f	f
245	CATEGORY	Category	Board of Equalization Payable	164925	2022-08-02 20:25:06.913183+00	2022-08-02 20:25:06.91321+00	1	\N	\N	f	f
246	CATEGORY	Category	Business Expense	164926	2022-08-02 20:25:06.913394+00	2022-08-02 20:25:06.913422+00	1	\N	\N	f	f
247	CATEGORY	Category	California Department of Tax and Fee Administration Payable	164927	2022-08-02 20:25:06.913479+00	2022-08-02 20:25:06.913507+00	1	\N	\N	f	f
248	CATEGORY	Category	Loan Payable	164929	2022-08-02 20:25:06.913563+00	2022-08-02 20:25:06.91359+00	1	\N	\N	f	f
249	CATEGORY	Category	Miscellaneous	164930	2022-08-02 20:25:06.913647+00	2022-08-02 20:25:06.913674+00	1	\N	\N	f	f
250	CATEGORY	Category	Office Supplies 2	164932	2022-08-02 20:25:06.91373+00	2022-08-02 20:25:06.913757+00	1	\N	\N	f	f
251	CATEGORY	Category	Office/General Administrative Expenses	164933	2022-08-02 20:25:06.913814+00	2022-08-02 20:25:06.913842+00	1	\N	\N	f	f
252	CATEGORY	Category	Opening Balance Equity	164934	2022-08-02 20:25:06.913898+00	2022-08-02 20:25:06.913968+00	1	\N	\N	f	f
253	CATEGORY	Category	Out Of Scope Agency Payable	164935	2022-08-02 20:25:06.914031+00	2022-08-02 20:25:06.91406+00	1	\N	\N	f	f
254	CATEGORY	Category	Penalties & Settlements	164936	2022-08-02 20:25:06.91412+00	2022-08-02 20:25:06.914149+00	1	\N	\N	f	f
255	CATEGORY	Category	Uncategorized Asset	164937	2022-08-02 20:25:06.914334+00	2022-08-02 20:25:06.914484+00	1	\N	\N	f	f
256	CATEGORY	Category	Exchange Gain or Loss	164121	2022-08-02 20:25:06.914553+00	2022-08-02 20:25:06.914583+00	1	\N	\N	f	f
257	CATEGORY	Category	Utilities:Telephone	152622	2022-08-02 20:25:06.914696+00	2022-08-02 20:25:06.914792+00	1	\N	\N	f	f
258	CATEGORY	Category	Meals and Entertainment	124309	2022-08-02 20:25:06.914926+00	2022-08-02 20:25:06.914971+00	1	\N	\N	f	f
259	CATEGORY	Category	Job Expenses:Job Materials:Fountain and Garden Lighting	152611	2022-08-02 20:25:06.91505+00	2022-08-02 20:25:06.915202+00	1	\N	\N	f	f
260	CATEGORY	Category	Job Expenses:Job Materials:Plants and Soil	152612	2022-08-02 20:25:06.915381+00	2022-08-02 20:25:06.915467+00	1	\N	\N	f	f
261	CATEGORY	Category	Job Expenses:Job Materials:Sprinklers and Drip Systems	152613	2022-08-02 20:25:06.91557+00	2022-08-02 20:25:06.918592+00	1	\N	\N	f	f
262	CATEGORY	Category	Job Expenses:Permits	152614	2022-08-02 20:25:06.918765+00	2022-08-02 20:25:06.918797+00	1	\N	\N	f	f
263	CATEGORY	Category	Legal & Professional Fees:Accounting	152615	2022-08-02 20:25:06.918876+00	2022-08-02 20:25:06.918908+00	1	\N	\N	f	f
264	CATEGORY	Category	Legal & Professional Fees:Bookkeeper	152616	2022-08-02 20:25:06.918978+00	2022-08-02 20:25:06.919008+00	1	\N	\N	f	f
265	CATEGORY	Category	Legal & Professional Fees:Lawyer	152617	2022-08-02 20:25:06.919227+00	2022-08-02 20:25:06.919279+00	1	\N	\N	f	f
266	CATEGORY	Category	Maintenance and Repair:Building Repairs	152618	2022-08-02 20:25:06.919389+00	2022-08-02 20:25:06.919474+00	1	\N	\N	f	f
267	CATEGORY	Category	Maintenance and Repair:Computer Repairs	152619	2022-08-02 20:25:06.91955+00	2022-08-02 20:25:06.91958+00	1	\N	\N	f	f
268	CATEGORY	Category	Maintenance and Repair:Equipment Repairs	152620	2022-08-02 20:25:06.919642+00	2022-08-02 20:25:06.919672+00	1	\N	\N	f	f
269	CATEGORY	Category	Utilities:Gas and Electric	152621	2022-08-02 20:25:06.919733+00	2022-08-02 20:25:06.919762+00	1	\N	\N	f	f
270	CATEGORY	Category	Legal and professional fees	151877	2022-08-02 20:25:06.919824+00	2022-08-02 20:25:06.919853+00	1	\N	\N	f	f
271	CATEGORY	Category	Loss on discontinued operations, net of tax	151878	2022-08-02 20:25:06.919914+00	2022-08-02 20:25:06.919944+00	1	\N	\N	f	f
272	CATEGORY	Category	Management compensation	151879	2022-08-02 20:25:06.946392+00	2022-08-02 20:25:06.946436+00	1	\N	\N	f	f
273	CATEGORY	Category	Other general and administrative expenses	151882	2022-08-02 20:25:06.946624+00	2022-08-02 20:25:06.946656+00	1	\N	\N	f	f
274	CATEGORY	Category	Other selling expenses	151883	2022-08-02 20:25:06.946783+00	2022-08-02 20:25:06.946836+00	1	\N	\N	f	f
275	CATEGORY	Category	Other Types of Expenses-Advertising Expenses	151884	2022-08-02 20:25:06.946953+00	2022-08-02 20:25:06.946993+00	1	\N	\N	f	f
276	CATEGORY	Category	Rent or lease payments	151885	2022-08-02 20:25:06.947069+00	2022-08-02 20:25:06.947099+00	1	\N	\N	f	f
277	CATEGORY	Category	Shipping and delivery expense	151886	2022-08-02 20:25:06.947183+00	2022-08-02 20:25:06.947646+00	1	\N	\N	f	f
278	CATEGORY	Category	Stationery and printing	151887	2022-08-02 20:25:06.948707+00	2022-08-02 20:25:06.948753+00	1	\N	\N	f	f
279	CATEGORY	Category	Supplies	151888	2022-08-02 20:25:06.948827+00	2022-08-02 20:25:06.948856+00	1	\N	\N	f	f
280	CATEGORY	Category	Travel expenses - general and admin expenses	151889	2022-08-02 20:25:06.948918+00	2022-08-02 20:25:06.948946+00	1	\N	\N	f	f
281	CATEGORY	Category	Travel expenses - selling expenses	151890	2022-08-02 20:25:06.949006+00	2022-08-02 20:25:06.949033+00	1	\N	\N	f	f
282	CATEGORY	Category	Utilities - Electric & Gas	151891	2022-08-02 20:25:06.949091+00	2022-08-02 20:25:06.949119+00	1	\N	\N	f	f
283	CATEGORY	Category	Utilities - Water	151892	2022-08-02 20:25:06.94919+00	2022-08-02 20:25:06.949341+00	1	\N	\N	f	f
284	CATEGORY	Category	Wage expenses	151893	2022-08-02 20:25:06.949398+00	2022-08-02 20:25:06.949469+00	1	\N	\N	f	f
285	CATEGORY	Category	Bank Charges	123387	2022-08-02 20:25:06.949528+00	2022-08-02 20:25:06.949556+00	1	\N	\N	f	f
286	CATEGORY	Category	Amortisation (and depreciation) expense	151865	2022-08-02 20:25:06.949614+00	2022-08-02 20:25:06.949642+00	1	\N	\N	f	f
287	CATEGORY	Category	Bad debts	151866	2022-08-02 20:25:06.949699+00	2022-08-02 20:25:06.949727+00	1	\N	\N	f	f
288	CATEGORY	Category	BAS Expense	151868	2022-08-02 20:25:06.949784+00	2022-08-02 20:25:06.949812+00	1	\N	\N	f	f
289	CATEGORY	Category	Commissions and fees	151869	2022-08-02 20:25:06.94987+00	2022-08-02 20:25:06.949897+00	1	\N	\N	f	f
290	CATEGORY	Category	Communication Expense - Fixed	151870	2022-08-02 20:25:06.949954+00	2022-08-02 20:25:06.949981+00	1	\N	\N	f	f
291	CATEGORY	Category	Insurance - Disability	151874	2022-08-02 20:25:06.950038+00	2022-08-02 20:25:06.950065+00	1	\N	\N	f	f
292	CATEGORY	Category	Insurance - General	151875	2022-08-02 20:25:06.950123+00	2022-08-02 20:25:06.95015+00	1	\N	\N	f	f
293	CATEGORY	Category	Insurance - Liability	151876	2022-08-02 20:25:06.950207+00	2022-08-02 20:25:06.950245+00	1	\N	\N	f	f
294	CATEGORY	Category	Automobile:Fuel	152603	2022-08-02 20:25:06.950417+00	2022-08-02 20:25:06.950437+00	1	\N	\N	f	f
295	CATEGORY	Category	Insurance:Workers Compensation	152604	2022-08-02 20:25:06.950497+00	2022-08-02 20:25:06.950527+00	1	\N	\N	f	f
296	CATEGORY	Category	Job Expenses:Cost of Labor	152605	2022-08-02 20:25:06.950596+00	2022-08-02 20:25:06.950624+00	1	\N	\N	f	f
297	CATEGORY	Category	Job Expenses:Cost of Labor:Installation	152606	2022-08-02 20:25:06.950681+00	2022-08-02 20:25:06.950708+00	1	\N	\N	f	f
298	CATEGORY	Category	Job Expenses:Cost of Labor:Maintenance and Repairs	152607	2022-08-02 20:25:06.950766+00	2022-08-02 20:25:06.950793+00	1	\N	\N	f	f
299	CATEGORY	Category	Job Expenses:Equipment Rental	152608	2022-08-02 20:25:06.95085+00	2022-08-02 20:25:06.950877+00	1	\N	\N	f	f
300	CATEGORY	Category	Job Expenses:Job Materials	152609	2022-08-02 20:25:06.950944+00	2022-08-02 20:25:06.950989+00	1	\N	\N	f	f
301	CATEGORY	Category	Job Expenses:Job Materials:Decks and Patios	152610	2022-08-02 20:25:06.951054+00	2022-08-02 20:25:06.951265+00	1	\N	\N	f	f
302	CATEGORY	Category	Ground Transportation-Parking	149800	2022-08-02 20:25:06.951808+00	2022-08-02 20:25:06.951877+00	1	\N	\N	f	f
303	CATEGORY	Category	Hotel-Lodging	149801	2022-08-02 20:25:06.952005+00	2022-08-02 20:25:06.952036+00	1	\N	\N	f	f
304	CATEGORY	Category	Fyle	124347	2022-08-02 20:25:06.952268+00	2022-08-02 20:25:06.952306+00	1	\N	\N	f	f
305	CATEGORY	Category	ASHWIN MANUALLY ADDED THIS	124348	2022-08-02 20:25:06.952429+00	2022-08-02 20:25:06.952475+00	1	\N	\N	f	f
306	CATEGORY	Category	ASHWIN MANUALLY ADDED THIS2	124349	2022-08-02 20:25:06.95256+00	2022-08-02 20:25:06.952591+00	1	\N	\N	f	f
307	CATEGORY	Category	Patents & Licenses	124353	2022-08-02 20:25:06.952656+00	2022-08-02 20:25:06.952686+00	1	\N	\N	f	f
308	CATEGORY	Category	Employee Benefits	124354	2022-08-02 20:25:06.952801+00	2022-08-02 20:25:06.952838+00	1	\N	\N	f	f
309	CATEGORY	Category	Commission	124355	2022-08-02 20:25:06.953047+00	2022-08-02 20:25:06.95308+00	1	\N	\N	f	f
310	CATEGORY	Category	Office Suppliesdfsd	124356	2022-08-02 20:25:06.953141+00	2022-08-02 20:25:06.953169+00	1	\N	\N	f	f
311	CATEGORY	Category	Employee Deductions	124357	2022-08-02 20:25:06.953226+00	2022-08-02 20:25:06.953254+00	1	\N	\N	f	f
312	CATEGORY	Category	Payroll Expense	124358	2022-08-02 20:25:06.953458+00	2022-08-02 20:25:06.953487+00	1	\N	\N	f	f
313	CATEGORY	Category	Travel Expenses which supports National  International	124117	2022-08-02 20:25:06.953548+00	2022-08-02 20:25:06.953587+00	1	\N	\N	f	f
314	CATEGORY	Category	Automobile	123386	2022-08-02 20:25:06.953644+00	2022-08-02 20:25:06.953672+00	1	\N	\N	f	f
315	CATEGORY	Category	Commissions & fees	123388	2022-08-02 20:25:06.953728+00	2022-08-02 20:25:06.953755+00	1	\N	\N	f	f
316	CATEGORY	Category	Disposal Fees	123389	2022-08-02 20:25:06.953812+00	2022-08-02 20:25:06.953839+00	1	\N	\N	f	f
317	CATEGORY	Category	Dues & Subscriptions	123390	2022-08-02 20:25:06.953895+00	2022-08-02 20:25:06.953922+00	1	\N	\N	f	f
318	CATEGORY	Category	Incremental Account	123392	2022-08-02 20:25:06.953979+00	2022-08-02 20:25:06.954006+00	1	\N	\N	f	f
319	CATEGORY	Category	Workers Compensation	123394	2022-08-02 20:25:06.954074+00	2022-08-02 20:25:06.954247+00	1	\N	\N	f	f
320	CATEGORY	Category	Job Expenses	123395	2022-08-02 20:25:06.954344+00	2022-08-02 20:25:06.954375+00	1	\N	\N	f	f
321	CATEGORY	Category	Cost of Labor	123396	2022-08-02 20:25:06.954437+00	2022-08-02 20:25:06.954466+00	1	\N	\N	f	f
322	CATEGORY	Category	Installation	123397	2022-08-02 20:25:06.962793+00	2022-08-02 20:25:06.962852+00	1	\N	\N	f	f
323	CATEGORY	Category	Maintenance and Repairs	123398	2022-08-02 20:25:06.963055+00	2022-08-02 20:25:06.963105+00	1	\N	\N	f	f
324	CATEGORY	Category	Job Materials	123400	2022-08-02 20:25:06.963344+00	2022-08-02 20:25:06.96339+00	1	\N	\N	f	f
325	CATEGORY	Category	Decks and Patios	123401	2022-08-02 20:25:06.963571+00	2022-08-02 20:25:06.96362+00	1	\N	\N	f	f
326	CATEGORY	Category	Fountain and Garden Lighting	123402	2022-08-02 20:25:06.963989+00	2022-08-02 20:25:06.964999+00	1	\N	\N	f	f
327	CATEGORY	Category	Plants and Soil	123403	2022-08-02 20:25:06.965252+00	2022-08-02 20:25:06.965286+00	1	\N	\N	f	f
328	CATEGORY	Category	Sprinklers and Drip Systems	123404	2022-08-02 20:25:06.96535+00	2022-08-02 20:25:06.965379+00	1	\N	\N	f	f
329	CATEGORY	Category	Permits	123405	2022-08-02 20:25:06.96544+00	2022-08-02 20:25:06.965469+00	1	\N	\N	f	f
330	CATEGORY	Category	Legal & Professional Fees	123406	2022-08-02 20:25:06.96553+00	2022-08-02 20:25:06.965559+00	1	\N	\N	f	f
331	CATEGORY	Category	Depreciation Expense - 1	121970	2022-08-02 20:25:06.965619+00	2022-08-02 20:25:06.965648+00	1	\N	\N	f	f
332	CATEGORY	Category	duumy	121971	2022-08-02 20:25:06.965709+00	2022-08-02 20:25:06.965738+00	1	\N	\N	f	f
333	CATEGORY	Category	Insurance Expense-General Liability Insurance	121903	2022-08-02 20:25:06.965799+00	2022-08-02 20:25:06.965828+00	1	\N	\N	f	f
334	CATEGORY	Category	Unapplied Cash Bill Payment Expense	121907	2022-08-02 20:25:06.965888+00	2022-08-02 20:25:06.965917+00	1	\N	\N	f	f
335	CATEGORY	Category	Uncategorised Expense	121908	2022-08-02 20:25:06.965978+00	2022-08-02 20:25:06.966007+00	1	\N	\N	f	f
336	CATEGORY	Category	Artist	54541	2022-08-02 20:25:06.966067+00	2022-08-02 20:25:06.966096+00	1	\N	\N	f	f
337	CATEGORY	Category	asd	118451	2022-08-02 20:25:06.966157+00	2022-08-02 20:25:06.966186+00	1	\N	\N	f	f
338	CATEGORY	Category	asdmain	118452	2022-08-02 20:25:06.966246+00	2022-08-02 20:25:06.966382+00	1	\N	\N	f	f
339	CATEGORY	Category	AR-Retainage	124339	2022-08-02 20:25:06.966444+00	2022-08-02 20:25:06.966473+00	1	\N	\N	f	f
340	CATEGORY	Category	Software and Licenses	124342	2022-08-02 20:25:06.966533+00	2022-08-02 20:25:06.966563+00	1	\N	\N	f	f
341	CATEGORY	Category	Fyle Expenses!	124343	2022-08-02 20:25:06.966623+00	2022-08-02 20:25:06.966652+00	1	\N	\N	f	f
342	CATEGORY	Category	Fyle Expenses	124344	2022-08-02 20:25:06.966712+00	2022-08-02 20:25:06.96674+00	1	\N	\N	f	f
343	CATEGORY	Category	Fyleasdads	124345	2022-08-02 20:25:06.966801+00	2022-08-02 20:25:06.96683+00	1	\N	\N	f	f
344	CATEGORY	Category	test category 37	125708	2022-08-02 20:25:06.966891+00	2022-08-02 20:25:06.96692+00	1	\N	\N	f	f
345	CATEGORY	Category	Capitalized Software Costs	125722	2022-08-02 20:25:06.96698+00	2022-08-02 20:25:06.967009+00	1	\N	\N	f	f
346	CATEGORY	Category	Cellular Phone	125951	2022-08-02 20:25:06.96707+00	2022-08-02 20:25:06.967099+00	1	\N	\N	f	f
347	CATEGORY	Category	Integration Test Account	125952	2022-08-02 20:25:06.967159+00	2022-08-02 20:25:06.967188+00	1	\N	\N	f	f
348	CATEGORY	Category	CoronaGo	125953	2022-08-02 20:25:06.967339+00	2022-08-02 20:25:06.967369+00	1	\N	\N	f	f
349	CATEGORY	Category	lol sob	125954	2022-08-02 20:25:06.96743+00	2022-08-02 20:25:06.967459+00	1	\N	\N	f	f
350	CATEGORY	Category	expense category ash	125955	2022-08-02 20:25:06.967519+00	2022-08-02 20:25:06.967548+00	1	\N	\N	f	f
351	CATEGORY	Category	Excise Tax	124332	2022-08-02 20:25:06.967608+00	2022-08-02 20:25:06.967637+00	1	\N	\N	f	f
352	CATEGORY	Category	Other Taxes	124333	2022-08-02 20:25:06.967698+00	2022-08-02 20:25:06.967726+00	1	\N	\N	f	f
353	CATEGORY	Category	Other Expense	124334	2022-08-02 20:25:06.967787+00	2022-08-02 20:25:06.967816+00	1	\N	\N	f	f
354	CATEGORY	Category	Allocations	124335	2022-08-02 20:25:06.967876+00	2022-08-02 20:25:06.967905+00	1	\N	\N	f	f
355	CATEGORY	Category	Other Income	124336	2022-08-02 20:25:06.967965+00	2022-08-02 20:25:06.967994+00	1	\N	\N	f	f
356	CATEGORY	Category	Accounts Receivable - Other	124338	2022-08-02 20:25:06.968055+00	2022-08-02 20:25:06.968084+00	1	\N	\N	f	f
357	CATEGORY	Category	Due from Entity 200	124322	2022-08-02 20:25:06.968144+00	2022-08-02 20:25:06.968173+00	1	\N	\N	f	f
358	CATEGORY	Category	Due from Entity 300	124323	2022-08-02 20:25:06.968234+00	2022-08-02 20:25:06.968358+00	1	\N	\N	f	f
359	CATEGORY	Category	Buildings	124324	2022-08-02 20:25:06.968422+00	2022-08-02 20:25:06.968452+00	1	\N	\N	f	f
360	CATEGORY	Category	Buildings Accm.Depr.	124325	2022-08-02 20:25:06.968513+00	2022-08-02 20:25:06.968542+00	1	\N	\N	f	f
361	CATEGORY	Category	Machinery & Equipment Accm.Depr.	124327	2022-08-02 20:25:06.968603+00	2022-08-02 20:25:06.968632+00	1	\N	\N	f	f
362	CATEGORY	Category	Retained Earnings	124329	2022-08-02 20:25:06.968693+00	2022-08-02 20:25:06.968722+00	1	\N	\N	f	f
363	CATEGORY	Category	COGS Sales	124330	2022-08-02 20:25:06.968783+00	2022-08-02 20:25:06.968812+00	1	\N	\N	f	f
364	CATEGORY	Category	COGS-Damage, Scrap, Spoilage	124331	2022-08-02 20:25:06.968872+00	2022-08-02 20:25:06.968901+00	1	\N	\N	f	f
365	CATEGORY	Category	Revenue - Accessories	124304	2022-08-02 20:25:06.968962+00	2022-08-02 20:25:06.968991+00	1	\N	\N	f	f
366	CATEGORY	Category	Notes Payable	124305	2022-08-02 20:25:06.969052+00	2022-08-02 20:25:06.969081+00	1	\N	\N	f	f
367	CATEGORY	Category	Marketing and Advertising	124306	2022-08-02 20:25:06.969259+00	2022-08-02 20:25:06.969293+00	1	\N	\N	f	f
368	CATEGORY	Category	Trade Shows and Exhibits	124307	2022-08-02 20:25:06.969357+00	2022-08-02 20:25:06.969387+00	1	\N	\N	f	f
369	CATEGORY	Category	Professional Fees Expense	124308	2022-08-02 20:25:06.969449+00	2022-08-02 20:25:06.969478+00	1	\N	\N	f	f
370	CATEGORY	Category	Salaries and Wages	124311	2022-08-02 20:25:06.96954+00	2022-08-02 20:25:06.969569+00	1	\N	\N	f	f
371	CATEGORY	Category	Gain for Sale of an asset	124312	2022-08-02 20:25:06.969631+00	2022-08-02 20:25:06.96966+00	1	\N	\N	f	f
372	CATEGORY	Category	Dividends	124313	2022-08-02 20:25:06.979726+00	2022-08-02 20:25:06.979786+00	1	\N	\N	f	f
373	CATEGORY	Category	SVB Checking	124314	2022-08-02 20:25:06.979891+00	2022-08-02 20:25:06.980172+00	1	\N	\N	f	f
374	CATEGORY	Category	SVB Checking 2	124315	2022-08-02 20:25:06.981594+00	2022-08-02 20:25:06.981639+00	1	\N	\N	f	f
375	CATEGORY	Category	SVB Checking 3	124316	2022-08-02 20:25:06.981705+00	2022-08-02 20:25:06.981735+00	1	\N	\N	f	f
376	CATEGORY	Category	Cash	124317	2022-08-02 20:25:06.981796+00	2022-08-02 20:25:06.981825+00	1	\N	\N	f	f
377	CATEGORY	Category	Cash Equivalents	124318	2022-08-02 20:25:06.981887+00	2022-08-02 20:25:06.981916+00	1	\N	\N	f	f
378	CATEGORY	Category	Investments and Securities	124319	2022-08-02 20:25:06.981976+00	2022-08-02 20:25:06.982005+00	1	\N	\N	f	f
379	CATEGORY	Category	Intercompany Receivables	124320	2022-08-02 20:25:06.982066+00	2022-08-02 20:25:06.982095+00	1	\N	\N	f	f
380	CATEGORY	Category	Due from Entity 100	124321	2022-08-02 20:25:06.982155+00	2022-08-02 20:25:06.982185+00	1	\N	\N	f	f
381	CATEGORY	Category	Company Credit Card Offset	124299	2022-08-02 20:25:06.982245+00	2022-08-02 20:25:06.982432+00	1	\N	\N	f	f
382	CATEGORY	Category	Telecommunication Expense	124300	2022-08-02 20:25:06.9825+00	2022-08-02 20:25:06.982529+00	1	\N	\N	f	f
383	CATEGORY	Category	Goodwill	124301	2022-08-02 20:25:06.982594+00	2022-08-02 20:25:06.982633+00	1	\N	\N	f	f
384	CATEGORY	Category	Revenue - Surveillance	124302	2022-08-02 20:25:06.982692+00	2022-08-02 20:25:06.982707+00	1	\N	\N	f	f
385	CATEGORY	Category	Revenue - Entry	124303	2022-08-02 20:25:06.98276+00	2022-08-02 20:25:06.982789+00	1	\N	\N	f	f
386	CATEGORY	Category	Estimated Landed Costs	124292	2022-08-02 20:25:06.983002+00	2022-08-02 20:25:06.983035+00	1	\N	\N	f	f
387	CATEGORY	Category	Actual Landed Costs	124293	2022-08-02 20:25:06.983112+00	2022-08-02 20:25:06.983141+00	1	\N	\N	f	f
388	CATEGORY	Category	Goods Received Not Invoiced (GRNI)	124294	2022-08-02 20:25:06.983202+00	2022-08-02 20:25:06.983388+00	1	\N	\N	f	f
389	CATEGORY	Category	Accrued Sales Tax Payable	124295	2022-08-02 20:25:06.983468+00	2022-08-02 20:25:06.983496+00	1	\N	\N	f	f
390	CATEGORY	Category	Accrued Payroll Tax Payable	124296	2022-08-02 20:25:06.983554+00	2022-08-02 20:25:06.983581+00	1	\N	\N	f	f
391	CATEGORY	Category	Other G&A	124298	2022-08-02 20:25:06.983638+00	2022-08-02 20:25:06.983665+00	1	\N	\N	f	f
392	CATEGORY	Category	Preferred Stock	124272	2022-08-02 20:25:06.983722+00	2022-08-02 20:25:06.983749+00	1	\N	\N	f	f
393	CATEGORY	Category	COGS Services	124274	2022-08-02 20:25:06.983805+00	2022-08-02 20:25:06.983832+00	1	\N	\N	f	f
394	CATEGORY	Category	Spot Bonus	124275	2022-08-02 20:25:06.983889+00	2022-08-02 20:25:06.983916+00	1	\N	\N	f	f
395	CATEGORY	Category	COGS-Billable Hours	124276	2022-08-02 20:25:06.983973+00	2022-08-02 20:25:06.984+00	1	\N	\N	f	f
396	CATEGORY	Category	COGS-Non-Billable Hours	124277	2022-08-02 20:25:06.984056+00	2022-08-02 20:25:06.984083+00	1	\N	\N	f	f
397	CATEGORY	Category	COGS-Burden on Projects	124278	2022-08-02 20:25:06.98414+00	2022-08-02 20:25:06.984167+00	1	\N	\N	f	f
398	CATEGORY	Category	COGS-Overhead on Projects	124279	2022-08-02 20:25:06.98437+00	2022-08-02 20:25:06.984403+00	1	\N	\N	f	f
399	CATEGORY	Category	COGS-G&A on Projects	124280	2022-08-02 20:25:06.98518+00	2022-08-02 20:25:06.985202+00	1	\N	\N	f	f
400	CATEGORY	Category	COGS-Indirect projects Costs Offset	124281	2022-08-02 20:25:06.985247+00	2022-08-02 20:25:06.985267+00	1	\N	\N	f	f
401	CATEGORY	Category	COGS-Reimbursed Expenses	124282	2022-08-02 20:25:06.985336+00	2022-08-02 20:25:06.985363+00	1	\N	\N	f	f
402	CATEGORY	Category	Labor Cost Offset	124285	2022-08-02 20:25:06.985421+00	2022-08-02 20:25:06.985448+00	1	\N	\N	f	f
403	CATEGORY	Category	Labor Cost Variance	124286	2022-08-02 20:25:06.985504+00	2022-08-02 20:25:06.985531+00	1	\N	\N	f	f
405	CATEGORY	Category	Prepaid Insurance	124288	2022-08-02 20:25:06.985672+00	2022-08-02 20:25:06.9857+00	1	\N	\N	f	f
406	CATEGORY	Category	Prepaid Rent	124289	2022-08-02 20:25:06.985756+00	2022-08-02 20:25:06.985811+00	1	\N	\N	f	f
407	CATEGORY	Category	Prepaid Other	124290	2022-08-02 20:25:06.985904+00	2022-08-02 20:25:06.985935+00	1	\N	\N	f	f
408	CATEGORY	Category	Salaries Payable	124291	2022-08-02 20:25:06.986018+00	2022-08-02 20:25:06.986051+00	1	\N	\N	f	f
409	CATEGORY	Category	Common Stock	124271	2022-08-02 20:25:06.986508+00	2022-08-02 20:25:06.986541+00	1	\N	\N	f	f
410	CATEGORY	Category	Payroll Taxes	124264	2022-08-02 20:25:06.9866+00	2022-08-02 20:25:06.98663+00	1	\N	\N	f	f
411	CATEGORY	Category	Inventory	124265	2022-08-02 20:25:06.986825+00	2022-08-02 20:25:06.986859+00	1	\N	\N	f	f
412	CATEGORY	Category	Inventory-Kits	124266	2022-08-02 20:25:06.98694+00	2022-08-02 20:25:06.987018+00	1	\N	\N	f	f
413	CATEGORY	Category	Goods in Transit	124267	2022-08-02 20:25:06.987412+00	2022-08-02 20:25:06.987466+00	1	\N	\N	f	f
414	CATEGORY	Category	Inventory-Other	124268	2022-08-02 20:25:06.987644+00	2022-08-02 20:25:06.98769+00	1	\N	\N	f	f
415	CATEGORY	Category	Other Intangible Assets	124269	2022-08-02 20:25:06.987791+00	2022-08-02 20:25:06.987832+00	1	\N	\N	f	f
416	CATEGORY	Category	Other Assets	124270	2022-08-02 20:25:06.987927+00	2022-08-02 20:25:06.988012+00	1	\N	\N	f	f
417	CATEGORY	Category	Intercompany Payables	124255	2022-08-02 20:25:06.988799+00	2022-08-02 20:25:06.988835+00	1	\N	\N	f	f
418	CATEGORY	Category	Due to Entity 100	124256	2022-08-02 20:25:06.9889+00	2022-08-02 20:25:06.988928+00	1	\N	\N	f	f
419	CATEGORY	Category	Due to Entity 200	124257	2022-08-02 20:25:06.988989+00	2022-08-02 20:25:06.989016+00	1	\N	\N	f	f
420	CATEGORY	Category	Due to Entity 300	124258	2022-08-02 20:25:06.989076+00	2022-08-02 20:25:06.989104+00	1	\N	\N	f	f
421	CATEGORY	Category	Intercompany Professional Fees	124260	2022-08-02 20:25:06.989278+00	2022-08-02 20:25:06.989308+00	1	\N	\N	f	f
422	CATEGORY	Category	Accumulated OCI	124261	2022-08-02 20:25:07.541123+00	2022-08-02 20:25:07.541162+00	1	\N	\N	f	f
423	CATEGORY	Category	AmortizationExpense	124262	2022-08-02 20:25:07.541235+00	2022-08-02 20:25:07.541371+00	1	\N	\N	f	f
424	CATEGORY	Category	Revenue - Other	124263	2022-08-02 20:25:07.54144+00	2022-08-02 20:25:07.541468+00	1	\N	\N	f	f
425	CATEGORY	Category	Deferred Revenue Contra	124254	2022-08-02 20:25:07.541525+00	2022-08-02 20:25:07.541552+00	1	\N	\N	f	f
426	CATEGORY	Category	Description about Toll Charge	124155	2022-08-02 20:25:07.541609+00	2022-08-02 20:25:07.541637+00	1	\N	\N	f	f
427	CATEGORY	Category	Description about Train	124156	2022-08-02 20:25:07.541692+00	2022-08-02 20:25:07.54172+00	1	\N	\N	f	f
428	CATEGORY	Category	Description about Training	124157	2022-08-02 20:25:07.541776+00	2022-08-02 20:25:07.541804+00	1	\N	\N	f	f
429	CATEGORY	Category	Description about Utility	124160	2022-08-02 20:25:07.54186+00	2022-08-02 20:25:07.541888+00	1	\N	\N	f	f
430	CATEGORY	Category	Description about test	124161	2022-08-02 20:25:07.541944+00	2022-08-02 20:25:07.541972+00	1	\N	\N	f	f
431	CATEGORY	Category	Description about yoYoyo	124162	2022-08-02 20:25:07.542028+00	2022-08-02 20:25:07.542056+00	1	\N	\N	f	f
432	CATEGORY	Category	Lol lol	124163	2022-08-02 20:25:07.542113+00	2022-08-02 20:25:07.54214+00	1	\N	\N	f	f
433	CATEGORY	Category	Accm.Depr. Furniture & Fixtures	124251	2022-08-02 20:25:07.542197+00	2022-08-02 20:25:07.542236+00	1	\N	\N	f	f
434	CATEGORY	Category	CapitalizedSoftwareCosts	124252	2022-08-02 20:25:07.542433+00	2022-08-02 20:25:07.542466+00	1	\N	\N	f	f
435	CATEGORY	Category	Deferred Revenue	124253	2022-08-02 20:25:07.542536+00	2022-08-02 20:25:07.542564+00	1	\N	\N	f	f
436	CATEGORY	Category	Description about Internet	124143	2022-08-02 20:25:07.54262+00	2022-08-02 20:25:07.542647+00	1	\N	\N	f	f
437	CATEGORY	Category	Description about Mileage	124144	2022-08-02 20:25:07.542703+00	2022-08-02 20:25:07.54273+00	1	\N	\N	f	f
438	CATEGORY	Category	Description about Office Party	124145	2022-08-02 20:25:07.542787+00	2022-08-02 20:25:07.542814+00	1	\N	\N	f	f
439	CATEGORY	Category	Description about Office Supplies	124146	2022-08-02 20:25:07.542871+00	2022-08-02 20:25:07.542898+00	1	\N	\N	f	f
440	CATEGORY	Category	Description about Others	124147	2022-08-02 20:25:07.542954+00	2022-08-02 20:25:07.542981+00	1	\N	\N	f	f
441	CATEGORY	Category	Description about Parking	124148	2022-08-02 20:25:07.543038+00	2022-08-02 20:25:07.543065+00	1	\N	\N	f	f
442	CATEGORY	Category	Description about Phone	124149	2022-08-02 20:25:07.543121+00	2022-08-02 20:25:07.543149+00	1	\N	\N	f	f
443	CATEGORY	Category	Description about Professional Services	124150	2022-08-02 20:25:07.543205+00	2022-08-02 20:25:07.543346+00	1	\N	\N	f	f
444	CATEGORY	Category	Description about Snacks	124151	2022-08-02 20:25:07.543415+00	2022-08-02 20:25:07.543443+00	1	\N	\N	f	f
445	CATEGORY	Category	Description about Software	124152	2022-08-02 20:25:07.543499+00	2022-08-02 20:25:07.543526+00	1	\N	\N	f	f
446	CATEGORY	Category	Description about Tax	124153	2022-08-02 20:25:07.543583+00	2022-08-02 20:25:07.54361+00	1	\N	\N	f	f
447	CATEGORY	Category	Description about Flight	124138	2022-08-02 20:25:07.543666+00	2022-08-02 20:25:07.543693+00	1	\N	\N	f	f
448	CATEGORY	Category	Description about Food	124139	2022-08-02 20:25:07.54375+00	2022-08-02 20:25:07.543777+00	1	\N	\N	f	f
449	CATEGORY	Category	Description about Fuel	124140	2022-08-02 20:25:07.543833+00	2022-08-02 20:25:07.54386+00	1	\N	\N	f	f
450	CATEGORY	Category	Hehehe	124141	2022-08-02 20:25:07.543917+00	2022-08-02 20:25:07.543944+00	1	\N	\N	f	f
451	CATEGORY	Category	Description about Hotel	124142	2022-08-02 20:25:07.544+00	2022-08-02 20:25:07.544027+00	1	\N	\N	f	f
452	CATEGORY	Category	Description about Courier	124136	2022-08-02 20:25:07.544083+00	2022-08-02 20:25:07.54411+00	1	\N	\N	f	f
453	CATEGORY	Category	Description about Entertainment	124137	2022-08-02 20:25:07.544166+00	2022-08-02 20:25:07.544194+00	1	\N	\N	f	f
454	CATEGORY	Category	Description about Aahis is a very very long category name with no meaning	124133	2022-08-02 20:25:07.544373+00	2022-08-02 20:25:07.544411+00	1	\N	\N	f	f
455	CATEGORY	Category	Description about Activity	124134	2022-08-02 20:25:07.544468+00	2022-08-02 20:25:07.544496+00	1	\N	\N	f	f
456	CATEGORY	Category	Description about Bus	124135	2022-08-02 20:25:07.544552+00	2022-08-02 20:25:07.544579+00	1	\N	\N	f	f
457	CATEGORY	Category	Description about 123456	124125	2022-08-02 20:25:07.544636+00	2022-08-02 20:25:07.544663+00	1	\N	\N	f	f
458	CATEGORY	Category	Description about 323423	124126	2022-08-02 20:25:07.544719+00	2022-08-02 20:25:07.544746+00	1	\N	\N	f	f
459	CATEGORY	Category	Description about 7504 SA - Travel (Fuel,Parking,Tolls,etc)	124127	2022-08-02 20:25:07.544803+00	2022-08-02 20:25:07.54483+00	1	\N	\N	f	f
460	CATEGORY	Category	Description about AA	124128	2022-08-02 20:25:07.544887+00	2022-08-02 20:25:07.544914+00	1	\N	\N	f	f
461	CATEGORY	Category	Description about AAAA	124129	2022-08-02 20:25:07.54497+00	2022-08-02 20:25:07.544997+00	1	\N	\N	f	f
462	CATEGORY	Category	Description about ABCDE	124130	2022-08-02 20:25:07.545053+00	2022-08-02 20:25:07.54508+00	1	\N	\N	f	f
463	CATEGORY	Category	Description about 0000	124122	2022-08-02 20:25:07.545137+00	2022-08-02 20:25:07.545164+00	1	\N	\N	f	f
464	CATEGORY	Category	Description about 1	124123	2022-08-02 20:25:07.545231+00	2022-08-02 20:25:07.545372+00	1	\N	\N	f	f
465	CATEGORY	Category	Description about 123	124124	2022-08-02 20:25:07.545433+00	2022-08-02 20:25:07.545479+00	1	\N	\N	f	f
466	CATEGORY	Category	Gas and Electric	123427	2022-08-02 20:25:07.545743+00	2022-08-02 20:25:07.54579+00	1	\N	\N	f	f
467	CATEGORY	Category	Telephone	123428	2022-08-02 20:25:07.54589+00	2022-08-02 20:25:07.545932+00	1	\N	\N	f	f
468	CATEGORY	Category	Taxes & Licenses	123420	2022-08-02 20:25:07.546211+00	2022-08-02 20:25:07.546378+00	1	\N	\N	f	f
469	CATEGORY	Category	Test 2	123421	2022-08-02 20:25:07.546443+00	2022-08-02 20:25:07.546471+00	1	\N	\N	f	f
470	CATEGORY	Category	Test Staging	123422	2022-08-02 20:25:07.546528+00	2022-08-02 20:25:07.546559+00	1	\N	\N	f	f
471	CATEGORY	Category	Travel	123423	2022-08-02 20:25:07.546631+00	2022-08-02 20:25:07.546661+00	1	\N	\N	f	f
472	CATEGORY	Category	Travel Meals	123424	2022-08-02 20:25:07.55306+00	2022-08-02 20:25:07.553101+00	1	\N	\N	f	f
473	CATEGORY	Category	Uncategorized Expense	123425	2022-08-02 20:25:07.553172+00	2022-08-02 20:25:07.553331+00	1	\N	\N	f	f
474	CATEGORY	Category	Stationery & Printing	123418	2022-08-02 20:25:07.553401+00	2022-08-02 20:25:07.553429+00	1	\N	\N	f	f
475	CATEGORY	Category	Supplies Test 2	123419	2022-08-02 20:25:07.553487+00	2022-08-02 20:25:07.553514+00	1	\N	\N	f	f
476	CATEGORY	Category	Bookkeeper	123408	2022-08-02 20:25:07.553571+00	2022-08-02 20:25:07.553599+00	1	\N	\N	f	f
477	CATEGORY	Category	Lawyer	123409	2022-08-02 20:25:07.553656+00	2022-08-02 20:25:07.553684+00	1	\N	\N	f	f
478	CATEGORY	Category	Maintenance and Repair	123410	2022-08-02 20:25:07.553741+00	2022-08-02 20:25:07.553769+00	1	\N	\N	f	f
479	CATEGORY	Category	Building Repairs	123411	2022-08-02 20:25:07.553826+00	2022-08-02 20:25:07.553853+00	1	\N	\N	f	f
480	CATEGORY	Category	Computer Repairs	123412	2022-08-02 20:25:07.55391+00	2022-08-02 20:25:07.553937+00	1	\N	\N	f	f
481	CATEGORY	Category	Equipment Repairs	123413	2022-08-02 20:25:07.553994+00	2022-08-02 20:25:07.554022+00	1	\N	\N	f	f
482	CATEGORY	Category	Promotional	123416	2022-08-02 20:25:07.554078+00	2022-08-02 20:25:07.554105+00	1	\N	\N	f	f
483	CATEGORY	Category	Rent or Lease	123417	2022-08-02 20:25:07.554162+00	2022-08-02 20:25:07.554189+00	1	\N	\N	f	f
484	CATEGORY	Category	suhas_cat1	59658	2022-08-02 20:25:07.554377+00	2022-08-02 20:25:07.554617+00	1	\N	\N	f	f
485	CATEGORY	Category	cat1	59666	2022-08-02 20:25:07.554676+00	2022-08-02 20:25:07.554703+00	1	\N	\N	f	f
486	CATEGORY	Category	cat2	59667	2022-08-02 20:25:07.55476+00	2022-08-02 20:25:07.554788+00	1	\N	\N	f	f
487	CATEGORY	Category	Tour	54539	2022-08-02 20:25:07.554845+00	2022-08-02 20:25:07.554872+00	1	\N	\N	f	f
488	CATEGORY	Category	Recording Costs	54540	2022-08-02 20:25:07.554929+00	2022-08-02 20:25:07.554956+00	1	\N	\N	f	f
489	CATEGORY	Category	Merch	54542	2022-08-02 20:25:07.555013+00	2022-08-02 20:25:07.555041+00	1	\N	\N	f	f
490	CATEGORY	Category	POSTMANN-3 /  	191584	2022-08-02 20:25:07.555098+00	2022-08-02 20:25:07.555125+00	1	\N	\N	f	f
491	CATEGORY	Category	PASTMANN-2 / Turbo charged	191582	2022-08-02 20:25:07.555181+00	2022-08-02 20:25:07.555219+00	1	\N	\N	f	f
492	CATEGORY	Category	PASTMANN / Turbo charged	191581	2022-08-02 20:25:07.555394+00	2022-08-02 20:25:07.555422+00	1	\N	\N	f	f
493	CATEGORY	Category	asdmain / sub cat	118453	2022-08-02 20:25:07.555479+00	2022-08-02 20:25:07.555506+00	1	\N	\N	f	f
494	CATEGORY	Category	cat2 / sub-cat2	59669	2022-08-02 20:25:07.555563+00	2022-08-02 20:25:07.555591+00	1	\N	\N	f	f
495	CATEGORY	Category	cat1 / sub-cat1	59668	2022-08-02 20:25:07.555647+00	2022-08-02 20:25:07.555675+00	1	\N	\N	f	f
496	CATEGORY	Category	suhas_cat1 / suhas_subcat1	59659	2022-08-02 20:25:07.555731+00	2022-08-02 20:25:07.555759+00	1	\N	\N	f	f
497	CATEGORY	Category	Merch / Production/Artwork	54553	2022-08-02 20:25:07.555816+00	2022-08-02 20:25:07.555896+00	1	\N	\N	f	f
498	CATEGORY	Category	Artist / Artist Travel	54552	2022-08-02 20:25:07.555958+00	2022-08-02 20:25:07.555987+00	1	\N	\N	f	f
499	CATEGORY	Category	Recording Costs / All Other	54551	2022-08-02 20:25:07.556047+00	2022-08-02 20:25:07.556076+00	1	\N	\N	f	f
500	CATEGORY	Category	Recording Costs / Session Musicians and Vocalists	54550	2022-08-02 20:25:07.556137+00	2022-08-02 20:25:07.556166+00	1	\N	\N	f	f
501	CATEGORY	Category	Tour / Crew - Production Manager	54549	2022-08-02 20:25:07.556409+00	2022-08-02 20:25:07.556459+00	1	\N	\N	f	f
502	CATEGORY	Category	Tour / Travel Other	54548	2022-08-02 20:25:07.556698+00	2022-08-02 20:25:07.556809+00	1	\N	\N	f	f
503	CATEGORY	Category	Tour / Wardrobe/Glam	54547	2022-08-02 20:25:07.556989+00	2022-08-02 20:25:07.557024+00	1	\N	\N	f	f
504	CATEGORY	Category	Tour / Crew Per Diems	54546	2022-08-02 20:25:07.55709+00	2022-08-02 20:25:07.55712+00	1	\N	\N	f	f
505	CATEGORY	Category	M&P / Artist Showcases	54545	2022-08-02 20:25:07.557449+00	2022-08-02 20:25:07.557481+00	1	\N	\N	f	f
506	CATEGORY	Category	M&P / Digital / Social Media	54544	2022-08-02 20:25:07.557541+00	2022-08-02 20:25:07.557569+00	1	\N	\N	f	f
507	CATEGORY	Category	M&P / External Publicity	54543	2022-08-02 20:25:07.557626+00	2022-08-02 20:25:07.557653+00	1	\N	\N	f	f
508	CATEGORY	Category	M&P / Marketing & Promotion	54538	2022-08-02 20:25:07.557711+00	2022-08-02 20:25:07.557738+00	1	\N	\N	f	f
27	CATEGORY	Category	Office Expenses	123415	2022-08-02 20:25:06.617046+00	2022-08-02 20:25:06.617075+00	1	\N	\N	t	f
28	CATEGORY	Category	Cost of Goods Sold	124024	2022-08-02 20:25:06.617136+00	2022-08-02 20:25:06.617166+00	1	\N	\N	t	f
30	CATEGORY	Category	Repairs and Maintenance	124310	2022-08-02 20:25:06.617435+00	2022-08-02 20:25:06.617476+00	1	\N	\N	t	f
31	CATEGORY	Category	Income Tax Expense	151873	2022-08-02 20:25:06.617548+00	2022-08-02 20:25:06.617578+00	1	\N	\N	t	f
32	CATEGORY	Category	Depreciation	164928	2022-08-02 20:25:06.617639+00	2022-08-02 20:25:06.617677+00	1	\N	\N	t	f
33	CATEGORY	Category	Bank Fees	190410	2022-08-02 20:25:06.617734+00	2022-08-02 20:25:06.617762+00	1	\N	\N	t	f
34	CATEGORY	Category	Cleaning	190411	2022-08-02 20:25:06.61783+00	2022-08-02 20:25:06.618+00	1	\N	\N	t	f
35	CATEGORY	Category	Consulting & Accounting	190412	2022-08-02 20:25:06.618068+00	2022-08-02 20:25:06.618303+00	1	\N	\N	t	f
36	CATEGORY	Category	Freight & Courier	190413	2022-08-02 20:25:06.618519+00	2022-08-02 20:25:06.618549+00	1	\N	\N	t	f
37	CATEGORY	Category	General Expenses	190414	2022-08-02 20:25:06.618766+00	2022-08-02 20:25:06.618947+00	1	\N	\N	t	f
38	CATEGORY	Category	Legal expenses	190416	2022-08-02 20:25:06.619389+00	2022-08-02 20:25:06.619417+00	1	\N	\N	t	f
39	CATEGORY	Category	Light, Power, Heating	190417	2022-08-02 20:25:06.619475+00	2022-08-02 20:25:06.619503+00	1	\N	\N	t	f
40	CATEGORY	Category	Motor Vehicle Expenses	190418	2022-08-02 20:25:06.619561+00	2022-08-02 20:25:06.619588+00	1	\N	\N	t	f
523	PROJECT	Project	Adidas	300044	2022-08-02 20:25:07.835938+00	2022-08-02 20:25:07.835977+00	1	\N	\N	f	f
524	PROJECT	Project	cc1	300045	2022-08-02 20:25:07.836037+00	2022-08-02 20:25:07.836066+00	1	\N	\N	f	f
525	PROJECT	Project	cc2	300046	2022-08-02 20:25:07.836142+00	2022-08-02 20:25:07.836171+00	1	\N	\N	f	f
526	PROJECT	Project	Coachella	300047	2022-08-02 20:25:07.836327+00	2022-08-02 20:25:07.836362+00	1	\N	\N	f	f
527	PROJECT	Project	Fabrication	300048	2022-08-02 20:25:07.83652+00	2022-08-02 20:25:07.836552+00	1	\N	\N	f	f
528	PROJECT	Project	FAE:Mini FAE	300049	2022-08-02 20:25:07.83662+00	2022-08-02 20:25:07.836648+00	1	\N	\N	f	f
529	PROJECT	Project	Radio	300050	2022-08-02 20:25:07.836705+00	2022-08-02 20:25:07.836732+00	1	\N	\N	f	f
530	PROJECT	Project	Bebe Rexha	649	2022-08-02 20:25:07.836788+00	2022-08-02 20:25:07.836816+00	1	\N	\N	f	f
531	PROJECT	Project	Chase Ortega	650	2022-08-02 20:25:07.836873+00	2022-08-02 20:25:07.8369+00	1	\N	\N	f	f
532	PROJECT	Project	David Olshanetsky	651	2022-08-02 20:25:07.836958+00	2022-08-02 20:25:07.836985+00	1	\N	\N	f	f
533	PROJECT	Project	Invisible men (George Astasio, Jason Pebworth, Jon Shave)	653	2022-08-02 20:25:07.837042+00	2022-08-02 20:25:07.837069+00	1	\N	\N	f	f
534	PROJECT	Project	Lil Peep Documentary	654	2022-08-02 20:25:07.837128+00	2022-08-02 20:25:07.837156+00	1	\N	\N	f	f
535	PROJECT	Project	Naations	655	2022-08-02 20:25:07.837214+00	2022-08-02 20:25:07.837366+00	1	\N	\N	f	f
536	PROJECT	Project	Rita Ora	656	2022-08-02 20:25:07.837437+00	2022-08-02 20:25:07.837465+00	1	\N	\N	f	f
537	PROJECT	Project	Leomie Anderson	657	2022-08-02 20:25:07.837522+00	2022-08-02 20:25:07.837549+00	1	\N	\N	f	f
538	PROJECT	Project	suhas_p1	694	2022-08-02 20:25:07.837605+00	2022-08-02 20:25:07.837633+00	1	\N	\N	f	f
539	PROJECT	Project	p1	700	2022-08-02 20:25:07.837689+00	2022-08-02 20:25:07.837717+00	1	\N	\N	f	f
540	PROJECT	Project	p2	701	2022-08-02 20:25:07.837773+00	2022-08-02 20:25:07.837801+00	1	\N	\N	f	f
541	PROJECT	Project	Customer Acquisition	902	2022-08-02 20:25:07.837858+00	2022-08-02 20:25:07.837885+00	1	\N	\N	f	f
542	PROJECT	Project	116142-Voya-EBSalesforce-OFS	1182	2022-08-02 20:25:07.837942+00	2022-08-02 20:25:07.837969+00	1	\N	\N	f	f
543	PROJECT	Project	testing project chetanya	3105	2022-08-02 20:25:07.838027+00	2022-08-02 20:25:07.838054+00	1	\N	\N	f	f
544	PROJECT	Project	project chetanya	3106	2022-08-02 20:25:07.83811+00	2022-08-02 20:25:07.838137+00	1	\N	\N	f	f
545	PROJECT	Project	project mis reports	3107	2022-08-02 20:25:07.838195+00	2022-08-02 20:25:07.838234+00	1	\N	\N	f	f
546	PROJECT	Project	Abercrombie International Group	153621	2022-08-02 20:25:07.838414+00	2022-08-02 20:25:07.838441+00	1	\N	\N	f	f
547	PROJECT	Project	Adwin Ko	153622	2022-08-02 20:25:07.838498+00	2022-08-02 20:25:07.838525+00	1	\N	\N	f	f
548	PROJECT	Project	Benjamin Yeung	153623	2022-08-02 20:25:07.838582+00	2022-08-02 20:25:07.83861+00	1	\N	\N	f	f
549	PROJECT	Project	Cathy's Consulting Company	153624	2022-08-02 20:25:07.838667+00	2022-08-02 20:25:07.838694+00	1	\N	\N	f	f
550	PROJECT	Project	Cathy's Consulting Company:Quon - Employee Party 2014	153625	2022-08-02 20:25:07.838751+00	2022-08-02 20:25:07.838778+00	1	\N	\N	f	f
551	PROJECT	Project	Cathy's Consulting Company:Quon - Retreat 2014	153626	2022-08-02 20:25:07.838835+00	2022-08-02 20:25:07.838862+00	1	\N	\N	f	f
552	PROJECT	Project	Chadha's Consultants	153627	2022-08-02 20:25:07.838919+00	2022-08-02 20:25:07.838946+00	1	\N	\N	f	f
553	PROJECT	Project	Chadha's Consultants:Chadha - Employee Training	153628	2022-08-02 20:25:07.839003+00	2022-08-02 20:25:07.83903+00	1	\N	\N	f	f
554	PROJECT	Project	Clement's Cleaners	153629	2022-08-02 20:25:07.839086+00	2022-08-02 20:25:07.839114+00	1	\N	\N	f	f
555	PROJECT	Project	Ecker Designs	153630	2022-08-02 20:25:07.839171+00	2022-08-02 20:25:07.839198+00	1	\N	\N	f	f
556	PROJECT	Project	Ecker Designs:Ecker Holiday event	153631	2022-08-02 20:25:07.839382+00	2022-08-02 20:25:07.83941+00	1	\N	\N	f	f
557	PROJECT	Project	FAE	153632	2022-08-02 20:25:07.839467+00	2022-08-02 20:25:07.839495+00	1	\N	\N	f	f
558	PROJECT	Project	Froilan Rosqueta	153633	2022-08-02 20:25:07.839551+00	2022-08-02 20:25:07.839578+00	1	\N	\N	f	f
559	PROJECT	Project	Hazel Robinson	153634	2022-08-02 20:25:07.845956+00	2022-08-02 20:25:07.845995+00	1	\N	\N	f	f
560	PROJECT	Project	Himateja Madala	153635	2022-08-02 20:25:07.846056+00	2022-08-02 20:25:07.846084+00	1	\N	\N	f	f
561	PROJECT	Project	Ho Engineering Company	153636	2022-08-02 20:25:07.846141+00	2022-08-02 20:25:07.846168+00	1	\N	\N	f	f
562	PROJECT	Project	Jacint Tumacder	153637	2022-08-02 20:25:07.846225+00	2022-08-02 20:25:07.846252+00	1	\N	\N	f	f
563	PROJECT	Project	Jen Zaccarella	153638	2022-08-02 20:25:07.846477+00	2022-08-02 20:25:07.846506+00	1	\N	\N	f	f
564	PROJECT	Project	Jordan Burgess	153639	2022-08-02 20:25:07.846564+00	2022-08-02 20:25:07.846591+00	1	\N	\N	f	f
565	PROJECT	Project	Justine Outland	153640	2022-08-02 20:25:07.846648+00	2022-08-02 20:25:07.846675+00	1	\N	\N	f	f
566	PROJECT	Project	Kari Steblay	153641	2022-08-02 20:25:07.846732+00	2022-08-02 20:25:07.846759+00	1	\N	\N	f	f
567	PROJECT	Project	Karna Nisewaner	153642	2022-08-02 20:25:07.846816+00	2022-08-02 20:25:07.846843+00	1	\N	\N	f	f
568	PROJECT	Project	Lew Plumbing	153643	2022-08-02 20:25:07.846901+00	2022-08-02 20:25:07.846928+00	1	\N	\N	f	f
569	PROJECT	Project	Lok's Management Co.	153644	2022-08-02 20:25:07.846985+00	2022-08-02 20:25:07.847012+00	1	\N	\N	f	f
570	PROJECT	Project	Nadia Phillipchuk	153645	2022-08-02 20:25:07.847069+00	2022-08-02 20:25:07.847096+00	1	\N	\N	f	f
571	PROJECT	Project	Oxon Insurance Agency	153646	2022-08-02 20:25:07.847152+00	2022-08-02 20:25:07.847179+00	1	\N	\N	f	f
572	PROJECT	Project	Oxon Insurance Agency:Oxon - Holiday Party	153647	2022-08-02 20:25:07.847357+00	2022-08-02 20:25:07.847396+00	1	\N	\N	f	f
573	PROJECT	Project	Oxon Insurance Agency:Oxon - Retreat 2014	153648	2022-08-02 20:25:07.847453+00	2022-08-02 20:25:07.847481+00	1	\N	\N	f	f
574	PROJECT	Project	Rob deMontarnal	153649	2022-08-02 20:25:07.847538+00	2022-08-02 20:25:07.847565+00	1	\N	\N	f	f
575	PROJECT	Project	Whitehead and Sons	153650	2022-08-02 20:25:07.847621+00	2022-08-02 20:25:07.847649+00	1	\N	\N	f	f
576	PROJECT	Project	Whitehead and Sons:QBO	153651	2022-08-02 20:25:07.847706+00	2022-08-02 20:25:07.847733+00	1	\N	\N	f	f
649	PROJECT	Project	Eric Schmidt	156103	2022-08-02 20:25:07.859968+00	2022-08-02 20:25:07.859995+00	1	\N	\N	f	f
577	PROJECT	Project	Whitehead and Sons:Whitehead - Employee celebration	153652	2022-08-02 20:25:07.847789+00	2022-08-02 20:25:07.847817+00	1	\N	\N	f	f
578	PROJECT	Project	Alex Wolfe	156029	2022-08-02 20:25:07.847874+00	2022-08-02 20:25:07.847901+00	1	\N	\N	f	f
579	PROJECT	Project	Anderson Boughton Inc.	156030	2022-08-02 20:25:07.847958+00	2022-08-02 20:25:07.847985+00	1	\N	\N	f	f
580	PROJECT	Project	Chess Art Gallery	156031	2022-08-02 20:25:07.848042+00	2022-08-02 20:25:07.848069+00	1	\N	\N	f	f
581	PROJECT	Project	CVM Business Solutions	156032	2022-08-02 20:25:07.848125+00	2022-08-02 20:25:07.848153+00	1	\N	\N	f	f
582	PROJECT	Project	Justin Hartman	156033	2022-08-02 20:25:07.848209+00	2022-08-02 20:25:07.848359+00	1	\N	\N	f	f
583	PROJECT	Project	Kristen Welch	156034	2022-08-02 20:25:07.848429+00	2022-08-02 20:25:07.848456+00	1	\N	\N	f	f
584	PROJECT	Project	Monica Parker	156035	2022-08-02 20:25:07.848513+00	2022-08-02 20:25:07.84854+00	1	\N	\N	f	f
585	PROJECT	Project	Michael Spencer	156036	2022-08-02 20:25:07.848597+00	2022-08-02 20:25:07.848624+00	1	\N	\N	f	f
586	PROJECT	Project	Matthew Davison	156037	2022-08-02 20:25:07.848681+00	2022-08-02 20:25:07.848709+00	1	\N	\N	f	f
587	PROJECT	Project	Carrie Davis	156038	2022-08-02 20:25:07.848765+00	2022-08-02 20:25:07.848792+00	1	\N	\N	f	f
588	PROJECT	Project	Bay Media Research	156039	2022-08-02 20:25:07.848849+00	2022-08-02 20:25:07.848876+00	1	\N	\N	f	f
589	PROJECT	Project	B-Sharp Music	156040	2022-08-02 20:25:07.848932+00	2022-08-02 20:25:07.848959+00	1	\N	\N	f	f
590	PROJECT	Project	Bob Ledner	156041	2022-08-02 20:25:07.849016+00	2022-08-02 20:25:07.849043+00	1	\N	\N	f	f
591	PROJECT	Project	Kyle Keosian	156042	2022-08-02 20:25:07.8491+00	2022-08-02 20:25:07.849127+00	1	\N	\N	f	f
592	PROJECT	Project	Erin Kessman	156043	2022-08-02 20:25:07.849183+00	2022-08-02 20:25:07.84921+00	1	\N	\N	f	f
593	PROJECT	Project	Jennings Financial Inc.	156044	2022-08-02 20:25:07.849394+00	2022-08-02 20:25:07.849421+00	1	\N	\N	f	f
594	PROJECT	Project	St. Mark's Church	156045	2022-08-02 20:25:07.849478+00	2022-08-02 20:25:07.849506+00	1	\N	\N	f	f
595	PROJECT	Project	Gibsons Corporation	156046	2022-08-02 20:25:07.849563+00	2022-08-02 20:25:07.84959+00	1	\N	\N	f	f
596	PROJECT	Project	Mindy Peiris	156047	2022-08-02 20:25:07.849646+00	2022-08-02 20:25:07.849674+00	1	\N	\N	f	f
597	PROJECT	Project	Jason Paul Distribution	156048	2022-08-02 20:25:07.84973+00	2022-08-02 20:25:07.849758+00	1	\N	\N	f	f
598	PROJECT	Project	Seena Rose	156049	2022-08-02 20:25:07.849814+00	2022-08-02 20:25:07.849842+00	1	\N	\N	f	f
599	PROJECT	Project	Sebastian Inc.	156050	2022-08-02 20:25:07.849898+00	2022-08-02 20:25:07.849925+00	1	\N	\N	f	f
600	PROJECT	Project	Kavanaugh Real Estate	156051	2022-08-02 20:25:07.849983+00	2022-08-02 20:25:07.85001+00	1	\N	\N	f	f
601	PROJECT	Project	Tom Calhoun	156052	2022-08-02 20:25:07.850067+00	2022-08-02 20:25:07.850094+00	1	\N	\N	f	f
602	PROJECT	Project	Anthony Jacobs	156053	2022-08-02 20:25:07.850151+00	2022-08-02 20:25:07.850178+00	1	\N	\N	f	f
603	PROJECT	Project	Greg Yamashige	156054	2022-08-02 20:25:07.850351+00	2022-08-02 20:25:07.850391+00	1	\N	\N	f	f
604	PROJECT	Project	Bruce Storm	156055	2022-08-02 20:25:07.850449+00	2022-08-02 20:25:07.850476+00	1	\N	\N	f	f
605	PROJECT	Project	Julia Daniels	156056	2022-08-02 20:25:07.850533+00	2022-08-02 20:25:07.850561+00	1	\N	\N	f	f
606	PROJECT	Project	Mackenzie Corporation	156057	2022-08-02 20:25:07.850618+00	2022-08-02 20:25:07.850645+00	1	\N	\N	f	f
607	PROJECT	Project	Stephan Simms	156058	2022-08-02 20:25:07.850702+00	2022-08-02 20:25:07.850729+00	1	\N	\N	f	f
608	PROJECT	Project	Sandy King	156059	2022-08-02 20:25:07.850786+00	2022-08-02 20:25:07.850814+00	1	\N	\N	f	f
609	PROJECT	Project	Robert Solan	156060	2022-08-02 20:25:07.855779+00	2022-08-02 20:25:07.855818+00	1	\N	\N	f	f
610	PROJECT	Project	Amy Kall	156061	2022-08-02 20:25:07.855877+00	2022-08-02 20:25:07.855905+00	1	\N	\N	f	f
611	PROJECT	Project	Wallace Printers	156062	2022-08-02 20:25:07.855961+00	2022-08-02 20:25:07.855989+00	1	\N	\N	f	f
612	PROJECT	Project	China Cuisine	156063	2022-08-02 20:25:07.856045+00	2022-08-02 20:25:07.856072+00	1	\N	\N	f	f
613	PROJECT	Project	Fabrizio's Dry Cleaners	156064	2022-08-02 20:25:07.856128+00	2022-08-02 20:25:07.856155+00	1	\N	\N	f	f
614	PROJECT	Project	Stella Sebastian Inc	156065	2022-08-02 20:25:07.856212+00	2022-08-02 20:25:07.856254+00	1	\N	\N	f	f
615	PROJECT	Project	All World Produce	156066	2022-08-02 20:25:07.85645+00	2022-08-02 20:25:07.856477+00	1	\N	\N	f	f
616	PROJECT	Project	Careymon Dudley	156070	2022-08-02 20:25:07.856534+00	2022-08-02 20:25:07.856561+00	1	\N	\N	f	f
617	PROJECT	Project	Jason Jacob	156071	2022-08-02 20:25:07.856617+00	2022-08-02 20:25:07.856644+00	1	\N	\N	f	f
618	PROJECT	Project	Dillain Collins	156072	2022-08-02 20:25:07.856701+00	2022-08-02 20:25:07.856728+00	1	\N	\N	f	f
619	PROJECT	Project	Kerry Furnishings & Design	156073	2022-08-02 20:25:07.856785+00	2022-08-02 20:25:07.856812+00	1	\N	\N	f	f
620	PROJECT	Project	Kavanagh Brothers	156074	2022-08-02 20:25:07.856869+00	2022-08-02 20:25:07.856896+00	1	\N	\N	f	f
621	PROJECT	Project	Patel Cafe	156075	2022-08-02 20:25:07.856953+00	2022-08-02 20:25:07.85698+00	1	\N	\N	f	f
622	PROJECT	Project	ONLINE1	156076	2022-08-02 20:25:07.857036+00	2022-08-02 20:25:07.857063+00	1	\N	\N	f	f
623	PROJECT	Project	Bobby Strands (Bobby@Strands.com)	156077	2022-08-02 20:25:07.85712+00	2022-08-02 20:25:07.857147+00	1	\N	\N	f	f
624	PROJECT	Project	Palmer and Barnar Liquors Leasing	156078	2022-08-02 20:25:07.857204+00	2022-08-02 20:25:07.857342+00	1	\N	\N	f	f
625	PROJECT	Project	Cawthron and Ullo Windows Corporation	156079	2022-08-02 20:25:07.857412+00	2022-08-02 20:25:07.85744+00	1	\N	\N	f	f
626	PROJECT	Project	Midgette Markets	156080	2022-08-02 20:25:07.857496+00	2022-08-02 20:25:07.857524+00	1	\N	\N	f	f
627	PROJECT	Project	Streib and Cravy Hardware Rentals	156081	2022-08-02 20:25:07.85758+00	2022-08-02 20:25:07.857607+00	1	\N	\N	f	f
628	PROJECT	Project	Volden Publishing Systems	156082	2022-08-02 20:25:07.857663+00	2022-08-02 20:25:07.857691+00	1	\N	\N	f	f
629	PROJECT	Project	Benton Construction Inc.	156083	2022-08-02 20:25:07.857747+00	2022-08-02 20:25:07.857774+00	1	\N	\N	f	f
630	PROJECT	Project	Bankey and Marris Hardware Corporation	156084	2022-08-02 20:25:07.85783+00	2022-08-02 20:25:07.857858+00	1	\N	\N	f	f
631	PROJECT	Project	Ferrio and Donlon Builders Management	156085	2022-08-02 20:25:07.857914+00	2022-08-02 20:25:07.857942+00	1	\N	\N	f	f
632	PROJECT	Project	Sossong Plumbing Holding Corp.	156086	2022-08-02 20:25:07.857999+00	2022-08-02 20:25:07.858027+00	1	\N	\N	f	f
633	PROJECT	Project	Cruce Builders	156087	2022-08-02 20:25:07.858083+00	2022-08-02 20:25:07.85811+00	1	\N	\N	f	f
634	PROJECT	Project	Reinhardt and Sabori Painting Group	156088	2022-08-02 20:25:07.858167+00	2022-08-02 20:25:07.858195+00	1	\N	\N	f	f
635	PROJECT	Project	Carmel Valley Metal Fabricators Holding Corp.	156089	2022-08-02 20:25:07.858377+00	2022-08-02 20:25:07.858416+00	1	\N	\N	f	f
636	PROJECT	Project	Gainesville Plumbing Co.	156090	2022-08-02 20:25:07.858473+00	2022-08-02 20:25:07.8585+00	1	\N	\N	f	f
637	PROJECT	Project	Nordon Metal Fabricators Systems	156091	2022-08-02 20:25:07.858557+00	2022-08-02 20:25:07.858584+00	1	\N	\N	f	f
638	PROJECT	Project	Vessel Painting Holding Corp.	156092	2022-08-02 20:25:07.858641+00	2022-08-02 20:25:07.858668+00	1	\N	\N	f	f
639	PROJECT	Project	Buroker Markets Incorporated	156093	2022-08-02 20:25:07.858724+00	2022-08-02 20:25:07.858752+00	1	\N	\N	f	f
640	PROJECT	Project	Ursery Publishing Group	156094	2022-08-02 20:25:07.858808+00	2022-08-02 20:25:07.858835+00	1	\N	\N	f	f
641	PROJECT	Project	Helferty _ Services	156095	2022-08-02 20:25:07.859286+00	2022-08-02 20:25:07.859314+00	1	\N	\N	f	f
642	PROJECT	Project	Oldsmar Liquors and Associates	156096	2022-08-02 20:25:07.859369+00	2022-08-02 20:25:07.859407+00	1	\N	\N	f	f
643	PROJECT	Project	Bodfish Liquors Corporation	156097	2022-08-02 20:25:07.859465+00	2022-08-02 20:25:07.859493+00	1	\N	\N	f	f
644	PROJECT	Project	Santa Fe Springs Construction Corporation	156098	2022-08-02 20:25:07.859549+00	2022-08-02 20:25:07.859577+00	1	\N	\N	f	f
645	PROJECT	Project	Boisselle Windows Distributors	156099	2022-08-02 20:25:07.859633+00	2022-08-02 20:25:07.859661+00	1	\N	\N	f	f
646	PROJECT	Project	Oconner _ Holding Corp.	156100	2022-08-02 20:25:07.859717+00	2022-08-02 20:25:07.859744+00	1	\N	\N	f	f
647	PROJECT	Project	Sumter Apartments Systems	156101	2022-08-02 20:25:07.859801+00	2022-08-02 20:25:07.859828+00	1	\N	\N	f	f
648	PROJECT	Project	Bochenek and Skoog Liquors Company	156102	2022-08-02 20:25:07.859884+00	2022-08-02 20:25:07.859912+00	1	\N	\N	f	f
650	PROJECT	Project	Jones & Bernstein Law Firm	156104	2022-08-02 20:25:07.86011+00	2022-08-02 20:25:07.860139+00	1	\N	\N	f	f
651	PROJECT	Project	Jackson Alexander	156105	2022-08-02 20:25:07.860199+00	2022-08-02 20:25:07.860229+00	1	\N	\N	f	f
652	PROJECT	Project	Jennings Financial	156106	2022-08-02 20:25:07.860393+00	2022-08-02 20:25:07.860423+00	1	\N	\N	f	f
653	PROJECT	Project	Jonathan Ketner	156107	2022-08-02 20:25:07.860655+00	2022-08-02 20:25:07.86082+00	1	\N	\N	f	f
654	PROJECT	Project	Julie Frankel	156108	2022-08-02 20:25:07.861034+00	2022-08-02 20:25:07.86107+00	1	\N	\N	f	f
655	PROJECT	Project	Ken Chua	156109	2022-08-02 20:25:07.861331+00	2022-08-02 20:25:07.861379+00	1	\N	\N	f	f
656	PROJECT	Project	Lina's Dance Studio	156110	2022-08-02 20:25:07.861581+00	2022-08-02 20:25:07.861612+00	1	\N	\N	f	f
657	PROJECT	Project	Mark's Sporting Goods	156111	2022-08-02 20:25:07.86167+00	2022-08-02 20:25:07.861698+00	1	\N	\N	f	f
658	PROJECT	Project	Phillip Van Hook	156112	2022-08-02 20:25:07.861755+00	2022-08-02 20:25:07.861782+00	1	\N	\N	f	f
659	PROJECT	Project	Sandra Burns	156113	2022-08-02 20:25:07.866785+00	2022-08-02 20:25:07.866825+00	1	\N	\N	f	f
660	PROJECT	Project	Steve Davis	156114	2022-08-02 20:25:07.866884+00	2022-08-02 20:25:07.866912+00	1	\N	\N	f	f
661	PROJECT	Project	Tim Griffin	156115	2022-08-02 20:25:07.866969+00	2022-08-02 20:25:07.866996+00	1	\N	\N	f	f
662	PROJECT	Project	Tony Matsuda	156116	2022-08-02 20:25:07.867053+00	2022-08-02 20:25:07.867081+00	1	\N	\N	f	f
663	PROJECT	Project	Travis Gilbert	156117	2022-08-02 20:25:07.867137+00	2022-08-02 20:25:07.867165+00	1	\N	\N	f	f
664	PROJECT	Project	Williams Wireless World	156118	2022-08-02 20:25:07.867221+00	2022-08-02 20:25:07.867387+00	1	\N	\N	f	f
665	PROJECT	Project	Installation FP	156120	2022-08-02 20:25:07.867458+00	2022-08-02 20:25:07.867486+00	1	\N	\N	f	f
666	PROJECT	Project	Support T&M	156121	2022-08-02 20:25:07.867542+00	2022-08-02 20:25:07.867569+00	1	\N	\N	f	f
667	PROJECT	Project	Service Job	156122	2022-08-02 20:25:07.867626+00	2022-08-02 20:25:07.867653+00	1	\N	\N	f	f
668	PROJECT	Project	John Nguyen	156123	2022-08-02 20:25:07.867709+00	2022-08-02 20:25:07.867737+00	1	\N	\N	f	f
669	PROJECT	Project	Installation 2	156124	2022-08-02 20:25:07.867793+00	2022-08-02 20:25:07.86782+00	1	\N	\N	f	f
670	PROJECT	Project	Territory JMP 2	156125	2022-08-02 20:25:07.867876+00	2022-08-02 20:25:07.867903+00	1	\N	\N	f	f
671	PROJECT	Project	Territory JMP 3	156126	2022-08-02 20:25:07.867959+00	2022-08-02 20:25:07.867986+00	1	\N	\N	f	f
672	PROJECT	Project	Lizarrago Markets Corporation	156127	2022-08-02 20:25:07.868055+00	2022-08-02 20:25:07.868213+00	1	\N	\N	f	f
673	PROJECT	Project	Wapp Hardware Sales	156128	2022-08-02 20:25:07.868377+00	2022-08-02 20:25:07.868409+00	1	\N	\N	f	f
674	PROJECT	Project	Uimari Antiques Agency	156129	2022-08-02 20:25:07.868471+00	2022-08-02 20:25:07.868535+00	1	\N	\N	f	f
675	PROJECT	Project	Laramie Construction Co.	156130	2022-08-02 20:25:07.868633+00	2022-08-02 20:25:07.868664+00	1	\N	\N	f	f
676	PROJECT	Project	Smelley _ Manufacturing	156131	2022-08-02 20:25:07.868779+00	2022-08-02 20:25:07.868811+00	1	\N	\N	f	f
677	PROJECT	Project	Daquino Painting -	156132	2022-08-02 20:25:07.868875+00	2022-08-02 20:25:07.86904+00	1	\N	\N	f	f
678	PROJECT	Project	Shininger Lumber Holding Corp.	156133	2022-08-02 20:25:07.869276+00	2022-08-02 20:25:07.86931+00	1	\N	\N	f	f
679	PROJECT	Project	Gacad Publishing Co.	156134	2022-08-02 20:25:07.869499+00	2022-08-02 20:25:07.86953+00	1	\N	\N	f	f
680	PROJECT	Project	Kalisch Lumber Group	156135	2022-08-02 20:25:07.869587+00	2022-08-02 20:25:07.869621+00	1	\N	\N	f	f
681	PROJECT	Project	Markewich Builders Rentals	156136	2022-08-02 20:25:07.869675+00	2022-08-02 20:25:07.869714+00	1	\N	\N	f	f
682	PROJECT	Project	Bemo Publishing Corporation	156137	2022-08-02 20:25:07.869771+00	2022-08-02 20:25:07.869799+00	1	\N	\N	f	f
683	PROJECT	Project	Fagnani Builders	156138	2022-08-02 20:25:07.869856+00	2022-08-02 20:25:07.869883+00	1	\N	\N	f	f
684	PROJECT	Project	Angerman Markets Company	156139	2022-08-02 20:25:07.869939+00	2022-08-02 20:25:07.869966+00	1	\N	\N	f	f
685	PROJECT	Project	Jonas Island Applied Radiation	156140	2022-08-02 20:25:07.870023+00	2022-08-02 20:25:07.87005+00	1	\N	\N	f	f
686	PROJECT	Project	Pertuit Liquors Management	156141	2022-08-02 20:25:07.870107+00	2022-08-02 20:25:07.870134+00	1	\N	\N	f	f
687	PROJECT	Project	Lummus Telecom Rentals	156142	2022-08-02 20:25:07.870384+00	2022-08-02 20:25:07.870417+00	1	\N	\N	f	f
688	PROJECT	Project	Guidaboni Publishing Leasing	156143	2022-08-02 20:25:07.870478+00	2022-08-02 20:25:07.870506+00	1	\N	\N	f	f
689	PROJECT	Project	Gadison Electric Inc.	156144	2022-08-02 20:25:07.870562+00	2022-08-02 20:25:07.87059+00	1	\N	\N	f	f
690	PROJECT	Project	Brochard Metal Fabricators Incorporated	156145	2022-08-02 20:25:07.870647+00	2022-08-02 20:25:07.870674+00	1	\N	\N	f	f
691	PROJECT	Project	Hemet Builders Sales	156146	2022-08-02 20:25:07.87073+00	2022-08-02 20:25:07.870758+00	1	\N	\N	f	f
692	PROJECT	Project	Spurgin Telecom Agency	156147	2022-08-02 20:25:07.870814+00	2022-08-02 20:25:07.870841+00	1	\N	\N	f	f
693	PROJECT	Project	Wendler Markets Leasing	156148	2022-08-02 20:25:07.870897+00	2022-08-02 20:25:07.870924+00	1	\N	\N	f	f
694	PROJECT	Project	Grangeville Apartments Dynamics	156149	2022-08-02 20:25:07.870981+00	2022-08-02 20:25:07.871008+00	1	\N	\N	f	f
695	PROJECT	Project	Harting Electric Fabricators	156150	2022-08-02 20:25:07.871065+00	2022-08-02 20:25:07.871092+00	1	\N	\N	f	f
696	PROJECT	Project	Eberlein and Preslipsky _ Holding Corp.	156151	2022-08-02 20:25:07.871148+00	2022-08-02 20:25:07.871176+00	1	\N	\N	f	f
697	PROJECT	Project	Hixson Construction Agency	156152	2022-08-02 20:25:07.871243+00	2022-08-02 20:25:07.871375+00	1	\N	\N	f	f
698	PROJECT	Project	Sweeton and Ketron Liquors Group	156153	2022-08-02 20:25:07.871445+00	2022-08-02 20:25:07.871471+00	1	\N	\N	f	f
699	PROJECT	Project	Vellekamp Title Distributors	156154	2022-08-02 20:25:07.871528+00	2022-08-02 20:25:07.871555+00	1	\N	\N	f	f
700	PROJECT	Project	Grave Apartments Sales	156155	2022-08-02 20:25:07.871612+00	2022-08-02 20:25:07.871639+00	1	\N	\N	f	f
701	PROJECT	Project	Umbrell Liquors Rentals	156156	2022-08-02 20:25:07.871695+00	2022-08-02 20:25:07.871722+00	1	\N	\N	f	f
702	PROJECT	Project	Berschauer Leasing Rentals	156157	2022-08-02 20:25:07.871779+00	2022-08-02 20:25:07.871806+00	1	\N	\N	f	f
703	PROJECT	Project	Levitan Plumbing Dynamics	156158	2022-08-02 20:25:07.871862+00	2022-08-02 20:25:07.871889+00	1	\N	\N	f	f
704	PROJECT	Project	Channer Antiques Dynamics	156159	2022-08-02 20:25:07.871946+00	2022-08-02 20:25:07.871973+00	1	\N	\N	f	f
705	PROJECT	Project	Valley Center Catering Leasing	156160	2022-08-02 20:25:07.872029+00	2022-08-02 20:25:07.872056+00	1	\N	\N	f	f
706	PROJECT	Project	Iorio Lumber Incorporated	156161	2022-08-02 20:25:07.872113+00	2022-08-02 20:25:07.87214+00	1	\N	\N	f	f
707	PROJECT	Project	Dogan Painting Leasing	156162	2022-08-02 20:25:07.872196+00	2022-08-02 20:25:07.872235+00	1	\N	\N	f	f
708	PROJECT	Project	Engelkemier Catering Management	156163	2022-08-02 20:25:07.872403+00	2022-08-02 20:25:07.87243+00	1	\N	\N	f	f
709	PROJECT	Project	Rauf Catering	156164	2022-08-02 20:25:08.362374+00	2022-08-02 20:25:08.362418+00	1	\N	\N	f	f
710	PROJECT	Project	Kerfien Title Company	156165	2022-08-02 20:25:08.362492+00	2022-08-02 20:25:08.362522+00	1	\N	\N	f	f
711	PROJECT	Project	Thermo Electron Corporation	156166	2022-08-02 20:25:08.362585+00	2022-08-02 20:25:08.362614+00	1	\N	\N	f	f
712	PROJECT	Project	Fuster Builders Co.	156167	2022-08-02 20:25:08.362676+00	2022-08-02 20:25:08.362705+00	1	\N	\N	f	f
713	PROJECT	Project	Villanova Lumber Systems	156168	2022-08-02 20:25:08.362766+00	2022-08-02 20:25:08.362795+00	1	\N	\N	f	f
714	PROJECT	Project	Borowski Catering Management	156169	2022-08-02 20:25:08.362855+00	2022-08-02 20:25:08.362884+00	1	\N	\N	f	f
715	PROJECT	Project	Cooler Title Company	156170	2022-08-02 20:25:08.362944+00	2022-08-02 20:25:08.362972+00	1	\N	\N	f	f
716	PROJECT	Project	Princeton Automotive Management	156171	2022-08-02 20:25:08.363032+00	2022-08-02 20:25:08.363061+00	1	\N	\N	f	f
717	PROJECT	Project	Benbow Software	156172	2022-08-02 20:25:08.363122+00	2022-08-02 20:25:08.363151+00	1	\N	\N	f	f
718	PROJECT	Project	Twine Title Group	156173	2022-08-02 20:25:08.363211+00	2022-08-02 20:25:08.36324+00	1	\N	\N	f	f
719	PROJECT	Project	Kroetz Electric Dynamics	156174	2022-08-02 20:25:08.3633+00	2022-08-02 20:25:08.363329+00	1	\N	\N	f	f
720	PROJECT	Project	Lois Automotive Agency	156175	2022-08-02 20:25:08.363388+00	2022-08-02 20:25:08.363417+00	1	\N	\N	f	f
721	PROJECT	Project	Eichner Antiques -	156176	2022-08-02 20:25:08.363477+00	2022-08-02 20:25:08.363505+00	1	\N	\N	f	f
722	PROJECT	Project	Lyas Builders Inc.	156177	2022-08-02 20:25:08.363628+00	2022-08-02 20:25:08.363681+00	1	\N	\N	f	f
723	PROJECT	Project	Chittenden _ Agency	156178	2022-08-02 20:25:08.364039+00	2022-08-02 20:25:08.36407+00	1	\N	\N	f	f
724	PROJECT	Project	Fort Walton Beach Electric Company	156179	2022-08-02 20:25:08.364134+00	2022-08-02 20:25:08.364162+00	1	\N	\N	f	f
725	PROJECT	Project	Shutter Title Services	156180	2022-08-02 20:25:08.364223+00	2022-08-02 20:25:08.364252+00	1	\N	\N	f	f
726	PROJECT	Project	Vivas Electric Sales	156181	2022-08-02 20:25:08.364312+00	2022-08-02 20:25:08.364342+00	1	\N	\N	f	f
727	PROJECT	Project	Matsuzaki Builders Services	156182	2022-08-02 20:25:08.364436+00	2022-08-02 20:25:08.364478+00	1	\N	\N	f	f
728	PROJECT	Project	Central Islip Antiques Fabricators	156183	2022-08-02 20:25:08.378644+00	2022-08-02 20:25:08.378678+00	1	\N	\N	f	f
729	PROJECT	Project	Acme Systems Incorporated	156184	2022-08-02 20:25:08.378741+00	2022-08-02 20:25:08.378781+00	1	\N	\N	f	f
730	PROJECT	Project	Kenney Windows Dynamics	156185	2022-08-02 20:25:08.378872+00	2022-08-02 20:25:08.378911+00	1	\N	\N	f	f
731	PROJECT	Project	Yucca Valley Title Agency	156186	2022-08-02 20:25:08.382444+00	2022-08-02 20:25:08.382585+00	1	\N	\N	f	f
732	PROJECT	Project	Hendrikson Builders Corporation	156187	2022-08-02 20:25:08.382773+00	2022-08-02 20:25:08.382827+00	1	\N	\N	f	f
733	PROJECT	Project	Blier Lumber Dynamics	156188	2022-08-02 20:25:08.383209+00	2022-08-02 20:25:08.383263+00	1	\N	\N	f	f
734	PROJECT	Project	Ficke Apartments Group	156189	2022-08-02 20:25:08.384317+00	2022-08-02 20:25:08.384379+00	1	\N	\N	f	f
735	PROJECT	Project	Boynton Beach Title Networking	156190	2022-08-02 20:25:08.384815+00	2022-08-02 20:25:08.38486+00	1	\N	\N	f	f
736	PROJECT	Project	Mitani Hardware Company	156191	2022-08-02 20:25:08.385074+00	2022-08-02 20:25:08.385294+00	1	\N	\N	f	f
737	PROJECT	Project	Paveglio Leasing Leasing	156192	2022-08-02 20:25:08.40084+00	2022-08-02 20:25:08.40097+00	1	\N	\N	f	f
738	PROJECT	Project	Saenger _ Inc.	156193	2022-08-02 20:25:08.401068+00	2022-08-02 20:25:08.401099+00	1	\N	\N	f	f
739	PROJECT	Project	Mcoy and Donlin Attorneys Sales	156194	2022-08-02 20:25:08.401171+00	2022-08-02 20:25:08.401201+00	1	\N	\N	f	f
740	PROJECT	Project	Arlington Software Management	156195	2022-08-02 20:25:08.401283+00	2022-08-02 20:25:08.401313+00	1	\N	\N	f	f
741	PROJECT	Project	Epling Builders Inc.	156196	2022-08-02 20:25:08.401379+00	2022-08-02 20:25:08.401408+00	1	\N	\N	f	f
742	PROJECT	Project	Riverside Hospital and Associates	156197	2022-08-02 20:25:08.401471+00	2022-08-02 20:25:08.4015+00	1	\N	\N	f	f
743	PROJECT	Project	Summons Apartments Company	156198	2022-08-02 20:25:08.401563+00	2022-08-02 20:25:08.401592+00	1	\N	\N	f	f
744	PROJECT	Project	Teddy Leasing Manufacturing	156199	2022-08-02 20:25:08.401656+00	2022-08-02 20:25:08.401683+00	1	\N	\N	f	f
745	PROJECT	Project	Cottman Publishing Manufacturing	156200	2022-08-02 20:25:08.401738+00	2022-08-02 20:25:08.401758+00	1	\N	\N	f	f
746	PROJECT	Project	Schreck Hardware Systems	156201	2022-08-02 20:25:08.401811+00	2022-08-02 20:25:08.40184+00	1	\N	\N	f	f
747	PROJECT	Project	Austin Publishing Inc.	156202	2022-08-02 20:25:08.401902+00	2022-08-02 20:25:08.401922+00	1	\N	\N	f	f
748	PROJECT	Project	Vermont Attorneys Company	156203	2022-08-02 20:25:08.401967+00	2022-08-02 20:25:08.401988+00	1	\N	\N	f	f
749	PROJECT	Project	Tucson Apartments and Associates	156204	2022-08-02 20:25:08.402049+00	2022-08-02 20:25:08.402078+00	1	\N	\N	f	f
750	PROJECT	Project	Wagenheim Painting and Associates	156205	2022-08-02 20:25:08.40214+00	2022-08-02 20:25:08.402169+00	1	\N	\N	f	f
751	PROJECT	Project	Carloni Builders Company	156206	2022-08-02 20:25:08.40223+00	2022-08-02 20:25:08.402259+00	1	\N	\N	f	f
752	PROJECT	Project	Altamirano Apartments Services	156207	2022-08-02 20:25:08.40232+00	2022-08-02 20:25:08.402348+00	1	\N	\N	f	f
753	PROJECT	Project	Heeralall Metal Fabricators Incorporated	156208	2022-08-02 20:25:08.40241+00	2022-08-02 20:25:08.402439+00	1	\N	\N	f	f
754	PROJECT	Project	Bisonette Leasing	156209	2022-08-02 20:25:08.402499+00	2022-08-02 20:25:08.402528+00	1	\N	\N	f	f
755	PROJECT	Project	Penalver Automotive and Associates	156210	2022-08-02 20:25:08.402589+00	2022-08-02 20:25:08.402618+00	1	\N	\N	f	f
756	PROJECT	Project	Dambrose and Ottum Leasing Holding Corp.	156211	2022-08-02 20:25:08.40268+00	2022-08-02 20:25:08.402709+00	1	\N	\N	f	f
757	PROJECT	Project	Fernstrom Automotive Systems	156212	2022-08-02 20:25:08.40277+00	2022-08-02 20:25:08.402799+00	1	\N	\N	f	f
758	PROJECT	Project	Convery Attorneys and Associates	156213	2022-08-02 20:25:08.402859+00	2022-08-02 20:25:08.402889+00	1	\N	\N	f	f
759	PROJECT	Project	Scullion Telecom Agency	156214	2022-08-02 20:25:08.452446+00	2022-08-02 20:25:08.452488+00	1	\N	\N	f	f
760	PROJECT	Project	Wettlaufer Construction Systems	156215	2022-08-02 20:25:08.452553+00	2022-08-02 20:25:08.452581+00	1	\N	\N	f	f
761	PROJECT	Project	Peveler and Tyrer Software Networking	156217	2022-08-02 20:25:08.452639+00	2022-08-02 20:25:08.452667+00	1	\N	\N	f	f
762	PROJECT	Project	Oceanside Hardware	156218	2022-08-02 20:25:08.452724+00	2022-08-02 20:25:08.452751+00	1	\N	\N	f	f
763	PROJECT	Project	Gionest Metal Fabricators Co.	156219	2022-08-02 20:25:08.452808+00	2022-08-02 20:25:08.452835+00	1	\N	\N	f	f
764	PROJECT	Project	Pomona Hardware Leasing	156220	2022-08-02 20:25:08.452892+00	2022-08-02 20:25:08.45292+00	1	\N	\N	f	f
765	PROJECT	Project	Zombro Telecom Leasing	156221	2022-08-02 20:25:08.452977+00	2022-08-02 20:25:08.453004+00	1	\N	\N	f	f
766	PROJECT	Project	Foulds Plumbing -	156222	2022-08-02 20:25:08.453076+00	2022-08-02 20:25:08.453105+00	1	\N	\N	f	f
767	PROJECT	Project	Ralphs Attorneys Group	156223	2022-08-02 20:25:08.453502+00	2022-08-02 20:25:08.453534+00	1	\N	\N	f	f
768	PROJECT	Project	Lariosa Lumber Corporation	156224	2022-08-02 20:25:08.453593+00	2022-08-02 20:25:08.45362+00	1	\N	\N	f	f
769	PROJECT	Project	Huck Apartments Inc.	156225	2022-08-02 20:25:08.453677+00	2022-08-02 20:25:08.453704+00	1	\N	\N	f	f
770	PROJECT	Project	Ausbrooks Construction Incorporated	156226	2022-08-02 20:25:08.453777+00	2022-08-02 20:25:08.453833+00	1	\N	\N	f	f
771	PROJECT	Project	Riede Title and Associates	156227	2022-08-02 20:25:08.454037+00	2022-08-02 20:25:08.454071+00	1	\N	\N	f	f
772	PROJECT	Project	Botero Electric Co.	156228	2022-08-02 20:25:08.454184+00	2022-08-02 20:25:08.454231+00	1	\N	\N	f	f
773	PROJECT	Project	Kunstlinger Automotive Manufacturing	156229	2022-08-02 20:25:08.454883+00	2022-08-02 20:25:08.454927+00	1	\N	\N	f	f
774	PROJECT	Project	Soares Builders Inc.	156230	2022-08-02 20:25:08.455039+00	2022-08-02 20:25:08.455073+00	1	\N	\N	f	f
775	PROJECT	Project	Henneman Hardware	156231	2022-08-02 20:25:08.455482+00	2022-08-02 20:25:08.455535+00	1	\N	\N	f	f
776	PROJECT	Project	Roundtree Attorneys Inc.	156232	2022-08-02 20:25:08.455622+00	2022-08-02 20:25:08.455653+00	1	\N	\N	f	f
777	PROJECT	Project	Sandwich Telecom Sales	156233	2022-08-02 20:25:08.455749+00	2022-08-02 20:25:08.455779+00	1	\N	\N	f	f
778	PROJECT	Project	Furay and Bielawski Liquors Corporation	156234	2022-08-02 20:25:08.455844+00	2022-08-02 20:25:08.455882+00	1	\N	\N	f	f
779	PROJECT	Project	Evans Leasing Fabricators	156235	2022-08-02 20:25:08.456105+00	2022-08-02 20:25:08.456402+00	1	\N	\N	f	f
780	PROJECT	Project	Brosey Antiques -	156236	2022-08-02 20:25:08.456505+00	2022-08-02 20:25:08.456534+00	1	\N	\N	f	f
781	PROJECT	Project	Stotelmyer and Conelly Metal Fabricators Group	156237	2022-08-02 20:25:08.456594+00	2022-08-02 20:25:08.456622+00	1	\N	\N	f	f
782	PROJECT	Project	West Covina Builders Distributors	156238	2022-08-02 20:25:08.45668+00	2022-08-02 20:25:08.456707+00	1	\N	\N	f	f
783	PROJECT	Project	Fullerton Software Inc.	156239	2022-08-02 20:25:08.456765+00	2022-08-02 20:25:08.456792+00	1	\N	\N	f	f
784	PROJECT	Project	Harriott Construction Services	156240	2022-08-02 20:25:08.456849+00	2022-08-02 20:25:08.456877+00	1	\N	\N	f	f
785	PROJECT	Project	Pittsburgh Windows Incorporated	156241	2022-08-02 20:25:08.456935+00	2022-08-02 20:25:08.456962+00	1	\N	\N	f	f
786	PROJECT	Project	Olympia Antiques Management	156242	2022-08-02 20:25:08.457019+00	2022-08-02 20:25:08.457047+00	1	\N	\N	f	f
787	PROJECT	Project	Rosner and Savo Antiques Systems	156243	2022-08-02 20:25:08.457104+00	2022-08-02 20:25:08.457131+00	1	\N	\N	f	f
788	PROJECT	Project	Melville Painting Rentals	156244	2022-08-02 20:25:08.457188+00	2022-08-02 20:25:08.460307+00	1	\N	\N	f	f
789	PROJECT	Project	Knotek Hospital Company	156245	2022-08-02 20:25:08.460409+00	2022-08-02 20:25:08.460438+00	1	\N	\N	f	f
790	PROJECT	Project	Manivong Apartments Incorporated	156246	2022-08-02 20:25:08.4605+00	2022-08-02 20:25:08.460527+00	1	\N	\N	f	f
791	PROJECT	Project	Port Townsend Title Corporation	156247	2022-08-02 20:25:08.460586+00	2022-08-02 20:25:08.460613+00	1	\N	\N	f	f
792	PROJECT	Project	Harrop Attorneys Inc.	156248	2022-08-02 20:25:08.460671+00	2022-08-02 20:25:08.460698+00	1	\N	\N	f	f
793	PROJECT	Project	Mackie Painting Company	156249	2022-08-02 20:25:08.460756+00	2022-08-02 20:25:08.460783+00	1	\N	\N	f	f
794	PROJECT	Project	Busacker Liquors Services	156250	2022-08-02 20:25:08.46084+00	2022-08-02 20:25:08.460867+00	1	\N	\N	f	f
795	PROJECT	Project	Franklin Windows Inc.	156251	2022-08-02 20:25:08.460925+00	2022-08-02 20:25:08.460952+00	1	\N	\N	f	f
796	PROJECT	Project	Hurlbutt Markets -	156252	2022-08-02 20:25:08.461009+00	2022-08-02 20:25:08.461036+00	1	\N	\N	f	f
797	PROJECT	Project	Mcelderry Apartments Systems	156253	2022-08-02 20:25:08.461093+00	2022-08-02 20:25:08.461119+00	1	\N	\N	f	f
798	PROJECT	Project	Storch Title Manufacturing	156254	2022-08-02 20:25:08.463384+00	2022-08-02 20:25:08.463457+00	1	\N	\N	f	f
799	PROJECT	Project	Lindman and Kastens Antiques -	156255	2022-08-02 20:25:08.463827+00	2022-08-02 20:25:08.463877+00	1	\N	\N	f	f
800	PROJECT	Project	Gesamondo Construction Leasing	156256	2022-08-02 20:25:08.463963+00	2022-08-02 20:25:08.463993+00	1	\N	\N	f	f
801	PROJECT	Project	Kelleher Title Services	156257	2022-08-02 20:25:08.464055+00	2022-08-02 20:25:08.464096+00	1	\N	\N	f	f
802	PROJECT	Project	Liechti Lumber Sales	156258	2022-08-02 20:25:08.464417+00	2022-08-02 20:25:08.464449+00	1	\N	\N	f	f
803	PROJECT	Project	Ruts Construction Holding Corp.	156259	2022-08-02 20:25:08.464518+00	2022-08-02 20:25:08.464546+00	1	\N	\N	f	f
804	PROJECT	Project	Pickler Construction Leasing	156260	2022-08-02 20:25:08.464602+00	2022-08-02 20:25:08.46463+00	1	\N	\N	f	f
805	PROJECT	Project	Helfenbein Apartments Co.	156261	2022-08-02 20:25:08.464686+00	2022-08-02 20:25:08.464713+00	1	\N	\N	f	f
806	PROJECT	Project	Lucic and Perfect Publishing Systems	156262	2022-08-02 20:25:08.464771+00	2022-08-02 20:25:08.464798+00	1	\N	\N	f	f
807	PROJECT	Project	Baumgarn Windows and Associates	156263	2022-08-02 20:25:08.464854+00	2022-08-02 20:25:08.464882+00	1	\N	\N	f	f
808	PROJECT	Project	Dorey Attorneys Distributors	156264	2022-08-02 20:25:08.464938+00	2022-08-02 20:25:08.464965+00	1	\N	\N	f	f
809	PROJECT	Project	Estanislau and Brodka Electric Holding Corp.	156265	2022-08-02 20:25:08.499163+00	2022-08-02 20:25:08.499233+00	1	\N	\N	f	f
810	PROJECT	Project	Owasso Attorneys Holding Corp.	156266	2022-08-02 20:25:08.499346+00	2022-08-02 20:25:08.499388+00	1	\N	\N	f	f
811	PROJECT	Project	Astry Software Holding Corp.	156267	2022-08-02 20:25:08.499487+00	2022-08-02 20:25:08.499526+00	1	\N	\N	f	f
812	PROJECT	Project	Quiterio Windows Co.	156268	2022-08-02 20:25:08.499642+00	2022-08-02 20:25:08.499686+00	1	\N	\N	f	f
813	PROJECT	Project	Bramucci Construction	156269	2022-08-02 20:25:08.499792+00	2022-08-02 20:25:08.499839+00	1	\N	\N	f	f
814	PROJECT	Project	Swanger Spirits	156270	2022-08-02 20:25:08.49996+00	2022-08-02 20:25:08.500006+00	1	\N	\N	f	f
815	PROJECT	Project	Hemauer Builders Inc.	156271	2022-08-02 20:25:08.50036+00	2022-08-02 20:25:08.500403+00	1	\N	\N	f	f
816	PROJECT	Project	Reisdorf Title Services	156272	2022-08-02 20:25:08.500505+00	2022-08-02 20:25:08.500547+00	1	\N	\N	f	f
817	PROJECT	Project	Timinsky Lumber Dynamics	156273	2022-08-02 20:25:08.500645+00	2022-08-02 20:25:08.500685+00	1	\N	\N	f	f
818	PROJECT	Project	Lurtz Painting Co.	156274	2022-08-02 20:25:08.500783+00	2022-08-02 20:25:08.500823+00	1	\N	\N	f	f
819	PROJECT	Project	Svancara Antiques Holding Corp.	156276	2022-08-02 20:25:08.500918+00	2022-08-02 20:25:08.500959+00	1	\N	\N	f	f
820	PROJECT	Project	Meisner Software Inc.	156277	2022-08-02 20:25:08.501053+00	2022-08-02 20:25:08.501093+00	1	\N	\N	f	f
821	PROJECT	Project	Selia Metal Fabricators Company	156278	2022-08-02 20:25:08.501327+00	2022-08-02 20:25:08.501369+00	1	\N	\N	f	f
822	PROJECT	Project	Ashley Smoth	156279	2022-08-02 20:25:08.501466+00	2022-08-02 20:25:08.501506+00	1	\N	\N	f	f
823	PROJECT	Project	Qualle Metal Fabricators Distributors	156280	2022-08-02 20:25:08.5016+00	2022-08-02 20:25:08.50164+00	1	\N	\N	f	f
824	PROJECT	Project	Sarchett Antiques Networking	156281	2022-08-02 20:25:08.501733+00	2022-08-02 20:25:08.501773+00	1	\N	\N	f	f
825	PROJECT	Project	Zucca Electric Agency	156282	2022-08-02 20:25:08.501866+00	2022-08-02 20:25:08.501906+00	1	\N	\N	f	f
826	PROJECT	Project	Hurtgen Hospital Manufacturing	156283	2022-08-02 20:25:08.502004+00	2022-08-02 20:25:08.502044+00	1	\N	\N	f	f
827	PROJECT	Project	Koshi Metal Fabricators Corporation	156284	2022-08-02 20:25:08.502136+00	2022-08-02 20:25:08.502177+00	1	\N	\N	f	f
828	PROJECT	Project	Dorminy Windows Rentals	156285	2022-08-02 20:25:08.50227+00	2022-08-02 20:25:08.50231+00	1	\N	\N	f	f
829	PROJECT	Project	Ammann Builders Fabricators	156286	2022-08-02 20:25:08.502545+00	2022-08-02 20:25:08.502589+00	1	\N	\N	f	f
830	PROJECT	Project	Bezak Construction Dynamics	156287	2022-08-02 20:25:08.502685+00	2022-08-02 20:25:08.502725+00	1	\N	\N	f	f
831	PROJECT	Project	Therrell Publishing Networking	156288	2022-08-02 20:25:08.502936+00	2022-08-02 20:25:08.502976+00	1	\N	\N	f	f
832	PROJECT	Project	Pigler Plumbing Management	156289	2022-08-02 20:25:08.503069+00	2022-08-02 20:25:08.503231+00	1	\N	\N	f	f
833	PROJECT	Project	Udoh Publishing Manufacturing	156290	2022-08-02 20:25:08.503338+00	2022-08-02 20:25:08.503381+00	1	\N	\N	f	f
834	PROJECT	Project	Osler Antiques -	156291	2022-08-02 20:25:08.503486+00	2022-08-02 20:25:08.503528+00	1	\N	\N	f	f
835	PROJECT	Project	Garitty Metal Fabricators Rentals	156292	2022-08-02 20:25:08.503627+00	2022-08-02 20:25:08.503667+00	1	\N	\N	f	f
836	PROJECT	Project	Duroseau Publishing	156293	2022-08-02 20:25:08.503788+00	2022-08-02 20:25:08.5041+00	1	\N	\N	f	f
837	PROJECT	Project	Wiesel Construction Dynamics	156294	2022-08-02 20:25:08.505439+00	2022-08-02 20:25:08.505528+00	1	\N	\N	f	f
838	PROJECT	Project	Scholl Catering -	156295	2022-08-02 20:25:08.506342+00	2022-08-02 20:25:08.506406+00	1	\N	\N	f	f
839	PROJECT	Project	Santa Monica Attorneys Manufacturing	156296	2022-08-02 20:25:08.506536+00	2022-08-02 20:25:08.506583+00	1	\N	\N	f	f
840	PROJECT	Project	Jasmer Antiques Management	156297	2022-08-02 20:25:08.506816+00	2022-08-02 20:25:08.506868+00	1	\N	\N	f	f
841	PROJECT	Project	Alesna Leasing Sales	156298	2022-08-02 20:25:08.507026+00	2022-08-02 20:25:08.50707+00	1	\N	\N	f	f
842	PROJECT	Project	Ortego Construction Distributors	156299	2022-08-02 20:25:08.507337+00	2022-08-02 20:25:08.507383+00	1	\N	\N	f	f
843	PROJECT	Project	Kirkville Builders -	156300	2022-08-02 20:25:08.507485+00	2022-08-02 20:25:08.507526+00	1	\N	\N	f	f
844	PROJECT	Project	Glore Apartments Distributors	156301	2022-08-02 20:25:08.507629+00	2022-08-02 20:25:08.507669+00	1	\N	\N	f	f
845	PROJECT	Project	Konecny Markets Co.	156302	2022-08-02 20:25:08.50777+00	2022-08-02 20:25:08.50781+00	1	\N	\N	f	f
846	PROJECT	Project	Colony Antiques	156303	2022-08-02 20:25:08.507943+00	2022-08-02 20:25:08.507982+00	1	\N	\N	f	f
847	PROJECT	Project	Harriage Plumbing Dynamics	156304	2022-08-02 20:25:08.508082+00	2022-08-02 20:25:08.508121+00	1	\N	\N	f	f
848	PROJECT	Project	Tracy Attorneys Management	156305	2022-08-02 20:25:08.508222+00	2022-08-02 20:25:08.508268+00	1	\N	\N	f	f
849	PROJECT	Project	Barnhurst Title Inc.	156306	2022-08-02 20:25:08.508783+00	2022-08-02 20:25:08.508834+00	1	\N	\N	f	f
850	PROJECT	Project	Rey Software Inc.	156307	2022-08-02 20:25:08.50894+00	2022-08-02 20:25:08.508982+00	1	\N	\N	f	f
851	PROJECT	Project	Hawk Liquors Agency	156308	2022-08-02 20:25:08.509082+00	2022-08-02 20:25:08.509123+00	1	\N	\N	f	f
852	PROJECT	Project	Yarnell Catering Holding Corp.	156309	2022-08-02 20:25:08.509221+00	2022-08-02 20:25:08.5094+00	1	\N	\N	f	f
853	PROJECT	Project	Wolfenden Markets Holding Corp.	156310	2022-08-02 20:25:08.509508+00	2022-08-02 20:25:08.50955+00	1	\N	\N	f	f
854	PROJECT	Project	Alamo Catering Group	156311	2022-08-02 20:25:08.509646+00	2022-08-02 20:25:08.509684+00	1	\N	\N	f	f
855	PROJECT	Project	Frankland Attorneys Sales	156312	2022-08-02 20:25:08.509778+00	2022-08-02 20:25:08.509817+00	1	\N	\N	f	f
856	PROJECT	Project	San Diego Plumbing Distributors	156313	2022-08-02 20:25:08.509958+00	2022-08-02 20:25:08.51+00	1	\N	\N	f	f
857	PROJECT	Project	Schmauder Markets Corporation	156314	2022-08-02 20:25:08.51057+00	2022-08-02 20:25:08.510623+00	1	\N	\N	f	f
858	PROJECT	Project	Berthelette Antiques	156315	2022-08-02 20:25:08.510732+00	2022-08-02 20:25:08.510772+00	1	\N	\N	f	f
859	PROJECT	Project	Pittsburgh Quantum Analytics	156316	2022-08-02 20:25:08.540207+00	2022-08-02 20:25:08.540258+00	1	\N	\N	f	f
1421	PROJECT	Project	Flores Inc	156881	2022-08-02 20:25:09.968364+00	2022-08-02 20:25:09.968392+00	1	\N	\N	f	f
860	PROJECT	Project	Veradale Telecom Manufacturing	156317	2022-08-02 20:25:08.540438+00	2022-08-02 20:25:08.540471+00	1	\N	\N	f	f
861	PROJECT	Project	Zurasky Markets Dynamics	156318	2022-08-02 20:25:08.540537+00	2022-08-02 20:25:08.540567+00	1	\N	\N	f	f
862	PROJECT	Project	Asch _ Agency	156319	2022-08-02 20:25:08.54063+00	2022-08-02 20:25:08.54066+00	1	\N	\N	f	f
863	PROJECT	Project	Helvey Catering Distributors	156320	2022-08-02 20:25:08.540722+00	2022-08-02 20:25:08.540752+00	1	\N	\N	f	f
864	PROJECT	Project	Wicklund Leasing Corporation	156321	2022-08-02 20:25:08.540815+00	2022-08-02 20:25:08.540844+00	1	\N	\N	f	f
865	PROJECT	Project	Ahonen Catering Group	156322	2022-08-02 20:25:08.540906+00	2022-08-02 20:25:08.540935+00	1	\N	\N	f	f
866	PROJECT	Project	Diluzio Automotive Group	156323	2022-08-02 20:25:08.54103+00	2022-08-02 20:25:08.541074+00	1	\N	\N	f	f
867	PROJECT	Project	Simi Valley Telecom Dynamics	156324	2022-08-02 20:25:08.541153+00	2022-08-02 20:25:08.541423+00	1	\N	\N	f	f
868	PROJECT	Project	Purchase Construction Agency	156325	2022-08-02 20:25:08.541558+00	2022-08-02 20:25:08.541588+00	1	\N	\N	f	f
869	PROJECT	Project	Seyler Title Distributors	156326	2022-08-02 20:25:08.541651+00	2022-08-02 20:25:08.54182+00	1	\N	\N	f	f
870	PROJECT	Project	Clubb Electric Co.	156327	2022-08-02 20:25:08.542366+00	2022-08-02 20:25:08.542688+00	1	\N	\N	f	f
871	PROJECT	Project	Eliszewski Windows Dynamics	156328	2022-08-02 20:25:08.542825+00	2022-08-02 20:25:08.54287+00	1	\N	\N	f	f
872	PROJECT	Project	Ruleman Title Distributors	156329	2022-08-02 20:25:08.543384+00	2022-08-02 20:25:08.543483+00	1	\N	\N	f	f
873	PROJECT	Project	El Paso Hardware Co.	156330	2022-08-02 20:25:08.576721+00	2022-08-02 20:25:08.576802+00	1	\N	\N	f	f
874	PROJECT	Project	Belgrade Telecom -	156331	2022-08-02 20:25:08.576962+00	2022-08-02 20:25:08.577016+00	1	\N	\N	f	f
875	PROJECT	Project	Keblish Catering Distributors	156332	2022-08-02 20:25:08.577147+00	2022-08-02 20:25:08.577195+00	1	\N	\N	f	f
876	PROJECT	Project	Kempker Title Manufacturing	156333	2022-08-02 20:25:08.577822+00	2022-08-02 20:25:08.577903+00	1	\N	\N	f	f
877	PROJECT	Project	Penister Hospital Fabricators	156334	2022-08-02 20:25:08.57813+00	2022-08-02 20:25:08.578194+00	1	\N	\N	f	f
878	PROJECT	Project	Foxe Windows Management	156335	2022-08-02 20:25:08.578545+00	2022-08-02 20:25:08.578596+00	1	\N	\N	f	f
879	PROJECT	Project	Constanza Liquors -	156336	2022-08-02 20:25:08.578777+00	2022-08-02 20:25:08.578809+00	1	\N	\N	f	f
880	PROJECT	Project	Gallaugher Title Dynamics	156337	2022-08-02 20:25:08.57887+00	2022-08-02 20:25:08.5789+00	1	\N	\N	f	f
881	PROJECT	Project	Barham Automotive Services	156338	2022-08-02 20:25:08.578961+00	2022-08-02 20:25:08.578991+00	1	\N	\N	f	f
882	PROJECT	Project	Kerekes Lumber Networking	156339	2022-08-02 20:25:08.579052+00	2022-08-02 20:25:08.579081+00	1	\N	\N	f	f
883	PROJECT	Project	Poland and Burrus Plumbing	156340	2022-08-02 20:25:08.579141+00	2022-08-02 20:25:08.579171+00	1	\N	\N	f	f
884	PROJECT	Project	Labarba Markets Corporation	156341	2022-08-02 20:25:08.579253+00	2022-08-02 20:25:08.579282+00	1	\N	\N	f	f
885	PROJECT	Project	Broadnay and Posthuma Lumber and Associates	156342	2022-08-02 20:25:08.579343+00	2022-08-02 20:25:08.579373+00	1	\N	\N	f	f
886	PROJECT	Project	Indianapolis Liquors Rentals	156343	2022-08-02 20:25:08.579433+00	2022-08-02 20:25:08.579462+00	1	\N	\N	f	f
887	PROJECT	Project	Republic Builders and Associates	156344	2022-08-02 20:25:08.579523+00	2022-08-02 20:25:08.579552+00	1	\N	\N	f	f
888	PROJECT	Project	Slankard Automotive	156345	2022-08-02 20:25:08.579613+00	2022-08-02 20:25:08.579796+00	1	\N	\N	f	f
889	PROJECT	Project	Florence Liquors and Associates	156346	2022-08-02 20:25:08.579943+00	2022-08-02 20:25:08.579976+00	1	\N	\N	f	f
890	PROJECT	Project	Gauch Metal Fabricators Sales	156347	2022-08-02 20:25:08.580081+00	2022-08-02 20:25:08.580134+00	1	\N	\N	f	f
891	PROJECT	Project	Kemme Builders Management	156348	2022-08-02 20:25:08.58023+00	2022-08-02 20:25:08.580389+00	1	\N	\N	f	f
892	PROJECT	Project	Palys Attorneys	156349	2022-08-02 20:25:08.580454+00	2022-08-02 20:25:08.580483+00	1	\N	\N	f	f
893	PROJECT	Project	Yockey Markets Inc.	156350	2022-08-02 20:25:08.580544+00	2022-08-02 20:25:08.580573+00	1	\N	\N	f	f
894	PROJECT	Project	Formisano Hardware -	156351	2022-08-02 20:25:08.580633+00	2022-08-02 20:25:08.580662+00	1	\N	\N	f	f
895	PROJECT	Project	Ede Title Rentals	156352	2022-08-02 20:25:08.580722+00	2022-08-02 20:25:08.580751+00	1	\N	\N	f	f
896	PROJECT	Project	Marabella Title Agency	156353	2022-08-02 20:25:08.580811+00	2022-08-02 20:25:08.58084+00	1	\N	\N	f	f
897	PROJECT	Project	AcuVision Eye Centre	156354	2022-08-02 20:25:08.5809+00	2022-08-02 20:25:08.580929+00	1	\N	\N	f	f
898	PROJECT	Project	Computer Training Associates	156355	2022-08-02 20:25:08.580989+00	2022-08-02 20:25:08.581018+00	1	\N	\N	f	f
899	PROJECT	Project	Gregory Daniels	156356	2022-08-02 20:25:08.581077+00	2022-08-02 20:25:08.581106+00	1	\N	\N	f	f
900	PROJECT	Project	Cheese Factory	156357	2022-08-02 20:25:08.581166+00	2022-08-02 20:25:08.581195+00	1	\N	\N	f	f
901	PROJECT	Project	Timmy Brown	156358	2022-08-02 20:25:08.581255+00	2022-08-02 20:25:08.581284+00	1	\N	\N	f	f
902	PROJECT	Project	Sally Ward	156359	2022-08-02 20:25:08.581344+00	2022-08-02 20:25:08.581372+00	1	\N	\N	f	f
903	PROJECT	Project	Art Institute of California	156360	2022-08-02 20:25:08.581432+00	2022-08-02 20:25:08.581461+00	1	\N	\N	f	f
904	PROJECT	Project	All Occassions Event Coordination	156361	2022-08-02 20:25:08.581521+00	2022-08-02 20:25:08.58155+00	1	\N	\N	f	f
905	PROJECT	Project	By The Beach Cafe	156362	2022-08-02 20:25:08.58161+00	2022-08-02 20:25:08.581639+00	1	\N	\N	f	f
906	PROJECT	Project	Superior Car care Inc.	156363	2022-08-02 20:25:08.5817+00	2022-08-02 20:25:08.581729+00	1	\N	\N	f	f
907	PROJECT	Project	Wilson Kaplan	156364	2022-08-02 20:25:08.581789+00	2022-08-02 20:25:08.581817+00	1	\N	\N	f	f
908	PROJECT	Project	Holly Romine	156365	2022-08-02 20:25:08.581877+00	2022-08-02 20:25:08.581906+00	1	\N	\N	f	f
909	PROJECT	Project	Tamara Gibson	156366	2022-08-02 20:25:09.05058+00	2022-08-02 20:25:09.050615+00	1	\N	\N	f	f
910	PROJECT	Project	Avani Walters	156367	2022-08-02 20:25:09.05067+00	2022-08-02 20:25:09.050701+00	1	\N	\N	f	f
911	PROJECT	Project	Bolder Construction Inc.	156368	2022-08-02 20:25:09.050758+00	2022-08-02 20:25:09.05078+00	1	\N	\N	f	f
912	PROJECT	Project	Woods Publishing Co.	156369	2022-08-02 20:25:09.050874+00	2022-08-02 20:25:09.051006+00	1	\N	\N	f	f
913	PROJECT	Project	Charlotte Hospital Incorporated	156370	2022-08-02 20:25:09.052761+00	2022-08-02 20:25:09.053361+00	1	\N	\N	f	f
914	PROJECT	Project	Caquias and Jank Catering Distributors	156371	2022-08-02 20:25:09.053515+00	2022-08-02 20:25:09.05354+00	1	\N	\N	f	f
915	PROJECT	Project	Lonabaugh Markets Distributors	156372	2022-08-02 20:25:09.053596+00	2022-08-02 20:25:09.053623+00	1	\N	\N	f	f
916	PROJECT	Project	Barich Metal Fabricators Inc.	156373	2022-08-02 20:25:09.054879+00	2022-08-02 20:25:09.055+00	1	\N	\N	f	f
917	PROJECT	Project	All Outdoors	156374	2022-08-02 20:25:09.170356+00	2022-08-02 20:25:09.170456+00	1	\N	\N	f	f
918	PROJECT	Project	Hanninen Painting Distributors	156375	2022-08-02 20:25:09.170641+00	2022-08-02 20:25:09.17068+00	1	\N	\N	f	f
919	PROJECT	Project	Orange Leasing -	156376	2022-08-02 20:25:09.170763+00	2022-08-02 20:25:09.170802+00	1	\N	\N	f	f
920	PROJECT	Project	Bright Brothers Design	156377	2022-08-02 20:25:09.170892+00	2022-08-02 20:25:09.170931+00	1	\N	\N	f	f
921	PROJECT	Project	Tanya Guerrero	156378	2022-08-02 20:25:09.17102+00	2022-08-02 20:25:09.171058+00	1	\N	\N	f	f
922	PROJECT	Project	Kara's Cafe	156379	2022-08-02 20:25:09.171146+00	2022-08-02 20:25:09.171176+00	1	\N	\N	f	f
923	PROJECT	Project	Foxmoor Formula	156380	2022-08-02 20:25:09.171764+00	2022-08-02 20:25:09.173424+00	1	\N	\N	f	f
924	PROJECT	Project	Sharon Stone	156381	2022-08-02 20:25:09.17389+00	2022-08-02 20:25:09.173953+00	1	\N	\N	f	f
925	PROJECT	Project	John Boba	156382	2022-08-02 20:25:09.17431+00	2022-08-02 20:25:09.174609+00	1	\N	\N	f	f
926	PROJECT	Project	Kramer Construction	156385	2022-08-02 20:25:09.174764+00	2022-08-02 20:25:09.174818+00	1	\N	\N	f	f
927	PROJECT	Project	Champaign Painting Rentals	156386	2022-08-02 20:25:09.191473+00	2022-08-02 20:25:09.191544+00	1	\N	\N	f	f
928	PROJECT	Project	Pilkerton Windows Sales	156387	2022-08-02 20:25:09.1917+00	2022-08-02 20:25:09.191743+00	1	\N	\N	f	f
929	PROJECT	Project	Agrela Apartments Agency	156388	2022-08-02 20:25:09.191845+00	2022-08-02 20:25:09.191886+00	1	\N	\N	f	f
930	PROJECT	Project	Whetzell and Maymon Antiques Sales	156389	2022-08-02 20:25:09.196597+00	2022-08-02 20:25:09.19679+00	1	\N	\N	f	f
931	PROJECT	Project	Holgerson Automotive Services	156390	2022-08-02 20:25:09.196857+00	2022-08-02 20:25:09.196886+00	1	\N	\N	f	f
932	PROJECT	Project	Imperial Liquors Distributors	156391	2022-08-02 20:25:09.196944+00	2022-08-02 20:25:09.196971+00	1	\N	\N	f	f
933	PROJECT	Project	Coressel _ -	156392	2022-08-02 20:25:09.197029+00	2022-08-02 20:25:09.197056+00	1	\N	\N	f	f
934	PROJECT	Project	Moreb Plumbing Corporation	156393	2022-08-02 20:25:09.197113+00	2022-08-02 20:25:09.197363+00	1	\N	\N	f	f
935	PROJECT	Project	Zechiel _ Management	156394	2022-08-02 20:25:09.197457+00	2022-08-02 20:25:09.197485+00	1	\N	\N	f	f
936	PROJECT	Project	Danniels Antiques Inc.	156395	2022-08-02 20:25:09.197543+00	2022-08-02 20:25:09.197571+00	1	\N	\N	f	f
937	PROJECT	Project	Bertot Attorneys Company	156396	2022-08-02 20:25:09.197628+00	2022-08-02 20:25:09.197655+00	1	\N	\N	f	f
938	PROJECT	Project	Vanwyngaarden Title Systems	156397	2022-08-02 20:25:09.197712+00	2022-08-02 20:25:09.197749+00	1	\N	\N	f	f
939	PROJECT	Project	Slatter Metal Fabricators Inc.	156398	2022-08-02 20:25:09.197817+00	2022-08-02 20:25:09.197844+00	1	\N	\N	f	f
940	PROJECT	Project	Hirschy and Fahrenwald Liquors Incorporated	156399	2022-08-02 20:25:09.197901+00	2022-08-02 20:25:09.197928+00	1	\N	\N	f	f
941	PROJECT	Project	Mcburnie Hardware Dynamics	156400	2022-08-02 20:25:09.197985+00	2022-08-02 20:25:09.198012+00	1	\N	\N	f	f
942	PROJECT	Project	Vance Construction and Associates	156401	2022-08-02 20:25:09.198069+00	2022-08-02 20:25:09.198096+00	1	\N	\N	f	f
943	PROJECT	Project	Days Creek Electric Services	156402	2022-08-02 20:25:09.198152+00	2022-08-02 20:25:09.198179+00	1	\N	\N	f	f
944	PROJECT	Project	Wasager Wine Sales	156403	2022-08-02 20:25:09.19832+00	2022-08-02 20:25:09.209662+00	1	\N	\N	f	f
945	PROJECT	Project	Jelle Catering Group	156404	2022-08-02 20:25:09.209986+00	2022-08-02 20:25:09.210016+00	1	\N	\N	f	f
946	PROJECT	Project	Scottsbluff Lumber -	156405	2022-08-02 20:25:09.210297+00	2022-08-02 20:25:09.210373+00	1	\N	\N	f	f
947	PROJECT	Project	Pagliari Builders Services	156406	2022-08-02 20:25:09.210538+00	2022-08-02 20:25:09.210557+00	1	\N	\N	f	f
948	PROJECT	Project	Cwik and Klayman Metal Fabricators Holding Corp.	156407	2022-08-02 20:25:09.210725+00	2022-08-02 20:25:09.21075+00	1	\N	\N	f	f
949	PROJECT	Project	Schlicker Metal Fabricators Fabricators	156408	2022-08-02 20:25:09.210929+00	2022-08-02 20:25:09.211045+00	1	\N	\N	f	f
950	PROJECT	Project	Lanning and Urraca Construction Corporation	156409	2022-08-02 20:25:09.211103+00	2022-08-02 20:25:09.211128+00	1	\N	\N	f	f
951	PROJECT	Project	Grana Automotive and Associates	156410	2022-08-02 20:25:09.211181+00	2022-08-02 20:25:09.211471+00	1	\N	\N	f	f
952	PROJECT	Project	Fetterolf and Loud Apartments Inc.	156411	2022-08-02 20:25:09.211872+00	2022-08-02 20:25:09.211903+00	1	\N	\N	f	f
953	PROJECT	Project	Eckler Leasing	156412	2022-08-02 20:25:09.212205+00	2022-08-02 20:25:09.212236+00	1	\N	\N	f	f
954	PROJECT	Project	Galas Electric Rentals	156413	2022-08-02 20:25:09.214234+00	2022-08-02 20:25:09.214526+00	1	\N	\N	f	f
955	PROJECT	Project	Aslanian Publishing Agency	156414	2022-08-02 20:25:09.21768+00	2022-08-02 20:25:09.217827+00	1	\N	\N	f	f
956	PROJECT	Project	Wilkey Markets Group	156415	2022-08-02 20:25:09.218592+00	2022-08-02 20:25:09.218845+00	1	\N	\N	f	f
957	PROJECT	Project	Ostling Metal Fabricators Fabricators	156416	2022-08-02 20:25:09.219008+00	2022-08-02 20:25:09.219305+00	1	\N	\N	f	f
958	PROJECT	Project	Siddiq Software -	156417	2022-08-02 20:25:09.219558+00	2022-08-02 20:25:09.219633+00	1	\N	\N	f	f
959	PROJECT	Project	Mineral Painting Inc.	156418	2022-08-02 20:25:09.231749+00	2022-08-02 20:25:09.231799+00	1	\N	\N	f	f
960	PROJECT	Project	Taback Construction Leasing	156419	2022-08-02 20:25:09.231878+00	2022-08-02 20:25:09.23191+00	1	\N	\N	f	f
961	PROJECT	Project	Symore Construction Dynamics	156420	2022-08-02 20:25:09.231979+00	2022-08-02 20:25:09.232009+00	1	\N	\N	f	f
962	PROJECT	Project	Urwin Leasing Group	156421	2022-08-02 20:25:09.23246+00	2022-08-02 20:25:09.232645+00	1	\N	\N	f	f
963	PROJECT	Project	Dries Hospital Manufacturing	156422	2022-08-02 20:25:09.232879+00	2022-08-02 20:25:09.232923+00	1	\N	\N	f	f
964	PROJECT	Project	Colorado Springs Leasing Fabricators	156423	2022-08-02 20:25:09.233431+00	2022-08-02 20:25:09.233469+00	1	\N	\N	f	f
965	PROJECT	Project	Ramal Builders Incorporated	156424	2022-08-02 20:25:09.233691+00	2022-08-02 20:25:09.233861+00	1	\N	\N	f	f
966	PROJECT	Project	Touchard Liquors Holding Corp.	156425	2022-08-02 20:25:09.234184+00	2022-08-02 20:25:09.234294+00	1	\N	\N	f	f
967	PROJECT	Project	Wilner Liquors	156426	2022-08-02 20:25:09.234583+00	2022-08-02 20:25:09.234629+00	1	\N	\N	f	f
968	PROJECT	Project	Lancaster Liquors Inc.	156427	2022-08-02 20:25:09.234725+00	2022-08-02 20:25:09.234766+00	1	\N	\N	f	f
969	PROJECT	Project	Brick Metal Fabricators Services	156428	2022-08-02 20:25:09.234878+00	2022-08-02 20:25:09.234917+00	1	\N	\N	f	f
970	PROJECT	Project	Hollyday Construction Networking	156429	2022-08-02 20:25:09.235007+00	2022-08-02 20:25:09.235047+00	1	\N	\N	f	f
971	PROJECT	Project	Yahl Markets Incorporated	156430	2022-08-02 20:25:09.235138+00	2022-08-02 20:25:09.235178+00	1	\N	\N	f	f
972	PROJECT	Project	Gilcrease Telecom Systems	156431	2022-08-02 20:25:09.235268+00	2022-08-02 20:25:09.235307+00	1	\N	\N	f	f
973	PROJECT	Project	Doerrer Apartments Inc.	156432	2022-08-02 20:25:09.235398+00	2022-08-02 20:25:09.235436+00	1	\N	\N	f	f
974	PROJECT	Project	Johar Software Corporation	156433	2022-08-02 20:25:09.235721+00	2022-08-02 20:25:09.235752+00	1	\N	\N	f	f
975	PROJECT	Project	Freier Markets Incorporated	156434	2022-08-02 20:25:09.235814+00	2022-08-02 20:25:09.235843+00	1	\N	\N	f	f
976	PROJECT	Project	Panora Lumber Dynamics	156435	2022-08-02 20:25:09.235905+00	2022-08-02 20:25:09.235933+00	1	\N	\N	f	f
977	PROJECT	Project	Antioch Construction Company	156436	2022-08-02 20:25:09.235994+00	2022-08-02 20:25:09.236023+00	1	\N	\N	f	f
978	PROJECT	Project	Burney and Oesterreich Title Manufacturing	156437	2022-08-02 20:25:09.236083+00	2022-08-02 20:25:09.236112+00	1	\N	\N	f	f
979	PROJECT	Project	Colosimo Catering and Associates	156438	2022-08-02 20:25:09.236173+00	2022-08-02 20:25:09.236201+00	1	\N	\N	f	f
980	PROJECT	Project	Tarangelo and Mccrea Apartments Holding Corp.	156439	2022-08-02 20:25:09.236262+00	2022-08-02 20:25:09.236291+00	1	\N	\N	f	f
981	PROJECT	Project	Conterras and Katen Attorneys Services	156440	2022-08-02 20:25:09.236351+00	2022-08-02 20:25:09.236685+00	1	\N	\N	f	f
982	PROJECT	Project	Sindt Electric	156441	2022-08-02 20:25:09.237056+00	2022-08-02 20:25:09.237245+00	1	\N	\N	f	f
983	PROJECT	Project	Below Liquors Corporation	156442	2022-08-02 20:25:09.237475+00	2022-08-02 20:25:09.237631+00	1	\N	\N	f	f
984	PROJECT	Project	Wraight Software and Associates	156443	2022-08-02 20:25:09.2377+00	2022-08-02 20:25:09.237859+00	1	\N	\N	f	f
985	PROJECT	Project	Niedzwiedz Antiques and Associates	156444	2022-08-02 20:25:09.238036+00	2022-08-02 20:25:09.23807+00	1	\N	\N	f	f
986	PROJECT	Project	Ostrzyeki Markets Distributors	156445	2022-08-02 20:25:09.2387+00	2022-08-02 20:25:09.238876+00	1	\N	\N	f	f
987	PROJECT	Project	Largo Lumber Co.	156446	2022-08-02 20:25:09.239269+00	2022-08-02 20:25:09.23933+00	1	\N	\N	f	f
988	PROJECT	Project	Bethurum Telecom Sales	156447	2022-08-02 20:25:09.239684+00	2022-08-02 20:25:09.239794+00	1	\N	\N	f	f
989	PROJECT	Project	Seney Windows Agency	156448	2022-08-02 20:25:09.240346+00	2022-08-02 20:25:09.240392+00	1	\N	\N	f	f
990	PROJECT	Project	Kallmeyer Antiques Dynamics	156449	2022-08-02 20:25:09.240613+00	2022-08-02 20:25:09.240814+00	1	\N	\N	f	f
991	PROJECT	Project	San Angelo Automotive Rentals	156450	2022-08-02 20:25:09.241059+00	2022-08-02 20:25:09.241091+00	1	\N	\N	f	f
992	PROJECT	Project	Rezentes Catering Dynamics	156451	2022-08-02 20:25:09.241151+00	2022-08-02 20:25:09.241178+00	1	\N	\N	f	f
993	PROJECT	Project	Downey Catering Agency	156452	2022-08-02 20:25:09.241235+00	2022-08-02 20:25:09.241385+00	1	\N	\N	f	f
994	PROJECT	Project	Vanaken Apartments Holding Corp.	156453	2022-08-02 20:25:09.241454+00	2022-08-02 20:25:09.241482+00	1	\N	\N	f	f
995	PROJECT	Project	Cottew Publishing Inc.	156454	2022-08-02 20:25:09.241539+00	2022-08-02 20:25:09.241566+00	1	\N	\N	f	f
996	PROJECT	Project	Honolulu Markets Group	156455	2022-08-02 20:25:09.241622+00	2022-08-02 20:25:09.241649+00	1	\N	\N	f	f
997	PROJECT	Project	Janiak Attorneys Inc.	156456	2022-08-02 20:25:09.241705+00	2022-08-02 20:25:09.241733+00	1	\N	\N	f	f
998	PROJECT	Project	Guzalak Leasing Leasing	156457	2022-08-02 20:25:09.241789+00	2022-08-02 20:25:09.241816+00	1	\N	\N	f	f
999	PROJECT	Project	Coxum Software Dynamics	156458	2022-08-02 20:25:09.241872+00	2022-08-02 20:25:09.2419+00	1	\N	\N	f	f
1000	PROJECT	Project	Lompoc _ Systems	156459	2022-08-02 20:25:09.241956+00	2022-08-02 20:25:09.241983+00	1	\N	\N	f	f
1001	PROJECT	Project	Berliner Apartments Networking	156460	2022-08-02 20:25:09.242039+00	2022-08-02 20:25:09.242066+00	1	\N	\N	f	f
1002	PROJECT	Project	Marietta Title Co.	156461	2022-08-02 20:25:09.242122+00	2022-08-02 20:25:09.242149+00	1	\N	\N	f	f
1003	PROJECT	Project	Russell Telecom	156462	2022-08-02 20:25:09.242204+00	2022-08-02 20:25:09.242338+00	1	\N	\N	f	f
1004	PROJECT	Project	Beams Electric Agency	156463	2022-08-02 20:25:09.243007+00	2022-08-02 20:25:09.243043+00	1	\N	\N	f	f
1005	PROJECT	Project	Joanne Miller	156464	2022-08-02 20:25:09.243129+00	2022-08-02 20:25:09.243336+00	1	\N	\N	f	f
1006	PROJECT	Project	Amsterdam Drug Store	156465	2022-08-02 20:25:09.24345+00	2022-08-02 20:25:09.243473+00	1	\N	\N	f	f
1007	PROJECT	Project	Territory JMP 4	156466	2022-08-02 20:25:09.243536+00	2022-08-02 20:25:09.243564+00	1	\N	\N	f	f
1008	PROJECT	Project	Tower PL-01	156467	2022-08-02 20:25:09.243632+00	2022-08-02 20:25:09.243659+00	1	\N	\N	f	f
1009	PROJECT	Project	Remodel	156468	2022-08-02 20:25:09.251337+00	2022-08-02 20:25:09.251406+00	1	\N	\N	f	f
1010	PROJECT	Project	Tower AV and Telephone Install	156469	2022-08-02 20:25:09.251475+00	2022-08-02 20:25:09.251503+00	1	\N	\N	f	f
1011	PROJECT	Project	Office Remodel	156470	2022-08-02 20:25:09.251574+00	2022-08-02 20:25:09.251602+00	1	\N	\N	f	f
1012	PROJECT	Project	Lobby Remodel	156471	2022-08-02 20:25:09.251671+00	2022-08-02 20:25:09.251699+00	1	\N	\N	f	f
1013	PROJECT	Project	Parking Lot Construction	156472	2022-08-02 20:25:09.251755+00	2022-08-02 20:25:09.251782+00	1	\N	\N	f	f
1014	PROJECT	Project	FA-HB Job	156473	2022-08-02 20:25:09.251839+00	2022-08-02 20:25:09.252244+00	1	\N	\N	f	f
1015	PROJECT	Project	New Server Rack Design	156474	2022-08-02 20:25:09.252541+00	2022-08-02 20:25:09.252596+00	1	\N	\N	f	f
1016	PROJECT	Project	New Design of Rack	156475	2022-08-02 20:25:09.252748+00	2022-08-02 20:25:09.252778+00	1	\N	\N	f	f
1017	PROJECT	Project	Another Killer Product	156476	2022-08-02 20:25:09.252939+00	2022-08-02 20:25:09.252972+00	1	\N	\N	f	f
1018	PROJECT	Project	Another Killer Product 1	156477	2022-08-02 20:25:09.253031+00	2022-08-02 20:25:09.253058+00	1	\N	\N	f	f
1019	PROJECT	Project	ugkas	156478	2022-08-02 20:25:09.253115+00	2022-08-02 20:25:09.253143+00	1	\N	\N	f	f
1020	PROJECT	Project	Mcdorman Software Holding Corp.	156479	2022-08-02 20:25:09.253199+00	2022-08-02 20:25:09.253227+00	1	\N	\N	f	f
1021	PROJECT	Project	Caleb Attorneys Distributors	156480	2022-08-02 20:25:09.253554+00	2022-08-02 20:25:09.253594+00	1	\N	\N	f	f
1022	PROJECT	Project	Stoett Telecom Rentals	156481	2022-08-02 20:25:09.253803+00	2022-08-02 20:25:09.253893+00	1	\N	\N	f	f
1023	PROJECT	Project	Billafuerte Software Company	156482	2022-08-02 20:25:09.253951+00	2022-08-02 20:25:09.253977+00	1	\N	\N	f	f
1024	PROJECT	Project	Thomison Windows Networking	156483	2022-08-02 20:25:09.254036+00	2022-08-02 20:25:09.254057+00	1	\N	\N	f	f
1025	PROJECT	Project	Roswell Leasing Management	156484	2022-08-02 20:25:09.254118+00	2022-08-02 20:25:09.254184+00	1	\N	\N	f	f
1026	PROJECT	Project	Matzke Title Co.	156485	2022-08-02 20:25:09.254391+00	2022-08-02 20:25:09.25442+00	1	\N	\N	f	f
1027	PROJECT	Project	Kiedrowski Telecom Services	156486	2022-08-02 20:25:09.254477+00	2022-08-02 20:25:09.254504+00	1	\N	\N	f	f
1028	PROJECT	Project	Huntsville Apartments and Associates	156487	2022-08-02 20:25:09.25456+00	2022-08-02 20:25:09.254588+00	1	\N	\N	f	f
1029	PROJECT	Project	Webster Electric	156488	2022-08-02 20:25:09.254644+00	2022-08-02 20:25:09.254671+00	1	\N	\N	f	f
1030	PROJECT	Project	Dolfi Software Group	156489	2022-08-02 20:25:09.254727+00	2022-08-02 20:25:09.254755+00	1	\N	\N	f	f
1031	PROJECT	Project	Steep and Cloud Liquors Co.	156490	2022-08-02 20:25:09.254823+00	2022-08-02 20:25:09.254852+00	1	\N	\N	f	f
1032	PROJECT	Project	Volmink Builders Inc.	156491	2022-08-02 20:25:09.254912+00	2022-08-02 20:25:09.254949+00	1	\N	\N	f	f
1033	PROJECT	Project	Tredwell Lumber Holding Corp.	156492	2022-08-02 20:25:09.255089+00	2022-08-02 20:25:09.255118+00	1	\N	\N	f	f
1034	PROJECT	Project	Faske Software Group	156493	2022-08-02 20:25:09.255174+00	2022-08-02 20:25:09.255202+00	1	\N	\N	f	f
1035	PROJECT	Project	Umeh Telecom Management	156494	2022-08-02 20:25:09.255378+00	2022-08-02 20:25:09.255406+00	1	\N	\N	f	f
1036	PROJECT	Project	Redick Antiques Inc.	156495	2022-08-02 20:25:09.255463+00	2022-08-02 20:25:09.25549+00	1	\N	\N	f	f
1037	PROJECT	Project	San Luis Obispo Construction Inc.	156496	2022-08-02 20:25:09.255548+00	2022-08-02 20:25:09.255575+00	1	\N	\N	f	f
1038	PROJECT	Project	Pueblo Construction Fabricators	156497	2022-08-02 20:25:09.255631+00	2022-08-02 20:25:09.255658+00	1	\N	\N	f	f
1039	PROJECT	Project	Nephew Publishing Group	156498	2022-08-02 20:25:09.255715+00	2022-08-02 20:25:09.255742+00	1	\N	\N	f	f
1040	PROJECT	Project	Lorandeau Builders Holding Corp.	156499	2022-08-02 20:25:09.255799+00	2022-08-02 20:25:09.255839+00	1	\N	\N	f	f
1041	PROJECT	Project	Stitch Software Distributors	156500	2022-08-02 20:25:09.255901+00	2022-08-02 20:25:09.255922+00	1	\N	\N	f	f
1042	PROJECT	Project	Goepel Windows Management	156501	2022-08-02 20:25:09.256641+00	2022-08-02 20:25:09.25669+00	1	\N	\N	f	f
1043	PROJECT	Project	Reisman Windows Management	156502	2022-08-02 20:25:09.256784+00	2022-08-02 20:25:09.256812+00	1	\N	\N	f	f
1044	PROJECT	Project	Zucconi Telecom Sales	156503	2022-08-02 20:25:09.256869+00	2022-08-02 20:25:09.256897+00	1	\N	\N	f	f
1045	PROJECT	Project	Marionneaux Catering Incorporated	156504	2022-08-02 20:25:09.256954+00	2022-08-02 20:25:09.256981+00	1	\N	\N	f	f
1046	PROJECT	Project	Wedge Automotive Fabricators	156505	2022-08-02 20:25:09.257037+00	2022-08-02 20:25:09.257064+00	1	\N	\N	f	f
1047	PROJECT	Project	Twigg Attorneys Company	156506	2022-08-02 20:25:09.25712+00	2022-08-02 20:25:09.257148+00	1	\N	\N	f	f
1048	PROJECT	Project	Warnberg Automotive and Associates	156507	2022-08-02 20:25:09.257361+00	2022-08-02 20:25:09.257453+00	1	\N	\N	f	f
1049	PROJECT	Project	Bollman Attorneys Company	156508	2022-08-02 20:25:09.257512+00	2022-08-02 20:25:09.257539+00	1	\N	\N	f	f
1050	PROJECT	Project	Bleser Antiques Incorporated	156509	2022-08-02 20:25:09.257596+00	2022-08-02 20:25:09.257624+00	1	\N	\N	f	f
1051	PROJECT	Project	Honolulu Attorneys Sales	156510	2022-08-02 20:25:09.25768+00	2022-08-02 20:25:09.257708+00	1	\N	\N	f	f
1052	PROJECT	Project	Carpinteria Leasing Services	156511	2022-08-02 20:25:09.257764+00	2022-08-02 20:25:09.257791+00	1	\N	\N	f	f
1053	PROJECT	Project	Helker and Heidkamp Software Systems	156512	2022-08-02 20:25:09.257847+00	2022-08-02 20:25:09.257874+00	1	\N	\N	f	f
1054	PROJECT	Project	Benge Liquors Incorporated	156513	2022-08-02 20:25:09.25793+00	2022-08-02 20:25:09.257957+00	1	\N	\N	f	f
1055	PROJECT	Project	Stower Electric Company	156514	2022-08-02 20:25:09.258014+00	2022-08-02 20:25:09.258041+00	1	\N	\N	f	f
1056	PROJECT	Project	Las Vegas Electric Manufacturing	156515	2022-08-02 20:25:09.258098+00	2022-08-02 20:25:09.258125+00	1	\N	\N	f	f
1057	PROJECT	Project	Edin Lumber Distributors	156516	2022-08-02 20:25:09.258181+00	2022-08-02 20:25:09.258208+00	1	\N	\N	f	f
1058	PROJECT	Project	Lenza and Lanzoni Plumbing Co.	156517	2022-08-02 20:25:09.258364+00	2022-08-02 20:25:09.258393+00	1	\N	\N	f	f
1059	PROJECT	Project	Tenen Markets Dynamics	156518	2022-08-02 20:25:09.263805+00	2022-08-02 20:25:09.263844+00	1	\N	\N	f	f
1060	PROJECT	Project	Duhamel Lumber Co.	156519	2022-08-02 20:25:09.263903+00	2022-08-02 20:25:09.26393+00	1	\N	\N	f	f
1061	PROJECT	Project	Eachus Metal Fabricators Incorporated	156520	2022-08-02 20:25:09.263986+00	2022-08-02 20:25:09.264013+00	1	\N	\N	f	f
1062	PROJECT	Project	Sawatzky Catering Rentals	156521	2022-08-02 20:25:09.26407+00	2022-08-02 20:25:09.264096+00	1	\N	\N	f	f
1063	PROJECT	Project	Steffensmeier Markets Co.	156522	2022-08-02 20:25:09.264212+00	2022-08-02 20:25:09.264242+00	1	\N	\N	f	f
1064	PROJECT	Project	Cerritos Telecom and Associates	156523	2022-08-02 20:25:09.264436+00	2022-08-02 20:25:09.264467+00	1	\N	\N	f	f
1065	PROJECT	Project	Amarillo Apartments Distributors	156524	2022-08-02 20:25:09.264528+00	2022-08-02 20:25:09.264583+00	1	\N	\N	f	f
1066	PROJECT	Project	Brent Apartments Rentals	156525	2022-08-02 20:25:09.264698+00	2022-08-02 20:25:09.264728+00	1	\N	\N	f	f
1067	PROJECT	Project	Bayas Hardware Dynamics	156526	2022-08-02 20:25:09.26479+00	2022-08-02 20:25:09.264819+00	1	\N	\N	f	f
1068	PROJECT	Project	Galvan Attorneys Systems	156527	2022-08-02 20:25:09.264887+00	2022-08-02 20:25:09.264915+00	1	\N	\N	f	f
1069	PROJECT	Project	Estevez Title and Associates	156528	2022-08-02 20:25:09.264971+00	2022-08-02 20:25:09.264999+00	1	\N	\N	f	f
1070	PROJECT	Project	Beatie Leasing Networking	156529	2022-08-02 20:25:09.265055+00	2022-08-02 20:25:09.265082+00	1	\N	\N	f	f
1071	PROJECT	Project	Knoop Telecom Agency	156530	2022-08-02 20:25:09.265275+00	2022-08-02 20:25:09.265306+00	1	\N	\N	f	f
1072	PROJECT	Project	Arcizo Automotive Sales	156531	2022-08-02 20:25:09.265378+00	2022-08-02 20:25:09.265406+00	1	\N	\N	f	f
1073	PROJECT	Project	Mount Lake Terrace Markets Fabricators	156532	2022-08-02 20:25:09.265462+00	2022-08-02 20:25:09.26549+00	1	\N	\N	f	f
1074	PROJECT	Project	Lawley and Barends Painting Distributors	156533	2022-08-02 20:25:09.265546+00	2022-08-02 20:25:09.265573+00	1	\N	\N	f	f
1075	PROJECT	Project	Witten Antiques Services	156534	2022-08-02 20:25:09.26563+00	2022-08-02 20:25:09.265657+00	1	\N	\N	f	f
1076	PROJECT	Project	Wever Apartments -	156535	2022-08-02 20:25:09.265714+00	2022-08-02 20:25:09.265741+00	1	\N	\N	f	f
1077	PROJECT	Project	Big Bear Lake Plumbing Holding Corp.	156536	2022-08-02 20:25:09.265797+00	2022-08-02 20:25:09.265824+00	1	\N	\N	f	f
1078	PROJECT	Project	Selders Distributors	156537	2022-08-02 20:25:09.26588+00	2022-08-02 20:25:09.265907+00	1	\N	\N	f	f
1079	PROJECT	Project	Apfel Electric Co.	156538	2022-08-02 20:25:09.265964+00	2022-08-02 20:25:09.265991+00	1	\N	\N	f	f
1080	PROJECT	Project	Healy Lumber -	156539	2022-08-02 20:25:09.266048+00	2022-08-02 20:25:09.266075+00	1	\N	\N	f	f
1081	PROJECT	Project	Deblasio Painting Holding Corp.	156540	2022-08-02 20:25:09.266131+00	2022-08-02 20:25:09.266159+00	1	\N	\N	f	f
1082	PROJECT	Project	Bridgham Electric Inc.	156541	2022-08-02 20:25:09.266215+00	2022-08-02 20:25:09.266243+00	1	\N	\N	f	f
1083	PROJECT	Project	Salisbury Attorneys Group	156542	2022-08-02 20:25:09.266429+00	2022-08-02 20:25:09.266457+00	1	\N	\N	f	f
1084	PROJECT	Project	Boise Publishing Co.	156543	2022-08-02 20:25:09.266513+00	2022-08-02 20:25:09.26654+00	1	\N	\N	f	f
1085	PROJECT	Project	Conteras Liquors Agency	156544	2022-08-02 20:25:09.266598+00	2022-08-02 20:25:09.266625+00	1	\N	\N	f	f
1086	PROJECT	Project	Moots Painting Distributors	156545	2022-08-02 20:25:09.266681+00	2022-08-02 20:25:09.266709+00	1	\N	\N	f	f
1087	PROJECT	Project	Virginia Beach Hospital Manufacturing	156546	2022-08-02 20:25:09.266766+00	2022-08-02 20:25:09.266793+00	1	\N	\N	f	f
1088	PROJECT	Project	Ben Lomond Software Incorporated	156547	2022-08-02 20:25:09.26685+00	2022-08-02 20:25:09.266877+00	1	\N	\N	f	f
1089	PROJECT	Project	Laser Images Inc.	156548	2022-08-02 20:25:09.266934+00	2022-08-02 20:25:09.266961+00	1	\N	\N	f	f
1090	PROJECT	Project	Sur Windows Services	156549	2022-08-02 20:25:09.267018+00	2022-08-02 20:25:09.267045+00	1	\N	\N	f	f
1091	PROJECT	Project	Wollan Software Rentals	156550	2022-08-02 20:25:09.267102+00	2022-08-02 20:25:09.267129+00	1	\N	\N	f	f
1092	PROJECT	Project	Coklow Leasing Dynamics	156551	2022-08-02 20:25:09.267185+00	2022-08-02 20:25:09.267223+00	1	\N	\N	f	f
1093	PROJECT	Project	Brandwein Builders Fabricators	156552	2022-08-02 20:25:09.267399+00	2022-08-02 20:25:09.267427+00	1	\N	\N	f	f
1094	PROJECT	Project	Sandwich Antiques Services	156553	2022-08-02 20:25:09.267484+00	2022-08-02 20:25:09.267511+00	1	\N	\N	f	f
1095	PROJECT	Project	Woon Hardware Networking	156554	2022-08-02 20:25:09.267568+00	2022-08-02 20:25:09.267596+00	1	\N	\N	f	f
1096	PROJECT	Project	Chiaminto Attorneys Agency	156555	2022-08-02 20:25:09.267652+00	2022-08-02 20:25:09.267679+00	1	\N	\N	f	f
1097	PROJECT	Project	Linberg Windows Agency	156556	2022-08-02 20:25:09.267736+00	2022-08-02 20:25:09.267763+00	1	\N	\N	f	f
1098	PROJECT	Project	Diekema Attorneys Manufacturing	156557	2022-08-02 20:25:09.26782+00	2022-08-02 20:25:09.267847+00	1	\N	\N	f	f
1099	PROJECT	Project	Rickers Apartments Company	156558	2022-08-02 20:25:09.267903+00	2022-08-02 20:25:09.267931+00	1	\N	\N	f	f
1100	PROJECT	Project	Bowling Green Painting Incorporated	156559	2022-08-02 20:25:09.267988+00	2022-08-02 20:25:09.268015+00	1	\N	\N	f	f
1101	PROJECT	Project	Weare and Norvell Painting Co.	156560	2022-08-02 20:25:09.268072+00	2022-08-02 20:25:09.268099+00	1	\N	\N	f	f
1102	PROJECT	Project	Doiel and Mcdivitt Construction Holding Corp.	156561	2022-08-02 20:25:09.268156+00	2022-08-02 20:25:09.268183+00	1	\N	\N	f	f
1103	PROJECT	Project	Miquel Apartments Leasing	156562	2022-08-02 20:25:09.268364+00	2022-08-02 20:25:09.268397+00	1	\N	\N	f	f
1104	PROJECT	Project	Rastorfer Automotive Holding Corp.	156563	2022-08-02 20:25:09.268469+00	2022-08-02 20:25:09.268497+00	1	\N	\N	f	f
1105	PROJECT	Project	Beaubien Antiques Leasing	156564	2022-08-02 20:25:09.268553+00	2022-08-02 20:25:09.268581+00	1	\N	\N	f	f
1106	PROJECT	Project	Garret Leasing Rentals	156565	2022-08-02 20:25:09.268638+00	2022-08-02 20:25:09.268665+00	1	\N	\N	f	f
1107	PROJECT	Project	Summerton Hospital Services	156566	2022-08-02 20:25:09.268722+00	2022-08-02 20:25:09.268749+00	1	\N	\N	f	f
1108	PROJECT	Project	Wahlers Lumber Management	156567	2022-08-02 20:25:09.268805+00	2022-08-02 20:25:09.268832+00	1	\N	\N	f	f
1109	PROJECT	Project	Mitchelle Title -	156568	2022-08-02 20:25:09.514519+00	2022-08-02 20:25:09.514586+00	1	\N	\N	f	f
1110	PROJECT	Project	Ertle Painting Leasing	156569	2022-08-02 20:25:09.514692+00	2022-08-02 20:25:09.514737+00	1	\N	\N	f	f
1111	PROJECT	Project	Fasefax Systems	156570	2022-08-02 20:25:09.514867+00	2022-08-02 20:25:09.514967+00	1	\N	\N	f	f
1112	PROJECT	Project	Novida and Chochrek Leasing Manufacturing	156571	2022-08-02 20:25:09.515085+00	2022-08-02 20:25:09.515129+00	1	\N	\N	f	f
1113	PROJECT	Project	Marrello Software Services	156572	2022-08-02 20:25:09.515241+00	2022-08-02 20:25:09.515285+00	1	\N	\N	f	f
1114	PROJECT	Project	Malena Construction Fabricators	156573	2022-08-02 20:25:09.515809+00	2022-08-02 20:25:09.515909+00	1	\N	\N	f	f
1115	PROJECT	Project	Pritts Construction Distributors	156574	2022-08-02 20:25:09.516302+00	2022-08-02 20:25:09.516343+00	1	\N	\N	f	f
1116	PROJECT	Project	Andersson Hospital Inc.	156575	2022-08-02 20:25:09.516423+00	2022-08-02 20:25:09.516453+00	1	\N	\N	f	f
1117	PROJECT	Project	Kababik and Ramariz Liquors Corporation	156576	2022-08-02 20:25:09.517267+00	2022-08-02 20:25:09.517408+00	1	\N	\N	f	f
1118	PROJECT	Project	Falls Church _ Agency	156577	2022-08-02 20:25:09.517525+00	2022-08-02 20:25:09.517569+00	1	\N	\N	f	f
1119	PROJECT	Project	Genis Builders Holding Corp.	156578	2022-08-02 20:25:09.517637+00	2022-08-02 20:25:09.517664+00	1	\N	\N	f	f
1120	PROJECT	Project	Austin Builders Distributors	156579	2022-08-02 20:25:09.517724+00	2022-08-02 20:25:09.517752+00	1	\N	\N	f	f
1121	PROJECT	Project	Podvin Software Networking	156580	2022-08-02 20:25:09.517811+00	2022-08-02 20:25:09.517838+00	1	\N	\N	f	f
1122	PROJECT	Project	Lake Worth Markets Fabricators	156581	2022-08-02 20:25:09.517896+00	2022-08-02 20:25:09.517923+00	1	\N	\N	f	f
1123	PROJECT	Project	Hood River Telecom	156582	2022-08-02 20:25:09.517981+00	2022-08-02 20:25:09.518008+00	1	\N	\N	f	f
1124	PROJECT	Project	Wickenhauser Hardware Management	156583	2022-08-02 20:25:09.518065+00	2022-08-02 20:25:09.518093+00	1	\N	\N	f	f
1125	PROJECT	Project	Drumgoole Attorneys Corporation	156584	2022-08-02 20:25:09.51815+00	2022-08-02 20:25:09.518177+00	1	\N	\N	f	f
1126	PROJECT	Project	Marston Hardware -	156585	2022-08-02 20:25:09.518235+00	2022-08-02 20:25:09.51839+00	1	\N	\N	f	f
1127	PROJECT	Project	Wethersfield Hardware Dynamics	156586	2022-08-02 20:25:09.518462+00	2022-08-02 20:25:09.51849+00	1	\N	\N	f	f
1128	PROJECT	Project	Gerney Antiques Management	156587	2022-08-02 20:25:09.518547+00	2022-08-02 20:25:09.518574+00	1	\N	\N	f	f
1129	PROJECT	Project	Honie Hospital Systems	156588	2022-08-02 20:25:09.518631+00	2022-08-02 20:25:09.518658+00	1	\N	\N	f	f
1130	PROJECT	Project	Swinea Antiques Holding Corp.	156589	2022-08-02 20:25:09.518715+00	2022-08-02 20:25:09.518743+00	1	\N	\N	f	f
1131	PROJECT	Project	Duman Windows Sales	156590	2022-08-02 20:25:09.518799+00	2022-08-02 20:25:09.518826+00	1	\N	\N	f	f
1132	PROJECT	Project	Hillian Construction Fabricators	156591	2022-08-02 20:25:09.518883+00	2022-08-02 20:25:09.51891+00	1	\N	\N	f	f
1133	PROJECT	Project	Santa Ana Telecom Management	156592	2022-08-02 20:25:09.518966+00	2022-08-02 20:25:09.518994+00	1	\N	\N	f	f
1134	PROJECT	Project	Scottsbluff Plumbing Rentals	156593	2022-08-02 20:25:09.51905+00	2022-08-02 20:25:09.519077+00	1	\N	\N	f	f
1135	PROJECT	Project	Limbo Leasing Leasing	156594	2022-08-02 20:25:09.519134+00	2022-08-02 20:25:09.519161+00	1	\N	\N	f	f
1136	PROJECT	Project	Scalley Construction Inc.	156595	2022-08-02 20:25:09.519335+00	2022-08-02 20:25:09.519375+00	1	\N	\N	f	f
1137	PROJECT	Project	Stonum Catering Group	156596	2022-08-02 20:25:09.519433+00	2022-08-02 20:25:09.519461+00	1	\N	\N	f	f
1138	PROJECT	Project	Talboti and Pauli Title Agency	156597	2022-08-02 20:25:09.519517+00	2022-08-02 20:25:09.519545+00	1	\N	\N	f	f
1139	PROJECT	Project	Benabides and Louris Builders Services	156598	2022-08-02 20:25:09.519602+00	2022-08-02 20:25:09.51963+00	1	\N	\N	f	f
1140	PROJECT	Project	Brea Painting Company	156599	2022-08-02 20:25:09.519687+00	2022-08-02 20:25:09.519714+00	1	\N	\N	f	f
1141	PROJECT	Project	Bakkala Catering Distributors	156600	2022-08-02 20:25:09.51977+00	2022-08-02 20:25:09.519797+00	1	\N	\N	f	f
1142	PROJECT	Project	Yucca Valley Camping	156601	2022-08-02 20:25:09.519853+00	2022-08-02 20:25:09.519881+00	1	\N	\N	f	f
1143	PROJECT	Project	Bartkus Automotive Company	156602	2022-08-02 20:25:09.519938+00	2022-08-02 20:25:09.519965+00	1	\N	\N	f	f
1144	PROJECT	Project	Eckerman Leasing Management	156603	2022-08-02 20:25:09.520021+00	2022-08-02 20:25:09.520049+00	1	\N	\N	f	f
1145	PROJECT	Project	Clayton and Bubash Telecom Services	156604	2022-08-02 20:25:09.520107+00	2022-08-02 20:25:09.520134+00	1	\N	\N	f	f
1146	PROJECT	Project	Gardnerville Automotive Sales	156605	2022-08-02 20:25:09.520191+00	2022-08-02 20:25:09.520228+00	1	\N	\N	f	f
1147	PROJECT	Project	Seecharan and Horten Hardware Manufacturing	156606	2022-08-02 20:25:09.520403+00	2022-08-02 20:25:09.52043+00	1	\N	\N	f	f
1148	PROJECT	Project	Linderman Builders Agency	156607	2022-08-02 20:25:09.520488+00	2022-08-02 20:25:09.520515+00	1	\N	\N	f	f
1149	PROJECT	Project	Kingman Antiques Corporation	156608	2022-08-02 20:25:09.520572+00	2022-08-02 20:25:09.520599+00	1	\N	\N	f	f
1150	PROJECT	Project	Ornelas and Ciejka Painting and Associates	156609	2022-08-02 20:25:09.520656+00	2022-08-02 20:25:09.520683+00	1	\N	\N	f	f
1151	PROJECT	Project	Liverpool Hospital Leasing	156610	2022-08-02 20:25:09.52074+00	2022-08-02 20:25:09.520768+00	1	\N	\N	f	f
1152	PROJECT	Project	Thongchanh Telecom Rentals	156611	2022-08-02 20:25:09.520825+00	2022-08-02 20:25:09.520852+00	1	\N	\N	f	f
1153	PROJECT	Project	Kovats Publishing	156612	2022-08-02 20:25:09.520909+00	2022-08-02 20:25:09.520937+00	1	\N	\N	f	f
1154	PROJECT	Project	Gilroy Electric Services	156613	2022-08-02 20:25:09.520993+00	2022-08-02 20:25:09.52102+00	1	\N	\N	f	f
1155	PROJECT	Project	Umali Publishing Distributors	156614	2022-08-02 20:25:09.521076+00	2022-08-02 20:25:09.521104+00	1	\N	\N	f	f
1156	PROJECT	Project	Reinfeld and Jurczak Hospital Incorporated	156615	2022-08-02 20:25:09.521161+00	2022-08-02 20:25:09.521188+00	1	\N	\N	f	f
1157	PROJECT	Project	Orlando Automotive Leasing	156616	2022-08-02 20:25:09.521361+00	2022-08-02 20:25:09.5214+00	1	\N	\N	f	f
1158	PROJECT	Project	Halick Title and Associates	156617	2022-08-02 20:25:09.521457+00	2022-08-02 20:25:09.521485+00	1	\N	\N	f	f
1159	PROJECT	Project	Brutsch Builders Incorporated	156618	2022-08-02 20:25:09.529803+00	2022-08-02 20:25:09.529849+00	1	\N	\N	f	f
1160	PROJECT	Project	Prokup Plumbing Corporation	156619	2022-08-02 20:25:09.52992+00	2022-08-02 20:25:09.52995+00	1	\N	\N	f	f
1161	PROJECT	Project	Moores Builders Agency	156620	2022-08-02 20:25:09.530146+00	2022-08-02 20:25:09.530179+00	1	\N	\N	f	f
1162	PROJECT	Project	Verrelli Construction -	156621	2022-08-02 20:25:09.53063+00	2022-08-02 20:25:09.530777+00	1	\N	\N	f	f
1163	PROJECT	Project	Santa Maria Lumber Inc.	156622	2022-08-02 20:25:09.531199+00	2022-08-02 20:25:09.531262+00	1	\N	\N	f	f
1164	PROJECT	Project	Reedus Telecom Group	156623	2022-08-02 20:25:09.532021+00	2022-08-02 20:25:09.53214+00	1	\N	\N	f	f
1165	PROJECT	Project	Wenatchee Builders Fabricators	156624	2022-08-02 20:25:09.532534+00	2022-08-02 20:25:09.532571+00	1	\N	\N	f	f
1166	PROJECT	Project	Windisch Title Corporation	156625	2022-08-02 20:25:09.532637+00	2022-08-02 20:25:09.532665+00	1	\N	\N	f	f
1167	PROJECT	Project	Sloman and Zeccardi Builders Agency	156626	2022-08-02 20:25:09.532725+00	2022-08-02 20:25:09.532753+00	1	\N	\N	f	f
1168	PROJECT	Project	Port Angeles Telecom Networking	156627	2022-08-02 20:25:09.532812+00	2022-08-02 20:25:09.53284+00	1	\N	\N	f	f
1169	PROJECT	Project	Solymani Electric Leasing	156628	2022-08-02 20:25:09.532898+00	2022-08-02 20:25:09.532926+00	1	\N	\N	f	f
1170	PROJECT	Project	Grines Apartments Co.	156629	2022-08-02 20:25:09.532983+00	2022-08-02 20:25:09.533011+00	1	\N	\N	f	f
1171	PROJECT	Project	Huit and Duer Publishing Dynamics	156630	2022-08-02 20:25:09.533069+00	2022-08-02 20:25:09.533096+00	1	\N	\N	f	f
1172	PROJECT	Project	Gerba Construction Corporation	156631	2022-08-02 20:25:09.533153+00	2022-08-02 20:25:09.53318+00	1	\N	\N	f	f
1173	PROJECT	Project	Casuse Liquors Inc.	156632	2022-08-02 20:25:09.53325+00	2022-08-02 20:25:09.533385+00	1	\N	\N	f	f
1174	PROJECT	Project	Kittel Hardware Dynamics	156633	2022-08-02 20:25:09.533455+00	2022-08-02 20:25:09.533482+00	1	\N	\N	f	f
1175	PROJECT	Project	Crisafulli Hardware Holding Corp.	156634	2022-08-02 20:25:09.53354+00	2022-08-02 20:25:09.533567+00	1	\N	\N	f	f
1176	PROJECT	Project	Seilhymer Antiques Distributors	156635	2022-08-02 20:25:09.533624+00	2022-08-02 20:25:09.533651+00	1	\N	\N	f	f
1177	PROJECT	Project	Stampe Leasing and Associates	156636	2022-08-02 20:25:09.533708+00	2022-08-02 20:25:09.533735+00	1	\N	\N	f	f
1178	PROJECT	Project	San Diego Windows Agency	156637	2022-08-02 20:25:09.533792+00	2022-08-02 20:25:09.533819+00	1	\N	\N	f	f
1179	PROJECT	Project	Whittier Hardware -	156638	2022-08-02 20:25:09.533876+00	2022-08-02 20:25:09.533903+00	1	\N	\N	f	f
1180	PROJECT	Project	Oeder Liquors Company	156639	2022-08-02 20:25:09.53396+00	2022-08-02 20:25:09.533987+00	1	\N	\N	f	f
1181	PROJECT	Project	Ptomey Title Group	156640	2022-08-02 20:25:09.534044+00	2022-08-02 20:25:09.534071+00	1	\N	\N	f	f
1182	PROJECT	Project	Skibo Construction Dynamics	156641	2022-08-02 20:25:09.534128+00	2022-08-02 20:25:09.534155+00	1	\N	\N	f	f
1183	PROJECT	Project	Linder Windows Rentals	156642	2022-08-02 20:25:09.534223+00	2022-08-02 20:25:09.534356+00	1	\N	\N	f	f
1184	PROJECT	Project	Ramsy Publishing Company	156643	2022-08-02 20:25:09.534425+00	2022-08-02 20:25:09.534452+00	1	\N	\N	f	f
1185	PROJECT	Project	Roule and Mattsey _ Management	156644	2022-08-02 20:25:09.53451+00	2022-08-02 20:25:09.534537+00	1	\N	\N	f	f
1186	PROJECT	Project	Quezad Lumber Leasing	156645	2022-08-02 20:25:09.534594+00	2022-08-02 20:25:09.534621+00	1	\N	\N	f	f
1187	PROJECT	Project	Taverna Liquors Networking	156646	2022-08-02 20:25:09.534678+00	2022-08-02 20:25:09.534706+00	1	\N	\N	f	f
1188	PROJECT	Project	Drown Markets Services	156647	2022-08-02 20:25:09.534763+00	2022-08-02 20:25:09.53479+00	1	\N	\N	f	f
1189	PROJECT	Project	Eckrote Construction Fabricators	156648	2022-08-02 20:25:09.534847+00	2022-08-02 20:25:09.534874+00	1	\N	\N	f	f
1190	PROJECT	Project	Diamond Bar Plumbing	156649	2022-08-02 20:25:09.534931+00	2022-08-02 20:25:09.534958+00	1	\N	\N	f	f
1191	PROJECT	Project	Mcguff and Spriggins Hospital Group	156650	2022-08-02 20:25:09.535015+00	2022-08-02 20:25:09.535042+00	1	\N	\N	f	f
1192	PROJECT	Project	Fuhrmann Lumber Manufacturing	156651	2022-08-02 20:25:09.535098+00	2022-08-02 20:25:09.535126+00	1	\N	\N	f	f
1193	PROJECT	Project	Zearfoss Windows Group	156652	2022-08-02 20:25:09.535182+00	2022-08-02 20:25:09.535209+00	1	\N	\N	f	f
1194	PROJECT	Project	Sax Lumber Co.	156653	2022-08-02 20:25:09.535394+00	2022-08-02 20:25:09.535422+00	1	\N	\N	f	f
1195	PROJECT	Project	Lexington Hospital Sales	156654	2022-08-02 20:25:09.535479+00	2022-08-02 20:25:09.535506+00	1	\N	\N	f	f
1196	PROJECT	Project	Galagher Plumbing Sales	156655	2022-08-02 20:25:09.535563+00	2022-08-02 20:25:09.53559+00	1	\N	\N	f	f
1197	PROJECT	Project	Henderson Liquors Manufacturing	156656	2022-08-02 20:25:09.535647+00	2022-08-02 20:25:09.535674+00	1	\N	\N	f	f
1198	PROJECT	Project	Kavadias Construction Sales	156657	2022-08-02 20:25:09.53573+00	2022-08-02 20:25:09.535758+00	1	\N	\N	f	f
1199	PROJECT	Project	West Palm Beach Painting Manufacturing	156658	2022-08-02 20:25:09.535815+00	2022-08-02 20:25:09.535842+00	1	\N	\N	f	f
1200	PROJECT	Project	Sheinbein Construction Fabricators	156659	2022-08-02 20:25:09.535899+00	2022-08-02 20:25:09.535926+00	1	\N	\N	f	f
1201	PROJECT	Project	Fauerbach _ Agency	156660	2022-08-02 20:25:09.535982+00	2022-08-02 20:25:09.536009+00	1	\N	\N	f	f
1202	PROJECT	Project	Lafayette Metal Fabricators Rentals	156661	2022-08-02 20:25:09.536066+00	2022-08-02 20:25:09.536093+00	1	\N	\N	f	f
1203	PROJECT	Project	Swiech Telecom Networking	156662	2022-08-02 20:25:09.53615+00	2022-08-02 20:25:09.536177+00	1	\N	\N	f	f
1204	PROJECT	Project	Downey and Sweezer Electric Group	156663	2022-08-02 20:25:09.53635+00	2022-08-02 20:25:09.536391+00	1	\N	\N	f	f
1205	PROJECT	Project	Leemans Builders Agency	156664	2022-08-02 20:25:09.536451+00	2022-08-02 20:25:09.536479+00	1	\N	\N	f	f
1206	PROJECT	Project	Stai Publishing -	156665	2022-08-02 20:25:09.536535+00	2022-08-02 20:25:09.536563+00	1	\N	\N	f	f
1656	PROJECT	Project	Aaron Abbott	157116	2022-08-02 20:25:10.279027+00	2022-08-02 20:25:10.279054+00	1	\N	\N	f	f
1207	PROJECT	Project	Hebden Automotive Dynamics	156666	2022-08-02 20:25:09.536619+00	2022-08-02 20:25:09.536647+00	1	\N	\N	f	f
1208	PROJECT	Project	Holtmeier Leasing -	156667	2022-08-02 20:25:09.536703+00	2022-08-02 20:25:09.53673+00	1	\N	\N	f	f
1209	PROJECT	Project	Douse Telecom Leasing	156668	2022-08-02 20:25:09.542498+00	2022-08-02 20:25:09.54254+00	1	\N	\N	f	f
1210	PROJECT	Project	Wence Antiques Rentals	156669	2022-08-02 20:25:09.542605+00	2022-08-02 20:25:09.542633+00	1	\N	\N	f	f
1211	PROJECT	Project	Underdown Metal Fabricators and Associates	156670	2022-08-02 20:25:09.542692+00	2022-08-02 20:25:09.542719+00	1	\N	\N	f	f
1212	PROJECT	Project	La Grande Liquors Dynamics	156671	2022-08-02 20:25:09.542777+00	2022-08-02 20:25:09.542805+00	1	\N	\N	f	f
1213	PROJECT	Project	Puyallup Liquors Networking	156672	2022-08-02 20:25:09.542863+00	2022-08-02 20:25:09.54289+00	1	\N	\N	f	f
1214	PROJECT	Project	Oestreich Liquors Inc.	156673	2022-08-02 20:25:09.542948+00	2022-08-02 20:25:09.542975+00	1	\N	\N	f	f
1215	PROJECT	Project	Sturrup Antiques Management	156674	2022-08-02 20:25:09.543033+00	2022-08-02 20:25:09.54306+00	1	\N	\N	f	f
1216	PROJECT	Project	Maleonado Publishing Company	156675	2022-08-02 20:25:09.543118+00	2022-08-02 20:25:09.543145+00	1	\N	\N	f	f
1217	PROJECT	Project	Westminster Lumber Sales	156676	2022-08-02 20:25:09.543202+00	2022-08-02 20:25:09.54323+00	1	\N	\N	f	f
1218	PROJECT	Project	Plexfase Construction Inc.	156677	2022-08-02 20:25:09.543456+00	2022-08-02 20:25:09.543497+00	1	\N	\N	f	f
1219	PROJECT	Project	Coen Publishing Co.	156678	2022-08-02 20:25:09.543556+00	2022-08-02 20:25:09.543583+00	1	\N	\N	f	f
1220	PROJECT	Project	Forest Grove Liquors Company	156679	2022-08-02 20:25:09.54364+00	2022-08-02 20:25:09.543668+00	1	\N	\N	f	f
1221	PROJECT	Project	Gearan Title Networking	156680	2022-08-02 20:25:09.543724+00	2022-08-02 20:25:09.543751+00	1	\N	\N	f	f
1222	PROJECT	Project	Dehaney Liquors Co.	156681	2022-08-02 20:25:09.543809+00	2022-08-02 20:25:09.543836+00	1	\N	\N	f	f
1223	PROJECT	Project	Warwick Lumber	156682	2022-08-02 20:25:09.543893+00	2022-08-02 20:25:09.54392+00	1	\N	\N	f	f
1224	PROJECT	Project	Calley Leasing and Associates	156683	2022-08-02 20:25:09.543976+00	2022-08-02 20:25:09.544003+00	1	\N	\N	f	f
1225	PROJECT	Project	Kamps Electric Systems	156684	2022-08-02 20:25:09.54406+00	2022-08-02 20:25:09.544087+00	1	\N	\N	f	f
1226	PROJECT	Project	Moss Builders	156685	2022-08-02 20:25:09.544143+00	2022-08-02 20:25:09.54417+00	1	\N	\N	f	f
1227	PROJECT	Project	Glish Hospital Incorporated	156686	2022-08-02 20:25:09.544346+00	2022-08-02 20:25:09.544378+00	1	\N	\N	f	f
1228	PROJECT	Project	Westminster Lumber Sales 1	156687	2022-08-02 20:25:09.544449+00	2022-08-02 20:25:09.544476+00	1	\N	\N	f	f
1229	PROJECT	Project	Crighton Catering Company	156688	2022-08-02 20:25:09.544534+00	2022-08-02 20:25:09.544561+00	1	\N	\N	f	f
1230	PROJECT	Project	Nania Painting Networking	156689	2022-08-02 20:25:09.544618+00	2022-08-02 20:25:09.544646+00	1	\N	\N	f	f
1231	PROJECT	Project	Rabeck Liquors Group	156690	2022-08-02 20:25:09.544702+00	2022-08-02 20:25:09.544729+00	1	\N	\N	f	f
1232	PROJECT	Project	Szewczyk Apartments Holding Corp.	156691	2022-08-02 20:25:09.544786+00	2022-08-02 20:25:09.544813+00	1	\N	\N	f	f
1233	PROJECT	Project	Tuy and Sinha Construction Manufacturing	156692	2022-08-02 20:25:09.54487+00	2022-08-02 20:25:09.544897+00	1	\N	\N	f	f
1234	PROJECT	Project	Killian Construction Networking	156693	2022-08-02 20:25:09.544954+00	2022-08-02 20:25:09.544982+00	1	\N	\N	f	f
1235	PROJECT	Project	Palmisano Hospital Fabricators	156694	2022-08-02 20:25:09.545039+00	2022-08-02 20:25:09.545066+00	1	\N	\N	f	f
1236	PROJECT	Project	Dipiano Automotive Sales	156695	2022-08-02 20:25:09.545123+00	2022-08-02 20:25:09.54515+00	1	\N	\N	f	f
1237	PROJECT	Project	Herline Hospital Holding Corp.	156696	2022-08-02 20:25:09.545206+00	2022-08-02 20:25:09.545244+00	1	\N	\N	f	f
1238	PROJECT	Project	Sternberger Telecom Incorporated	156697	2022-08-02 20:25:09.545518+00	2022-08-02 20:25:09.545551+00	1	\N	\N	f	f
1239	PROJECT	Project	Ridderhoff Painting Services	156698	2022-08-02 20:25:09.545615+00	2022-08-02 20:25:09.545644+00	1	\N	\N	f	f
1240	PROJECT	Project	Lodato Painting and Associates	156699	2022-08-02 20:25:09.545707+00	2022-08-02 20:25:09.545736+00	1	\N	\N	f	f
1241	PROJECT	Project	Chandrasekara Markets Sales	156700	2022-08-02 20:25:09.5458+00	2022-08-02 20:25:09.54583+00	1	\N	\N	f	f
1242	PROJECT	Project	Fujimura Catering Corporation	156701	2022-08-02 20:25:09.545891+00	2022-08-02 20:25:09.54592+00	1	\N	\N	f	f
1243	PROJECT	Project	Tebo Builders Management	156702	2022-08-02 20:25:09.54605+00	2022-08-02 20:25:09.546214+00	1	\N	\N	f	f
1244	PROJECT	Project	Sarasota Software Rentals	156703	2022-08-02 20:25:09.546324+00	2022-08-02 20:25:09.546364+00	1	\N	\N	f	f
1245	PROJECT	Project	Volmar Liquors and Associates	156704	2022-08-02 20:25:09.546424+00	2022-08-02 20:25:09.546452+00	1	\N	\N	f	f
1246	PROJECT	Project	Ridgeway Corporation	156705	2022-08-02 20:25:09.54651+00	2022-08-02 20:25:09.546537+00	1	\N	\N	f	f
1247	PROJECT	Project	Vanasse Antiques Networking	156706	2022-08-02 20:25:09.546594+00	2022-08-02 20:25:09.546621+00	1	\N	\N	f	f
1248	PROJECT	Project	Creasman Antiques Holding Corp.	156707	2022-08-02 20:25:09.546678+00	2022-08-02 20:25:09.546706+00	1	\N	\N	f	f
1249	PROJECT	Project	Fenceroy and Herling Metal Fabricators Management	156708	2022-08-02 20:25:09.546762+00	2022-08-02 20:25:09.546789+00	1	\N	\N	f	f
1250	PROJECT	Project	Rennemeyer Liquors Systems	156709	2022-08-02 20:25:09.546846+00	2022-08-02 20:25:09.546873+00	1	\N	\N	f	f
1251	PROJECT	Project	Pasanen Attorneys Agency	156710	2022-08-02 20:25:09.54693+00	2022-08-02 20:25:09.546957+00	1	\N	\N	f	f
1252	PROJECT	Project	Arredla and Hillseth Hardware -	156711	2022-08-02 20:25:09.547014+00	2022-08-02 20:25:09.547041+00	1	\N	\N	f	f
1253	PROJECT	Project	Boney Electric Dynamics	156712	2022-08-02 20:25:09.547098+00	2022-08-02 20:25:09.547125+00	1	\N	\N	f	f
1254	PROJECT	Project	Jeziorski _ Dynamics	156713	2022-08-02 20:25:09.547182+00	2022-08-02 20:25:09.547209+00	1	\N	\N	f	f
1255	PROJECT	Project	Gettenberg Title Manufacturing	156714	2022-08-02 20:25:09.547277+00	2022-08-02 20:25:09.547411+00	1	\N	\N	f	f
1256	PROJECT	Project	Petticrew Apartments Incorporated	156715	2022-08-02 20:25:09.54748+00	2022-08-02 20:25:09.547508+00	1	\N	\N	f	f
1257	PROJECT	Project	Jeune Antiques Group	156716	2022-08-02 20:25:09.547564+00	2022-08-02 20:25:09.547592+00	1	\N	\N	f	f
1258	PROJECT	Project	Snode and Draper Leasing Rentals	156717	2022-08-02 20:25:09.547648+00	2022-08-02 20:25:09.547675+00	1	\N	\N	f	f
1259	PROJECT	Project	Robare Builders Corporation	156718	2022-08-02 20:25:09.55644+00	2022-08-02 20:25:09.556488+00	1	\N	\N	f	f
1260	PROJECT	Project	Big Bear Lake Electric	156719	2022-08-02 20:25:09.556562+00	2022-08-02 20:25:09.556592+00	1	\N	\N	f	f
1261	PROJECT	Project	Tarbutton Software Management	156720	2022-08-02 20:25:09.556654+00	2022-08-02 20:25:09.556683+00	1	\N	\N	f	f
1262	PROJECT	Project	Momphard Painting Sales	156721	2022-08-02 20:25:09.556742+00	2022-08-02 20:25:09.55677+00	1	\N	\N	f	f
1263	PROJECT	Project	Dary Construction Corporation	156722	2022-08-02 20:25:09.556831+00	2022-08-02 20:25:09.556859+00	1	\N	\N	f	f
1264	PROJECT	Project	Freshour Apartments Agency	156723	2022-08-02 20:25:09.556918+00	2022-08-02 20:25:09.556946+00	1	\N	\N	f	f
1265	PROJECT	Project	Luffy Apartments Company	156724	2022-08-02 20:25:09.557004+00	2022-08-02 20:25:09.557031+00	1	\N	\N	f	f
1266	PROJECT	Project	Cosimini Software Agency	156725	2022-08-02 20:25:09.557089+00	2022-08-02 20:25:09.557117+00	1	\N	\N	f	f
1267	PROJECT	Project	Manwarren Markets Holding Corp.	156726	2022-08-02 20:25:09.557174+00	2022-08-02 20:25:09.557201+00	1	\N	\N	f	f
1268	PROJECT	Project	Ras Windows -	156727	2022-08-02 20:25:09.55738+00	2022-08-02 20:25:09.55742+00	1	\N	\N	f	f
1269	PROJECT	Project	Towsend Software Co.	156728	2022-08-02 20:25:09.557478+00	2022-08-02 20:25:09.557505+00	1	\N	\N	f	f
1270	PROJECT	Project	Turso Catering Agency	156729	2022-08-02 20:25:09.557562+00	2022-08-02 20:25:09.557589+00	1	\N	\N	f	f
1271	PROJECT	Project	Baim Lumber -	156730	2022-08-02 20:25:09.557646+00	2022-08-02 20:25:09.557674+00	1	\N	\N	f	f
1272	PROJECT	Project	Cambareri Painting Sales	156731	2022-08-02 20:25:09.55773+00	2022-08-02 20:25:09.557758+00	1	\N	\N	f	f
1273	PROJECT	Project	Ellenberger Windows Management	156732	2022-08-02 20:25:09.557814+00	2022-08-02 20:25:09.557842+00	1	\N	\N	f	f
1274	PROJECT	Project	Garden Automotive Systems	156733	2022-08-02 20:25:09.557898+00	2022-08-02 20:25:09.557926+00	1	\N	\N	f	f
1275	PROJECT	Project	Lafayette Hardware Services	156734	2022-08-02 20:25:09.557982+00	2022-08-02 20:25:09.55801+00	1	\N	\N	f	f
1276	PROJECT	Project	Mele Plumbing Manufacturing	156735	2022-08-02 20:25:09.558067+00	2022-08-02 20:25:09.558094+00	1	\N	\N	f	f
1277	PROJECT	Project	Jaenicke Builders Management	156736	2022-08-02 20:25:09.558151+00	2022-08-02 20:25:09.558179+00	1	\N	\N	f	f
1278	PROJECT	Project	Meneses Telecom Corporation	156737	2022-08-02 20:25:09.558384+00	2022-08-02 20:25:09.55842+00	1	\N	\N	f	f
1279	PROJECT	Project	Kieff Software Fabricators	156738	2022-08-02 20:25:09.558493+00	2022-08-02 20:25:09.558521+00	1	\N	\N	f	f
1280	PROJECT	Project	Schneck Automotive Group	156739	2022-08-02 20:25:09.558621+00	2022-08-02 20:25:09.558652+00	1	\N	\N	f	f
1281	PROJECT	Project	Kalfa Painting Holding Corp.	156740	2022-08-02 20:25:09.558713+00	2022-08-02 20:25:09.558742+00	1	\N	\N	f	f
1282	PROJECT	Project	Sterr Lumber Systems	156741	2022-08-02 20:25:09.558802+00	2022-08-02 20:25:09.558831+00	1	\N	\N	f	f
1283	PROJECT	Project	Haleiwa Windows Leasing	156742	2022-08-02 20:25:09.558891+00	2022-08-02 20:25:09.55892+00	1	\N	\N	f	f
1284	PROJECT	Project	Coletta Hospital Inc.	156743	2022-08-02 20:25:09.55898+00	2022-08-02 20:25:09.559233+00	1	\N	\N	f	f
1285	PROJECT	Project	Sebek Builders Distributors	156744	2022-08-02 20:25:09.559347+00	2022-08-02 20:25:09.559428+00	1	\N	\N	f	f
1286	PROJECT	Project	Schwarzenbach Attorneys Systems	156745	2022-08-02 20:25:09.55958+00	2022-08-02 20:25:09.559616+00	1	\N	\N	f	f
1287	PROJECT	Project	Boise Antiques and Associates	156746	2022-08-02 20:25:09.559709+00	2022-08-02 20:25:09.559751+00	1	\N	\N	f	f
1288	PROJECT	Project	Loeza Catering Agency	156747	2022-08-02 20:25:09.559942+00	2022-08-02 20:25:09.559991+00	1	\N	\N	f	f
1289	PROJECT	Project	Pote Leasing Rentals	156748	2022-08-02 20:25:09.560093+00	2022-08-02 20:25:09.560135+00	1	\N	\N	f	f
1290	PROJECT	Project	Carpentersville Publishing	156749	2022-08-02 20:25:09.560828+00	2022-08-02 20:25:09.560952+00	1	\N	\N	f	f
1291	PROJECT	Project	Rhody Leasing and Associates	156750	2022-08-02 20:25:09.561115+00	2022-08-02 20:25:09.561146+00	1	\N	\N	f	f
1292	PROJECT	Project	Laditka and Ceppetelli Publishing Holding Corp.	156751	2022-08-02 20:25:09.561207+00	2022-08-02 20:25:09.561235+00	1	\N	\N	f	f
1293	PROJECT	Project	Wassenaar Construction Services	156752	2022-08-02 20:25:09.56148+00	2022-08-02 20:25:09.561547+00	1	\N	\N	f	f
1294	PROJECT	Project	Rio Rancho Painting Agency	156753	2022-08-02 20:25:09.561633+00	2022-08-02 20:25:09.561966+00	1	\N	\N	f	f
1295	PROJECT	Project	Difebbo and Lewelling Markets Agency	156754	2022-08-02 20:25:09.562048+00	2022-08-02 20:25:09.562088+00	1	\N	\N	f	f
1296	PROJECT	Project	Steinberg Electric Networking	156755	2022-08-02 20:25:09.562149+00	2022-08-02 20:25:09.562176+00	1	\N	\N	f	f
1297	PROJECT	Project	Molesworth and Repress Liquors Leasing	156756	2022-08-02 20:25:09.562355+00	2022-08-02 20:25:09.562387+00	1	\N	\N	f	f
1298	PROJECT	Project	Barners and Rushlow Liquors Sales	156757	2022-08-02 20:25:09.562456+00	2022-08-02 20:25:09.562485+00	1	\N	\N	f	f
1299	PROJECT	Project	Demaire Automotive Systems	156758	2022-08-02 20:25:09.562549+00	2022-08-02 20:25:09.562578+00	1	\N	\N	f	f
1300	PROJECT	Project	Yanity Apartments and Associates	156759	2022-08-02 20:25:09.56264+00	2022-08-02 20:25:09.562671+00	1	\N	\N	f	f
1301	PROJECT	Project	Cotterman Software Company	156760	2022-08-02 20:25:09.562734+00	2022-08-02 20:25:09.562765+00	1	\N	\N	f	f
1302	PROJECT	Project	Aquino Apartments Dynamics	156761	2022-08-02 20:25:09.562827+00	2022-08-02 20:25:09.562856+00	1	\N	\N	f	f
1303	PROJECT	Project	Lucie Hospital Group	156762	2022-08-02 20:25:09.562918+00	2022-08-02 20:25:09.562947+00	1	\N	\N	f	f
1304	PROJECT	Project	Vista Lumber Agency	156763	2022-08-02 20:25:09.563008+00	2022-08-02 20:25:09.563037+00	1	\N	\N	f	f
1305	PROJECT	Project	Loven and Frothingham Hardware Distributors	156764	2022-08-02 20:25:09.563099+00	2022-08-02 20:25:09.563128+00	1	\N	\N	f	f
1306	PROJECT	Project	Sequim Automotive Systems	156765	2022-08-02 20:25:09.56319+00	2022-08-02 20:25:09.563219+00	1	\N	\N	f	f
1307	PROJECT	Project	Cochell Markets Group	156766	2022-08-02 20:25:09.563285+00	2022-08-02 20:25:09.563315+00	1	\N	\N	f	f
1308	PROJECT	Project	Fredericksburg Liquors Dynamics	156767	2022-08-02 20:25:09.563376+00	2022-08-02 20:25:09.563406+00	1	\N	\N	f	f
1309	PROJECT	Project	Altonen Windows Rentals	156768	2022-08-02 20:25:09.933367+00	2022-08-02 20:25:09.93342+00	1	\N	\N	f	f
1310	PROJECT	Project	Shackelton Hospital Sales	156769	2022-08-02 20:25:09.933486+00	2022-08-02 20:25:09.933514+00	1	\N	\N	f	f
1311	PROJECT	Project	Belisle Title Networking	156770	2022-08-02 20:25:09.933572+00	2022-08-02 20:25:09.933599+00	1	\N	\N	f	f
1312	PROJECT	Project	Dunlevy Software Corporation	156771	2022-08-02 20:25:09.933657+00	2022-08-02 20:25:09.933684+00	1	\N	\N	f	f
1313	PROJECT	Project	Unnold Hospital Co.	156772	2022-08-02 20:25:09.93374+00	2022-08-02 20:25:09.933767+00	1	\N	\N	f	f
1314	PROJECT	Project	Stofflet Hardware Incorporated	156773	2022-08-02 20:25:09.933823+00	2022-08-02 20:25:09.93385+00	1	\N	\N	f	f
1315	PROJECT	Project	Dennis Batemanger	156774	2022-08-02 20:25:09.933907+00	2022-08-02 20:25:09.933934+00	1	\N	\N	f	f
1316	PROJECT	Project	Vegas Tours	156775	2022-08-02 20:25:09.933991+00	2022-08-02 20:25:09.934018+00	1	\N	\N	f	f
1317	PROJECT	Project	Hahn & Associates	156776	2022-08-02 20:25:09.934075+00	2022-08-02 20:25:09.934102+00	1	\N	\N	f	f
1318	PROJECT	Project	The Coffee Corner	156777	2022-08-02 20:25:09.934158+00	2022-08-02 20:25:09.934185+00	1	\N	\N	f	f
1319	PROJECT	Project	Hansen Car Dealership	156778	2022-08-02 20:25:09.934331+00	2022-08-02 20:25:09.934358+00	1	\N	\N	f	f
1320	PROJECT	Project	Jim's Custom Frames	156779	2022-08-02 20:25:09.934428+00	2022-08-02 20:25:09.934456+00	1	\N	\N	f	f
1321	PROJECT	Project	Humphrey Yogurt	156780	2022-08-02 20:25:09.934513+00	2022-08-02 20:25:09.93454+00	1	\N	\N	f	f
1322	PROJECT	Project	Miller's Dry Cleaning	156781	2022-08-02 20:25:09.934596+00	2022-08-02 20:25:09.934623+00	1	\N	\N	f	f
1323	PROJECT	Project	Stewart's Valet Parking	156782	2022-08-02 20:25:09.93468+00	2022-08-02 20:25:09.934707+00	1	\N	\N	f	f
1324	PROJECT	Project	Mason's Travel Services	156783	2022-08-02 20:25:09.934774+00	2022-08-02 20:25:09.934803+00	1	\N	\N	f	f
1325	PROJECT	Project	Kim Wilson	156784	2022-08-02 20:25:09.934863+00	2022-08-02 20:25:09.934892+00	1	\N	\N	f	f
1326	PROJECT	Project	Will's Leather Co.	156785	2022-08-02 20:25:09.934952+00	2022-08-02 20:25:09.934981+00	1	\N	\N	f	f
1327	PROJECT	Project	Formal Furnishings	156786	2022-08-02 20:25:09.935041+00	2022-08-02 20:25:09.93507+00	1	\N	\N	f	f
1328	PROJECT	Project	Elegance Interior Design	156787	2022-08-02 20:25:09.935131+00	2022-08-02 20:25:09.935159+00	1	\N	\N	f	f
1329	PROJECT	Project	Luigi Imports	156788	2022-08-02 20:25:09.935485+00	2022-08-02 20:25:09.935594+00	1	\N	\N	f	f
1330	PROJECT	Project	Graphics R Us	156789	2022-08-02 20:25:09.935745+00	2022-08-02 20:25:09.935781+00	1	\N	\N	f	f
1331	PROJECT	Project	Kalinsky Consulting Group	156790	2022-08-02 20:25:09.935866+00	2022-08-02 20:25:09.935907+00	1	\N	\N	f	f
1332	PROJECT	Project	Sandy Whines	156791	2022-08-02 20:25:09.936009+00	2022-08-02 20:25:09.936103+00	1	\N	\N	f	f
1333	PROJECT	Project	Walters Production Company	156792	2022-08-02 20:25:09.936239+00	2022-08-02 20:25:09.936282+00	1	\N	\N	f	f
1334	PROJECT	Project	Yong Yi	156793	2022-08-02 20:25:09.936797+00	2022-08-02 20:25:09.936856+00	1	\N	\N	f	f
1335	PROJECT	Project	Hambly Spirits	156794	2022-08-02 20:25:09.937325+00	2022-08-02 20:25:09.937371+00	1	\N	\N	f	f
1336	PROJECT	Project	DelRey Distributors	156795	2022-08-02 20:25:09.937449+00	2022-08-02 20:25:09.937478+00	1	\N	\N	f	f
1337	PROJECT	Project	John Smith Home Design	156797	2022-08-02 20:25:09.937538+00	2022-08-02 20:25:09.937566+00	1	\N	\N	f	f
1338	PROJECT	Project	Cray Systems	156798	2022-08-02 20:25:09.937624+00	2022-08-02 20:25:09.937652+00	1	\N	\N	f	f
1339	PROJECT	Project	Dale Jenson	156799	2022-08-02 20:25:09.937709+00	2022-08-02 20:25:09.937737+00	1	\N	\N	f	f
1340	PROJECT	Project	Oliver Skin Supplies	156800	2022-08-02 20:25:09.937794+00	2022-08-02 20:25:09.937821+00	1	\N	\N	f	f
1341	PROJECT	Project	Hess Sundries	156801	2022-08-02 20:25:09.937878+00	2022-08-02 20:25:09.937906+00	1	\N	\N	f	f
1342	PROJECT	Project	Baron Chess	156802	2022-08-02 20:25:09.937963+00	2022-08-02 20:25:09.93799+00	1	\N	\N	f	f
1343	PROJECT	Project	Schmidt Sporting Goods	156803	2022-08-02 20:25:09.938047+00	2022-08-02 20:25:09.938075+00	1	\N	\N	f	f
1344	PROJECT	Project	Mike Franko	156804	2022-08-02 20:25:09.938132+00	2022-08-02 20:25:09.93816+00	1	\N	\N	f	f
1345	PROJECT	Project	Fabre Enterprises	156805	2022-08-02 20:25:09.938217+00	2022-08-02 20:25:09.938257+00	1	\N	\N	f	f
1346	PROJECT	Project	Spectrum Eye	156806	2022-08-02 20:25:09.93843+00	2022-08-02 20:25:09.938457+00	1	\N	\N	f	f
1657	PROJECT	Project	FA-HB Inc.	157117	2022-08-02 20:25:10.279111+00	2022-08-02 20:25:10.279138+00	1	\N	\N	f	f
1347	PROJECT	Project	Academy Vision Science Clinic	156807	2022-08-02 20:25:09.938515+00	2022-08-02 20:25:09.938542+00	1	\N	\N	f	f
1348	PROJECT	Project	Focal Point Opticians	156808	2022-08-02 20:25:09.938599+00	2022-08-02 20:25:09.938627+00	1	\N	\N	f	f
1349	PROJECT	Project	John G. Roche Opticians	156809	2022-08-02 20:25:09.938684+00	2022-08-02 20:25:09.938711+00	1	\N	\N	f	f
1350	PROJECT	Project	Mission Liquors	156810	2022-08-02 20:25:09.938768+00	2022-08-02 20:25:09.938796+00	1	\N	\N	f	f
1351	PROJECT	Project	Everett Fine Wines	156811	2022-08-02 20:25:09.938853+00	2022-08-02 20:25:09.93888+00	1	\N	\N	f	f
1352	PROJECT	Project	Academy Avenue Liquor Store	156812	2022-08-02 20:25:09.939247+00	2022-08-02 20:25:09.939278+00	1	\N	\N	f	f
1353	PROJECT	Project	The Liquor Barn	156813	2022-08-02 20:25:09.939338+00	2022-08-02 20:25:09.939366+00	1	\N	\N	f	f
1354	PROJECT	Project	Underwood Systems	156814	2022-08-02 20:25:09.939434+00	2022-08-02 20:25:09.939466+00	1	\N	\N	f	f
1355	PROJECT	Project	Hughson Runners	156815	2022-08-02 20:25:09.939528+00	2022-08-02 20:25:09.939557+00	1	\N	\N	f	f
1356	PROJECT	Project	Grant Electronics	156816	2022-08-02 20:25:09.939619+00	2022-08-02 20:25:09.939648+00	1	\N	\N	f	f
1357	PROJECT	Project	Trenton Upwood Ltd	156817	2022-08-02 20:25:09.939709+00	2022-08-02 20:25:09.939738+00	1	\N	\N	f	f
1358	PROJECT	Project	D&H Manufacturing	156818	2022-08-02 20:25:09.939798+00	2022-08-02 20:25:09.939827+00	1	\N	\N	f	f
1359	PROJECT	Project	Advanced Machining Techniques Inc.	156819	2022-08-02 20:25:09.949853+00	2022-08-02 20:25:09.9499+00	1	\N	\N	f	f
1360	PROJECT	Project	Y-Tec Manufacturing	156820	2022-08-02 20:25:09.949971+00	2022-08-02 20:25:09.950001+00	1	\N	\N	f	f
1361	PROJECT	Project	T-M Manufacturing Corp.	156821	2022-08-02 20:25:09.950064+00	2022-08-02 20:25:09.950094+00	1	\N	\N	f	f
1362	PROJECT	Project	Helping Hands Medical Supply	156822	2022-08-02 20:25:09.950155+00	2022-08-02 20:25:09.950184+00	1	\N	\N	f	f
1363	PROJECT	Project	Core Care Technologies Inc.	156823	2022-08-02 20:25:09.950503+00	2022-08-02 20:25:09.950563+00	1	\N	\N	f	f
1364	PROJECT	Project	Penco Medical Inc.	156824	2022-08-02 20:25:09.950632+00	2022-08-02 20:25:09.950659+00	1	\N	\N	f	f
1365	PROJECT	Project	Sunnybrook Hospital	156825	2022-08-02 20:25:09.950718+00	2022-08-02 20:25:09.950745+00	1	\N	\N	f	f
1366	PROJECT	Project	Teton Winter Sports	156826	2022-08-02 20:25:09.950861+00	2022-08-02 20:25:09.95089+00	1	\N	\N	f	f
1367	PROJECT	Project	Big 5 Sporting Goods	156827	2022-08-02 20:25:09.950951+00	2022-08-02 20:25:09.950979+00	1	\N	\N	f	f
1368	PROJECT	Project	Academy Sports & Outdoors	156828	2022-08-02 20:25:09.95104+00	2022-08-02 20:25:09.951068+00	1	\N	\N	f	f
1369	PROJECT	Project	Sports Authority	156829	2022-08-02 20:25:09.951129+00	2022-08-02 20:25:09.951158+00	1	\N	\N	f	f
1370	PROJECT	Project	Sport Station	156830	2022-08-02 20:25:09.951403+00	2022-08-02 20:25:09.95149+00	1	\N	\N	f	f
1371	PROJECT	Project	Bicycle Trailers	156831	2022-08-02 20:25:09.951656+00	2022-08-02 20:25:09.951752+00	1	\N	\N	f	f
1372	PROJECT	Project	Blue Street Liquor Store	156832	2022-08-02 20:25:09.951852+00	2022-08-02 20:25:09.951888+00	1	\N	\N	f	f
1373	PROJECT	Project	Maxx Corner Market	156833	2022-08-02 20:25:09.951985+00	2022-08-02 20:25:09.952028+00	1	\N	\N	f	f
1374	PROJECT	Project	San Francisco Design Center	156834	2022-08-02 20:25:09.952357+00	2022-08-02 20:25:09.952577+00	1	\N	\N	f	f
1375	PROJECT	Project	BaySide Office Space	156835	2022-08-02 20:25:09.952766+00	2022-08-02 20:25:09.952816+00	1	\N	\N	f	f
1376	PROJECT	Project	Bob Walsh Funiture Store	156836	2022-08-02 20:25:09.953084+00	2022-08-02 20:25:09.953405+00	1	\N	\N	f	f
1377	PROJECT	Project	Interior Solutions	156837	2022-08-02 20:25:09.953481+00	2022-08-02 20:25:09.95351+00	1	\N	\N	f	f
1378	PROJECT	Project	Wood Wonders Funiture	156838	2022-08-02 20:25:09.95357+00	2022-08-02 20:25:09.953598+00	1	\N	\N	f	f
1379	PROJECT	Project	Furniture Concepts	156839	2022-08-02 20:25:09.953655+00	2022-08-02 20:25:09.953683+00	1	\N	\N	f	f
1380	PROJECT	Project	Smith Inc.	156840	2022-08-02 20:25:09.95374+00	2022-08-02 20:25:09.953767+00	1	\N	\N	f	f
1381	PROJECT	Project	Future Office Designs	156841	2022-08-02 20:25:09.953824+00	2022-08-02 20:25:09.953851+00	1	\N	\N	f	f
1382	PROJECT	Project	Better Buy	156842	2022-08-02 20:25:09.953908+00	2022-08-02 20:25:09.953935+00	1	\N	\N	f	f
1383	PROJECT	Project	Circuit Cities	156843	2022-08-02 20:25:09.953992+00	2022-08-02 20:25:09.954019+00	1	\N	\N	f	f
1384	PROJECT	Project	Franklin Photography	156844	2022-08-02 20:25:09.954076+00	2022-08-02 20:25:09.954103+00	1	\N	\N	f	f
1385	PROJECT	Project	Smith Photographic Equipment	156845	2022-08-02 20:25:09.95416+00	2022-08-02 20:25:09.954187+00	1	\N	\N	f	f
1386	PROJECT	Project	Williams Electronics and Communications	156846	2022-08-02 20:25:09.954364+00	2022-08-02 20:25:09.954403+00	1	\N	\N	f	f
1387	PROJECT	Project	Electronics Direct to You	156847	2022-08-02 20:25:09.95446+00	2022-08-02 20:25:09.954487+00	1	\N	\N	f	f
1388	PROJECT	Project	Underwood New York	156848	2022-08-02 20:25:09.954544+00	2022-08-02 20:25:09.954571+00	1	\N	\N	f	f
1389	PROJECT	Project	Advanced Design & Drafting Ltd	156849	2022-08-02 20:25:09.954628+00	2022-08-02 20:25:09.954655+00	1	\N	\N	f	f
1390	PROJECT	Project	Juno Gold Wines	156850	2022-08-02 20:25:09.954711+00	2022-08-02 20:25:09.954738+00	1	\N	\N	f	f
1391	PROJECT	Project	Green Street Spirits	156851	2022-08-02 20:25:09.954795+00	2022-08-02 20:25:09.954822+00	1	\N	\N	f	f
1392	PROJECT	Project	Atherton Grocery	156852	2022-08-02 20:25:09.954878+00	2022-08-02 20:25:09.954906+00	1	\N	\N	f	f
1393	PROJECT	Project	Green Grocery	156853	2022-08-02 20:25:09.954962+00	2022-08-02 20:25:09.954989+00	1	\N	\N	f	f
1394	PROJECT	Project	Alpine Cafe and Wine Bar	156854	2022-08-02 20:25:09.955046+00	2022-08-02 20:25:09.955073+00	1	\N	\N	f	f
1395	PROJECT	Project	Tam Liquors	156855	2022-08-02 20:25:09.95513+00	2022-08-02 20:25:09.955158+00	1	\N	\N	f	f
1396	PROJECT	Project	Star Structural	156856	2022-08-02 20:25:09.955214+00	2022-08-02 20:25:09.955362+00	1	\N	\N	f	f
1397	PROJECT	Project	CPS ltd	156857	2022-08-02 20:25:09.955431+00	2022-08-02 20:25:09.955458+00	1	\N	\N	f	f
1398	PROJECT	Project	Microskills	156858	2022-08-02 20:25:09.955515+00	2022-08-02 20:25:09.955542+00	1	\N	\N	f	f
1399	PROJECT	Project	Kugan Autodesk Inc	156859	2022-08-02 20:25:09.955722+00	2022-08-02 20:25:09.955829+00	1	\N	\N	f	f
1400	PROJECT	Project	Connectus	156860	2022-08-02 20:25:09.955897+00	2022-08-02 20:25:09.955925+00	1	\N	\N	f	f
1401	PROJECT	Project	Tom MacGillivray	156861	2022-08-02 20:25:09.955983+00	2022-08-02 20:25:09.95601+00	1	\N	\N	f	f
1402	PROJECT	Project	Ross Nepean	156862	2022-08-02 20:25:09.956068+00	2022-08-02 20:25:09.956095+00	1	\N	\N	f	f
1403	PROJECT	Project	Capano Labs	156863	2022-08-02 20:25:09.956182+00	2022-08-02 20:25:09.956211+00	1	\N	\N	f	f
1404	PROJECT	Project	Defaveri Construction	156864	2022-08-02 20:25:09.956272+00	2022-08-02 20:25:09.956301+00	1	\N	\N	f	f
1405	PROJECT	Project	St Lawrence Starch	156865	2022-08-02 20:25:09.956362+00	2022-08-02 20:25:09.956391+00	1	\N	\N	f	f
1406	PROJECT	Project	Efficiency Engineering	156866	2022-08-02 20:25:09.956452+00	2022-08-02 20:25:09.956481+00	1	\N	\N	f	f
1407	PROJECT	Project	FuTech	156867	2022-08-02 20:25:09.956542+00	2022-08-02 20:25:09.95657+00	1	\N	\N	f	f
1408	PROJECT	Project	Pulse	156868	2022-08-02 20:25:09.95663+00	2022-08-02 20:25:09.956659+00	1	\N	\N	f	f
1409	PROJECT	Project	Andy Thompson	156869	2022-08-02 20:25:09.963738+00	2022-08-02 20:25:09.963792+00	1	\N	\N	f	f
1410	PROJECT	Project	Micehl Bertrand	156870	2022-08-02 20:25:09.963878+00	2022-08-02 20:25:09.964061+00	1	\N	\N	f	f
1411	PROJECT	Project	Denise Sweet	156871	2022-08-02 20:25:09.964197+00	2022-08-02 20:25:09.964229+00	1	\N	\N	f	f
1412	PROJECT	Project	Neal Ferguson	156872	2022-08-02 20:25:09.965554+00	2022-08-02 20:25:09.965635+00	1	\N	\N	f	f
1413	PROJECT	Project	Peak Products	156873	2022-08-02 20:25:09.96576+00	2022-08-02 20:25:09.965802+00	1	\N	\N	f	f
1414	PROJECT	Project	Refco	156874	2022-08-02 20:25:09.96665+00	2022-08-02 20:25:09.966692+00	1	\N	\N	f	f
1415	PROJECT	Project	Ed Obuz	156875	2022-08-02 20:25:09.96677+00	2022-08-02 20:25:09.966798+00	1	\N	\N	f	f
1416	PROJECT	Project	TST Solutions Inc	156876	2022-08-02 20:25:09.966917+00	2022-08-02 20:25:09.966947+00	1	\N	\N	f	f
1417	PROJECT	Project	Primas Consulting	156877	2022-08-02 20:25:09.96701+00	2022-08-02 20:25:09.967039+00	1	\N	\N	f	f
1418	PROJECT	Project	Russ Mygrant	156878	2022-08-02 20:25:09.967102+00	2022-08-02 20:25:09.967131+00	1	\N	\N	f	f
1419	PROJECT	Project	Ashton Consulting Ltd	156879	2022-08-02 20:25:09.967192+00	2022-08-02 20:25:09.967221+00	1	\N	\N	f	f
1420	PROJECT	Project	Alex Benedet	156880	2022-08-02 20:25:09.968067+00	2022-08-02 20:25:09.968273+00	1	\N	\N	f	f
1422	PROJECT	Project	Peterson Builders & Assoc	156882	2022-08-02 20:25:09.96845+00	2022-08-02 20:25:09.968478+00	1	\N	\N	f	f
1423	PROJECT	Project	Michael Jannsen	156883	2022-08-02 20:25:09.968535+00	2022-08-02 20:25:09.968572+00	1	\N	\N	f	f
1424	PROJECT	Project	Cino & Cino	156884	2022-08-02 20:25:09.968633+00	2022-08-02 20:25:09.968661+00	1	\N	\N	f	f
1425	PROJECT	Project	Robert Lee	156885	2022-08-02 20:25:09.968722+00	2022-08-02 20:25:09.968751+00	1	\N	\N	f	f
1426	PROJECT	Project	InterWorks Ltd	156886	2022-08-02 20:25:09.968812+00	2022-08-02 20:25:09.96884+00	1	\N	\N	f	f
1427	PROJECT	Project	Braithwaite Tech	156887	2022-08-02 20:25:09.9689+00	2022-08-02 20:25:09.968929+00	1	\N	\N	f	f
1428	PROJECT	Project	Walter Martin	156888	2022-08-02 20:25:09.96899+00	2022-08-02 20:25:09.969018+00	1	\N	\N	f	f
1429	PROJECT	Project	Vodaphone	156889	2022-08-02 20:25:09.969078+00	2022-08-02 20:25:09.969107+00	1	\N	\N	f	f
1430	PROJECT	Project	Jeff Campbell	156890	2022-08-02 20:25:09.969167+00	2022-08-02 20:25:09.969196+00	1	\N	\N	f	f
1431	PROJECT	Project	Hilltop Info Inc	156891	2022-08-02 20:25:09.969601+00	2022-08-02 20:25:09.969719+00	1	\N	\N	f	f
1432	PROJECT	Project	OREA	156892	2022-08-02 20:25:09.969793+00	2022-08-02 20:25:09.96982+00	1	\N	\N	f	f
1433	PROJECT	Project	Mitchell & assoc	156893	2022-08-02 20:25:09.969877+00	2022-08-02 20:25:09.969904+00	1	\N	\N	f	f
1434	PROJECT	Project	Steacy Tech Inc	156894	2022-08-02 20:25:09.969961+00	2022-08-02 20:25:09.969988+00	1	\N	\N	f	f
1435	PROJECT	Project	Eyram Marketing	156895	2022-08-02 20:25:09.970045+00	2022-08-02 20:25:09.970072+00	1	\N	\N	f	f
1436	PROJECT	Project	Pittaway Inc	156896	2022-08-02 20:25:09.970129+00	2022-08-02 20:25:09.970156+00	1	\N	\N	f	f
1437	PROJECT	Project	Kevin Smith	156897	2022-08-02 20:25:09.970442+00	2022-08-02 20:25:09.970485+00	1	\N	\N	f	f
1438	PROJECT	Project	TTS inc	156898	2022-08-02 20:25:09.970746+00	2022-08-02 20:25:09.970774+00	1	\N	\N	f	f
1439	PROJECT	Project	AIQ Networks	156899	2022-08-02 20:25:09.970832+00	2022-08-02 20:25:09.970859+00	1	\N	\N	f	f
1440	PROJECT	Project	Roycroft Construction	156900	2022-08-02 20:25:09.970916+00	2022-08-02 20:25:09.970943+00	1	\N	\N	f	f
1441	PROJECT	Project	Canuck Door Systems Co.	156901	2022-08-02 20:25:09.971001+00	2022-08-02 20:25:09.971028+00	1	\N	\N	f	f
1442	PROJECT	Project	Fiore Fashion Inc	156902	2022-08-02 20:25:09.971084+00	2022-08-02 20:25:09.971112+00	1	\N	\N	f	f
1443	PROJECT	Project	Ford Models Inc	156903	2022-08-02 20:25:09.971286+00	2022-08-02 20:25:09.971348+00	1	\N	\N	f	f
1444	PROJECT	Project	CICA	156904	2022-08-02 20:25:09.971421+00	2022-08-02 20:25:09.971449+00	1	\N	\N	f	f
1445	PROJECT	Project	Applications to go Inc	156905	2022-08-02 20:25:09.971506+00	2022-08-02 20:25:09.971533+00	1	\N	\N	f	f
1446	PROJECT	Project	Lintex Group	156906	2022-08-02 20:25:09.971589+00	2022-08-02 20:25:09.971617+00	1	\N	\N	f	f
1447	PROJECT	Project	Alchemy PR	156907	2022-08-02 20:25:09.971673+00	2022-08-02 20:25:09.9717+00	1	\N	\N	f	f
1448	PROJECT	Project	Emergys	156908	2022-08-02 20:25:09.971756+00	2022-08-02 20:25:09.971783+00	1	\N	\N	f	f
1449	PROJECT	Project	Bona Source	156909	2022-08-02 20:25:09.97184+00	2022-08-02 20:25:09.971867+00	1	\N	\N	f	f
1450	PROJECT	Project	Cytec Industries Inc	156910	2022-08-02 20:25:09.971923+00	2022-08-02 20:25:09.97195+00	1	\N	\N	f	f
1451	PROJECT	Project	NetPace Promotions	156911	2022-08-02 20:25:09.972006+00	2022-08-02 20:25:09.972033+00	1	\N	\N	f	f
1452	PROJECT	Project	Creighton & Company	156912	2022-08-02 20:25:09.972089+00	2022-08-02 20:25:09.972116+00	1	\N	\N	f	f
1453	PROJECT	Project	Mitra	156913	2022-08-02 20:25:09.972172+00	2022-08-02 20:25:09.972199+00	1	\N	\N	f	f
1454	PROJECT	Project	The Validation Group	156914	2022-08-02 20:25:09.972492+00	2022-08-02 20:25:09.972535+00	1	\N	\N	f	f
1455	PROJECT	Project	CH2M Hill Ltd	156915	2022-08-02 20:25:09.972595+00	2022-08-02 20:25:09.972623+00	1	\N	\N	f	f
1456	PROJECT	Project	Chamberlain Service Ltd	156916	2022-08-02 20:25:09.972681+00	2022-08-02 20:25:09.972708+00	1	\N	\N	f	f
1457	PROJECT	Project	Steve Smith	156917	2022-08-02 20:25:09.972765+00	2022-08-02 20:25:09.972792+00	1	\N	\N	f	f
1458	PROJECT	Project	Imran Kahn	156918	2022-08-02 20:25:09.972877+00	2022-08-02 20:25:09.972907+00	1	\N	\N	f	f
1459	PROJECT	Project	X Eye Corp	156919	2022-08-02 20:25:09.97887+00	2022-08-02 20:25:09.978911+00	1	\N	\N	f	f
1460	PROJECT	Project	OSPE Inc	156920	2022-08-02 20:25:09.97897+00	2022-08-02 20:25:09.978998+00	1	\N	\N	f	f
1461	PROJECT	Project	Soltrus	156921	2022-08-02 20:25:09.979055+00	2022-08-02 20:25:09.979082+00	1	\N	\N	f	f
1462	PROJECT	Project	Stone & Cox	156922	2022-08-02 20:25:09.979139+00	2022-08-02 20:25:09.979167+00	1	\N	\N	f	f
1463	PROJECT	Project	Integrys Ltd	156923	2022-08-02 20:25:09.979529+00	2022-08-02 20:25:09.979702+00	1	\N	\N	f	f
1464	PROJECT	Project	Empire Financial Group	156924	2022-08-02 20:25:09.979891+00	2022-08-02 20:25:09.979926+00	1	\N	\N	f	f
1465	PROJECT	Project	TWC Financial	156925	2022-08-02 20:25:09.980146+00	2022-08-02 20:25:09.980466+00	1	\N	\N	f	f
1466	PROJECT	Project	Lead 154	156926	2022-08-02 20:25:09.980557+00	2022-08-02 20:25:09.980585+00	1	\N	\N	f	f
1467	PROJECT	Project	Lead 155	156927	2022-08-02 20:25:09.980642+00	2022-08-02 20:25:09.980669+00	1	\N	\N	f	f
1468	PROJECT	Project	Effectiovation Inc	156928	2022-08-02 20:25:09.980726+00	2022-08-02 20:25:09.980753+00	1	\N	\N	f	f
1469	PROJECT	Project	SlingShot Communications	156929	2022-08-02 20:25:09.98081+00	2022-08-02 20:25:09.980837+00	1	\N	\N	f	f
1470	PROJECT	Project	Mentor Graphics	156930	2022-08-02 20:25:09.980894+00	2022-08-02 20:25:09.980921+00	1	\N	\N	f	f
1471	PROJECT	Project	Absolute Location Support	156931	2022-08-02 20:25:09.980977+00	2022-08-02 20:25:09.981004+00	1	\N	\N	f	f
1472	PROJECT	Project	AmerCaire	156932	2022-08-02 20:25:09.98106+00	2022-08-02 20:25:09.981087+00	1	\N	\N	f	f
1473	PROJECT	Project	Top Drawer Creative	156933	2022-08-02 20:25:09.981144+00	2022-08-02 20:25:09.981171+00	1	\N	\N	f	f
1474	PROJECT	Project	Espar Heater Systems	156934	2022-08-02 20:25:09.981227+00	2022-08-02 20:25:09.981254+00	1	\N	\N	f	f
1475	PROJECT	Project	Gresham	156935	2022-08-02 20:25:09.981434+00	2022-08-02 20:25:09.981473+00	1	\N	\N	f	f
1476	PROJECT	Project	Megaloid labs	156936	2022-08-02 20:25:09.98153+00	2022-08-02 20:25:09.981558+00	1	\N	\N	f	f
1477	PROJECT	Project	Orion Hardware	156937	2022-08-02 20:25:09.981614+00	2022-08-02 20:25:09.981642+00	1	\N	\N	f	f
1478	PROJECT	Project	Brytor Inetrnational	156938	2022-08-02 20:25:09.981698+00	2022-08-02 20:25:09.981725+00	1	\N	\N	f	f
1479	PROJECT	Project	Axxess Group	156939	2022-08-02 20:25:09.981782+00	2022-08-02 20:25:09.981809+00	1	\N	\N	f	f
1480	PROJECT	Project	MuscleTech	156940	2022-08-02 20:25:09.981866+00	2022-08-02 20:25:09.981893+00	1	\N	\N	f	f
1481	PROJECT	Project	McKay Financial	156941	2022-08-02 20:25:09.981949+00	2022-08-02 20:25:09.981976+00	1	\N	\N	f	f
1482	PROJECT	Project	eNable Corp	156942	2022-08-02 20:25:09.982033+00	2022-08-02 20:25:09.982059+00	1	\N	\N	f	f
1483	PROJECT	Project	Kino Inc	156943	2022-08-02 20:25:09.982116+00	2022-08-02 20:25:09.982143+00	1	\N	\N	f	f
1484	PROJECT	Project	Progress Inc	156944	2022-08-02 20:25:09.98221+00	2022-08-02 20:25:09.98239+00	1	\N	\N	f	f
1485	PROJECT	Project	Quantum X	156945	2022-08-02 20:25:09.982464+00	2022-08-02 20:25:09.982504+00	1	\N	\N	f	f
1486	PROJECT	Project	BFI Inc	156946	2022-08-02 20:25:09.982562+00	2022-08-02 20:25:09.98259+00	1	\N	\N	f	f
1487	PROJECT	Project	ACM Group	156947	2022-08-02 20:25:09.982647+00	2022-08-02 20:25:09.982674+00	1	\N	\N	f	f
1488	PROJECT	Project	Dominion Consulting	156948	2022-08-02 20:25:09.982731+00	2022-08-02 20:25:09.982759+00	1	\N	\N	f	f
1489	PROJECT	Project	Lou Baus	156949	2022-08-02 20:25:09.982815+00	2022-08-02 20:25:09.982842+00	1	\N	\N	f	f
1490	PROJECT	Project	Computer Literacy	156950	2022-08-02 20:25:09.982911+00	2022-08-02 20:25:09.98294+00	1	\N	\N	f	f
1491	PROJECT	Project	Simatry	156951	2022-08-02 20:25:09.983001+00	2022-08-02 20:25:09.98303+00	1	\N	\N	f	f
1492	PROJECT	Project	Moving Store	156952	2022-08-02 20:25:09.98309+00	2022-08-02 20:25:09.983119+00	1	\N	\N	f	f
1493	PROJECT	Project	Pitney Bowes	156953	2022-08-02 20:25:09.983179+00	2022-08-02 20:25:09.983208+00	1	\N	\N	f	f
1494	PROJECT	Project	Bushnell	156954	2022-08-02 20:25:09.983268+00	2022-08-02 20:25:09.983495+00	1	\N	\N	f	f
1495	PROJECT	Project	TES Inc	156955	2022-08-02 20:25:09.983591+00	2022-08-02 20:25:09.98362+00	1	\N	\N	f	f
1496	PROJECT	Project	Wood-Mizer	156956	2022-08-02 20:25:09.983678+00	2022-08-02 20:25:09.983706+00	1	\N	\N	f	f
1497	PROJECT	Project	Medcan Mgmt Inc	156957	2022-08-02 20:25:09.983762+00	2022-08-02 20:25:09.983789+00	1	\N	\N	f	f
1498	PROJECT	Project	Mandos	156958	2022-08-02 20:25:09.983845+00	2022-08-02 20:25:09.983872+00	1	\N	\N	f	f
1499	PROJECT	Project	McEdwards & Whitwell	156959	2022-08-02 20:25:09.983929+00	2022-08-02 20:25:09.983956+00	1	\N	\N	f	f
1500	PROJECT	Project	Titam Business Services	156960	2022-08-02 20:25:09.984011+00	2022-08-02 20:25:09.984038+00	1	\N	\N	f	f
1501	PROJECT	Project	TSM	156961	2022-08-02 20:25:09.984094+00	2022-08-02 20:25:09.984121+00	1	\N	\N	f	f
1502	PROJECT	Project	Technology Consultants	156962	2022-08-02 20:25:09.984178+00	2022-08-02 20:25:09.984316+00	1	\N	\N	f	f
1503	PROJECT	Project	Solidd Group Ltd	156963	2022-08-02 20:25:09.984386+00	2022-08-02 20:25:09.984413+00	1	\N	\N	f	f
1504	PROJECT	Project	CIS Environmental Services	156964	2022-08-02 20:25:09.98447+00	2022-08-02 20:25:09.984497+00	1	\N	\N	f	f
1505	PROJECT	Project	Upper 49th	156965	2022-08-02 20:25:09.984553+00	2022-08-02 20:25:09.98458+00	1	\N	\N	f	f
1506	PROJECT	Project	Team Industrial	156966	2022-08-02 20:25:09.984636+00	2022-08-02 20:25:09.984663+00	1	\N	\N	f	f
1507	PROJECT	Project	David Langhor	156967	2022-08-02 20:25:09.984719+00	2022-08-02 20:25:09.984746+00	1	\N	\N	f	f
1508	PROJECT	Project	MPower	156968	2022-08-02 20:25:09.984803+00	2022-08-02 20:25:09.98483+00	1	\N	\N	f	f
1509	PROJECT	Project	Alain Henderson	156969	2022-08-02 20:25:10.246464+00	2022-08-02 20:25:10.246516+00	1	\N	\N	f	f
1510	PROJECT	Project	Samantha Walker	156970	2022-08-02 20:25:10.2466+00	2022-08-02 20:25:10.246634+00	1	\N	\N	f	f
1511	PROJECT	Project	ICC Inc	156971	2022-08-02 20:25:10.246712+00	2022-08-02 20:25:10.246745+00	1	\N	\N	f	f
1512	PROJECT	Project	Lomax Transportation	156972	2022-08-02 20:25:10.246812+00	2022-08-02 20:25:10.246843+00	1	\N	\N	f	f
1513	PROJECT	Project	Graber & Assoc	156973	2022-08-02 20:25:10.246908+00	2022-08-02 20:25:10.24694+00	1	\N	\N	f	f
1514	PROJECT	Project	Carlos Beato	156974	2022-08-02 20:25:10.247007+00	2022-08-02 20:25:10.247374+00	1	\N	\N	f	f
1515	PROJECT	Project	Graydon	156975	2022-08-02 20:25:10.247736+00	2022-08-02 20:25:10.24779+00	1	\N	\N	f	f
1516	PROJECT	Project	Bennett Consulting	156976	2022-08-02 20:25:10.24787+00	2022-08-02 20:25:10.247898+00	1	\N	\N	f	f
1517	PROJECT	Project	Cooper Equipment	156977	2022-08-02 20:25:10.247956+00	2022-08-02 20:25:10.247983+00	1	\N	\N	f	f
1518	PROJECT	Project	Sedlak Inc	156978	2022-08-02 20:25:10.248041+00	2022-08-02 20:25:10.248069+00	1	\N	\N	f	f
1519	PROJECT	Project	TargetVision	156979	2022-08-02 20:25:10.248126+00	2022-08-02 20:25:10.248154+00	1	\N	\N	f	f
1520	PROJECT	Project	Spany ltd	156980	2022-08-02 20:25:10.248211+00	2022-08-02 20:25:10.248371+00	1	\N	\N	f	f
1521	PROJECT	Project	Tomlinson	156981	2022-08-02 20:25:10.248443+00	2022-08-02 20:25:10.248471+00	1	\N	\N	f	f
1522	PROJECT	Project	Mortgage Center	156982	2022-08-02 20:25:10.248528+00	2022-08-02 20:25:10.248555+00	1	\N	\N	f	f
1523	PROJECT	Project	TAB Ltd	156983	2022-08-02 20:25:10.248612+00	2022-08-02 20:25:10.248639+00	1	\N	\N	f	f
1524	PROJECT	Project	Oaks and Winters Inc	156984	2022-08-02 20:25:10.248696+00	2022-08-02 20:25:10.248723+00	1	\N	\N	f	f
1525	PROJECT	Project	Maple Leaf Foods	156985	2022-08-02 20:25:10.24878+00	2022-08-02 20:25:10.248808+00	1	\N	\N	f	f
1526	PROJECT	Project	Martin Gelina	156986	2022-08-02 20:25:10.248864+00	2022-08-02 20:25:10.248891+00	1	\N	\N	f	f
1527	PROJECT	Project	Hextall Consulting	156987	2022-08-02 20:25:10.248948+00	2022-08-02 20:25:10.248975+00	1	\N	\N	f	f
1528	PROJECT	Project	Conway Products	156988	2022-08-02 20:25:10.249033+00	2022-08-02 20:25:10.24906+00	1	\N	\N	f	f
1529	PROJECT	Project	Sandoval Products Inc	156989	2022-08-02 20:25:10.249117+00	2022-08-02 20:25:10.249144+00	1	\N	\N	f	f
1530	PROJECT	Project	All-Lift Inc	156990	2022-08-02 20:25:10.2492+00	2022-08-02 20:25:10.24935+00	1	\N	\N	f	f
1531	PROJECT	Project	Stirling Truck Services	156991	2022-08-02 20:25:10.249483+00	2022-08-02 20:25:10.24951+00	1	\N	\N	f	f
1532	PROJECT	Project	Bracken Works Inc	156992	2022-08-02 20:25:10.249567+00	2022-08-02 20:25:10.249594+00	1	\N	\N	f	f
1533	PROJECT	Project	Ponniah	156993	2022-08-02 20:25:10.249651+00	2022-08-02 20:25:10.249678+00	1	\N	\N	f	f
1534	PROJECT	Project	Lillian Thurham	156994	2022-08-02 20:25:10.249735+00	2022-08-02 20:25:10.249762+00	1	\N	\N	f	f
1535	PROJECT	Project	NetStar Inc	156995	2022-08-02 20:25:10.24982+00	2022-08-02 20:25:10.249848+00	1	\N	\N	f	f
1536	PROJECT	Project	Cathy Thoms	156996	2022-08-02 20:25:10.249905+00	2022-08-02 20:25:10.249932+00	1	\N	\N	f	f
1537	PROJECT	Project	Lisa Fiore	156997	2022-08-02 20:25:10.249989+00	2022-08-02 20:25:10.250016+00	1	\N	\N	f	f
1538	PROJECT	Project	Jackie Kugan	156998	2022-08-02 20:25:10.250073+00	2022-08-02 20:25:10.2501+00	1	\N	\N	f	f
1539	PROJECT	Project	Krista Thomas Recruiting	156999	2022-08-02 20:25:10.250157+00	2022-08-02 20:25:10.250184+00	1	\N	\N	f	f
1540	PROJECT	Project	Rowie Williams	157000	2022-08-02 20:25:10.25041+00	2022-08-02 20:25:10.250438+00	1	\N	\N	f	f
1541	PROJECT	Project	Henderson Cooper	157001	2022-08-02 20:25:10.250496+00	2022-08-02 20:25:10.250536+00	1	\N	\N	f	f
1542	PROJECT	Project	AB&I Holdings	157002	2022-08-02 20:25:10.251285+00	2022-08-02 20:25:10.251315+00	1	\N	\N	f	f
1543	PROJECT	Project	Prudential	157003	2022-08-02 20:25:10.251472+00	2022-08-02 20:25:10.251511+00	1	\N	\N	f	f
1544	PROJECT	Project	Acera	157004	2022-08-02 20:25:10.251568+00	2022-08-02 20:25:10.251596+00	1	\N	\N	f	f
1545	PROJECT	Project	Fossil Watch Limited	157005	2022-08-02 20:25:10.251654+00	2022-08-02 20:25:10.251681+00	1	\N	\N	f	f
1546	PROJECT	Project	Bertulli & Assoc	157006	2022-08-02 20:25:10.251738+00	2022-08-02 20:25:10.251766+00	1	\N	\N	f	f
1547	PROJECT	Project	Beattie Batteries	157007	2022-08-02 20:25:10.251822+00	2022-08-02 20:25:10.25185+00	1	\N	\N	f	f
1626	PROJECT	Project	Test 2	157086	2022-08-02 20:25:10.276129+00	2022-08-02 20:25:10.276156+00	1	\N	\N	f	f
1548	PROJECT	Project	Gale Custom Sailboat	157008	2022-08-02 20:25:10.251907+00	2022-08-02 20:25:10.251934+00	1	\N	\N	f	f
1549	PROJECT	Project	Thorne & Assoc	157009	2022-08-02 20:25:10.251992+00	2022-08-02 20:25:10.252019+00	1	\N	\N	f	f
1550	PROJECT	Project	RedPath Sugars	157010	2022-08-02 20:25:10.252077+00	2022-08-02 20:25:10.252104+00	1	\N	\N	f	f
1551	PROJECT	Project	Trebor Allen Candy	157011	2022-08-02 20:25:10.252161+00	2022-08-02 20:25:10.252188+00	1	\N	\N	f	f
1552	PROJECT	Project	Lakeside Inc	157012	2022-08-02 20:25:10.252381+00	2022-08-02 20:25:10.252417+00	1	\N	\N	f	f
1553	PROJECT	Project	Brewers Retail	157013	2022-08-02 20:25:10.252489+00	2022-08-02 20:25:10.252517+00	1	\N	\N	f	f
1554	PROJECT	Project	Hershey's Canada	157014	2022-08-02 20:25:10.252574+00	2022-08-02 20:25:10.252601+00	1	\N	\N	f	f
1555	PROJECT	Project	SS&C	157015	2022-08-02 20:25:10.252658+00	2022-08-02 20:25:10.252686+00	1	\N	\N	f	f
1556	PROJECT	Project	Nikon	157016	2022-08-02 20:25:10.252743+00	2022-08-02 20:25:10.25277+00	1	\N	\N	f	f
1557	PROJECT	Project	AMG Inc	157017	2022-08-02 20:25:10.252827+00	2022-08-02 20:25:10.252854+00	1	\N	\N	f	f
1558	PROJECT	Project	Cash & Warren	157018	2022-08-02 20:25:10.25291+00	2022-08-02 20:25:10.252937+00	1	\N	\N	f	f
1559	PROJECT	Project	Medved	157019	2022-08-02 20:25:10.260568+00	2022-08-02 20:25:10.26061+00	1	\N	\N	f	f
1560	PROJECT	Project	Castek Inc	157020	2022-08-02 20:25:10.260678+00	2022-08-02 20:25:10.260706+00	1	\N	\N	f	f
1561	PROJECT	Project	Millenium Engineering	157021	2022-08-02 20:25:10.260766+00	2022-08-02 20:25:10.260794+00	1	\N	\N	f	f
1562	PROJECT	Project	QJunction Inc	157022	2022-08-02 20:25:10.260852+00	2022-08-02 20:25:10.26088+00	1	\N	\N	f	f
1563	PROJECT	Project	FigmentSoft Inc	157023	2022-08-02 20:25:10.260937+00	2022-08-02 20:25:10.260965+00	1	\N	\N	f	f
1564	PROJECT	Project	UniExchange	157024	2022-08-02 20:25:10.261023+00	2022-08-02 20:25:10.26105+00	1	\N	\N	f	f
1565	PROJECT	Project	AIM Accounting	157025	2022-08-02 20:25:10.261108+00	2022-08-02 20:25:10.261135+00	1	\N	\N	f	f
1566	PROJECT	Project	Polard Windows	157026	2022-08-02 20:25:10.261193+00	2022-08-02 20:25:10.26122+00	1	\N	\N	f	f
1567	PROJECT	Project	GlassHouse Systems	157027	2022-08-02 20:25:10.261438+00	2022-08-02 20:25:10.261466+00	1	\N	\N	f	f
1568	PROJECT	Project	Fantasy Gemmart	157028	2022-08-02 20:25:10.261538+00	2022-08-02 20:25:10.261565+00	1	\N	\N	f	f
1569	PROJECT	Project	Stantec Inc	157029	2022-08-02 20:25:10.261623+00	2022-08-02 20:25:10.261651+00	1	\N	\N	f	f
1570	PROJECT	Project	Johnson & Johnson	157030	2022-08-02 20:25:10.261709+00	2022-08-02 20:25:10.261737+00	1	\N	\N	f	f
1571	PROJECT	Project	Vertex	157031	2022-08-02 20:25:10.261794+00	2022-08-02 20:25:10.261821+00	1	\N	\N	f	f
1572	PROJECT	Project	Novx	157032	2022-08-02 20:25:10.261879+00	2022-08-02 20:25:10.261907+00	1	\N	\N	f	f
1573	PROJECT	Project	Linear International Footwear	157033	2022-08-02 20:25:10.261964+00	2022-08-02 20:25:10.261992+00	1	\N	\N	f	f
1574	PROJECT	Project	Baylore	157034	2022-08-02 20:25:10.262049+00	2022-08-02 20:25:10.262077+00	1	\N	\N	f	f
1575	PROJECT	Project	Whole Oats Markets	157035	2022-08-02 20:25:10.262134+00	2022-08-02 20:25:10.262162+00	1	\N	\N	f	f
1576	PROJECT	Project	Melissa Wine Shop	157036	2022-08-02 20:25:10.262233+00	2022-08-02 20:25:10.262373+00	1	\N	\N	f	f
1577	PROJECT	Project	Everett International	157037	2022-08-02 20:25:10.262438+00	2022-08-02 20:25:10.262467+00	1	\N	\N	f	f
1578	PROJECT	Project	Core Care Canada	157038	2022-08-02 20:25:10.262536+00	2022-08-02 20:25:10.262563+00	1	\N	\N	f	f
1579	PROJECT	Project	Smith East	157039	2022-08-02 20:25:10.262621+00	2022-08-02 20:25:10.262648+00	1	\N	\N	f	f
1580	PROJECT	Project	Bob Smith (bsmith@bobsmith.com)	157040	2022-08-02 20:25:10.262705+00	2022-08-02 20:25:10.262733+00	1	\N	\N	f	f
1581	PROJECT	Project	New Ventures	157041	2022-08-02 20:25:10.26279+00	2022-08-02 20:25:10.262818+00	1	\N	\N	f	f
1582	PROJECT	Project	Avac Supplies Ltd.	157042	2022-08-02 20:25:10.262874+00	2022-08-02 20:25:10.262901+00	1	\N	\N	f	f
1583	PROJECT	Project	Culprit Inc.	157043	2022-08-02 20:25:10.262958+00	2022-08-02 20:25:10.262986+00	1	\N	\N	f	f
1584	PROJECT	Project	Joe Smith	157044	2022-08-02 20:25:10.263043+00	2022-08-02 20:25:10.26307+00	1	\N	\N	f	f
1585	PROJECT	Project	Mike Miller	157045	2022-08-02 20:25:10.263185+00	2022-08-02 20:25:10.263314+00	1	\N	\N	f	f
1586	PROJECT	Project	HGH Vision	157046	2022-08-02 20:25:10.2634+00	2022-08-02 20:25:10.263431+00	1	\N	\N	f	f
1587	PROJECT	Project	Watertown Hicks	157047	2022-08-02 20:25:10.263492+00	2022-08-02 20:25:10.263521+00	1	\N	\N	f	f
1588	PROJECT	Project	Jake Hamilton	157048	2022-08-02 20:25:10.263776+00	2022-08-02 20:25:10.263831+00	1	\N	\N	f	f
1589	PROJECT	Project	Bobby Kelly	157049	2022-08-02 20:25:10.26398+00	2022-08-02 20:25:10.264026+00	1	\N	\N	f	f
1590	PROJECT	Project	Gary Underwood	157050	2022-08-02 20:25:10.264137+00	2022-08-02 20:25:10.264471+00	1	\N	\N	f	f
1591	PROJECT	Project	Frank Edwards	157051	2022-08-02 20:25:10.264655+00	2022-08-02 20:25:10.264705+00	1	\N	\N	f	f
1592	PROJECT	Project	Kate Winters	157052	2022-08-02 20:25:10.265015+00	2022-08-02 20:25:10.265053+00	1	\N	\N	f	f
1593	PROJECT	Project	Mike Dee	157053	2022-08-02 20:25:10.265404+00	2022-08-02 20:25:10.265453+00	1	\N	\N	f	f
1594	PROJECT	Project	Greg Muller	157054	2022-08-02 20:25:10.265537+00	2022-08-02 20:25:10.265565+00	1	\N	\N	f	f
1595	PROJECT	Project	Arnold Tanner	157055	2022-08-02 20:25:10.265625+00	2022-08-02 20:25:10.265652+00	1	\N	\N	f	f
1596	PROJECT	Project	Trent Barry	157056	2022-08-02 20:25:10.26571+00	2022-08-02 20:25:10.265737+00	1	\N	\N	f	f
1597	PROJECT	Project	Tom Kratz	157057	2022-08-02 20:25:10.265794+00	2022-08-02 20:25:10.265822+00	1	\N	\N	f	f
1598	PROJECT	Project	Oiler Corporation	157058	2022-08-02 20:25:10.265879+00	2022-08-02 20:25:10.265906+00	1	\N	\N	f	f
1599	PROJECT	Project	Randy Rudd	157059	2022-08-02 20:25:10.265963+00	2022-08-02 20:25:10.26599+00	1	\N	\N	f	f
1600	PROJECT	Project	IBA Enterprises Inc	157060	2022-08-02 20:25:10.266046+00	2022-08-02 20:25:10.266074+00	1	\N	\N	f	f
1601	PROJECT	Project	Accountants Inc	157061	2022-08-02 20:25:10.266131+00	2022-08-02 20:25:10.266158+00	1	\N	\N	f	f
1602	PROJECT	Project	qa 54	157062	2022-08-02 20:25:10.266215+00	2022-08-02 20:25:10.266254+00	1	\N	\N	f	f
1603	PROJECT	Project	Ben Sandler	157063	2022-08-02 20:25:10.26648+00	2022-08-02 20:25:10.266519+00	1	\N	\N	f	f
1604	PROJECT	Project	Andrew Mager	157064	2022-08-02 20:25:10.266577+00	2022-08-02 20:25:10.266604+00	1	\N	\N	f	f
1605	PROJECT	Project	James McClure	157065	2022-08-02 20:25:10.26666+00	2022-08-02 20:25:10.266687+00	1	\N	\N	f	f
1606	PROJECT	Project	Louis Fabre	157066	2022-08-02 20:25:10.266744+00	2022-08-02 20:25:10.266772+00	1	\N	\N	f	f
1607	PROJECT	Project	Andy Johnson	157067	2022-08-02 20:25:10.266828+00	2022-08-02 20:25:10.266855+00	1	\N	\N	f	f
1608	PROJECT	Project	Robert Brady	157068	2022-08-02 20:25:10.266912+00	2022-08-02 20:25:10.266939+00	1	\N	\N	f	f
1609	PROJECT	Project	Jamie Taylor	157069	2022-08-02 20:25:10.273843+00	2022-08-02 20:25:10.273902+00	1	\N	\N	f	f
1610	PROJECT	Project	Robert Huffman	157070	2022-08-02 20:25:10.273991+00	2022-08-02 20:25:10.274027+00	1	\N	\N	f	f
1611	PROJECT	Project	KEM Corporation	157071	2022-08-02 20:25:10.274104+00	2022-08-02 20:25:10.274138+00	1	\N	\N	f	f
1612	PROJECT	Project	Jim Strong	157072	2022-08-02 20:25:10.274642+00	2022-08-02 20:25:10.274699+00	1	\N	\N	f	f
1613	PROJECT	Project	Randy James	157073	2022-08-02 20:25:10.274783+00	2022-08-02 20:25:10.274813+00	1	\N	\N	f	f
1614	PROJECT	Project	Sam Brown	157074	2022-08-02 20:25:10.274878+00	2022-08-02 20:25:10.274915+00	1	\N	\N	f	f
1615	PROJECT	Project	Lisa Wilson	157075	2022-08-02 20:25:10.274975+00	2022-08-02 20:25:10.275002+00	1	\N	\N	f	f
1616	PROJECT	Project	Justin Ramos	157076	2022-08-02 20:25:10.275061+00	2022-08-02 20:25:10.275088+00	1	\N	\N	f	f
1617	PROJECT	Project	Alex Fabre	157077	2022-08-02 20:25:10.275145+00	2022-08-02 20:25:10.275184+00	1	\N	\N	f	f
1618	PROJECT	Project	Michael Wakefield	157078	2022-08-02 20:25:10.27536+00	2022-08-02 20:25:10.275394+00	1	\N	\N	f	f
1619	PROJECT	Project	Eric Korb	157079	2022-08-02 20:25:10.275464+00	2022-08-02 20:25:10.275491+00	1	\N	\N	f	f
1620	PROJECT	Project	Katie Fischer	157080	2022-08-02 20:25:10.275549+00	2022-08-02 20:25:10.275576+00	1	\N	\N	f	f
1621	PROJECT	Project	Test a	157081	2022-08-02 20:25:10.275633+00	2022-08-02 20:25:10.27566+00	1	\N	\N	f	f
1622	PROJECT	Project	CPSA	157082	2022-08-02 20:25:10.275717+00	2022-08-02 20:25:10.275744+00	1	\N	\N	f	f
1623	PROJECT	Project	Celia Corp	157083	2022-08-02 20:25:10.275802+00	2022-08-02 20:25:10.275858+00	1	\N	\N	f	f
1624	PROJECT	Project	test	157084	2022-08-02 20:25:10.275957+00	2022-08-02 20:25:10.275986+00	1	\N	\N	f	f
1625	PROJECT	Project	Iain Bennett	157085	2022-08-02 20:25:10.276044+00	2022-08-02 20:25:10.276072+00	1	\N	\N	f	f
1627	PROJECT	Project	Wiggles Inc.	157087	2022-08-02 20:25:10.276213+00	2022-08-02 20:25:10.276332+00	1	\N	\N	f	f
1628	PROJECT	Project	JKL Co.	157088	2022-08-02 20:25:10.276402+00	2022-08-02 20:25:10.276429+00	1	\N	\N	f	f
1629	PROJECT	Project	Ambc	157089	2022-08-02 20:25:10.276486+00	2022-08-02 20:25:10.276514+00	1	\N	\N	f	f
1630	PROJECT	Project	3M	157090	2022-08-02 20:25:10.276571+00	2022-08-02 20:25:10.276597+00	1	\N	\N	f	f
1631	PROJECT	Project	Cooper Industries	157091	2022-08-02 20:25:10.276654+00	2022-08-02 20:25:10.276681+00	1	\N	\N	f	f
1632	PROJECT	Project	August Li	157092	2022-08-02 20:25:10.276738+00	2022-08-02 20:25:10.276765+00	1	\N	\N	f	f
1633	PROJECT	Project	Gus Li	157093	2022-08-02 20:25:10.276821+00	2022-08-02 20:25:10.276848+00	1	\N	\N	f	f
1634	PROJECT	Project	Gus Photography	157094	2022-08-02 20:25:10.276904+00	2022-08-02 20:25:10.276931+00	1	\N	\N	f	f
1635	PROJECT	Project	Gus Lee	157095	2022-08-02 20:25:10.276988+00	2022-08-02 20:25:10.277016+00	1	\N	\N	f	f
1636	PROJECT	Project	Tessa Darby	157096	2022-08-02 20:25:10.277072+00	2022-08-02 20:25:10.2771+00	1	\N	\N	f	f
1637	PROJECT	Project	South East	157097	2022-08-02 20:25:10.277158+00	2022-08-02 20:25:10.277303+00	1	\N	\N	f	f
1638	PROJECT	Project	Smith West	157098	2022-08-02 20:25:10.277374+00	2022-08-02 20:25:10.277402+00	1	\N	\N	f	f
1639	PROJECT	Project	Pacific Northwest	157099	2022-08-02 20:25:10.277458+00	2022-08-02 20:25:10.277486+00	1	\N	\N	f	f
1640	PROJECT	Project	Canadian Customer	157100	2022-08-02 20:25:10.277542+00	2022-08-02 20:25:10.27757+00	1	\N	\N	f	f
1641	PROJECT	Project	UK Customer	157101	2022-08-02 20:25:10.277626+00	2022-08-02 20:25:10.277653+00	1	\N	\N	f	f
1642	PROJECT	Project	Webmaster Gproxy	157102	2022-08-02 20:25:10.277709+00	2022-08-02 20:25:10.277737+00	1	\N	\N	f	f
1643	PROJECT	Project	GProxy Online	157103	2022-08-02 20:25:10.277793+00	2022-08-02 20:25:10.27782+00	1	\N	\N	f	f
1644	PROJECT	Project	DellPack (UK)	157104	2022-08-02 20:25:10.277877+00	2022-08-02 20:25:10.277904+00	1	\N	\N	f	f
1645	PROJECT	Project	Plantronics (EUR)	157105	2022-08-02 20:25:10.277962+00	2022-08-02 20:25:10.277989+00	1	\N	\N	f	f
1646	PROJECT	Project	MW International (CAD)	157106	2022-08-02 20:25:10.278046+00	2022-08-02 20:25:10.278073+00	1	\N	\N	f	f
1647	PROJECT	Project	FSI Industries (EUR)	157107	2022-08-02 20:25:10.27813+00	2022-08-02 20:25:10.278157+00	1	\N	\N	f	f
1648	PROJECT	Project	Eugenio	157108	2022-08-02 20:25:10.278214+00	2022-08-02 20:25:10.278369+00	1	\N	\N	f	f
1649	PROJECT	Project	Test 3	157109	2022-08-02 20:25:10.27844+00	2022-08-02 20:25:10.278468+00	1	\N	\N	f	f
1650	PROJECT	Project	Alpart	157110	2022-08-02 20:25:10.278524+00	2022-08-02 20:25:10.278552+00	1	\N	\N	f	f
1651	PROJECT	Project	tester1	157111	2022-08-02 20:25:10.278608+00	2022-08-02 20:25:10.278635+00	1	\N	\N	f	f
1652	PROJECT	Project	Test Test	157112	2022-08-02 20:25:10.278692+00	2022-08-02 20:25:10.278719+00	1	\N	\N	f	f
1653	PROJECT	Project	Rogers Communication	157113	2022-08-02 20:25:10.278776+00	2022-08-02 20:25:10.278803+00	1	\N	\N	f	f
1654	PROJECT	Project	Global Supplies Inc.	157114	2022-08-02 20:25:10.27886+00	2022-08-02 20:25:10.278887+00	1	\N	\N	f	f
1655	PROJECT	Project	John Paulsen	157115	2022-08-02 20:25:10.278943+00	2022-08-02 20:25:10.27897+00	1	\N	\N	f	f
1658	PROJECT	Project	NetSuite Incorp	157118	2022-08-02 20:25:10.279209+00	2022-08-02 20:25:10.279336+00	1	\N	\N	f	f
1659	PROJECT	Project	MAC	157119	2022-08-02 20:25:10.285509+00	2022-08-02 20:25:10.285552+00	1	\N	\N	f	f
1660	PROJECT	Project	Estee Lauder	157120	2022-08-02 20:25:10.285619+00	2022-08-02 20:25:10.285648+00	1	\N	\N	f	f
1661	PROJECT	Project	Anonymous Customer HQ	157121	2022-08-02 20:25:10.285708+00	2022-08-02 20:25:10.285736+00	1	\N	\N	f	f
1662	PROJECT	Project	St. Francis Yacht Club	157122	2022-08-02 20:25:10.285794+00	2022-08-02 20:25:10.285822+00	1	\N	\N	f	f
1663	PROJECT	Project	Sage Project 2	157123	2022-08-02 20:25:10.285879+00	2022-08-02 20:25:10.285906+00	1	\N	\N	f	f
1664	PROJECT	Project	Fyle Team Integrations	157124	2022-08-02 20:25:10.285965+00	2022-08-02 20:25:10.285992+00	1	\N	\N	f	f
1665	PROJECT	Project	Sage Project 4	157125	2022-08-02 20:25:10.286049+00	2022-08-02 20:25:10.286077+00	1	\N	\N	f	f
1666	PROJECT	Project	Sage Project 6	157126	2022-08-02 20:25:10.286134+00	2022-08-02 20:25:10.286162+00	1	\N	\N	f	f
1667	PROJECT	Project	Fyle Main Project	157127	2022-08-02 20:25:10.286219+00	2022-08-02 20:25:10.286257+00	1	\N	\N	f	f
1668	PROJECT	Project	Sage project fyle	157128	2022-08-02 20:25:10.286439+00	2022-08-02 20:25:10.286467+00	1	\N	\N	f	f
1669	PROJECT	Project	Fyle Engineering	157129	2022-08-02 20:25:10.286525+00	2022-08-02 20:25:10.286552+00	1	\N	\N	f	f
1670	PROJECT	Project	Customer Mapped Project	157130	2022-08-02 20:25:10.286609+00	2022-08-02 20:25:10.286636+00	1	\N	\N	f	f
1671	PROJECT	Project	Sage Project 10	157131	2022-08-02 20:25:10.286693+00	2022-08-02 20:25:10.28672+00	1	\N	\N	f	f
1672	PROJECT	Project	Sage Project 8	157132	2022-08-02 20:25:10.286777+00	2022-08-02 20:25:10.286805+00	1	\N	\N	f	f
1673	PROJECT	Project	Server Upgrade	157133	2022-08-02 20:25:10.286861+00	2022-08-02 20:25:10.286888+00	1	\N	\N	f	f
1674	PROJECT	Project	Equipment Upgrade	157134	2022-08-02 20:25:10.286945+00	2022-08-02 20:25:10.286973+00	1	\N	\N	f	f
1675	PROJECT	Project	Internal Audit	157135	2022-08-02 20:25:10.28703+00	2022-08-02 20:25:10.287057+00	1	\N	\N	f	f
1676	PROJECT	Project	Training	157136	2022-08-02 20:25:10.287114+00	2022-08-02 20:25:10.287141+00	1	\N	\N	f	f
1677	PROJECT	Project	User Conference	157137	2022-08-02 20:25:10.287356+00	2022-08-02 20:25:10.287768+00	1	\N	\N	f	f
1678	PROJECT	Project	Sage Project 5	157138	2022-08-02 20:25:10.287872+00	2022-08-02 20:25:10.28798+00	1	\N	\N	f	f
1679	PROJECT	Project	Sage Project 3	157139	2022-08-02 20:25:10.288048+00	2022-08-02 20:25:10.288159+00	1	\N	\N	f	f
1680	PROJECT	Project	Sage Project 1	157140	2022-08-02 20:25:10.28823+00	2022-08-02 20:25:10.288257+00	1	\N	\N	f	f
1681	PROJECT	Project	Sage Project 9	157141	2022-08-02 20:25:10.288314+00	2022-08-02 20:25:10.288342+00	1	\N	\N	f	f
1682	PROJECT	Project	Sage Project 7	157142	2022-08-02 20:25:10.288398+00	2022-08-02 20:25:10.288426+00	1	\N	\N	f	f
1683	PROJECT	Project	Amy's Bird Sanctuary	159604	2022-08-02 20:25:10.288482+00	2022-08-02 20:25:10.28851+00	1	\N	\N	f	f
1684	PROJECT	Project	Amy's Bird Sanctuary:Test Project	159605	2022-08-02 20:25:10.288567+00	2022-08-02 20:25:10.288594+00	1	\N	\N	f	f
1685	PROJECT	Project	Bill's Windsurf Shop	159606	2022-08-02 20:25:10.288651+00	2022-08-02 20:25:10.288679+00	1	\N	\N	f	f
1686	PROJECT	Project	Cool Cars	159607	2022-08-02 20:25:10.288735+00	2022-08-02 20:25:10.288763+00	1	\N	\N	f	f
1687	PROJECT	Project	Diego Rodriguez	159608	2022-08-02 20:25:10.288819+00	2022-08-02 20:25:10.288846+00	1	\N	\N	f	f
1688	PROJECT	Project	Diego Rodriguez:Test Project	159609	2022-08-02 20:25:10.288903+00	2022-08-02 20:25:10.28893+00	1	\N	\N	f	f
1689	PROJECT	Project	Dukes Basketball Camp	159610	2022-08-02 20:25:10.288987+00	2022-08-02 20:25:10.289014+00	1	\N	\N	f	f
1690	PROJECT	Project	Dylan Sollfrank	159611	2022-08-02 20:25:10.28907+00	2022-08-02 20:25:10.289097+00	1	\N	\N	f	f
1691	PROJECT	Project	Freeman Sporting Goods	159612	2022-08-02 20:25:10.289154+00	2022-08-02 20:25:10.289181+00	1	\N	\N	f	f
1692	PROJECT	Project	Freeman Sporting Goods:0969 Ocean View Road	159613	2022-08-02 20:25:10.289237+00	2022-08-02 20:25:10.289265+00	1	\N	\N	f	f
1693	PROJECT	Project	Freeman Sporting Goods:55 Twin Lane	159614	2022-08-02 20:25:10.289621+00	2022-08-02 20:25:10.289654+00	1	\N	\N	f	f
1694	PROJECT	Project	Geeta Kalapatapu	159615	2022-08-02 20:25:10.289713+00	2022-08-02 20:25:10.289741+00	1	\N	\N	f	f
1695	PROJECT	Project	Gevelber Photography	159616	2022-08-02 20:25:10.289799+00	2022-08-02 20:25:10.289826+00	1	\N	\N	f	f
1696	PROJECT	Project	Jeff's Jalopies	159617	2022-08-02 20:25:10.289995+00	2022-08-02 20:25:10.290033+00	1	\N	\N	f	f
1697	PROJECT	Project	John Melton	159618	2022-08-02 20:25:10.290105+00	2022-08-02 20:25:10.290134+00	1	\N	\N	f	f
1698	PROJECT	Project	Kate Whelan	159619	2022-08-02 20:25:10.290305+00	2022-08-02 20:25:10.290337+00	1	\N	\N	f	f
1699	PROJECT	Project	Kookies by Kathy	159620	2022-08-02 20:25:10.2904+00	2022-08-02 20:25:10.29043+00	1	\N	\N	f	f
1700	PROJECT	Project	Mark Cho	159621	2022-08-02 20:25:10.290492+00	2022-08-02 20:25:10.290521+00	1	\N	\N	f	f
1701	PROJECT	Project	Paulsen Medical Supplies	159622	2022-08-02 20:25:10.290585+00	2022-08-02 20:25:10.290614+00	1	\N	\N	f	f
1702	PROJECT	Project	Pye's Cakes	159623	2022-08-02 20:25:10.290675+00	2022-08-02 20:25:10.290704+00	1	\N	\N	f	f
1703	PROJECT	Project	Rago Travel Agency	159624	2022-08-02 20:25:10.290765+00	2022-08-02 20:25:10.291579+00	1	\N	\N	f	f
1704	PROJECT	Project	Red Rock Diner	159625	2022-08-02 20:25:10.291671+00	2022-08-02 20:25:10.291699+00	1	\N	\N	f	f
1705	PROJECT	Project	Rondonuwu Fruit and Vegi	159626	2022-08-02 20:25:10.291757+00	2022-08-02 20:25:10.291784+00	1	\N	\N	f	f
1706	PROJECT	Project	Shara Barnett	159627	2022-08-02 20:25:10.291841+00	2022-08-02 20:25:10.291868+00	1	\N	\N	f	f
1707	PROJECT	Project	Shara Barnett:Barnett Design	159628	2022-08-02 20:25:10.291925+00	2022-08-02 20:25:10.291952+00	1	\N	\N	f	f
1708	PROJECT	Project	Sheldon Cooper	159629	2022-08-02 20:25:10.292008+00	2022-08-02 20:25:10.292035+00	1	\N	\N	f	f
1709	PROJECT	Project	Sheldon Cooper:Incremental Project	159630	2022-08-02 20:25:10.489395+00	2022-08-02 20:25:10.48947+00	1	\N	\N	f	f
1710	PROJECT	Project	Sonnenschein Family Store	159631	2022-08-02 20:25:10.489616+00	2022-08-02 20:25:10.489669+00	1	\N	\N	f	f
1711	PROJECT	Project	Sushi by Katsuyuki	159632	2022-08-02 20:25:10.490451+00	2022-08-02 20:25:10.490541+00	1	\N	\N	f	f
1712	PROJECT	Project	Travis Waldron	159633	2022-08-02 20:25:10.491856+00	2022-08-02 20:25:10.49192+00	1	\N	\N	f	f
1713	PROJECT	Project	Video Games by Dan	159634	2022-08-02 20:25:10.49206+00	2022-08-02 20:25:10.492106+00	1	\N	\N	f	f
1714	PROJECT	Project	Wedding Planning by Whitney	159635	2022-08-02 20:25:10.492222+00	2022-08-02 20:25:10.492265+00	1	\N	\N	f	f
1715	PROJECT	Project	Weiskopf Consulting	159636	2022-08-02 20:25:10.492396+00	2022-08-02 20:25:10.492439+00	1	\N	\N	f	f
1716	PROJECT	Project	Sravan Prod Test Pr@d	159638	2022-08-02 20:25:10.493493+00	2022-08-02 20:25:10.497527+00	1	\N	\N	f	f
1717	PROJECT	Project	Project Red	251294	2022-08-02 20:25:10.497661+00	2022-08-02 20:25:10.497692+00	1	\N	\N	f	f
1718	PROJECT	Project	Sravan Prod Test Prod	254078	2022-08-02 20:25:10.49778+00	2022-08-02 20:25:10.497812+00	1	\N	\N	f	f
1719	PROJECT	Project	Sample Test	278300	2022-08-02 20:25:10.497883+00	2022-08-02 20:25:10.497914+00	1	\N	\N	f	f
1720	PROJECT	Project	Fixed Fee Project with Five Tasks	284386	2022-08-02 20:25:10.497981+00	2022-08-02 20:25:10.498016+00	1	\N	\N	f	f
1721	PROJECT	Project	Fyle NetSuite Integration	284387	2022-08-02 20:25:10.498861+00	2022-08-02 20:25:10.500052+00	1	\N	\N	f	f
1722	PROJECT	Project	Fyle Sage Intacct Integration	284388	2022-08-02 20:25:10.510622+00	2022-08-02 20:25:10.51071+00	1	\N	\N	f	f
1723	PROJECT	Project	General Overhead	284389	2022-08-02 20:25:10.510986+00	2022-08-02 20:25:10.51105+00	1	\N	\N	f	f
1724	PROJECT	Project	General Overhead-Current	284390	2022-08-02 20:25:10.511337+00	2022-08-02 20:25:10.511516+00	1	\N	\N	f	f
1725	PROJECT	Project	Integrations	284391	2022-08-02 20:25:10.51162+00	2022-08-02 20:25:10.511779+00	1	\N	\N	f	f
1726	PROJECT	Project	Mobile App Redesign	284392	2022-08-02 20:25:10.511854+00	2022-08-02 20:25:10.512181+00	1	\N	\N	f	f
1727	PROJECT	Project	Platform APIs	284393	2022-08-02 20:25:10.512323+00	2022-08-02 20:25:10.512381+00	1	\N	\N	f	f
1728	PROJECT	Project	Support Taxes	284394	2022-08-02 20:25:10.512766+00	2022-08-02 20:25:10.512907+00	1	\N	\N	f	f
1729	PROJECT	Project	T&M Project with Five Tasks	284395	2022-08-02 20:25:10.512991+00	2022-08-02 20:25:10.513023+00	1	\N	\N	f	f
1730	PROJECT	Project	Branding Analysis	284396	2022-08-02 20:25:10.513113+00	2022-08-02 20:25:10.513144+00	1	\N	\N	f	f
1731	PROJECT	Project	Branding Follow Up	284397	2022-08-02 20:25:10.513259+00	2022-08-02 20:25:10.513354+00	1	\N	\N	f	f
1732	PROJECT	Project	Direct Mail Campaign	284398	2022-08-02 20:25:10.513481+00	2022-08-02 20:25:10.51356+00	1	\N	\N	f	f
1733	PROJECT	Project	Ecommerce Campaign	284399	2022-08-02 20:25:10.513637+00	2022-08-02 20:25:10.513671+00	1	\N	\N	f	f
1734	PROJECT	Project	Alex Blakey	284572	2022-08-02 20:25:10.513864+00	2022-08-02 20:25:10.513917+00	1	\N	\N	f	f
1735	PROJECT	Project	Cathy Quon	284573	2022-08-02 20:25:10.514019+00	2022-08-02 20:25:10.514061+00	1	\N	\N	f	f
1736	PROJECT	Project	Charlie Whitehead	284574	2022-08-02 20:25:10.514182+00	2022-08-02 20:25:10.514373+00	1	\N	\N	f	f
1737	PROJECT	Project	Cheng-Cheng Lok	284575	2022-08-02 20:25:10.514432+00	2022-08-02 20:25:10.514461+00	1	\N	\N	f	f
1738	PROJECT	Project	Gorman Ho	284576	2022-08-02 20:25:10.514516+00	2022-08-02 20:25:10.514537+00	1	\N	\N	f	f
1739	PROJECT	Project	Kristy Abercrombie	284577	2022-08-02 20:25:10.514597+00	2022-08-02 20:25:10.514627+00	1	\N	\N	f	f
1740	PROJECT	Project	Moturu Tapasvi	284578	2022-08-02 20:25:10.51469+00	2022-08-02 20:25:10.514727+00	1	\N	\N	f	f
1741	PROJECT	Project	Oxon Insurance Agency:Oxon - Retreat	284579	2022-08-02 20:25:10.514828+00	2022-08-02 20:25:10.514872+00	1	\N	\N	f	f
1742	PROJECT	Project	Oxon Insurance Agency:Oxon -- Holiday Party	284580	2022-08-02 20:25:10.515043+00	2022-08-02 20:25:10.515066+00	1	\N	\N	f	f
1743	PROJECT	Project	A Project	287122	2022-08-02 20:25:10.515119+00	2022-08-02 20:25:10.515148+00	1	\N	\N	f	f
1744	PROJECT	Project	New Project	287123	2022-08-02 20:25:10.51529+00	2022-08-02 20:25:10.515321+00	1	\N	\N	f	f
1745	PROJECT	Project	Vendor KSKS	292179	2022-08-02 20:25:10.515433+00	2022-08-02 20:25:10.515453+00	1	\N	\N	f	f
1746	PROJECT	Project	Bangalore	292292	2022-08-02 20:25:10.515504+00	2022-08-02 20:25:10.515525+00	1	\N	\N	f	f
1747	PROJECT	Project	San Fransisco	292529	2022-08-02 20:25:10.515586+00	2022-08-02 20:25:10.515625+00	1	\N	\N	f	f
1748	PROJECT	Project	USA Project	292601	2022-08-02 20:25:10.515699+00	2022-08-02 20:25:10.51571+00	1	\N	\N	f	f
1749	PROJECT	Project	QBO	295378	2022-08-02 20:25:10.515869+00	2022-08-02 20:25:10.515996+00	1	\N	\N	f	f
1750	COST_CENTER	Cost Center	Amy's Bird Sanctuary	12490	2022-08-02 20:25:10.73794+00	2022-08-02 20:25:10.737992+00	1	\N	\N	f	f
1751	COST_CENTER	Cost Center	Amy's Bird Sanctuary:Test Project	12491	2022-08-02 20:25:10.738075+00	2022-08-02 20:25:10.73812+00	1	\N	\N	f	f
1752	COST_CENTER	Cost Center	Ashwinn	12492	2022-08-02 20:25:10.738418+00	2022-08-02 20:25:10.738466+00	1	\N	\N	f	f
1753	COST_CENTER	Cost Center	Bill's Windsurf Shop	12493	2022-08-02 20:25:10.738538+00	2022-08-02 20:25:10.738568+00	1	\N	\N	f	f
1754	COST_CENTER	Cost Center	Cool Cars	12494	2022-08-02 20:25:10.738632+00	2022-08-02 20:25:10.738662+00	1	\N	\N	f	f
1755	COST_CENTER	Cost Center	Diego Rodriguez	12495	2022-08-02 20:25:10.738725+00	2022-08-02 20:25:10.738754+00	1	\N	\N	f	f
1756	COST_CENTER	Cost Center	Diego Rodriguez:Test Project	12496	2022-08-02 20:25:10.738816+00	2022-08-02 20:25:10.738844+00	1	\N	\N	f	f
1757	COST_CENTER	Cost Center	Dukes Basketball Camp	12497	2022-08-02 20:25:10.738906+00	2022-08-02 20:25:10.738935+00	1	\N	\N	f	f
1758	COST_CENTER	Cost Center	Dylan Sollfrank	12498	2022-08-02 20:25:10.738997+00	2022-08-02 20:25:10.739026+00	1	\N	\N	f	f
1759	COST_CENTER	Cost Center	Freeman Sporting Goods	12499	2022-08-02 20:25:10.739087+00	2022-08-02 20:25:10.739115+00	1	\N	\N	f	f
1760	COST_CENTER	Cost Center	Freeman Sporting Goods:0969 Ocean View Road	12500	2022-08-02 20:25:10.739177+00	2022-08-02 20:25:10.739206+00	1	\N	\N	f	f
1761	COST_CENTER	Cost Center	Freeman Sporting Goods:55 Twin Lane	12501	2022-08-02 20:25:10.739356+00	2022-08-02 20:25:10.739386+00	1	\N	\N	f	f
1762	COST_CENTER	Cost Center	Geeta Kalapatapu	12502	2022-08-02 20:25:10.739448+00	2022-08-02 20:25:10.739486+00	1	\N	\N	f	f
1763	COST_CENTER	Cost Center	Gevelber Photography	12503	2022-08-02 20:25:10.739545+00	2022-08-02 20:25:10.739572+00	1	\N	\N	f	f
1764	COST_CENTER	Cost Center	Jeff's Jalopies	12504	2022-08-02 20:25:10.739629+00	2022-08-02 20:25:10.739657+00	1	\N	\N	f	f
1765	COST_CENTER	Cost Center	John Melton	12505	2022-08-02 20:25:10.739714+00	2022-08-02 20:25:10.739741+00	1	\N	\N	f	f
1766	COST_CENTER	Cost Center	Kate Whelan	12506	2022-08-02 20:25:10.739799+00	2022-08-02 20:25:10.739826+00	1	\N	\N	f	f
1767	COST_CENTER	Cost Center	Kookies by Kathy	12507	2022-08-02 20:25:10.739883+00	2022-08-02 20:25:10.739911+00	1	\N	\N	f	f
1768	COST_CENTER	Cost Center	Mark Cho	12508	2022-08-02 20:25:10.739968+00	2022-08-02 20:25:10.739995+00	1	\N	\N	f	f
1769	COST_CENTER	Cost Center	naruto uzumaki	12509	2022-08-02 20:25:10.740053+00	2022-08-02 20:25:10.74008+00	1	\N	\N	f	f
1770	COST_CENTER	Cost Center	octane squad	12510	2022-08-02 20:25:10.740137+00	2022-08-02 20:25:10.740164+00	1	\N	\N	f	f
1771	COST_CENTER	Cost Center	Paulsen Medical Supplies	12511	2022-08-02 20:25:10.740232+00	2022-08-02 20:25:10.740348+00	1	\N	\N	f	f
1772	COST_CENTER	Cost Center	Pye's Cakes	12512	2022-08-02 20:25:10.740411+00	2022-08-02 20:25:10.74045+00	1	\N	\N	f	f
1773	COST_CENTER	Cost Center	Rago Travel Agency	12513	2022-08-02 20:25:10.740512+00	2022-08-02 20:25:10.74054+00	1	\N	\N	f	f
1774	COST_CENTER	Cost Center	Red Rock Diner	12514	2022-08-02 20:25:10.740602+00	2022-08-02 20:25:10.740631+00	1	\N	\N	f	f
1775	COST_CENTER	Cost Center	Rondonuwu Fruit and Vegi	12515	2022-08-02 20:25:10.740694+00	2022-08-02 20:25:10.740722+00	1	\N	\N	f	f
1776	COST_CENTER	Cost Center	Shara Barnett	12516	2022-08-02 20:25:10.740785+00	2022-08-02 20:25:10.740814+00	1	\N	\N	f	f
1777	COST_CENTER	Cost Center	Shara Barnett:Barnett Design	12517	2022-08-02 20:25:10.740875+00	2022-08-02 20:25:10.740904+00	1	\N	\N	f	f
1778	COST_CENTER	Cost Center	Sheldon Cooper	12518	2022-08-02 20:25:10.740965+00	2022-08-02 20:25:10.740994+00	1	\N	\N	f	f
1779	COST_CENTER	Cost Center	Sheldon Cooper:Incremental Project	12519	2022-08-02 20:25:10.741058+00	2022-08-02 20:25:10.741087+00	1	\N	\N	f	f
1780	COST_CENTER	Cost Center	Sonnenschein Family Store	12520	2022-08-02 20:25:10.741149+00	2022-08-02 20:25:10.741178+00	1	\N	\N	f	f
1781	COST_CENTER	Cost Center	Sravan BLR Customer	12521	2022-08-02 20:25:10.741377+00	2022-08-02 20:25:10.741422+00	1	\N	\N	f	f
1782	COST_CENTER	Cost Center	Sushi by Katsuyuki	12522	2022-08-02 20:25:10.741494+00	2022-08-02 20:25:10.741525+00	1	\N	\N	f	f
1783	COST_CENTER	Cost Center	Travis Waldron	12523	2022-08-02 20:25:10.741871+00	2022-08-02 20:25:10.742+00	1	\N	\N	f	f
1784	COST_CENTER	Cost Center	Video Games by Dan	12524	2022-08-02 20:25:10.742572+00	2022-08-02 20:25:10.742774+00	1	\N	\N	f	f
1785	COST_CENTER	Cost Center	Wedding Planning by Whitney	12525	2022-08-02 20:25:10.743303+00	2022-08-02 20:25:10.743342+00	1	\N	\N	f	f
1786	COST_CENTER	Cost Center	Weiskopf Consulting	12526	2022-08-02 20:25:10.743418+00	2022-08-02 20:25:10.743456+00	1	\N	\N	f	f
1787	COST_CENTER	Cost Center	wraith squad	12527	2022-08-02 20:25:10.743519+00	2022-08-02 20:25:10.743547+00	1	\N	\N	f	f
1788	COST_CENTER	Cost Center	Bebe Rexha	11533	2022-08-02 20:25:10.743606+00	2022-08-02 20:25:10.743634+00	1	\N	\N	f	f
1789	COST_CENTER	Cost Center	Chase Ortega	11534	2022-08-02 20:25:10.743693+00	2022-08-02 20:25:10.743734+00	1	\N	\N	f	f
1790	COST_CENTER	Cost Center	Customer Acquisition	11535	2022-08-02 20:25:10.74387+00	2022-08-02 20:25:10.743899+00	1	\N	\N	f	f
1791	COST_CENTER	Cost Center	David Olshanetsky	11536	2022-08-02 20:25:10.743959+00	2022-08-02 20:25:10.743986+00	1	\N	\N	f	f
1792	COST_CENTER	Cost Center	Invisible men (George Astasio, Jason Pebworth, Jon Shave)	11537	2022-08-02 20:25:10.744045+00	2022-08-02 20:25:10.744072+00	1	\N	\N	f	f
1793	COST_CENTER	Cost Center	Leomie Anderson	11538	2022-08-02 20:25:10.74413+00	2022-08-02 20:25:10.744157+00	1	\N	\N	f	f
1794	COST_CENTER	Cost Center	Lil Peep Documentary	11539	2022-08-02 20:25:10.744214+00	2022-08-02 20:25:10.744241+00	1	\N	\N	f	f
1795	COST_CENTER	Cost Center	Naations	11540	2022-08-02 20:25:10.744447+00	2022-08-02 20:25:10.744475+00	1	\N	\N	f	f
1796	COST_CENTER	Cost Center	QBO	11541	2022-08-02 20:25:10.744532+00	2022-08-02 20:25:10.744613+00	1	\N	\N	f	f
1797	COST_CENTER	Cost Center	Rita Ora	11542	2022-08-02 20:25:10.744676+00	2022-08-02 20:25:10.744798+00	1	\N	\N	f	f
1798	COST_CENTER	Cost Center	p1	11543	2022-08-02 20:25:10.744992+00	2022-08-02 20:25:10.745028+00	1	\N	\N	f	f
1799	COST_CENTER	Cost Center	p2	11544	2022-08-02 20:25:10.745119+00	2022-08-02 20:25:10.745285+00	1	\N	\N	f	f
1800	COST_CENTER	Cost Center	suhas_p1	11545	2022-08-02 20:25:10.752479+00	2022-08-02 20:25:10.752521+00	1	\N	\N	f	f
1801	COST_CENTER	Cost Center	75757	10847	2022-08-02 20:25:10.752632+00	2022-08-02 20:25:10.752666+00	1	\N	\N	f	f
1802	COST_CENTER	Cost Center	1200191	9556	2022-08-02 20:25:10.752731+00	2022-08-02 20:25:10.75276+00	1	\N	\N	f	f
1803	COST_CENTER	Cost Center	7676	9557	2022-08-02 20:25:10.752823+00	2022-08-02 20:25:10.752852+00	1	\N	\N	f	f
1804	COST_CENTER	Cost Center	PF PF	9558	2022-08-02 20:25:10.752914+00	2022-08-02 20:25:10.752943+00	1	\N	\N	f	f
1805	COST_CENTER	Cost Center	BOOK	9540	2022-08-02 20:25:10.753005+00	2022-08-02 20:25:10.753224+00	1	\N	\N	f	f
1806	COST_CENTER	Cost Center	DevD	9541	2022-08-02 20:25:10.75334+00	2022-08-02 20:25:10.753368+00	1	\N	\N	f	f
1807	COST_CENTER	Cost Center	DevH	9542	2022-08-02 20:25:10.753426+00	2022-08-02 20:25:10.753454+00	1	\N	\N	f	f
1808	COST_CENTER	Cost Center	GB1-White	9543	2022-08-02 20:25:10.753511+00	2022-08-02 20:25:10.753538+00	1	\N	\N	f	f
1809	COST_CENTER	Cost Center	GB3-White	9544	2022-08-02 20:25:10.753596+00	2022-08-02 20:25:10.753623+00	1	\N	\N	f	f
1810	COST_CENTER	Cost Center	GB6-White	9545	2022-08-02 20:25:10.75368+00	2022-08-02 20:25:10.753707+00	1	\N	\N	f	f
1811	COST_CENTER	Cost Center	GB9-White	9546	2022-08-02 20:25:10.753764+00	2022-08-02 20:25:10.753791+00	1	\N	\N	f	f
1812	COST_CENTER	Cost Center	PMBr	9547	2022-08-02 20:25:10.753848+00	2022-08-02 20:25:10.753875+00	1	\N	\N	f	f
1813	COST_CENTER	Cost Center	PMD	9548	2022-08-02 20:25:10.753932+00	2022-08-02 20:25:10.753959+00	1	\N	\N	f	f
1814	COST_CENTER	Cost Center	PMDD	9549	2022-08-02 20:25:10.754015+00	2022-08-02 20:25:10.754043+00	1	\N	\N	f	f
1815	COST_CENTER	Cost Center	PMWe	9550	2022-08-02 20:25:10.754099+00	2022-08-02 20:25:10.754126+00	1	\N	\N	f	f
1816	COST_CENTER	Cost Center	Support-M	9551	2022-08-02 20:25:10.754183+00	2022-08-02 20:25:10.75421+00	1	\N	\N	f	f
1817	COST_CENTER	Cost Center	TSL - Black	9552	2022-08-02 20:25:10.754282+00	2022-08-02 20:25:10.75442+00	1	\N	\N	f	f
1818	COST_CENTER	Cost Center	TSM - Black	9553	2022-08-02 20:25:10.754474+00	2022-08-02 20:25:10.754496+00	1	\N	\N	f	f
1819	COST_CENTER	Cost Center	TSS - Black	9554	2022-08-02 20:25:10.754564+00	2022-08-02 20:25:10.754592+00	1	\N	\N	f	f
1820	COST_CENTER	Cost Center	Train-MS	9555	2022-08-02 20:25:10.754649+00	2022-08-02 20:25:10.754677+00	1	\N	\N	f	f
1821	COST_CENTER	Cost Center	POSTMANNN 	9535	2022-08-02 20:25:10.754733+00	2022-08-02 20:25:10.754761+00	1	\N	\N	f	f
1822	COST_CENTER	Cost Center	POSTMAN	9534	2022-08-02 20:25:10.754817+00	2022-08-02 20:25:10.754845+00	1	\N	\N	f	f
1823	COST_CENTER	Cost Center	Employees	9529	2022-08-02 20:25:10.754902+00	2022-08-02 20:25:10.754929+00	1	\N	\N	f	f
1824	COST_CENTER	Cost Center	Parties	9530	2022-08-02 20:25:10.754986+00	2022-08-02 20:25:10.755013+00	1	\N	\N	f	f
1825	COST_CENTER	Cost Center	Promotional Items	9531	2022-08-02 20:25:10.75507+00	2022-08-02 20:25:10.755098+00	1	\N	\N	f	f
1826	COST_CENTER	Cost Center	Retreats	9532	2022-08-02 20:25:10.755155+00	2022-08-02 20:25:10.755182+00	1	\N	\N	f	f
1827	COST_CENTER	Cost Center	Test	64	2022-08-02 20:25:10.755389+00	2022-08-02 20:25:10.755431+00	1	\N	\N	f	f
1828	COST_CENTER	Cost Center	suhas_cc1	2412	2022-08-02 20:25:10.755639+00	2022-08-02 20:25:10.755667+00	1	\N	\N	f	f
1829	COST_CENTER	Cost Center	Radio	96	2022-08-02 20:25:10.755724+00	2022-08-02 20:25:10.755752+00	1	\N	\N	f	f
1830	COST_CENTER	Cost Center	Coachella	95	2022-08-02 20:25:10.755808+00	2022-08-02 20:25:10.755836+00	1	\N	\N	f	f
1831	COST_CENTER	Cost Center	cc1	2415	2022-08-02 20:25:10.755892+00	2022-08-02 20:25:10.755919+00	1	\N	\N	f	f
1832	COST_CENTER	Cost Center	cc2	2416	2022-08-02 20:25:10.755976+00	2022-08-02 20:25:10.756003+00	1	\N	\N	f	f
1833	COST_CENTER	Cost Center	Adidas	94	2022-08-02 20:25:10.75606+00	2022-08-02 20:25:10.756088+00	1	\N	\N	f	f
1834	KILLUA	Killua	Hardware	expense_custom_field.killua.1	2022-08-02 20:25:10.95082+00	2022-08-02 20:25:10.950863+00	1	\N	{"placeholder": "Select Killua", "custom_field_id": 197382}	f	f
1835	KILLUA	Killua	Furniture	expense_custom_field.killua.2	2022-08-02 20:25:10.95094+00	2022-08-02 20:25:10.950969+00	1	\N	{"placeholder": "Select Killua", "custom_field_id": 197382}	f	f
1836	KILLUA	Killua	Office	expense_custom_field.killua.3	2022-08-02 20:25:10.951039+00	2022-08-02 20:25:10.951067+00	1	\N	{"placeholder": "Select Killua", "custom_field_id": 197382}	f	f
1837	KILLUA	Killua	Servers	expense_custom_field.killua.4	2022-08-02 20:25:10.951135+00	2022-08-02 20:25:10.951163+00	1	\N	{"placeholder": "Select Killua", "custom_field_id": 197382}	f	f
1838	KILLUA	Killua	Home	expense_custom_field.killua.5	2022-08-02 20:25:10.951347+00	2022-08-02 20:25:10.951378+00	1	\N	{"placeholder": "Select Killua", "custom_field_id": 197382}	f	f
1839	KILLUA	Killua	Other	expense_custom_field.killua.6	2022-08-02 20:25:10.95158+00	2022-08-02 20:25:10.951618+00	1	\N	{"placeholder": "Select Killua", "custom_field_id": 197382}	f	f
1840	KILLUA	Killua	Racks	expense_custom_field.killua.7	2022-08-02 20:25:10.952291+00	2022-08-02 20:25:10.95232+00	1	\N	{"placeholder": "Select Killua", "custom_field_id": 197382}	f	f
1841	KILLUA	Killua	Wood	expense_custom_field.killua.8	2022-08-02 20:25:10.952388+00	2022-08-02 20:25:10.952415+00	1	\N	{"placeholder": "Select Killua", "custom_field_id": 197382}	f	f
1842	KILLUA	Killua	Non Wood	expense_custom_field.killua.9	2022-08-02 20:25:10.952482+00	2022-08-02 20:25:10.952509+00	1	\N	{"placeholder": "Select Killua", "custom_field_id": 197382}	f	f
1843	KILLUA	Killua	Accessories	expense_custom_field.killua.10	2022-08-02 20:25:10.952575+00	2022-08-02 20:25:10.952602+00	1	\N	{"placeholder": "Select Killua", "custom_field_id": 197382}	f	f
1844	KILLUA	Killua	Miscellaneous	expense_custom_field.killua.11	2022-08-02 20:25:10.952669+00	2022-08-02 20:25:10.952696+00	1	\N	{"placeholder": "Select Killua", "custom_field_id": 197382}	f	f
1845	KILLUA	Killua	Merchandise	expense_custom_field.killua.12	2022-08-02 20:25:10.952762+00	2022-08-02 20:25:10.95279+00	1	\N	{"placeholder": "Select Killua", "custom_field_id": 197382}	f	f
1846	KILLUA	Killua	Consumer Goods	expense_custom_field.killua.13	2022-08-02 20:25:10.952855+00	2022-08-02 20:25:10.952882+00	1	\N	{"placeholder": "Select Killua", "custom_field_id": 197382}	f	f
1847	KILLUA	Killua	Services	expense_custom_field.killua.14	2022-08-02 20:25:10.952948+00	2022-08-02 20:25:10.952975+00	1	\N	{"placeholder": "Select Killua", "custom_field_id": 197382}	f	f
1848	KILLUA	Killua	Internal	expense_custom_field.killua.15	2022-08-02 20:25:10.953041+00	2022-08-02 20:25:10.953068+00	1	\N	{"placeholder": "Select Killua", "custom_field_id": 197382}	f	f
1849	KILLUA	Killua	R&D	expense_custom_field.killua.16	2022-08-02 20:25:10.953134+00	2022-08-02 20:25:10.953161+00	1	\N	{"placeholder": "Select Killua", "custom_field_id": 197382}	f	f
1850	KILLUA	Killua	Materials	expense_custom_field.killua.17	2022-08-02 20:25:10.953239+00	2022-08-02 20:25:10.95336+00	1	\N	{"placeholder": "Select Killua", "custom_field_id": 197382}	f	f
1851	KILLUA	Killua	Manufacturing	expense_custom_field.killua.18	2022-08-02 20:25:10.953438+00	2022-08-02 20:25:10.953468+00	1	\N	{"placeholder": "Select Killua", "custom_field_id": 197382}	f	f
1852	NEW_FIELD	New Field	PMD	expense_custom_field.new field.1	2022-08-02 20:25:10.970978+00	2022-08-02 20:25:10.971015+00	1	\N	{"placeholder": "Select New Field", "custom_field_id": 197383}	f	f
1853	NEW_FIELD	New Field	GB6-White	expense_custom_field.new field.2	2022-08-02 20:25:10.971097+00	2022-08-02 20:25:10.971126+00	1	\N	{"placeholder": "Select New Field", "custom_field_id": 197383}	f	f
1854	NEW_FIELD	New Field	Support-M	expense_custom_field.new field.3	2022-08-02 20:25:10.971198+00	2022-08-02 20:25:10.971232+00	1	\N	{"placeholder": "Select New Field", "custom_field_id": 197383}	f	f
1855	NEW_FIELD	New Field	DevD	expense_custom_field.new field.4	2022-08-02 20:25:10.971399+00	2022-08-02 20:25:10.971438+00	1	\N	{"placeholder": "Select New Field", "custom_field_id": 197383}	f	f
1856	NEW_FIELD	New Field	TSS - Black	expense_custom_field.new field.5	2022-08-02 20:25:10.971507+00	2022-08-02 20:25:10.971535+00	1	\N	{"placeholder": "Select New Field", "custom_field_id": 197383}	f	f
1857	NEW_FIELD	New Field	PMBr	expense_custom_field.new field.6	2022-08-02 20:25:10.971602+00	2022-08-02 20:25:10.971629+00	1	\N	{"placeholder": "Select New Field", "custom_field_id": 197383}	f	f
1858	NEW_FIELD	New Field	Train-MS	expense_custom_field.new field.7	2022-08-02 20:25:10.971696+00	2022-08-02 20:25:10.971723+00	1	\N	{"placeholder": "Select New Field", "custom_field_id": 197383}	f	f
1859	NEW_FIELD	New Field	PMDD	expense_custom_field.new field.8	2022-08-02 20:25:10.971789+00	2022-08-02 20:25:10.971816+00	1	\N	{"placeholder": "Select New Field", "custom_field_id": 197383}	f	f
1860	NEW_FIELD	New Field	PMWe	expense_custom_field.new field.9	2022-08-02 20:25:10.971883+00	2022-08-02 20:25:10.97191+00	1	\N	{"placeholder": "Select New Field", "custom_field_id": 197383}	f	f
1861	NEW_FIELD	New Field	BOOK	expense_custom_field.new field.10	2022-08-02 20:25:10.971977+00	2022-08-02 20:25:10.972004+00	1	\N	{"placeholder": "Select New Field", "custom_field_id": 197383}	f	f
1862	NEW_FIELD	New Field	TSL - Black	expense_custom_field.new field.11	2022-08-02 20:25:10.97207+00	2022-08-02 20:25:10.972097+00	1	\N	{"placeholder": "Select New Field", "custom_field_id": 197383}	f	f
1863	NEW_FIELD	New Field	GB9-White	expense_custom_field.new field.12	2022-08-02 20:25:10.972163+00	2022-08-02 20:25:10.972191+00	1	\N	{"placeholder": "Select New Field", "custom_field_id": 197383}	f	f
1864	NEW_FIELD	New Field	TSM - Black	expense_custom_field.new field.13	2022-08-02 20:25:10.972339+00	2022-08-02 20:25:10.972365+00	1	\N	{"placeholder": "Select New Field", "custom_field_id": 197383}	f	f
1865	NEW_FIELD	New Field	DevH	expense_custom_field.new field.14	2022-08-02 20:25:10.972441+00	2022-08-02 20:25:10.972469+00	1	\N	{"placeholder": "Select New Field", "custom_field_id": 197383}	f	f
1866	NEW_FIELD	New Field	GB1-White	expense_custom_field.new field.15	2022-08-02 20:25:10.972535+00	2022-08-02 20:25:10.972562+00	1	\N	{"placeholder": "Select New Field", "custom_field_id": 197383}	f	f
1867	NEW_FIELD	New Field	GB3-White	expense_custom_field.new field.16	2022-08-02 20:25:10.972628+00	2022-08-02 20:25:10.972655+00	1	\N	{"placeholder": "Select New Field", "custom_field_id": 197383}	f	f
1868	TESTING_THIS	Testing This	Amy's Bird Sanctuary	expense_custom_field.testing this.1	2022-08-02 20:25:10.996333+00	2022-08-02 20:25:10.996383+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1869	TESTING_THIS	Testing This	Bill's Windsurf Shop	expense_custom_field.testing this.2	2022-08-02 20:25:10.996476+00	2022-08-02 20:25:10.996506+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1870	TESTING_THIS	Testing This	Cool Cars	expense_custom_field.testing this.3	2022-08-02 20:25:10.996576+00	2022-08-02 20:25:10.996604+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1871	TESTING_THIS	Testing This	Customer UD	expense_custom_field.testing this.4	2022-08-02 20:25:10.996671+00	2022-08-02 20:25:10.996698+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1872	TESTING_THIS	Testing This	Diego Rodriguez	expense_custom_field.testing this.5	2022-08-02 20:25:10.996764+00	2022-08-02 20:25:10.996791+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1873	TESTING_THIS	Testing This	Dukes Basketball Camp	expense_custom_field.testing this.6	2022-08-02 20:25:10.996857+00	2022-08-02 20:25:10.996884+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1874	TESTING_THIS	Testing This	Dylan Sollfrank	expense_custom_field.testing this.7	2022-08-02 20:25:10.99695+00	2022-08-02 20:25:10.996977+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1875	TESTING_THIS	Testing This	Freeman Sporting Goods	expense_custom_field.testing this.8	2022-08-02 20:25:10.997042+00	2022-08-02 20:25:10.99707+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1876	TESTING_THIS	Testing This	Freeman Sporting Goods:0969 Ocean View Road	expense_custom_field.testing this.9	2022-08-02 20:25:10.997135+00	2022-08-02 20:25:10.997163+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1877	TESTING_THIS	Testing This	Freeman Sporting Goods:0969 Ocean View Road:Test Project	expense_custom_field.testing this.10	2022-08-02 20:25:10.997243+00	2022-08-02 20:25:10.997404+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1878	TESTING_THIS	Testing This	Freeman Sporting Goods:55 Twin Lane	expense_custom_field.testing this.11	2022-08-02 20:25:10.997481+00	2022-08-02 20:25:10.997517+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1879	TESTING_THIS	Testing This	Geeta Kalapatapu	expense_custom_field.testing this.12	2022-08-02 20:25:10.997592+00	2022-08-02 20:25:10.997621+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1880	TESTING_THIS	Testing This	Gevelber Photography	expense_custom_field.testing this.13	2022-08-02 20:25:10.997693+00	2022-08-02 20:25:10.997722+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1881	TESTING_THIS	Testing This	Jeff's Jalopies	expense_custom_field.testing this.14	2022-08-02 20:25:10.997793+00	2022-08-02 20:25:10.997825+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1882	TESTING_THIS	Testing This	John Melton	expense_custom_field.testing this.15	2022-08-02 20:25:10.997896+00	2022-08-02 20:25:10.997925+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1883	TESTING_THIS	Testing This	Kate Whelan	expense_custom_field.testing this.16	2022-08-02 20:25:10.997996+00	2022-08-02 20:25:10.998025+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1884	TESTING_THIS	Testing This	Kookies by Kathy	expense_custom_field.testing this.17	2022-08-02 20:25:10.998096+00	2022-08-02 20:25:10.998125+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1885	TESTING_THIS	Testing This	Lol aavea Haithyas iPartnersa Inca.	expense_custom_field.testing this.18	2022-08-02 20:25:10.9982+00	2022-08-02 20:25:10.99823+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1886	TESTING_THIS	Testing This	Mark Cho	expense_custom_field.testing this.19	2022-08-02 20:25:10.9983+00	2022-08-02 20:25:10.998329+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1887	TESTING_THIS	Testing This	Paulsen Medical Supplies	expense_custom_field.testing this.20	2022-08-02 20:25:10.998398+00	2022-08-02 20:25:10.998427+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1888	TESTING_THIS	Testing This	Pye's Cakes	expense_custom_field.testing this.21	2022-08-02 20:25:10.998496+00	2022-08-02 20:25:10.998525+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1889	TESTING_THIS	Testing This	Rago Travel Agency	expense_custom_field.testing this.22	2022-08-02 20:25:10.998593+00	2022-08-02 20:25:10.998622+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1890	TESTING_THIS	Testing This	Red Rock Diner	expense_custom_field.testing this.23	2022-08-02 20:25:10.99869+00	2022-08-02 20:25:10.998719+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1891	TESTING_THIS	Testing This	Rondonuwu Fruit and Vegi	expense_custom_field.testing this.24	2022-08-02 20:25:10.998793+00	2022-08-02 20:25:10.998823+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1892	TESTING_THIS	Testing This	Shara Barnett	expense_custom_field.testing this.25	2022-08-02 20:25:10.998892+00	2022-08-02 20:25:10.998921+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1893	TESTING_THIS	Testing This	Shara Barnett:Barnett Design	expense_custom_field.testing this.26	2022-08-02 20:25:10.998991+00	2022-08-02 20:25:10.99902+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1894	TESTING_THIS	Testing This	Sonnenschein Family Store	expense_custom_field.testing this.27	2022-08-02 20:25:10.99909+00	2022-08-02 20:25:10.999119+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1895	TESTING_THIS	Testing This	Sushi by Katsuyuki	expense_custom_field.testing this.28	2022-08-02 20:25:10.999189+00	2022-08-02 20:25:10.999218+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1896	TESTING_THIS	Testing This	Travis Waldron	expense_custom_field.testing this.29	2022-08-02 20:25:10.999287+00	2022-08-02 20:25:10.999316+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1897	TESTING_THIS	Testing This	Video Games by Dan	expense_custom_field.testing this.30	2022-08-02 20:25:10.999385+00	2022-08-02 20:25:10.999414+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1898	TESTING_THIS	Testing This	Wedding Planning by Whitney	expense_custom_field.testing this.31	2022-08-02 20:25:10.999483+00	2022-08-02 20:25:10.999512+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1899	TESTING_THIS	Testing This	Weiskopf Consulting	expense_custom_field.testing this.32	2022-08-02 20:25:10.999581+00	2022-08-02 20:25:10.99961+00	1	\N	{"placeholder": "Select Testing This", "custom_field_id": 197391}	f	f
1900	CLASSES	Classes	FAE	expense_custom_field.classes.1	2022-08-02 20:25:11.01732+00	2022-08-02 20:25:11.017369+00	1	\N	{"placeholder": "Select Classes", "custom_field_id": 205002}	f	f
1901	CLASSES	Classes	FAE:Mini FAE	expense_custom_field.classes.2	2022-08-02 20:25:11.017613+00	2022-08-02 20:25:11.017661+00	1	\N	{"placeholder": "Select Classes", "custom_field_id": 205002}	f	f
1902	CLASSES	Classes	Fabrication	expense_custom_field.classes.3	2022-08-02 20:25:11.017762+00	2022-08-02 20:25:11.017803+00	1	\N	{"placeholder": "Select Classes", "custom_field_id": 205002}	f	f
1903	CLASSES	Classes	Adidas	expense_custom_field.classes.4	2022-08-02 20:25:11.01796+00	2022-08-02 20:25:11.018031+00	1	\N	{"placeholder": "Select Classes", "custom_field_id": 205002}	f	f
1904	NETSUITE_CLASS	Netsuite Class	Amy's Bird Sanctuary	expense_custom_field.netsuite class.1	2022-08-02 20:25:11.030757+00	2022-08-02 20:25:11.030801+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1905	NETSUITE_CLASS	Netsuite Class	Amy's Bird Sanctuary:Test Project	expense_custom_field.netsuite class.2	2022-08-02 20:25:11.030884+00	2022-08-02 20:25:11.030914+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1906	NETSUITE_CLASS	Netsuite Class	Ashwinn	expense_custom_field.netsuite class.3	2022-08-02 20:25:11.030988+00	2022-08-02 20:25:11.031019+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1907	NETSUITE_CLASS	Netsuite Class	Bill's Windsurf Shop	expense_custom_field.netsuite class.4	2022-08-02 20:25:11.03109+00	2022-08-02 20:25:11.03112+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1908	NETSUITE_CLASS	Netsuite Class	Cool Cars	expense_custom_field.netsuite class.5	2022-08-02 20:25:11.03119+00	2022-08-02 20:25:11.03122+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1909	NETSUITE_CLASS	Netsuite Class	Diego Rodriguez	expense_custom_field.netsuite class.6	2022-08-02 20:25:11.031387+00	2022-08-02 20:25:11.031416+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1910	NETSUITE_CLASS	Netsuite Class	Diego Rodriguez:Test Project	expense_custom_field.netsuite class.7	2022-08-02 20:25:11.031486+00	2022-08-02 20:25:11.031515+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1911	NETSUITE_CLASS	Netsuite Class	Dukes Basketball Camp	expense_custom_field.netsuite class.8	2022-08-02 20:25:11.031585+00	2022-08-02 20:25:11.031614+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1912	NETSUITE_CLASS	Netsuite Class	Dylan Sollfrank	expense_custom_field.netsuite class.9	2022-08-02 20:25:11.031682+00	2022-08-02 20:25:11.031712+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1913	NETSUITE_CLASS	Netsuite Class	Freeman Sporting Goods	expense_custom_field.netsuite class.10	2022-08-02 20:25:11.031788+00	2022-08-02 20:25:11.031816+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1914	NETSUITE_CLASS	Netsuite Class	Freeman Sporting Goods:0969 Ocean View Road	expense_custom_field.netsuite class.11	2022-08-02 20:25:11.031882+00	2022-08-02 20:25:11.031909+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1915	NETSUITE_CLASS	Netsuite Class	Freeman Sporting Goods:55 Twin Lane	expense_custom_field.netsuite class.12	2022-08-02 20:25:11.031974+00	2022-08-02 20:25:11.032001+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
2032	TAX_GROUP	Tax Group	GST-free non-capital @0%	tg3vVLWluRLP	2022-08-02 20:25:31.719937+00	2022-08-02 20:25:31.719961+00	1	\N	{"tax_rate": 0.0}	f	f
1916	NETSUITE_CLASS	Netsuite Class	Geeta Kalapatapu	expense_custom_field.netsuite class.13	2022-08-02 20:25:11.032065+00	2022-08-02 20:25:11.032093+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1917	NETSUITE_CLASS	Netsuite Class	Gevelber Photography	expense_custom_field.netsuite class.14	2022-08-02 20:25:11.032157+00	2022-08-02 20:25:11.032185+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1918	NETSUITE_CLASS	Netsuite Class	Jeff's Jalopies	expense_custom_field.netsuite class.15	2022-08-02 20:25:11.032366+00	2022-08-02 20:25:11.032405+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1919	NETSUITE_CLASS	Netsuite Class	John Melton	expense_custom_field.netsuite class.16	2022-08-02 20:25:11.032472+00	2022-08-02 20:25:11.032499+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1920	NETSUITE_CLASS	Netsuite Class	Kate Whelan	expense_custom_field.netsuite class.17	2022-08-02 20:25:11.032564+00	2022-08-02 20:25:11.032592+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1921	NETSUITE_CLASS	Netsuite Class	Kookies by Kathy	expense_custom_field.netsuite class.18	2022-08-02 20:25:11.032656+00	2022-08-02 20:25:11.032683+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1922	NETSUITE_CLASS	Netsuite Class	Mark Cho	expense_custom_field.netsuite class.19	2022-08-02 20:25:11.032748+00	2022-08-02 20:25:11.032775+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1923	NETSUITE_CLASS	Netsuite Class	Paulsen Medical Supplies	expense_custom_field.netsuite class.20	2022-08-02 20:25:11.03284+00	2022-08-02 20:25:11.032867+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1924	NETSUITE_CLASS	Netsuite Class	Pye's Cakes	expense_custom_field.netsuite class.21	2022-08-02 20:25:11.032931+00	2022-08-02 20:25:11.032958+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1925	NETSUITE_CLASS	Netsuite Class	Rago Travel Agency	expense_custom_field.netsuite class.22	2022-08-02 20:25:11.033023+00	2022-08-02 20:25:11.03305+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1926	NETSUITE_CLASS	Netsuite Class	Red Rock Diner	expense_custom_field.netsuite class.23	2022-08-02 20:25:11.033115+00	2022-08-02 20:25:11.033142+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1927	NETSUITE_CLASS	Netsuite Class	Rondonuwu Fruit and Vegi	expense_custom_field.netsuite class.24	2022-08-02 20:25:11.033206+00	2022-08-02 20:25:11.033351+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1928	NETSUITE_CLASS	Netsuite Class	Shara Barnett	expense_custom_field.netsuite class.25	2022-08-02 20:25:11.03343+00	2022-08-02 20:25:11.033458+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
2003	CORPORATE_CARD	Corporate Card	American Express - xxx188	baccaF1eUjhxFE	2022-08-02 20:25:11.266256+00	2022-08-02 20:25:11.266285+00	1	\N	{"cardholder_name": "HOSPITALITY OAKLEAF"}	f	f
1929	NETSUITE_CLASS	Netsuite Class	Shara Barnett:Barnett Design	expense_custom_field.netsuite class.26	2022-08-02 20:25:11.033523+00	2022-08-02 20:25:11.03355+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1930	NETSUITE_CLASS	Netsuite Class	Sheldon Cooper	expense_custom_field.netsuite class.27	2022-08-02 20:25:11.033615+00	2022-08-02 20:25:11.033643+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1931	NETSUITE_CLASS	Netsuite Class	Sheldon Cooper:Incremental Project	expense_custom_field.netsuite class.28	2022-08-02 20:25:11.033768+00	2022-08-02 20:25:11.033797+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1932	NETSUITE_CLASS	Netsuite Class	Sonnenschein Family Store	expense_custom_field.netsuite class.29	2022-08-02 20:25:11.033866+00	2022-08-02 20:25:11.033895+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1933	NETSUITE_CLASS	Netsuite Class	Sushi by Katsuyuki	expense_custom_field.netsuite class.30	2022-08-02 20:25:11.033964+00	2022-08-02 20:25:11.033993+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1934	NETSUITE_CLASS	Netsuite Class	Travis Waldron	expense_custom_field.netsuite class.31	2022-08-02 20:25:11.034062+00	2022-08-02 20:25:11.034244+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1935	NETSUITE_CLASS	Netsuite Class	Video Games by Dan	expense_custom_field.netsuite class.32	2022-08-02 20:25:11.034416+00	2022-08-02 20:25:11.034452+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1936	NETSUITE_CLASS	Netsuite Class	Wedding Planning by Whitney	expense_custom_field.netsuite class.33	2022-08-02 20:25:11.034649+00	2022-08-02 20:25:11.034684+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1937	NETSUITE_CLASS	Netsuite Class	Weiskopf Consulting	expense_custom_field.netsuite class.34	2022-08-02 20:25:11.034806+00	2022-08-02 20:25:11.034836+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1938	NETSUITE_CLASS	Netsuite Class	Sravan BLR Customer	expense_custom_field.netsuite class.35	2022-08-02 20:25:11.034907+00	2022-08-02 20:25:11.034936+00	1	\N	{"placeholder": "Select Netsuite Class", "custom_field_id": 205266}	f	f
1939	POSTMAN_FIELD	Postman Field	San Francisco	expense_custom_field.postman field.1	2022-08-02 20:25:11.050047+00	2022-08-02 20:25:11.050091+00	1	\N	{"placeholder": "Select Postman Field", "custom_field_id": 205386}	f	f
1940	POSTMAN_FIELD	Postman Field	USA2	expense_custom_field.postman field.2	2022-08-02 20:25:11.050172+00	2022-08-02 20:25:11.050203+00	1	\N	{"placeholder": "Select Postman Field", "custom_field_id": 205386}	f	f
1941	POSTMAN_FIELD	Postman Field	Dallas	expense_custom_field.postman field.3	2022-08-02 20:25:11.05048+00	2022-08-02 20:25:11.050519+00	1	\N	{"placeholder": "Select Postman Field", "custom_field_id": 205386}	f	f
1942	PLATFORM_FIELD	Platform Field	Amy's Bird Sanctuary	expense_custom_field.platform field.1	2022-08-02 20:25:11.061173+00	2022-08-02 20:25:11.061225+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1943	PLATFORM_FIELD	Platform Field	Bill's Windsurf Shop	expense_custom_field.platform field.2	2022-08-02 20:25:11.061413+00	2022-08-02 20:25:11.061442+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1944	PLATFORM_FIELD	Platform Field	Cool Cars	expense_custom_field.platform field.3	2022-08-02 20:25:11.061523+00	2022-08-02 20:25:11.061553+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1945	PLATFORM_FIELD	Platform Field	Customer UD	expense_custom_field.platform field.4	2022-08-02 20:25:11.06166+00	2022-08-02 20:25:11.061688+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1946	PLATFORM_FIELD	Platform Field	Diego Rodriguez	expense_custom_field.platform field.5	2022-08-02 20:25:11.061754+00	2022-08-02 20:25:11.061782+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1947	PLATFORM_FIELD	Platform Field	Dukes Basketball Camp	expense_custom_field.platform field.6	2022-08-02 20:25:11.061847+00	2022-08-02 20:25:11.061875+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1948	PLATFORM_FIELD	Platform Field	Dylan Sollfrank	expense_custom_field.platform field.7	2022-08-02 20:25:11.06194+00	2022-08-02 20:25:11.061968+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1949	PLATFORM_FIELD	Platform Field	Freeman Sporting Goods	expense_custom_field.platform field.8	2022-08-02 20:25:11.062033+00	2022-08-02 20:25:11.062061+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1987	CORPORATE_CARD	Corporate Card	American Express - xx2454	bacc5vHLgdO8An	2022-08-02 20:25:11.264677+00	2022-08-02 20:25:11.264706+00	1	\N	{"cardholder_name": "FIRST IMPRESSIONS SUN"}	f	f
1950	PLATFORM_FIELD	Platform Field	Freeman Sporting Goods:0969 Ocean View Road	expense_custom_field.platform field.9	2022-08-02 20:25:11.062127+00	2022-08-02 20:25:11.062154+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1951	PLATFORM_FIELD	Platform Field	Freeman Sporting Goods:0969 Ocean View Road:Test Project	expense_custom_field.platform field.10	2022-08-02 20:25:11.06223+00	2022-08-02 20:25:11.062396+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1952	PLATFORM_FIELD	Platform Field	Freeman Sporting Goods:55 Twin Lane	expense_custom_field.platform field.11	2022-08-02 20:25:11.062463+00	2022-08-02 20:25:11.062491+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1953	PLATFORM_FIELD	Platform Field	Geeta Kalapatapu	expense_custom_field.platform field.12	2022-08-02 20:25:11.062556+00	2022-08-02 20:25:11.062584+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1954	PLATFORM_FIELD	Platform Field	Gevelber Photography	expense_custom_field.platform field.13	2022-08-02 20:25:11.062649+00	2022-08-02 20:25:11.062677+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1955	PLATFORM_FIELD	Platform Field	Jeff's Jalopies	expense_custom_field.platform field.14	2022-08-02 20:25:11.062742+00	2022-08-02 20:25:11.06277+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1956	PLATFORM_FIELD	Platform Field	John Melton	expense_custom_field.platform field.15	2022-08-02 20:25:11.062835+00	2022-08-02 20:25:11.062862+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1957	PLATFORM_FIELD	Platform Field	Kate Whelan	expense_custom_field.platform field.16	2022-08-02 20:25:11.062928+00	2022-08-02 20:25:11.062955+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1958	PLATFORM_FIELD	Platform Field	Kookies by Kathy	expense_custom_field.platform field.17	2022-08-02 20:25:11.06302+00	2022-08-02 20:25:11.063048+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1959	PLATFORM_FIELD	Platform Field	Lol aavea Haithyas iPartnersa Inca.	expense_custom_field.platform field.18	2022-08-02 20:25:11.063113+00	2022-08-02 20:25:11.063141+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1960	PLATFORM_FIELD	Platform Field	Mark Cho	expense_custom_field.platform field.19	2022-08-02 20:25:11.063207+00	2022-08-02 20:25:11.063351+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1961	PLATFORM_FIELD	Platform Field	Paulsen Medical Supplies	expense_custom_field.platform field.20	2022-08-02 20:25:11.06343+00	2022-08-02 20:25:11.063458+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1962	PLATFORM_FIELD	Platform Field	Pye's Cakes	expense_custom_field.platform field.21	2022-08-02 20:25:11.063523+00	2022-08-02 20:25:11.063551+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1963	PLATFORM_FIELD	Platform Field	Rago Travel Agency	expense_custom_field.platform field.22	2022-08-02 20:25:11.063616+00	2022-08-02 20:25:11.063643+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1964	PLATFORM_FIELD	Platform Field	Red Rock Diner	expense_custom_field.platform field.23	2022-08-02 20:25:11.063709+00	2022-08-02 20:25:11.063736+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1965	PLATFORM_FIELD	Platform Field	Rondonuwu Fruit and Vegi	expense_custom_field.platform field.24	2022-08-02 20:25:11.063801+00	2022-08-02 20:25:11.063829+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1966	PLATFORM_FIELD	Platform Field	Shara Barnett	expense_custom_field.platform field.25	2022-08-02 20:25:11.063894+00	2022-08-02 20:25:11.063922+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1967	PLATFORM_FIELD	Platform Field	Shara Barnett:Barnett Design	expense_custom_field.platform field.26	2022-08-02 20:25:11.063987+00	2022-08-02 20:25:11.064015+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1968	PLATFORM_FIELD	Platform Field	Sonnenschein Family Store	expense_custom_field.platform field.27	2022-08-02 20:25:11.06408+00	2022-08-02 20:25:11.064107+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1969	PLATFORM_FIELD	Platform Field	Sushi by Katsuyuki	expense_custom_field.platform field.28	2022-08-02 20:25:11.064172+00	2022-08-02 20:25:11.0642+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1970	PLATFORM_FIELD	Platform Field	Travis Waldron	expense_custom_field.platform field.29	2022-08-02 20:25:11.064394+00	2022-08-02 20:25:11.064423+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1971	PLATFORM_FIELD	Platform Field	Video Games by Dan	expense_custom_field.platform field.30	2022-08-02 20:25:11.064488+00	2022-08-02 20:25:11.064516+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1972	PLATFORM_FIELD	Platform Field	Wedding Planning by Whitney	expense_custom_field.platform field.31	2022-08-02 20:25:11.064582+00	2022-08-02 20:25:11.064609+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1973	PLATFORM_FIELD	Platform Field	Weiskopf Consulting	expense_custom_field.platform field.32	2022-08-02 20:25:11.064675+00	2022-08-02 20:25:11.064702+00	1	\N	{"placeholder": "Select Platform Field", "custom_field_id": 205387}	f	f
1974	HGFH	Hgfh	Accountants Inc	expense_custom_field.hgfh.1	2022-08-02 20:25:11.079707+00	2022-08-02 20:25:11.079747+00	1	\N	{"placeholder": "Select Hgfh", "custom_field_id": 209230}	f	f
1975	HGFH	Hgfh	Bangalore	expense_custom_field.hgfh.2	2022-08-02 20:25:11.080088+00	2022-08-02 20:25:11.080242+00	1	\N	{"placeholder": "Select Hgfh", "custom_field_id": 209230}	f	f
1976	HGFH	Hgfh	Delhi	expense_custom_field.hgfh.3	2022-08-02 20:25:11.080335+00	2022-08-02 20:25:11.080374+00	1	\N	{"placeholder": "Select Hgfh", "custom_field_id": 209230}	f	f
1977	HGFH	Hgfh	suhas_p1	expense_custom_field.hgfh.4	2022-08-02 20:25:11.08046+00	2022-08-02 20:25:11.080478+00	1	\N	{"placeholder": "Select Hgfh", "custom_field_id": 209230}	f	f
1978	HGFH	Hgfh	Chennai	expense_custom_field.hgfh.5	2022-08-02 20:25:11.080536+00	2022-08-02 20:25:11.080569+00	1	\N	{"placeholder": "Select Hgfh", "custom_field_id": 209230}	f	f
1979	HGFH	Hgfh	Bebe Rexha	expense_custom_field.hgfh.6	2022-08-02 20:25:11.080642+00	2022-08-02 20:25:11.080671+00	1	\N	{"placeholder": "Select Hgfh", "custom_field_id": 209230}	f	f
1980	CORPORATE_CARD	Corporate Card	American Express - xx4141	baccL3nemST6Ci	2022-08-02 20:25:11.263943+00	2022-08-02 20:25:11.263996+00	1	\N	{"cardholder_name": "Jennifer Davis"}	f	f
1981	CORPORATE_CARD	Corporate Card	American Express - xx3420	bacc0JqpLvqPfX	2022-08-02 20:25:11.264078+00	2022-08-02 20:25:11.26411+00	1	\N	{"cardholder_name": "EVENTS CENTRAL"}	f	f
1982	CORPORATE_CARD	Corporate Card	American Express - xx1069	baccwuqluTNMmY	2022-08-02 20:25:11.264182+00	2022-08-02 20:25:11.264212+00	1	\N	{"cardholder_name": "Jessica Triest"}	f	f
1983	CORPORATE_CARD	Corporate Card	American Express - xxx869	bacczsJzAI7yO4	2022-08-02 20:25:11.264283+00	2022-08-02 20:25:11.264312+00	1	\N	{"cardholder_name": "NEXT STEPS CENTRAL"}	f	f
1984	CORPORATE_CARD	Corporate Card	American Express - xx6975	baccQzgzQ9bSU5	2022-08-02 20:25:11.264381+00	2022-08-02 20:25:11.264411+00	1	\N	{"cardholder_name": "CONNECTIONS ADMIN"}	f	f
1985	CORPORATE_CARD	Corporate Card	American Express - xx5128	baccYoWGQm8vsv	2022-08-02 20:25:11.26448+00	2022-08-02 20:25:11.264509+00	1	\N	{"cardholder_name": "Laura Lang"}	f	f
1986	CORPORATE_CARD	Corporate Card	American Express - xx2285	baccIPOyVw9jz9	2022-08-02 20:25:11.264578+00	2022-08-02 20:25:11.264607+00	1	\N	{"cardholder_name": "Zack Crutchfield"}	f	f
1988	CORPORATE_CARD	Corporate Card	American Express - xx4498	bacc6O6ygKJ5RZ	2022-08-02 20:25:11.264776+00	2022-08-02 20:25:11.264805+00	1	\N	{"cardholder_name": "Kristal Staier"}	f	f
1989	CORPORATE_CARD	Corporate Card	American Express - xx6232	baccU0nZAQAjXW	2022-08-02 20:25:11.264875+00	2022-08-02 20:25:11.264904+00	1	\N	{"cardholder_name": "EKIDS ORANGE PARK"}	f	f
1990	CORPORATE_CARD	Corporate Card	American Express - xx9763	baccrQyl3zzHUD	2022-08-02 20:25:11.264973+00	2022-08-02 20:25:11.265002+00	1	\N	{"cardholder_name": "Jake Jaudes"}	f	f
1991	CORPORATE_CARD	Corporate Card	American Express - xx8297	baccN2XSXyabZ7	2022-08-02 20:25:11.265071+00	2022-08-02 20:25:11.2651+00	1	\N	{"cardholder_name": "ESTUDENTS ORANGE PARK"}	f	f
1992	CORPORATE_CARD	Corporate Card	American Express - xx4150	baccOnAzWJ4OWe	2022-08-02 20:25:11.265175+00	2022-08-02 20:25:11.265205+00	1	\N	{"cardholder_name": "Tonino Mallory"}	f	f
1993	CORPORATE_CARD	Corporate Card	American Express - xx3858	baccEYbDwJLXZm	2022-08-02 20:25:11.265275+00	2022-08-02 20:25:11.265304+00	1	\N	{"cardholder_name": "HOSPITALITY SAT OAKLEAF"}	f	f
1994	CORPORATE_CARD	Corporate Card	American Express - xx7217	bacctpbV5x8SXo	2022-08-02 20:25:11.265373+00	2022-08-02 20:25:11.265402+00	1	\N	{"cardholder_name": "EKIDS SAT OAKLEAF"}	f	f
1995	CORPORATE_CARD	Corporate Card	American Express - xx9650	bacc6glcp16XGR	2022-08-02 20:25:11.265471+00	2022-08-02 20:25:11.2655+00	1	\N	{"cardholder_name": "Beau Norton"}	f	f
1996	CORPORATE_CARD	Corporate Card	American Express - xx5078	bacclBSsBnkz7C	2022-08-02 20:25:11.265569+00	2022-08-02 20:25:11.265598+00	1	\N	{"cardholder_name": "ADMIN CENTRAL"}	f	f
1997	CORPORATE_CARD	Corporate Card	American Express - xxx323	baccUHPqjBHqQj	2022-08-02 20:25:11.265667+00	2022-08-02 20:25:11.265696+00	1	\N	{"cardholder_name": "Ethan Ormeo"}	f	f
1998	CORPORATE_CARD	Corporate Card	American Express - xx7938	baccppsFdxrWWA	2022-08-02 20:25:11.265765+00	2022-08-02 20:25:11.265794+00	1	\N	{"cardholder_name": "HOSPITALITY FLEMING"}	f	f
1999	CORPORATE_CARD	Corporate Card	American Express - xx6434	baccjr7nWMM4NJ	2022-08-02 20:25:11.265863+00	2022-08-02 20:25:11.265892+00	1	\N	{"cardholder_name": "HOSPITALITY ORANGE PARK"}	f	f
2000	CORPORATE_CARD	Corporate Card	American Express - xx8291	bacc0lEwS3OOfl	2022-08-02 20:25:11.265961+00	2022-08-02 20:25:11.26599+00	1	\N	{"cardholder_name": "D'morea Green"}	f	f
2001	CORPORATE_CARD	Corporate Card	American Express - xx1930	baccPksofv9tEs	2022-08-02 20:25:11.266059+00	2022-08-02 20:25:11.266088+00	1	\N	{"cardholder_name": "ESTUDENTS FLEMING"}	f	f
2002	CORPORATE_CARD	Corporate Card	American Express - xx6145	baccJZ7Hts78fu	2022-08-02 20:25:11.266157+00	2022-08-02 20:25:11.266187+00	1	\N	{"cardholder_name": "Kenil Edmond"}	f	f
2004	CORPORATE_CARD	Corporate Card	American Express - xx9945	baccNuIzDqCxuP	2022-08-02 20:25:11.266355+00	2022-08-02 20:25:11.266384+00	1	\N	{"cardholder_name": "EKIDS SUN OAKLEAF"}	f	f
2005	CORPORATE_CARD	Corporate Card	American Express - xx9224	baccV3w0GuuevD	2022-08-02 20:25:11.266453+00	2022-08-02 20:25:11.266483+00	1	\N	{"cardholder_name": "ESTUDENTS ADMIN"}	f	f
2006	CORPORATE_CARD	Corporate Card	American Express - xx2733	baccE7LNy9BHhB	2022-08-02 20:25:11.26669+00	2022-08-02 20:25:11.266741+00	1	\N	{"cardholder_name": "ELA CENTRAL"}	f	f
2007	CORPORATE_CARD	Corporate Card	American Express - xx7473	bacczpOVGbmE3g	2022-08-02 20:25:11.266849+00	2022-08-02 20:25:11.266889+00	1	\N	{"cardholder_name": "Jayme Ormeo"}	f	f
2008	CORPORATE_CARD	Corporate Card	American Express - xxx73	bacc0wCFcCTHds	2022-08-02 20:25:11.266988+00	2022-08-02 20:25:11.267155+00	1	\N	{"cardholder_name": "Cherelle Keen"}	f	f
2009	CORPORATE_CARD	Corporate Card	American Express - xxx564	baccELz3BhzERm	2022-08-02 20:25:11.267259+00	2022-08-02 20:25:11.26734+00	1	\N	{"cardholder_name": "Dustin Redd"}	f	f
2010	CORPORATE_CARD	Corporate Card	American Express - xx5280	baccBgt6aogdMU	2022-08-02 20:25:11.267522+00	2022-08-02 20:25:11.26777+00	1	\N	{"cardholder_name": "Caroline Whitworth"}	f	f
2011	CORPORATE_CARD	Corporate Card	American Express - xx1416	baccG3H5Q8vphP	2022-08-02 20:25:11.270843+00	2022-08-02 20:25:11.271067+00	1	\N	{"cardholder_name": "EKIDS ADMIN"}	f	f
2012	CORPORATE_CARD	Corporate Card	American Express - xx8544	baccnXdAMrc0Gp	2022-08-02 20:25:11.271372+00	2022-08-02 20:25:11.271414+00	1	\N	{"cardholder_name": "PRODUCTION SUN OAKLEAF"}	f	f
2013	CORPORATE_CARD	Corporate Card	American Express - xx3382	bacccYnyU5KvKT	2022-08-02 20:25:11.272278+00	2022-08-02 20:25:11.272348+00	1	\N	{"cardholder_name": "HOSPITALITY SUN OAKLEAF"}	f	f
2014	CORPORATE_CARD	Corporate Card	American Express - xx4486	baccCZ1CQYf6Sy	2022-08-02 20:25:11.272504+00	2022-08-02 20:25:11.272529+00	1	\N	{"cardholder_name": "EGROUPS CENTRAL"}	f	f
2015	CORPORATE_CARD	Corporate Card	American Express - xxx728	baccFrvYBXZ5ee	2022-08-02 20:25:11.272631+00	2022-08-02 20:25:11.272667+00	1	\N	{"cardholder_name": "Zack Crutchfield"}	f	f
2016	CORPORATE_CARD	Corporate Card	American Express - xx2171	baccb3ZTBsZlKR	2022-08-02 20:25:11.272786+00	2022-08-02 20:25:11.27282+00	1	\N	{"cardholder_name": "EKIDS FLEMING"}	f	f
2017	CORPORATE_CARD	Corporate Card	American Express - xx8418	bacctZjXzW6dt8	2022-08-02 20:25:11.272883+00	2022-08-02 20:25:11.272905+00	1	\N	{"cardholder_name": "Christopher Curry"}	f	f
2018	CORPORATE_CARD	Corporate Card	American Express - xx5755	baccBVCtbSbnEp	2022-08-02 20:25:11.27297+00	2022-08-02 20:25:11.272991+00	1	\N	{"cardholder_name": "MEDIA CENTRAL"}	f	f
2019	CORPORATE_CARD	Corporate Card	American Express - xx8370	bacc38bi6wVHXw	2022-08-02 20:25:11.273512+00	2022-08-02 20:25:11.273554+00	1	\N	{"cardholder_name": "Jake Jaudes"}	f	f
2020	CORPORATE_CARD	Corporate Card	American Express - xx3763	baccFj0n9AMg4j	2022-08-02 20:25:11.273638+00	2022-08-02 20:25:11.273661+00	1	\N	{"cardholder_name": "Kirk Jaudes"}	f	f
2021	CORPORATE_CARD	Corporate Card	American Express - xx3586	baccCqabAYVNCK	2022-08-02 20:25:11.273724+00	2022-08-02 20:25:11.27429+00	1	\N	{"cardholder_name": "Missions Central"}	f	f
2022	CORPORATE_CARD	Corporate Card	American Express - xx1306	baccWO78vU78Qu	2022-08-02 20:25:11.275757+00	2022-08-02 20:25:11.277076+00	1	\N	{"cardholder_name": "PRODUCTION FLEMING"}	f	f
2023	CORPORATE_CARD	Corporate Card	American Express - x7777	bacc0rGr9CnI07	2022-08-02 20:25:11.279786+00	2022-08-02 20:25:11.279979+00	1	\N	{"cardholder_name": "Monica E. Geller-Bing's account"}	f	f
2024	CORPORATE_CARD	Corporate Card	American Express - x3333	bacc8nSHqMKBm5	2022-08-02 20:25:11.280293+00	2022-08-02 20:25:11.280449+00	1	\N	{"cardholder_name": "Dr. Ross Eustace Geller's account"}	f	f
2025	CORPORATE_CARD	Corporate Card	American Express - x8888	baccqPND2ACDG0	2022-08-02 20:25:11.285071+00	2022-08-02 20:25:11.285394+00	1	\N	{"cardholder_name": "Joseph Francis Tribbiani, Jr's account"}	f	f
2026	CORPORATE_CARD	Corporate Card	American Express - x2222	baccxrtsvLlwJt	2022-08-02 20:25:11.286199+00	2022-08-02 20:25:11.28624+00	1	\N	{"cardholder_name": "Chandler Muriel Bing's account"}	f	f
2027	CORPORATE_CARD	Corporate Card	American Express - x9999	baccf77s3yLm3o	2022-08-02 20:25:11.287918+00	2022-08-02 20:25:11.287978+00	1	\N	{"cardholder_name": "Phoebe Buffay-Hannigan's account"}	f	f
41	CATEGORY	Category	Printing & Stationery	190419	2022-08-02 20:25:06.619647+00	2022-08-02 20:25:06.619674+00	1	\N	\N	t	f
2029	TAX_GROUP	Tax Group	Platform Tax @2%	tg1ysRcndInD	2022-08-02 20:25:31.719575+00	2022-08-02 20:25:31.719605+00	1	\N	{"tax_rate": 0.02}	f	f
2030	TAX_GROUP	Tax Group	CGsST	tg22tvjYZ8fi	2022-08-02 20:25:31.719677+00	2022-08-02 20:25:31.719697+00	1	\N	{"tax_rate": 0.45}	f	f
42	CATEGORY	Category	Wages and Salaries	190420	2022-08-02 20:25:06.619731+00	2022-08-02 20:25:06.619759+00	1	\N	\N	t	f
43	CATEGORY	Category	Superannuation	190421	2022-08-02 20:25:06.619816+00	2022-08-02 20:25:06.619843+00	1	\N	\N	t	f
2033	TAX_GROUP	Tax Group	0.0% ECS @0%	tg42cqMnvEuN	2022-08-02 20:25:31.720033+00	2022-08-02 20:25:31.720059+00	1	\N	{"tax_rate": 0.0}	f	f
2034	TAX_GROUP	Tax Group	Fyle Tax @10%	tg42zIB2AUEI	2022-08-02 20:25:31.720114+00	2022-08-02 20:25:31.720136+00	1	\N	{"tax_rate": 0.1}	f	f
2035	TAX_GROUP	Tax Group	SGST	tg4Ji2lm1TjY	2022-08-02 20:25:31.720508+00	2022-08-02 20:25:31.720538+00	1	\N	{"tax_rate": 0.25}	f	f
2036	TAX_GROUP	Tax Group	Fyle UK Purchase Tax @20%	tg4NTrM2rI3T	2022-08-02 20:25:31.720609+00	2022-08-02 20:25:31.720638+00	1	\N	{"tax_rate": 0.2}	f	f
2037	TAX_GROUP	Tax Group	tax for xero @2.5%	tg6kW4rcwIpR	2022-08-02 20:25:31.720709+00	2022-08-02 20:25:31.720738+00	1	\N	{"tax_rate": 0.03}	f	f
2038	TAX_GROUP	Tax Group	GST on capital @10%	tg7JkSia4QDa	2022-08-02 20:25:31.720808+00	2022-08-02 20:25:31.720837+00	1	\N	{"tax_rate": 0.1}	f	f
2039	TAX_GROUP	Tax Group	tax for sample @20.0%	tgaqu44d9tHA	2022-08-02 20:25:31.720908+00	2022-08-02 20:25:31.721041+00	1	\N	{"tax_rate": 0.2}	f	f
2040	TAX_GROUP	Tax Group	tax for zero @0.0%	tgB4n1w5kiWZ	2022-08-02 20:25:31.721113+00	2022-08-02 20:25:31.721142+00	1	\N	{"tax_rate": 0.0}	f	f
2041	TAX_GROUP	Tax Group	G0ZVX1015G	tgcOjihUXU6z	2022-08-02 20:25:31.721213+00	2022-08-02 20:25:31.721242+00	1	\N	{"tax_rate": 0.18}	f	f
2042	TAX_GROUP	Tax Group	VAT	tgF1ALQnBzqf	2022-08-02 20:25:31.721312+00	2022-08-02 20:25:31.721342+00	1	\N	{"tax_rate": 0.18}	f	f
2043	TAX_GROUP	Tax Group	KSK @10%	tggCLLBfraIa	2022-08-02 20:25:31.721468+00	2022-08-02 20:25:31.721545+00	1	\N	{"tax_rate": 0.1}	f	f
2044	TAX_GROUP	Tax Group	12.5% TR @12.5%	tgGEuMf8nNvy	2022-08-02 20:25:31.721679+00	2022-08-02 20:25:31.721722+00	1	\N	{"tax_rate": 0.12}	f	f
2045	TAX_GROUP	Tax Group	tax for twelve @12.5%	tgGImQ6xtcut	2022-08-02 20:25:31.721858+00	2022-08-02 20:25:31.721902+00	1	\N	{"tax_rate": 0.12}	f	f
2046	TAX_GROUP	Tax Group	Tax on Sales @0.0%	tgGTemokupGO	2022-08-02 20:25:31.722367+00	2022-08-02 20:25:31.722417+00	1	\N	{"tax_rate": 0.0}	f	f
2047	TAX_GROUP	Tax Group	Staging Tax @10%	tgGYBGZlDMvk	2022-08-02 20:25:31.722535+00	2022-08-02 20:25:31.722575+00	1	\N	{"tax_rate": 0.1}	f	f
44	CATEGORY	Category	Subscriptions	190422	2022-08-02 20:25:06.6199+00	2022-08-02 20:25:06.619927+00	1	\N	\N	t	f
2049	TAX_GROUP	Tax Group	5.0% R @5%	tgh3IXxRf3gV	2022-08-02 20:25:31.722871+00	2022-08-02 20:25:31.722901+00	1	\N	{"tax_rate": 0.05}	f	f
2050	TAX_GROUP	Tax Group	Pant Tax @20%	tghhNinCc8Nh	2022-08-02 20:25:31.723064+00	2022-08-02 20:25:31.723094+00	1	\N	{"tax_rate": 0.2}	f	f
2051	TAX_GROUP	Tax Group	GST @21%	tgHt9uUjaGlJ	2022-08-02 20:25:31.723167+00	2022-08-02 20:25:31.723196+00	1	\N	{"tax_rate": 0.21}	f	f
2052	TAX_GROUP	Tax Group	tax for ten @10.0%	tghwiPuzdFUX	2022-08-02 20:25:31.723266+00	2022-08-02 20:25:31.723295+00	1	\N	{"tax_rate": 0.1}	f	f
2053	TAX_GROUP	Tax Group	Input tax @0%	tgI1yAaGROYp	2022-08-02 20:25:31.723365+00	2022-08-02 20:25:31.723394+00	1	\N	{"tax_rate": 0.0}	f	f
2054	TAX_GROUP	Tax Group	KSK Tax @10%	tgIKsRuiUOmt	2022-08-02 20:25:31.723464+00	2022-08-02 20:25:31.723493+00	1	\N	{"tax_rate": 0.1}	f	f
2055	TAX_GROUP	Tax Group	Auto Look Up @0.0%	tgikYUW7IaA2	2022-08-02 20:25:31.723562+00	2022-08-02 20:25:31.723591+00	1	\N	{"tax_rate": 0.0}	f	f
2056	TAX_GROUP	Tax Group	GST-free capital @0%	tgkPbHSey2P8	2022-08-02 20:25:31.72366+00	2022-08-02 20:25:31.723689+00	1	\N	{"tax_rate": 0.0}	f	f
45	CATEGORY	Category	Telephone & Internet	190423	2022-08-02 20:25:06.619985+00	2022-08-02 20:25:06.620012+00	1	\N	\N	t	f
2058	TAX_GROUP	Tax Group	20.0% RC @0%	tgM48AuKIfg9	2022-08-02 20:25:31.723856+00	2022-08-02 20:25:31.723885+00	1	\N	{"tax_rate": 0.0}	f	f
2059	TAX_GROUP	Tax Group	20.0% RC MPCCs @0%	tgMLKepnn29c	2022-08-02 20:25:31.723953+00	2022-08-02 20:25:31.723982+00	1	\N	{"tax_rate": 0.0}	f	f
46	CATEGORY	Category	Travel - National	190424	2022-08-02 20:25:06.620069+00	2022-08-02 20:25:06.620097+00	1	\N	\N	t	f
47	CATEGORY	Category	Travel - International	190425	2022-08-02 20:25:06.620154+00	2022-08-02 20:25:06.620181+00	1	\N	\N	t	f
2062	TAX_GROUP	Tax Group	20.0% RC CIS @0%	tgNYZFh37Ohs	2022-08-02 20:25:31.724331+00	2022-08-02 20:25:31.72436+00	1	\N	{"tax_rate": 0.0}	f	f
2063	TAX_GROUP	Tax Group	PVA Import 0.0% @0%	tgO9u14YtEd2	2022-08-02 20:25:31.724428+00	2022-08-02 20:25:31.724457+00	1	\N	{"tax_rate": 0.0}	f	f
2064	TAX_GROUP	Tax Group	AUS Tax @20%	tgOgSigdcIfN	2022-08-02 20:25:31.724527+00	2022-08-02 20:25:31.724556+00	1	\N	{"tax_rate": 0.2}	f	f
2065	TAX_GROUP	Tax Group	20.0% ECG @0%	tgokXLoUA6sX	2022-08-02 20:25:31.724625+00	2022-08-02 20:25:31.724654+00	1	\N	{"tax_rate": 0.0}	f	f
2066	TAX_GROUP	Tax Group	CGST	tgpRUOwOJWrM	2022-08-02 20:25:31.724724+00	2022-08-02 20:25:31.724753+00	1	\N	{"tax_rate": 0.45}	f	f
2067	TAX_GROUP	Tax Group	20.0% ECS @0%	tgQtjzfQcG6x	2022-08-02 20:25:31.724821+00	2022-08-02 20:25:31.72485+00	1	\N	{"tax_rate": 0.0}	f	f
2068	TAX_GROUP	Tax Group	0.0% Z @0%	tgqzXkzQUvak	2022-08-02 20:25:31.724919+00	2022-08-02 20:25:31.724948+00	1	\N	{"tax_rate": 0.0}	f	f
2069	TAX_GROUP	Tax Group	Exempt @0%	tgReWuoGJ3bY	2022-08-02 20:25:31.725143+00	2022-08-02 20:25:31.725185+00	1	\N	{"tax_rate": 0.0}	f	f
48	CATEGORY	Category	Bank Revaluations	190426	2022-08-02 20:25:06.620239+00	2022-08-02 20:25:06.620389+00	1	\N	\N	t	f
2071	TAX_GROUP	Tax Group	Tax on Purchases @0.0%	tgsIkR0An9nU	2022-08-02 20:25:31.725537+00	2022-08-02 20:25:31.725584+00	1	\N	{"tax_rate": 0.0}	f	f
2072	TAX_GROUP	Tax Group	PVA Import 20.0% @0%	tgTQgdaJsKuy	2022-08-02 20:25:31.72569+00	2022-08-02 20:25:31.725719+00	1	\N	{"tax_rate": 0.0}	f	f
2073	TAX_GROUP	Tax Group	0.0% ECG @0%	tgTQOCcawgKE	2022-08-02 20:25:31.725788+00	2022-08-02 20:25:31.725817+00	1	\N	{"tax_rate": 0.0}	f	f
2074	TAX_GROUP	Tax Group	CGSssdfdT	tgU9CDyVByvm	2022-08-02 20:25:31.725888+00	2022-08-02 20:25:31.725917+00	1	\N	{"tax_rate": 0.45}	f	f
2075	TAX_GROUP	Tax Group	Nilesh Nice @10%	tgv7ezwMH3dy	2022-08-02 20:25:31.725987+00	2022-08-02 20:25:31.726094+00	1	\N	{"tax_rate": 0.1}	f	f
2076	TAX_GROUP	Tax Group	tax for jadu @20.0%	tgvOS2dDHpwx	2022-08-02 20:25:31.726176+00	2022-08-02 20:25:31.726205+00	1	\N	{"tax_rate": 0.2}	f	f
2077	TAX_GROUP	Tax Group	20.0% RC SG @0%	tgvTo8lWu7w8	2022-08-02 20:25:31.726274+00	2022-08-02 20:25:31.726303+00	1	\N	{"tax_rate": 0.0}	f	f
2078	TAX_GROUP	Tax Group	5.0% RC CIS @0%	tgvu4aiSYKG2	2022-08-02 20:25:31.753485+00	2022-08-02 20:25:31.753527+00	1	\N	{"tax_rate": 0.0}	f	f
2079	TAX_GROUP	Tax Group	GST on non-capital @10%	tgvu9jSCsCXI	2022-08-02 20:25:31.753604+00	2022-08-02 20:25:31.753634+00	1	\N	{"tax_rate": 0.1}	f	f
2080	TAX_GROUP	Tax Group	20.0% S @20%	tgYBj1SKQlWH	2022-08-02 20:25:31.753707+00	2022-08-02 20:25:31.753736+00	1	\N	{"tax_rate": 0.2}	f	f
2081	TAX_GROUP	Tax Group	No VAT @0%	tgyruoo6Cu7B	2022-08-02 20:25:31.753806+00	2022-08-02 20:25:31.753836+00	1	\N	{"tax_rate": 0.0}	f	f
2082	TAX_GROUP	Tax Group	Nilesh Tax @10%	tgZFMdbUmGUw	2022-08-02 20:25:31.753906+00	2022-08-02 20:25:31.753935+00	1	\N	{"tax_rate": 0.1}	f	f
49	CATEGORY	Category	Unrealised Currency Gains	190427	2022-08-02 20:25:06.620459+00	2022-08-02 20:25:06.620486+00	1	\N	\N	t	f
509	PROJECT	Project	Bank West	300071	2022-08-02 20:25:07.833955+00	2022-08-02 20:25:07.833997+00	1	\N	\N	t	f
510	PROJECT	Project	Basket Case	300072	2022-08-02 20:25:07.834059+00	2022-08-02 20:25:07.834087+00	1	\N	\N	t	f
511	PROJECT	Project	Bayside Club	300073	2022-08-02 20:25:07.834144+00	2022-08-02 20:25:07.834172+00	1	\N	\N	t	f
512	PROJECT	Project	Boom FM	300074	2022-08-02 20:25:07.834349+00	2022-08-02 20:25:07.83439+00	1	\N	\N	t	f
513	PROJECT	Project	City Agency	300075	2022-08-02 20:25:07.834449+00	2022-08-02 20:25:07.834477+00	1	\N	\N	t	f
50	CATEGORY	Category	Realised Currency Gains	190428	2022-08-02 20:25:06.620543+00	2022-08-02 20:25:06.620571+00	1	\N	\N	t	f
514	PROJECT	Project	City Limousines	300076	2022-08-02 20:25:07.834534+00	2022-08-02 20:25:07.834567+00	1	\N	\N	t	f
515	PROJECT	Project	DIISR - Small Business Services	300077	2022-08-02 20:25:07.83464+00	2022-08-02 20:25:07.83467+00	1	\N	\N	t	f
516	PROJECT	Project	Hamilton Smith Ltd	300078	2022-08-02 20:25:07.834774+00	2022-08-02 20:25:07.834872+00	1	\N	\N	t	f
517	PROJECT	Project	Marine Systems	300079	2022-08-02 20:25:07.835036+00	2022-08-02 20:25:07.835078+00	1	\N	\N	t	f
518	PROJECT	Project	Petrie McLoud Watson & Associates	300080	2022-08-02 20:25:07.835193+00	2022-08-02 20:25:07.835418+00	1	\N	\N	t	f
519	PROJECT	Project	Port & Philip Freight	300081	2022-08-02 20:25:07.835538+00	2022-08-02 20:25:07.835583+00	1	\N	\N	t	f
520	PROJECT	Project	Rex Media Group	300082	2022-08-02 20:25:07.835687+00	2022-08-02 20:25:07.835714+00	1	\N	\N	t	f
521	PROJECT	Project	Ridgeway University	300083	2022-08-02 20:25:07.835771+00	2022-08-02 20:25:07.835798+00	1	\N	\N	t	f
522	PROJECT	Project	Young Bros Transport	300084	2022-08-02 20:25:07.835855+00	2022-08-02 20:25:07.835882+00	1	\N	\N	t	f
2028	TAX_GROUP	Tax Group	Exempt Sales @0.0%	tg0gTsClGjLp	2022-08-02 20:25:31.719457+00	2022-08-02 20:25:31.7195+00	1	\N	{"tax_rate": 0.0}	t	f
2031	TAX_GROUP	Tax Group	Tax Exempt @0.0%	tg2hTvShxrs3	2022-08-02 20:25:31.719756+00	2022-08-02 20:25:31.719785+00	1	\N	{"tax_rate": 0.0}	t	f
2048	TAX_GROUP	Tax Group	MB - GST/RST on Purchases @12.0%	tgh2SlAqltId	2022-08-02 20:25:31.722688+00	2022-08-02 20:25:31.722775+00	1	\N	{"tax_rate": 0.12}	t	f
2057	TAX_GROUP	Tax Group	Tax on Goods @8.75%	tgKydO7aGwzM	2022-08-02 20:25:31.723758+00	2022-08-02 20:25:31.723788+00	1	\N	{"tax_rate": 0.09}	t	f
2060	TAX_GROUP	Tax Group	Tax on Purchases @8.25%	tgmw3ZLz1cWw	2022-08-02 20:25:31.724133+00	2022-08-02 20:25:31.724163+00	1	\N	{"tax_rate": 0.08}	t	f
2061	TAX_GROUP	Tax Group	Sales Tax on Imports @0.0%	tgNLAzTq9jwm	2022-08-02 20:25:31.724232+00	2022-08-02 20:25:31.724261+00	1	\N	{"tax_rate": 0.0}	t	f
2070	TAX_GROUP	Tax Group	Tax on Consulting @8.25%	tgsHT9Jff1aH	2022-08-02 20:25:31.725298+00	2022-08-02 20:25:31.725337+00	1	\N	{"tax_rate": 0.08}	t	f
2083	TAX_GROUP	Tax Group	MB - GST/RST on Sales @12.0%	tgZlRFCaIxvQ	2022-08-02 20:25:31.754224+00	2022-08-02 20:25:31.754269+00	1	\N	{"tax_rate": 0.12}	t	f
1	EMPLOYEE	Employee	sravan.kumar@fyle.in	oulpZnCS6Mmt	2022-08-02 20:25:06.273228+00	2022-08-02 20:25:06.273431+00	1	\N	{"user_id": "ust5Ga9HC3qc", "location": null, "full_name": "Sravan K", "department": null, "department_id": null, "employee_code": "1234", "department_code": null}	t	f
8	EMPLOYEE	Employee	ashwin.t@fyle.in	ouWFNP49TXyP	2022-08-02 20:25:06.274284+00	2022-08-02 20:25:06.274306+00	1	\N	{"user_id": "usqywo0f3nBY", "location": null, "full_name": "Joanna", "department": null, "department_id": null, "employee_code": null, "department_code": null}	t	f
\.


--
-- Data for Name: expense_fields; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expense_fields (id, attribute_type, source_field_id, is_enabled, created_at, updated_at, workspace_id) FROM stdin;
\.


--
-- Data for Name: expense_group_settings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expense_group_settings (id, reimbursable_expense_group_fields, corporate_credit_card_expense_group_fields, expense_state, reimbursable_export_date_type, created_at, updated_at, workspace_id, ccc_export_date_type, ccc_expense_state, reimbursable_expense_state, import_card_credits) FROM stdin;
1	{employee_email,report_id,claim_number,fund_source}	{report_id,fund_source,employee_email,claim_number,expense_id}	PAYMENT_PROCESSING	current_date	2022-08-02 20:24:42.329794+00	2022-08-02 20:25:24.6873+00	1	spent_at	PAYMENT_PROCESSING	PAYMENT_PROCESSING	t
\.


--
-- Data for Name: expense_groups; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expense_groups (id, fund_source, description, created_at, exported_at, updated_at, workspace_id, response_logs, employee_name) FROM stdin;
2	PERSONAL	{"report_id": "rpE2JyATZhDe", "fund_source": "PERSONAL", "claim_number": "C/2022/05/R/16", "employee_email": "ashwin.t@fyle.in"}	2022-08-02 20:26:22.944108+00	2022-08-02 20:27:44.873229+00	2022-08-02 20:27:44.873778+00	1	\N	\N
4	PERSONAL	{"report_id": "rpKuJtEv6h0n", "fund_source": "PERSONAL", "claim_number": "C/2022/06/R/1", "employee_email": "sravan.kumar@fyle.in"}	2022-08-02 20:26:22.953025+00	2022-08-02 20:27:48.929649+00	2022-08-02 20:27:48.929826+00	1	\N	\N
1	PERSONAL	{"report_id": "rp9EvDF8Umk6", "fund_source": "PERSONAL", "claim_number": "C/2022/06/R/2", "employee_email": "ashwin.t@fyle.in"}	2022-08-02 20:26:22.939437+00	2022-08-02 20:27:52.017417+00	2022-08-02 20:27:52.017711+00	1	\N	\N
3	PERSONAL	{"report_id": "rpNeZt3cv9wz", "fund_source": "PERSONAL", "claim_number": "C/2022/06/R/3", "employee_email": "ashwin.t@fyle.in"}	2022-08-02 20:26:22.948473+00	2022-08-02 20:27:55.12672+00	2022-08-02 20:27:55.127073+00	1	\N	\N
10	CCC	{"spent_at": "2022-05-25", "report_id": "rpVvNQvE2wbm", "expense_id": "txBMQRkBQciI", "fund_source": "CCC", "claim_number": "C/2022/05/R/13", "employee_email": "sravan.kumar@fyle.in"}	2022-08-02 20:26:22.974361+00	2022-08-02 20:27:59.397949+00	2022-08-02 20:27:59.39816+00	1	\N	\N
5	CCC	{"spent_at": "2022-05-24", "report_id": "rp5lITpxFLxE", "expense_id": "txkw3dt3umkN", "fund_source": "CCC", "claim_number": "C/2022/05/R/12", "employee_email": "sravan.kumar@fyle.in"}	2022-08-02 20:26:22.956314+00	2022-08-02 20:28:03.682322+00	2022-08-02 20:28:03.682555+00	1	\N	\N
8	CCC	{"spent_at": "2022-05-25", "report_id": "rprwGgzOZyfR", "expense_id": "tx1FW3uxYZG6", "fund_source": "CCC", "claim_number": "C/2022/05/R/15", "employee_email": "sravan.kumar@fyle.in"}	2022-08-02 20:26:22.966799+00	2022-08-02 20:28:07.656716+00	2022-08-02 20:28:07.657378+00	1	\N	\N
6	CCC	{"spent_at": "2022-05-25", "report_id": "rpLawO11bFib", "expense_id": "txjIqTCtkkC8", "fund_source": "CCC", "claim_number": "C/2022/05/R/18", "employee_email": "sravan.kumar@fyle.in"}	2022-08-02 20:26:22.959403+00	2022-08-02 20:28:11.748729+00	2022-08-02 20:28:11.748944+00	1	\N	\N
9	CCC	{"spent_at": "2021-01-01", "report_id": "rpv1txzAsgr3", "expense_id": "txUPRc3VwxOP", "fund_source": "CCC", "claim_number": "C/2022/05/R/17", "employee_email": "sravan.kumar@fyle.in"}	2022-08-02 20:26:22.97121+00	2022-08-02 20:28:16.115273+00	2022-08-02 20:28:16.115482+00	1	\N	\N
7	CCC	{"spent_at": "2022-05-25", "report_id": "rpnG3lZYDsHU", "expense_id": "txVXhyVB8mgK", "fund_source": "CCC", "claim_number": "C/2022/05/R/14", "employee_email": "sravan.kumar@fyle.in"}	2022-08-02 20:26:22.962947+00	2022-08-02 20:28:20.026921+00	2022-08-02 20:28:20.027277+00	1	\N	\N
\.


--
-- Data for Name: expense_groups_expenses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expense_groups_expenses (id, expensegroup_id, expense_id) FROM stdin;
1	1	1
2	2	6
3	3	2
4	4	3
5	5	10
6	6	4
7	7	8
8	8	7
9	9	5
10	10	9
\.


--
-- Data for Name: expenses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expenses (id, employee_email, category, sub_category, project, expense_id, expense_number, claim_number, amount, currency, foreign_amount, foreign_currency, settlement_id, reimbursable, state, vendor, cost_center, purpose, report_id, spent_at, approved_at, expense_created_at, expense_updated_at, created_at, updated_at, fund_source, verified_at, custom_properties, paid_on_xero, org_id, file_ids, corporate_card_id, tax_amount, tax_group_id, billable, employee_name, posted_at) FROM stdin;
1	ashwin.t@fyle.in	Food	\N	\N	txaaVBj3yKGW	E/2022/06/T/4	C/2022/06/R/2	1	USD	\N	\N	setrunCck8hLH	t	PAYMENT_PROCESSING	\N	\N	\N	rp9EvDF8Umk6	2022-06-27 17:00:00+00	2022-06-27 09:06:52.951+00	2022-06-27 09:06:13.135764+00	2022-06-27 09:08:23.340321+00	2022-08-02 20:26:22.81033+00	2022-08-02 20:26:22.810363+00	PERSONAL	\N	{"Card": "", "Killua": "", "Classes": "", "avc_123": null, "New Field": "", "Multi field": "", "Testing This": "", "abc in [123]": null, "Postman Field": "", "Netsuite Class": ""}	f	orPJvXuoLqvJ	{}	\N	\N	\N	f	\N	\N
2	ashwin.t@fyle.in	Food	\N	\N	txB6D8k0Ws8a	E/2022/06/T/2	C/2022/06/R/3	4	USD	\N	\N	setrunCck8hLH	t	PAYMENT_PROCESSING	\N	\N	\N	rpNeZt3cv9wz	2022-06-27 17:00:00+00	2022-06-27 09:07:16.556+00	2022-06-27 09:05:45.738+00	2022-06-27 09:08:23.340321+00	2022-08-02 20:26:22.82716+00	2022-08-02 20:26:22.827194+00	PERSONAL	\N	{"Card": "", "Killua": "", "Classes": "", "avc_123": null, "New Field": "", "Multi field": "", "Testing This": "", "abc in [123]": null, "Postman Field": "", "Netsuite Class": ""}	f	orPJvXuoLqvJ	{}	\N	\N	\N	f	\N	\N
3	sravan.kumar@fyle.in	Food	\N	Bebe Rexha	txGilVGolf60	E/2022/06/T/1	C/2022/06/R/1	10	USD	\N	\N	setlpIUKpdvsT	t	PAYMENT_PROCESSING	\N	Adidas	\N	rpKuJtEv6h0n	2020-01-01 17:00:00+00	2022-06-08 04:28:30.61+00	2022-06-08 04:27:35.274447+00	2022-06-08 04:28:51.237261+00	2022-08-02 20:26:22.835984+00	2022-08-02 20:26:22.83608+00	PERSONAL	\N	{"Card": "", "Killua": "", "Classes": "", "avc_123": null, "New Field": "", "Multi field": "", "Testing This": "", "abc in [123]": null, "POSTMAN FIELD": "", "Netsuite Class": ""}	f	orPJvXuoLqvJ	{}	\N	1	tg0gTsClGjLp	f	\N	\N
4	sravan.kumar@fyle.in	Food	\N	\N	txjIqTCtkkC8	E/2022/05/T/21	C/2022/05/R/18	100	USD	\N	\N	set3ZMFXrDPL3	f	PAYMENT_PROCESSING	\N	\N	\N	rpLawO11bFib	2022-05-25 17:00:00+00	2022-05-25 08:59:25.649+00	2022-05-25 08:59:07.718891+00	2022-05-25 09:04:05.66983+00	2022-08-02 20:26:22.844927+00	2022-08-02 20:26:22.844961+00	CCC	\N	{"Card": "", "Killua": "", "Classes": "", "avc_123": null, "New Field": "", "Multi field": "", "Testing This": "", "abc in [123]": null, "POSTMAN FIELD": "", "Netsuite Class": ""}	f	orPJvXuoLqvJ	{}	\N	\N	\N	f	\N	\N
5	sravan.kumar@fyle.in	WIP	\N	Bebe Rexha	txUPRc3VwxOP	E/2022/05/T/19	C/2022/05/R/17	101	USD	\N	\N	setb1pSLMIok8	f	PAYMENT_PROCESSING	\N	Adidas	\N	rpv1txzAsgr3	2021-01-01 17:00:00+00	2022-05-25 07:24:12.987+00	2022-05-25 07:21:40.598113+00	2022-05-25 07:25:00.848892+00	2022-08-02 20:26:22.857516+00	2022-08-02 20:26:22.857675+00	CCC	\N	{"Card": "", "Killua": "", "Classes": "", "avc_123": null, "New Field": "", "Multi field": "", "Testing This": "", "abc in [123]": null, "POSTMAN FIELD": "", "Netsuite Class": ""}	f	orPJvXuoLqvJ	{}	\N	\N	\N	f	\N	\N
6	ashwin.t@fyle.in	Food	\N	\N	txUDvDmEV4ep	E/2022/05/T/18	C/2022/05/R/16	5	USD	\N	\N	set33iAVXO7BA	t	PAYMENT_PROCESSING	\N	\N	\N	rpE2JyATZhDe	2020-05-25 17:00:00+00	2022-05-25 06:05:23.362+00	2022-05-25 06:04:46.557927+00	2022-05-25 06:05:47.36985+00	2022-08-02 20:26:22.870854+00	2022-08-02 20:26:22.87089+00	PERSONAL	\N	{"Card": "", "Killua": "", "Classes": "", "avc_123": null, "New Field": "", "Multi field": "", "Testing This": "", "abc in [123]": null, "POSTMAN FIELD": "", "Netsuite Class": ""}	f	orPJvXuoLqvJ	{}	\N	\N	\N	f	\N	\N
7	sravan.kumar@fyle.in	WIP	\N	Bebe Rexha	tx1FW3uxYZG6	E/2022/05/T/16	C/2022/05/R/15	151	USD	\N	\N	setzFn3FK5t80	f	PAYMENT_PROCESSING	\N	Adidas	\N	rprwGgzOZyfR	2022-05-25 17:00:00+00	2022-05-25 03:41:49.042+00	2022-05-25 03:41:28.839711+00	2022-05-25 03:42:10.145663+00	2022-08-02 20:26:22.882803+00	2022-08-02 20:26:22.882836+00	CCC	\N	{"Card": "", "Killua": "", "Classes": "", "avc_123": null, "New Field": "", "Multi field": "", "Testing This": "", "abc in [123]": null, "POSTMAN FIELD": "", "Netsuite Class": ""}	f	orPJvXuoLqvJ	{}	\N	\N	\N	f	\N	\N
8	sravan.kumar@fyle.in	WIP	\N	Bebe Rexha	txVXhyVB8mgK	E/2022/05/T/15	C/2022/05/R/14	45	USD	\N	\N	setsN8cLD9KIn	f	PAYMENT_PROCESSING	\N	Adidas	\N	rpnG3lZYDsHU	2022-05-25 17:00:00+00	2022-05-25 02:48:53.791+00	2022-05-25 02:48:37.432989+00	2022-05-25 02:49:18.189037+00	2022-08-02 20:26:22.894793+00	2022-08-02 20:26:22.894827+00	CCC	\N	{"Card": "", "Killua": "", "Classes": "", "avc_123": null, "New Field": "", "Multi field": "", "Testing This": "", "abc in [123]": null, "POSTMAN FIELD": "", "Netsuite Class": ""}	f	orPJvXuoLqvJ	{}	\N	\N	\N	f	\N	\N
9	sravan.kumar@fyle.in	WIP	\N	Bebe Rexha	txBMQRkBQciI	E/2022/05/T/14	C/2022/05/R/13	10	USD	\N	\N	setanDKqMZfXB	f	PAYMENT_PROCESSING	\N	Adidas	\N	rpVvNQvE2wbm	2022-05-25 17:00:00+00	2022-05-25 02:38:40.858+00	2022-05-25 02:38:25.832419+00	2022-05-25 02:39:08.208877+00	2022-08-02 20:26:22.908632+00	2022-08-02 20:26:22.908661+00	CCC	\N	{"Card": "", "Killua": "", "Classes": "", "avc_123": null, "New Field": "", "Multi field": "", "Testing This": "", "abc in [123]": null, "POSTMAN FIELD": "", "Netsuite Class": ""}	f	orPJvXuoLqvJ	{}	\N	\N	\N	f	\N	\N
10	sravan.kumar@fyle.in	WIP	\N	Bebe Rexha	txkw3dt3umkN	E/2022/05/T/12	C/2022/05/R/12	101	USD	\N	\N	setBe6qAlNXPU	f	PAYMENT_PROCESSING	\N	Adidas	\N	rp5lITpxFLxE	2022-05-24 17:00:00+00	2022-05-24 15:59:13.26+00	2022-05-24 15:55:50.369024+00	2022-05-24 16:00:27.982+00	2022-08-02 20:26:22.921466+00	2022-08-02 20:26:22.9215+00	CCC	\N	{"Card": "", "Killua": "", "Classes": "", "avc_123": null, "New Field": "", "Multi field": "", "Testing This": "", "abc in [123]": null, "POSTMAN FIELD": "", "Netsuite Class": ""}	f	orPJvXuoLqvJ	{}	\N	1	tg0gTsClGjLp	f	\N	\N
\.


--
-- Data for Name: fyle_credentials; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fyle_credentials (id, refresh_token, created_at, updated_at, workspace_id, cluster_domain) FROM stdin;
1	eyJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2NTk0NzE4NzgsImlzcyI6IkZ5bGVBcHAiLCJvcmdfdXNlcl9pZCI6Ilwib3VXRk5QNDlUWHlQXCIiLCJ0cGFfaWQiOiJcInRwYW9Ua2VFYWlGZWdcIiIsInRwYV9uYW1lIjoiXCJGeWxlIFhlcm8gSW50ZWcuLlwiIiwiY2x1c3Rlcl9kb21haW4iOiJcImh0dHBzOi8vc3RhZ2luZy5meWxlLnRlY2hcIiIsImV4cCI6MTk3NDgzMTg3OH0.mOHEigQMVW9MO1SQaKMjIzZ1kD79lYrhGXo_-zSmD04	2022-08-02 20:24:42.685568+00	2022-08-02 20:24:42.68561+00	1	https://staging.fyle.tech
\.


--
-- Data for Name: general_mappings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.general_mappings (id, bank_account_name, bank_account_id, created_at, updated_at, workspace_id, payment_account_id, payment_account_name, default_tax_code_id, default_tax_code_name) FROM stdin;
1	Business Bank Account	562555f2-8cde-4ce9-8203-0363922537a4	2022-08-02 20:27:35.368956+00	2022-08-02 20:27:35.368996+00	1	\N	\N	INPUT	Tax on Purchases @8.25%
\.


--
-- Data for Name: last_export_details; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.last_export_details (id, last_exported_at, export_mode, total_expense_groups_count, successful_expense_groups_count, failed_expense_groups_count, created_at, updated_at, workspace_id) FROM stdin;
\.


--
-- Data for Name: mapping_settings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mapping_settings (id, source_field, destination_field, created_at, updated_at, workspace_id, import_to_fyle, is_custom, source_placeholder, expense_field_id) FROM stdin;
1	CATEGORY	ACCOUNT	2022-08-02 20:25:24.632318+00	2022-08-02 20:25:24.632372+00	1	f	f	\N	\N
2	EMPLOYEE	CONTACT	2022-08-02 20:25:24.647585+00	2022-08-02 20:25:24.647636+00	1	f	f	\N	\N
3	PROJECT	CUSTOMER	2022-08-02 20:25:24.660915+00	2022-08-02 20:25:24.660954+00	1	t	f	\N	\N
4	CORPORATE_CARD	BANK_ACCOUNT	2022-08-02 20:25:24.662017+00	2022-08-02 20:25:24.662053+00	1	f	f	\N	\N
5	TAX_GROUP	TAX_CODE	2022-08-02 20:25:24.67454+00	2022-08-02 20:25:24.674589+00	1	f	f	\N	\N
99	COST_CENTER	DEPARTMENT	2022-08-02 20:25:24.67454+00	2022-08-02 20:25:24.674589+00	1	f	f	\N	\N
\.


--
-- Data for Name: mappings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mappings (id, source_type, destination_type, created_at, updated_at, destination_id, source_id, workspace_id) FROM stdin;
1	PROJECT	CUSTOMER	2022-08-02 20:25:32.063599+00	2022-08-02 20:25:32.06364+00	117	509	1
2	PROJECT	CUSTOMER	2022-08-02 20:25:32.063695+00	2022-08-02 20:25:32.063725+00	119	510	1
3	PROJECT	CUSTOMER	2022-08-02 20:25:32.063777+00	2022-08-02 20:25:32.063806+00	111	511	1
4	PROJECT	CUSTOMER	2022-08-02 20:25:32.063858+00	2022-08-02 20:25:32.063887+00	110	512	1
5	PROJECT	CUSTOMER	2022-08-02 20:25:32.064041+00	2022-08-02 20:25:32.064071+00	113	513	1
6	PROJECT	CUSTOMER	2022-08-02 20:25:32.064123+00	2022-08-02 20:25:32.064152+00	121	514	1
7	PROJECT	CUSTOMER	2022-08-02 20:25:32.064204+00	2022-08-02 20:25:32.064233+00	114	515	1
8	PROJECT	CUSTOMER	2022-08-02 20:25:32.064284+00	2022-08-02 20:25:32.064313+00	108	516	1
9	PROJECT	CUSTOMER	2022-08-02 20:25:32.064365+00	2022-08-02 20:25:32.064394+00	112	517	1
10	PROJECT	CUSTOMER	2022-08-02 20:25:32.064445+00	2022-08-02 20:25:32.064474+00	120	518	1
11	PROJECT	CUSTOMER	2022-08-02 20:25:32.064526+00	2022-08-02 20:25:32.064554+00	116	519	1
12	PROJECT	CUSTOMER	2022-08-02 20:25:32.064606+00	2022-08-02 20:25:32.064634+00	118	520	1
13	PROJECT	CUSTOMER	2022-08-02 20:25:32.064686+00	2022-08-02 20:25:32.064715+00	109	521	1
14	PROJECT	CUSTOMER	2022-08-02 20:25:32.064828+00	2022-08-02 20:25:32.064857+00	115	522	1
15	TAX_GROUP	TAX_CODE	2022-08-02 20:25:32.706774+00	2022-08-02 20:25:32.706814+00	142	2028	1
16	TAX_GROUP	TAX_CODE	2022-08-02 20:25:32.706865+00	2022-08-02 20:25:32.706893+00	143	2048	1
17	TAX_GROUP	TAX_CODE	2022-08-02 20:25:32.706942+00	2022-08-02 20:25:32.706969+00	144	2083	1
18	TAX_GROUP	TAX_CODE	2022-08-02 20:25:32.70713+00	2022-08-02 20:25:32.70717+00	145	2061	1
19	TAX_GROUP	TAX_CODE	2022-08-02 20:25:32.707219+00	2022-08-02 20:25:32.707246+00	146	2031	1
20	TAX_GROUP	TAX_CODE	2022-08-02 20:25:32.707294+00	2022-08-02 20:25:32.707321+00	147	2070	1
21	TAX_GROUP	TAX_CODE	2022-08-02 20:25:32.707382+00	2022-08-02 20:25:32.707527+00	148	2057	1
22	TAX_GROUP	TAX_CODE	2022-08-02 20:25:32.707575+00	2022-08-02 20:25:32.707603+00	149	2060	1
23	EMPLOYEE	CONTACT	2022-08-02 20:25:32.850568+00	2022-08-02 20:25:32.850614+00	106	1	1
24	EMPLOYEE	CONTACT	2022-08-02 20:25:32.850669+00	2022-08-02 20:25:32.850698+00	105	8	1
25	CORPORATE_CARD	BANK_ACCOUNT	2022-08-02 20:25:52.611743+00	2022-08-02 20:25:52.611789+00	2	2026	1
26	CATEGORY	ACCOUNT	2022-08-02 20:25:59.064972+00	2022-08-02 20:25:59.065016+00	7	24	1
27	CATEGORY	ACCOUNT	2022-08-02 20:25:59.065075+00	2022-08-02 20:25:59.065104+00	8	28	1
28	CATEGORY	ACCOUNT	2022-08-02 20:25:59.065158+00	2022-08-02 20:25:59.065187+00	9	25	1
29	CATEGORY	ACCOUNT	2022-08-02 20:25:59.06524+00	2022-08-02 20:25:59.06527+00	10	33	1
30	CATEGORY	ACCOUNT	2022-08-02 20:25:59.065322+00	2022-08-02 20:25:59.065351+00	11	34	1
31	CATEGORY	ACCOUNT	2022-08-02 20:25:59.065403+00	2022-08-02 20:25:59.065432+00	12	35	1
32	CATEGORY	ACCOUNT	2022-08-02 20:25:59.065483+00	2022-08-02 20:25:59.065512+00	13	32	1
33	CATEGORY	ACCOUNT	2022-08-02 20:25:59.065564+00	2022-08-02 20:25:59.065593+00	14	22	1
34	CATEGORY	ACCOUNT	2022-08-02 20:25:59.06575+00	2022-08-02 20:25:59.06578+00	15	36	1
35	CATEGORY	ACCOUNT	2022-08-02 20:25:59.065869+00	2022-08-02 20:25:59.065967+00	16	37	1
36	CATEGORY	ACCOUNT	2022-08-02 20:25:59.066118+00	2022-08-02 20:25:59.066168+00	17	26	1
37	CATEGORY	ACCOUNT	2022-08-02 20:25:59.066221+00	2022-08-02 20:25:59.066249+00	18	23	1
38	CATEGORY	ACCOUNT	2022-08-02 20:25:59.066298+00	2022-08-02 20:25:59.066325+00	19	38	1
39	CATEGORY	ACCOUNT	2022-08-02 20:25:59.066403+00	2022-08-02 20:25:59.066432+00	20	39	1
40	CATEGORY	ACCOUNT	2022-08-02 20:25:59.066485+00	2022-08-02 20:25:59.066514+00	21	40	1
41	CATEGORY	ACCOUNT	2022-08-02 20:25:59.066736+00	2022-08-02 20:25:59.066808+00	22	27	1
42	CATEGORY	ACCOUNT	2022-08-02 20:25:59.066966+00	2022-08-02 20:25:59.067015+00	23	41	1
43	CATEGORY	ACCOUNT	2022-08-02 20:25:59.067228+00	2022-08-02 20:25:59.06765+00	24	29	1
44	CATEGORY	ACCOUNT	2022-08-02 20:25:59.068197+00	2022-08-02 20:25:59.068268+00	25	30	1
45	CATEGORY	ACCOUNT	2022-08-02 20:25:59.06836+00	2022-08-02 20:25:59.06839+00	26	42	1
46	CATEGORY	ACCOUNT	2022-08-02 20:25:59.068444+00	2022-08-02 20:25:59.068472+00	27	43	1
47	CATEGORY	ACCOUNT	2022-08-02 20:25:59.068523+00	2022-08-02 20:25:59.068564+00	28	44	1
48	CATEGORY	ACCOUNT	2022-08-02 20:25:59.068752+00	2022-08-02 20:25:59.06878+00	29	45	1
49	CATEGORY	ACCOUNT	2022-08-02 20:25:59.06883+00	2022-08-02 20:25:59.068857+00	30	46	1
50	CATEGORY	ACCOUNT	2022-08-02 20:25:59.068906+00	2022-08-02 20:25:59.068933+00	31	47	1
51	CATEGORY	ACCOUNT	2022-08-02 20:25:59.068982+00	2022-08-02 20:25:59.069009+00	32	48	1
52	CATEGORY	ACCOUNT	2022-08-02 20:25:59.069059+00	2022-08-02 20:25:59.069085+00	33	49	1
53	CATEGORY	ACCOUNT	2022-08-02 20:25:59.069134+00	2022-08-02 20:25:59.069161+00	34	50	1
54	CATEGORY	ACCOUNT	2022-08-02 20:25:59.06921+00	2022-08-02 20:25:59.069236+00	35	31	1
55	CATEGORY	ACCOUNT	2022-08-02 20:26:05.206966+00	2022-08-02 20:26:05.207015+00	16	59	1
56	CATEGORY	ACCOUNT	2022-08-02 20:26:16.883225+00	2022-08-02 20:26:16.883277+00	16	112	1
\.


--
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payments (id, invoice_id, account_id, created_at, updated_at, expense_group_id, workspace_id, amount) FROM stdin;
\.


--
-- Data for Name: reimbursements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reimbursements (id, settlement_id, reimbursement_id, state, created_at, updated_at, workspace_id) FROM stdin;
\.


--
-- Data for Name: task_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.task_logs (id, type, task_id, status, detail, created_at, updated_at, expense_group_id, workspace_id, bank_transaction_id, bill_id, xero_errors, payment_id) FROM stdin;
1	FETCHING_EXPENSES	\N	COMPLETE	{"message": "Creating expense groups"}	2022-08-02 20:26:21.861637+00	2022-08-02 20:26:22.98676+00	\N	1	\N	\N	\N	\N
10	CREATING_BANK_TRANSACTION	\N	COMPLETE	{"Id": "f0d77b89-f43d-4a12-af5a-62f9fb00ba46", "Status": "OK", "DateTimeUTC": "/Date(1659472096062)/", "ProviderName": "Fyle Staging", "BankTransactions": [{"Date": "/Date(1609459200000+0000)/", "Type": "SPEND", "Total": 101.0, "Status": "AUTHORISED", "Contact": {"Name": "Credit Card Misc", "Phones": [{"PhoneType": "DEFAULT", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "DDI", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "FAX", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "MOBILE", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}], "LastName": "Misc", "Addresses": [{"City": "", "Region": "", "Country": "", "PostalCode": "", "AddressType": "STREET"}, {"City": "", "Region": "", "Country": "", "PostalCode": "", "AddressType": "POBOX"}], "ContactID": "3aaf24ba-6d35-455f-b92a-9e0dc20d3d9a", "FirstName": "Credit", "EmailAddress": "", "ContactGroups": [], "ContactStatus": "ACTIVE", "ContactPersons": [], "UpdatedDateUTC": "/Date(1659470543540+0000)/", "BankAccountDetails": "", "HasValidationErrors": false}, "SubTotal": 93.3, "TotalTax": 7.7, "LineItems": [{"TaxType": "INPUT", "Quantity": 1.0, "Tracking": [], "AccountID": "4281c446-efb4-445d-b32d-c441a4ef5678", "TaxAmount": 7.7, "LineAmount": 93.3, "LineItemID": "d04728ba-27b2-411a-9110-26061ca3342a", "UnitAmount": 93.3, "AccountCode": "429", "Description": "sravan.kumar@fyle.in, category - WIP spent on 2021-01-01, report number - C/2022/05/R/17  - https://staging.fyle.tech/app/admin/#/enterprise/view_expense/txUPRc3VwxOP?org_id=orPJvXuoLqvJ", "ValidationErrors": []}], "Reference": "9 - sravan.kumar@fyle.in", "DateString": "2021-01-01T00:00:00", "BankAccount": {"Code": "090", "Name": "Business Bank Account", "AccountID": "562555f2-8cde-4ce9-8203-0363922537a4"}, "CurrencyCode": "USD", "CurrencyRate": 1.0, "IsReconciled": false, "UpdatedDateUTC": "/Date(1659472096000+0000)/", "LineAmountTypes": "Exclusive", "BankTransactionID": "7311b70a-e270-46e9-a182-84031e99b222"}]}	2022-08-02 20:26:29.158969+00	2022-08-02 20:28:16.111948+00	9	1	5	\N	\N	\N
6	CREATING_BANK_TRANSACTION	\N	COMPLETE	{"Id": "a8d6c40e-8904-49ed-81c2-66effecbadd0", "Status": "OK", "DateTimeUTC": "/Date(1659472079257)/", "ProviderName": "Fyle Staging", "BankTransactions": [{"Date": "/Date(1653436800000+0000)/", "Type": "SPEND", "Total": 10.0, "Status": "AUTHORISED", "Contact": {"Name": "Credit Card Misc", "Phones": [{"PhoneType": "DEFAULT", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "DDI", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "FAX", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "MOBILE", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}], "LastName": "Misc", "Addresses": [{"City": "", "Region": "", "Country": "", "PostalCode": "", "AddressType": "STREET"}, {"City": "", "Region": "", "Country": "", "PostalCode": "", "AddressType": "POBOX"}], "ContactID": "3aaf24ba-6d35-455f-b92a-9e0dc20d3d9a", "FirstName": "Credit", "EmailAddress": "", "ContactGroups": [], "ContactStatus": "ACTIVE", "ContactPersons": [], "UpdatedDateUTC": "/Date(1659470543540+0000)/", "BankAccountDetails": "", "HasValidationErrors": false}, "SubTotal": 9.24, "TotalTax": 0.76, "LineItems": [{"TaxType": "INPUT", "Quantity": 1.0, "Tracking": [], "AccountID": "4281c446-efb4-445d-b32d-c441a4ef5678", "TaxAmount": 0.76, "LineAmount": 9.24, "LineItemID": "c6608618-f41c-4496-8fad-e057433313e9", "UnitAmount": 9.24, "AccountCode": "429", "Description": "sravan.kumar@fyle.in, category - WIP spent on 2022-05-25, report number - C/2022/05/R/13  - https://staging.fyle.tech/app/admin/#/enterprise/view_expense/txBMQRkBQciI?org_id=orPJvXuoLqvJ", "ValidationErrors": []}], "Reference": "10 - sravan.kumar@fyle.in", "DateString": "2022-05-25T00:00:00", "BankAccount": {"Code": "090", "Name": "Business Bank Account", "AccountID": "562555f2-8cde-4ce9-8203-0363922537a4"}, "CurrencyCode": "USD", "CurrencyRate": 1.0, "IsReconciled": false, "UpdatedDateUTC": "/Date(1659472079210+0000)/", "LineAmountTypes": "Exclusive", "BankTransactionID": "a66a279c-f510-4723-a1ef-7fc9488aa3cb"}]}	2022-08-02 20:26:29.106743+00	2022-08-02 20:27:59.393494+00	10	1	1	\N	\N	\N
3	CREATING_BILL	\N	COMPLETE	{"Id": "e13f84ce-dfa5-4a55-84a9-8c357c046ab4", "Status": "OK", "Invoices": [{"Date": "/Date(1659398400000+0000)/", "Type": "ACCPAY", "Total": 10.0, "Status": "AUTHORISED", "Contact": {"Name": "Sravan K", "Phones": [{"PhoneType": "DEFAULT", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "DDI", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "FAX", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "MOBILE", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}], "LastName": "K", "Addresses": [{"City": "", "Region": "", "Country": "", "PostalCode": "", "AddressType": "STREET"}, {"City": "", "Region": "", "Country": "", "PostalCode": "", "AddressType": "POBOX"}], "ContactID": "229b7701-21a2-4539-b39e-5c34f56e1711", "FirstName": "Sravan", "IsCustomer": false, "IsSupplier": true, "EmailAddress": "sravan.kumar@fyle.in", "ContactGroups": [], "ContactStatus": "ACTIVE", "ContactPersons": [], "UpdatedDateUTC": "/Date(1659470532603+0000)/", "BankAccountDetails": "", "HasValidationErrors": false, "SalesTrackingCategories": [], "PurchasesTrackingCategories": []}, "DueDate": "/Date(1660608000000+0000)/", "SubTotal": 9.24, "TotalTax": 0.76, "AmountDue": 10.0, "HasErrors": false, "InvoiceID": "2780aebc-2f8c-4b47-a7e2-64b920c5e7c1", "LineItems": [{"TaxType": "INPUT", "Quantity": 1.0, "Tracking": [], "TaxAmount": 0.76, "LineAmount": 9.24, "LineItemID": "dd9fa5fc-11f7-4113-b67a-e799220811e7", "UnitAmount": 9.24, "AccountCode": "429", "Description": "sravan.kumar@fyle.in, category - Food spent on 2020-01-01, report number - C/2022/06/R/1  - https://staging.fyle.tech/app/admin/#/enterprise/view_expense/txGilVGolf60?org_id=orPJvXuoLqvJ", "ValidationErrors": []}], "Reference": "4 - sravan.kumar@fyle.in", "AmountPaid": 0.0, "DateString": "2022-08-02T00:00:00", "Prepayments": [], "CurrencyCode": "USD", "CurrencyRate": 1.0, "IsDiscounted": false, "Overpayments": [], "DueDateString": "2022-08-16T00:00:00", "InvoiceNumber": "", "SentToContact": false, "UpdatedDateUTC": "/Date(1659472068803+0000)/", "LineAmountTypes": "Exclusive"}], "DateTimeUTC": "/Date(1659472068850)/", "ProviderName": "Fyle Staging"}	2022-08-02 20:26:29.051754+00	2022-08-02 20:27:48.926432+00	4	1	\N	2	\N	\N
2	CREATING_BILL	\N	COMPLETE	{"Id": "7dad1217-3f81-4548-816c-2ca262e3dacf", "Status": "OK", "Invoices": [{"Date": "/Date(1659398400000+0000)/", "Type": "ACCPAY", "Total": 5.0, "Status": "AUTHORISED", "Contact": {"Name": "Joanna", "Phones": [{"PhoneType": "DEFAULT", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "DDI", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "FAX", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "MOBILE", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}], "LastName": "", "Addresses": [{"City": "", "Region": "", "Country": "", "PostalCode": "", "AddressType": "STREET"}, {"City": "", "Region": "", "Country": "", "PostalCode": "", "AddressType": "POBOX"}], "ContactID": "9eecdd86-78bb-47c9-95df-986369748151", "FirstName": "Joanna", "IsCustomer": false, "IsSupplier": true, "EmailAddress": "ashwin.t@fyle.in", "ContactGroups": [], "ContactStatus": "ACTIVE", "ContactPersons": [], "UpdatedDateUTC": "/Date(1659085778640+0000)/", "BankAccountDetails": "", "HasValidationErrors": false, "SalesTrackingCategories": [], "PurchasesTrackingCategories": []}, "DueDate": "/Date(1660608000000+0000)/", "SubTotal": 4.62, "TotalTax": 0.38, "AmountDue": 5.0, "HasErrors": false, "InvoiceID": "c35cf4b3-784a-408b-9ddf-df111dd2e073", "LineItems": [{"TaxType": "INPUT", "Quantity": 1.0, "Tracking": [], "TaxAmount": 0.38, "LineAmount": 4.62, "LineItemID": "51cca2e7-5bef-452c-83fb-2ca8c0865f37", "UnitAmount": 4.62, "AccountCode": "429", "Description": "ashwin.t@fyle.in, category - Food spent on 2020-05-25, report number - C/2022/05/R/16  - https://staging.fyle.tech/app/admin/#/enterprise/view_expense/txUDvDmEV4ep?org_id=orPJvXuoLqvJ", "ValidationErrors": []}], "Reference": "2 - ashwin.t@fyle.in", "AmountPaid": 0.0, "DateString": "2022-08-02T00:00:00", "Prepayments": [], "CurrencyCode": "USD", "CurrencyRate": 1.0, "IsDiscounted": false, "Overpayments": [], "DueDateString": "2022-08-16T00:00:00", "InvoiceNumber": "", "SentToContact": false, "UpdatedDateUTC": "/Date(1659472064663+0000)/", "LineAmountTypes": "Exclusive"}], "DateTimeUTC": "/Date(1659472064725)/", "ProviderName": "Fyle Staging"}	2022-08-02 20:26:29.035108+00	2022-08-02 20:27:44.868535+00	2	1	\N	1	\N	\N
4	CREATING_BILL	\N	COMPLETE	{"Id": "f48d1fe5-8267-4407-8f9f-b9d0ed585863", "Status": "OK", "Invoices": [{"Date": "/Date(1659398400000+0000)/", "Type": "ACCPAY", "Total": 1.0, "Status": "AUTHORISED", "Contact": {"Name": "Joanna", "Phones": [{"PhoneType": "DEFAULT", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "DDI", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "FAX", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "MOBILE", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}], "LastName": "", "Addresses": [{"City": "", "Region": "", "Country": "", "PostalCode": "", "AddressType": "STREET"}, {"City": "", "Region": "", "Country": "", "PostalCode": "", "AddressType": "POBOX"}], "ContactID": "9eecdd86-78bb-47c9-95df-986369748151", "FirstName": "Joanna", "IsCustomer": false, "IsSupplier": true, "EmailAddress": "ashwin.t@fyle.in", "ContactGroups": [], "ContactStatus": "ACTIVE", "ContactPersons": [], "UpdatedDateUTC": "/Date(1659085778640+0000)/", "BankAccountDetails": "", "HasValidationErrors": false, "SalesTrackingCategories": [], "PurchasesTrackingCategories": []}, "DueDate": "/Date(1660608000000+0000)/", "SubTotal": 0.92, "TotalTax": 0.08, "AmountDue": 1.0, "HasErrors": false, "InvoiceID": "c70ce61b-5157-4e11-97c7-6d1f843b2a5f", "LineItems": [{"TaxType": "INPUT", "Quantity": 1.0, "Tracking": [], "TaxAmount": 0.08, "LineAmount": 0.92, "LineItemID": "bd0a73f3-16bf-44fa-ad49-302692bbff14", "UnitAmount": 0.92, "AccountCode": "429", "Description": "ashwin.t@fyle.in, category - Food spent on 2022-06-27, report number - C/2022/06/R/2  - https://staging.fyle.tech/app/admin/#/enterprise/view_expense/txaaVBj3yKGW?org_id=orPJvXuoLqvJ", "ValidationErrors": []}], "Reference": "1 - ashwin.t@fyle.in", "AmountPaid": 0.0, "DateString": "2022-08-02T00:00:00", "Prepayments": [], "CurrencyCode": "USD", "CurrencyRate": 1.0, "IsDiscounted": false, "Overpayments": [], "DueDateString": "2022-08-16T00:00:00", "InvoiceNumber": "", "SentToContact": false, "UpdatedDateUTC": "/Date(1659472071907+0000)/", "LineAmountTypes": "Exclusive"}], "DateTimeUTC": "/Date(1659472071950)/", "ProviderName": "Fyle Staging"}	2022-08-02 20:26:29.065572+00	2022-08-02 20:27:52.013717+00	1	1	\N	3	\N	\N
5	CREATING_BILL	\N	COMPLETE	{"Id": "ae7ddcb0-7988-4c8d-abbd-2cb4368b0a28", "Status": "OK", "Invoices": [{"Date": "/Date(1659398400000+0000)/", "Type": "ACCPAY", "Total": 4.0, "Status": "AUTHORISED", "Contact": {"Name": "Joanna", "Phones": [{"PhoneType": "DEFAULT", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "DDI", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "FAX", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "MOBILE", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}], "LastName": "", "Addresses": [{"City": "", "Region": "", "Country": "", "PostalCode": "", "AddressType": "STREET"}, {"City": "", "Region": "", "Country": "", "PostalCode": "", "AddressType": "POBOX"}], "ContactID": "9eecdd86-78bb-47c9-95df-986369748151", "FirstName": "Joanna", "IsCustomer": false, "IsSupplier": true, "EmailAddress": "ashwin.t@fyle.in", "ContactGroups": [], "ContactStatus": "ACTIVE", "ContactPersons": [], "UpdatedDateUTC": "/Date(1659085778640+0000)/", "BankAccountDetails": "", "HasValidationErrors": false, "SalesTrackingCategories": [], "PurchasesTrackingCategories": []}, "DueDate": "/Date(1660608000000+0000)/", "SubTotal": 3.7, "TotalTax": 0.3, "AmountDue": 4.0, "HasErrors": false, "InvoiceID": "9520557e-c20c-4fa4-b4b4-702102866beb", "LineItems": [{"TaxType": "INPUT", "Quantity": 1.0, "Tracking": [], "TaxAmount": 0.3, "LineAmount": 3.7, "LineItemID": "913aa7a1-fc6f-4156-a263-46a85b7cfbc9", "UnitAmount": 3.7, "AccountCode": "429", "Description": "ashwin.t@fyle.in, category - Food spent on 2022-06-27, report number - C/2022/06/R/3  - https://staging.fyle.tech/app/admin/#/enterprise/view_expense/txB6D8k0Ws8a?org_id=orPJvXuoLqvJ", "ValidationErrors": []}], "Reference": "3 - ashwin.t@fyle.in", "AmountPaid": 0.0, "DateString": "2022-08-02T00:00:00", "Prepayments": [], "CurrencyCode": "USD", "CurrencyRate": 1.0, "IsDiscounted": false, "Overpayments": [], "DueDateString": "2022-08-16T00:00:00", "InvoiceNumber": "", "SentToContact": false, "UpdatedDateUTC": "/Date(1659472075027+0000)/", "LineAmountTypes": "Exclusive"}], "DateTimeUTC": "/Date(1659472075073)/", "ProviderName": "Fyle Staging"}	2022-08-02 20:26:29.084513+00	2022-08-02 20:27:55.122186+00	3	1	\N	4	\N	\N
7	CREATING_BANK_TRANSACTION	\N	COMPLETE	{"Id": "a1776aec-3315-4902-8593-fd03dcb2d650", "Status": "OK", "DateTimeUTC": "/Date(1659472083505)/", "ProviderName": "Fyle Staging", "BankTransactions": [{"Date": "/Date(1653350400000+0000)/", "Type": "SPEND", "Total": 101.0, "Status": "AUTHORISED", "Contact": {"Name": "Credit Card Misc", "Phones": [{"PhoneType": "DEFAULT", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "DDI", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "FAX", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "MOBILE", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}], "LastName": "Misc", "Addresses": [{"City": "", "Region": "", "Country": "", "PostalCode": "", "AddressType": "STREET"}, {"City": "", "Region": "", "Country": "", "PostalCode": "", "AddressType": "POBOX"}], "ContactID": "3aaf24ba-6d35-455f-b92a-9e0dc20d3d9a", "FirstName": "Credit", "EmailAddress": "", "ContactGroups": [], "ContactStatus": "ACTIVE", "ContactPersons": [], "UpdatedDateUTC": "/Date(1659470543540+0000)/", "BankAccountDetails": "", "HasValidationErrors": false}, "SubTotal": 93.3, "TotalTax": 7.7, "LineItems": [{"TaxType": "INPUT", "Quantity": 1.0, "Tracking": [], "AccountID": "4281c446-efb4-445d-b32d-c441a4ef5678", "TaxAmount": 7.7, "LineAmount": 93.3, "LineItemID": "e683b297-e13a-4cd5-9c0e-33eabe20b9b1", "UnitAmount": 93.3, "AccountCode": "429", "Description": "sravan.kumar@fyle.in, category - WIP spent on 2022-05-24, report number - C/2022/05/R/12  - https://staging.fyle.tech/app/admin/#/enterprise/view_expense/txkw3dt3umkN?org_id=orPJvXuoLqvJ", "ValidationErrors": []}], "Reference": "5 - sravan.kumar@fyle.in", "DateString": "2022-05-24T00:00:00", "BankAccount": {"Code": "090", "Name": "Business Bank Account", "AccountID": "562555f2-8cde-4ce9-8203-0363922537a4"}, "CurrencyCode": "USD", "CurrencyRate": 1.0, "IsReconciled": false, "UpdatedDateUTC": "/Date(1659472083343+0000)/", "LineAmountTypes": "Exclusive", "BankTransactionID": "a00e1785-4aac-404c-80a5-f80a1a7f58cc"}]}	2022-08-02 20:26:29.118859+00	2022-08-02 20:28:03.6795+00	5	1	2	\N	\N	\N
8	CREATING_BANK_TRANSACTION	\N	COMPLETE	{"Id": "a7812a09-e912-433f-837a-ddf47b617f48", "Status": "OK", "DateTimeUTC": "/Date(1659472087647)/", "ProviderName": "Fyle Staging", "BankTransactions": [{"Date": "/Date(1653436800000+0000)/", "Type": "SPEND", "Total": 151.0, "Status": "AUTHORISED", "Contact": {"Name": "Credit Card Misc", "Phones": [{"PhoneType": "DEFAULT", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "DDI", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "FAX", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "MOBILE", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}], "LastName": "Misc", "Addresses": [{"City": "", "Region": "", "Country": "", "PostalCode": "", "AddressType": "STREET"}, {"City": "", "Region": "", "Country": "", "PostalCode": "", "AddressType": "POBOX"}], "ContactID": "3aaf24ba-6d35-455f-b92a-9e0dc20d3d9a", "FirstName": "Credit", "EmailAddress": "", "ContactGroups": [], "ContactStatus": "ACTIVE", "ContactPersons": [], "UpdatedDateUTC": "/Date(1659470543540+0000)/", "BankAccountDetails": "", "HasValidationErrors": false}, "SubTotal": 139.49, "TotalTax": 11.51, "LineItems": [{"TaxType": "INPUT", "Quantity": 1.0, "Tracking": [], "AccountID": "4281c446-efb4-445d-b32d-c441a4ef5678", "TaxAmount": 11.51, "LineAmount": 139.49, "LineItemID": "813ee68f-0f2f-4a5d-b50a-cc5da5167bfc", "UnitAmount": 139.49, "AccountCode": "429", "Description": "sravan.kumar@fyle.in, category - WIP spent on 2022-05-25, report number - C/2022/05/R/15  - https://staging.fyle.tech/app/admin/#/enterprise/view_expense/tx1FW3uxYZG6?org_id=orPJvXuoLqvJ", "ValidationErrors": []}], "Reference": "8 - sravan.kumar@fyle.in", "DateString": "2022-05-25T00:00:00", "BankAccount": {"Code": "090", "Name": "Business Bank Account", "AccountID": "562555f2-8cde-4ce9-8203-0363922537a4"}, "CurrencyCode": "USD", "CurrencyRate": 1.0, "IsReconciled": false, "UpdatedDateUTC": "/Date(1659472087600+0000)/", "LineAmountTypes": "Exclusive", "BankTransactionID": "3539faf8-19bf-4737-a218-90705824fa97"}]}	2022-08-02 20:26:29.13365+00	2022-08-02 20:28:07.653419+00	8	1	3	\N	\N	\N
9	CREATING_BANK_TRANSACTION	\N	COMPLETE	{"Id": "a9cdb780-f63e-49d7-838f-b69b7a1581c0", "Status": "OK", "DateTimeUTC": "/Date(1659472091715)/", "ProviderName": "Fyle Staging", "BankTransactions": [{"Date": "/Date(1653436800000+0000)/", "Type": "SPEND", "Total": 100.0, "Status": "AUTHORISED", "Contact": {"Name": "Credit Card Misc", "Phones": [{"PhoneType": "DEFAULT", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "DDI", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "FAX", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "MOBILE", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}], "LastName": "Misc", "Addresses": [{"City": "", "Region": "", "Country": "", "PostalCode": "", "AddressType": "STREET"}, {"City": "", "Region": "", "Country": "", "PostalCode": "", "AddressType": "POBOX"}], "ContactID": "3aaf24ba-6d35-455f-b92a-9e0dc20d3d9a", "FirstName": "Credit", "EmailAddress": "", "ContactGroups": [], "ContactStatus": "ACTIVE", "ContactPersons": [], "UpdatedDateUTC": "/Date(1659470543540+0000)/", "BankAccountDetails": "", "HasValidationErrors": false}, "SubTotal": 92.38, "TotalTax": 7.62, "LineItems": [{"TaxType": "INPUT", "Quantity": 1.0, "Tracking": [], "AccountID": "4281c446-efb4-445d-b32d-c441a4ef5678", "TaxAmount": 7.62, "LineAmount": 92.38, "LineItemID": "1dcc3c7c-02a5-4b26-b913-8f7d4af3a2b5", "UnitAmount": 92.38, "AccountCode": "429", "Description": "sravan.kumar@fyle.in, category - Food spent on 2022-05-25, report number - C/2022/05/R/18  - https://staging.fyle.tech/app/admin/#/enterprise/view_expense/txjIqTCtkkC8?org_id=orPJvXuoLqvJ", "ValidationErrors": []}], "Reference": "6 - sravan.kumar@fyle.in", "DateString": "2022-05-25T00:00:00", "BankAccount": {"Code": "090", "Name": "Business Bank Account", "AccountID": "562555f2-8cde-4ce9-8203-0363922537a4"}, "CurrencyCode": "USD", "CurrencyRate": 1.0, "IsReconciled": false, "UpdatedDateUTC": "/Date(1659472091653+0000)/", "LineAmountTypes": "Exclusive", "BankTransactionID": "bbd472ed-d366-4695-a32b-f170b15eeb1b"}]}	2022-08-02 20:26:29.147051+00	2022-08-02 20:28:11.745001+00	6	1	4	\N	\N	\N
11	CREATING_BANK_TRANSACTION	\N	COMPLETE	{"Id": "a642fbec-2fee-4db7-863a-e0ebe3c4f5f6", "Status": "OK", "DateTimeUTC": "/Date(1659472099992)/", "ProviderName": "Fyle Staging", "BankTransactions": [{"Date": "/Date(1653436800000+0000)/", "Type": "SPEND", "Total": 45.0, "Status": "AUTHORISED", "Contact": {"Name": "Credit Card Misc", "Phones": [{"PhoneType": "DEFAULT", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "DDI", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "FAX", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}, {"PhoneType": "MOBILE", "PhoneNumber": "", "PhoneAreaCode": "", "PhoneCountryCode": ""}], "LastName": "Misc", "Addresses": [{"City": "", "Region": "", "Country": "", "PostalCode": "", "AddressType": "STREET"}, {"City": "", "Region": "", "Country": "", "PostalCode": "", "AddressType": "POBOX"}], "ContactID": "3aaf24ba-6d35-455f-b92a-9e0dc20d3d9a", "FirstName": "Credit", "EmailAddress": "", "ContactGroups": [], "ContactStatus": "ACTIVE", "ContactPersons": [], "UpdatedDateUTC": "/Date(1659470543540+0000)/", "BankAccountDetails": "", "HasValidationErrors": false}, "SubTotal": 41.57, "TotalTax": 3.43, "LineItems": [{"TaxType": "INPUT", "Quantity": 1.0, "Tracking": [], "AccountID": "4281c446-efb4-445d-b32d-c441a4ef5678", "TaxAmount": 3.43, "LineAmount": 41.57, "LineItemID": "b6256803-f91d-458b-88a5-3fc1d860aa62", "UnitAmount": 41.57, "AccountCode": "429", "Description": "sravan.kumar@fyle.in, category - WIP spent on 2022-05-25, report number - C/2022/05/R/14  - https://staging.fyle.tech/app/admin/#/enterprise/view_expense/txVXhyVB8mgK?org_id=orPJvXuoLqvJ", "ValidationErrors": []}], "Reference": "7 - sravan.kumar@fyle.in", "DateString": "2022-05-25T00:00:00", "BankAccount": {"Code": "090", "Name": "Business Bank Account", "AccountID": "562555f2-8cde-4ce9-8203-0363922537a4"}, "CurrencyCode": "USD", "CurrencyRate": 1.0, "IsReconciled": false, "UpdatedDateUTC": "/Date(1659472099960+0000)/", "LineAmountTypes": "Exclusive", "BankTransactionID": "7cad7d4b-b62f-4265-bdbb-b0e40da46df3"}]}	2022-08-02 20:26:29.191141+00	2022-08-02 20:28:20.024241+00	7	1	6	\N	\N	\N
\.


--
-- Data for Name: tenant_mappings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_mappings (id, tenant_name, tenant_id, created_at, updated_at, workspace_id, connection_id) FROM stdin;
1	Demo Company (Global)	36ab1910-11b3-4325-b545-8d1170668ab3	2022-08-02 20:25:03.704706+00	2022-08-02 20:25:03.704749+00	1	\N
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (password, last_login, id, email, user_id, full_name, active, staff, admin) FROM stdin;
	\N	1	ashwin.t@fyle.in	usqywo0f3nBY		t	f	f
\.


--
-- Data for Name: workspace_general_settings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.workspace_general_settings (id, reimbursable_expenses_object, corporate_credit_card_expenses_object, created_at, updated_at, workspace_id, sync_fyle_to_xero_payments, sync_xero_to_fyle_payments, import_categories, auto_map_employees, auto_create_destination_entity, map_merchant_to_contact, skip_cards_mapping, import_tax_codes, charts_of_accounts, import_customers, change_accounting_period, auto_create_merchant_destination_entity, is_simplify_report_closure_enabled, import_suppliers_as_merchants) FROM stdin;
1	PURCHASE BILL	BANK TRANSACTION	2022-08-02 20:25:24.644164+00	2022-08-02 20:25:24.644209+00	1	f	t	t	\N	t	t	f	t	{EXPENSE}	t	t	f	f	f
\.


--
-- Data for Name: workspace_schedules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.workspace_schedules (id, enabled, start_datetime, interval_hours, schedule_id, workspace_id, additional_email_options, emails_selected, error_count) FROM stdin;
\.


--
-- Data for Name: workspaces; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.workspaces (id, name, fyle_org_id, last_synced_at, created_at, updated_at, destination_synced_at, source_synced_at, xero_short_code, xero_accounts_last_synced_at, onboarding_state, app_version, fyle_currency, xero_currency, ccc_last_synced_at) FROM stdin;
1	FAE	orPJvXuoLqvJ	2022-08-02 20:26:22.798354+00	2022-08-02 20:24:42.324252+00	2022-08-02 20:26:22.798769+00	2022-08-02 20:25:10.973908+00	2022-08-02 20:25:11.322694+00	!Xg2Z4	2022-08-02 20:25:32.848125+00	CONNECTION	v1	\N	\N	\N
\.


--
-- Data for Name: workspaces_user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.workspaces_user (id, workspace_id, user_id) FROM stdin;
1	1	1
\.


--
-- Data for Name: xero_credentials; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.xero_credentials (id, refresh_token, created_at, updated_at, workspace_id, country, is_expired) FROM stdin;
1	cf7e4a4343f1c6f96125d1fb9ca84729b295a3520ba2c7a6b5ecda2883412f25	2022-08-02 20:24:56.04499+00	2022-08-02 20:28:18.97994+00	1	CA	f
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 152, true);


--
-- Name: bank_transaction_lineitems_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bank_transaction_lineitems_id_seq', 6, true);


--
-- Name: bank_transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bank_transactions_id_seq', 6, true);


--
-- Name: bill_lineitems_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bill_lineitems_id_seq', 4, true);


--
-- Name: bills_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bills_id_seq', 4, true);


--
-- Name: category_mappings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.category_mappings_id_seq', 1, false);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 1, false);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 38, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 144, true);


--
-- Name: django_q_ormq_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_q_ormq_id_seq', 28, true);


--
-- Name: django_q_schedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_q_schedule_id_seq', 6, true);


--
-- Name: employee_mappings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.employee_mappings_id_seq', 1, false);


--
-- Name: errors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.errors_id_seq', 1, false);


--
-- Name: expense_fields_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.expense_fields_id_seq', 1, false);


--
-- Name: expense_groups_expenses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.expense_groups_expenses_id_seq', 10, true);


--
-- Name: expense_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.expense_groups_id_seq', 10, true);


--
-- Name: expenses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.expenses_id_seq', 10, true);


--
-- Name: fyle_accounting_mappings_destinationattribute_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fyle_accounting_mappings_destinationattribute_id_seq', 149, true);


--
-- Name: fyle_accounting_mappings_expenseattribute_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fyle_accounting_mappings_expenseattribute_id_seq', 2083, true);


--
-- Name: fyle_accounting_mappings_mapping_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fyle_accounting_mappings_mapping_id_seq', 56, true);


--
-- Name: fyle_accounting_mappings_mappingsetting_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fyle_accounting_mappings_mappingsetting_id_seq', 5, true);


--
-- Name: fyle_credentials_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fyle_credentials_id_seq', 1, true);


--
-- Name: fyle_expensegroupsettings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fyle_expensegroupsettings_id_seq', 1, true);


--
-- Name: fyle_rest_auth_authtokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fyle_rest_auth_authtokens_id_seq', 1, true);


--
-- Name: general_mappings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.general_mappings_id_seq', 1, true);


--
-- Name: last_export_details_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.last_export_details_id_seq', 1, false);


--
-- Name: payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payments_id_seq', 1, false);


--
-- Name: reimbursements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reimbursements_id_seq', 1, false);


--
-- Name: task_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.task_log_id_seq', 11, true);


--
-- Name: tenant_mappings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tenant_mappings_id_seq', 1, true);


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_user_id_seq', 1, true);


--
-- Name: workspaces_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.workspaces_id_seq', 1, true);


--
-- Name: workspaces_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.workspaces_user_id_seq', 1, true);


--
-- Name: workspaces_workspacegeneralsettings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.workspaces_workspacegeneralsettings_id_seq', 1, true);


--
-- Name: workspaces_workspaceschedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.workspaces_workspaceschedule_id_seq', 1, false);


--
-- Name: xero_credentials_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.xero_credentials_id_seq', 1, true);


--
-- Name: auth_cache auth_cache_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_cache
    ADD CONSTRAINT auth_cache_pkey PRIMARY KEY (cache_key);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: bank_transaction_lineitems bank_transaction_lineitems_expense_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_transaction_lineitems
    ADD CONSTRAINT bank_transaction_lineitems_expense_id_key UNIQUE (expense_id);


--
-- Name: bank_transaction_lineitems bank_transaction_lineitems_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_transaction_lineitems
    ADD CONSTRAINT bank_transaction_lineitems_pkey PRIMARY KEY (id);


--
-- Name: bank_transactions bank_transactions_expense_group_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_transactions
    ADD CONSTRAINT bank_transactions_expense_group_id_key UNIQUE (expense_group_id);


--
-- Name: bank_transactions bank_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_transactions
    ADD CONSTRAINT bank_transactions_pkey PRIMARY KEY (id);


--
-- Name: bill_lineitems bill_lineitems_expense_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bill_lineitems
    ADD CONSTRAINT bill_lineitems_expense_id_key UNIQUE (expense_id);


--
-- Name: bill_lineitems bill_lineitems_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bill_lineitems
    ADD CONSTRAINT bill_lineitems_pkey PRIMARY KEY (id);


--
-- Name: bills bills_expense_group_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bills
    ADD CONSTRAINT bills_expense_group_id_key UNIQUE (expense_group_id);


--
-- Name: bills bills_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bills
    ADD CONSTRAINT bills_pkey PRIMARY KEY (id);


--
-- Name: category_mappings category_mappings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.category_mappings
    ADD CONSTRAINT category_mappings_pkey PRIMARY KEY (id);


--
-- Name: category_mappings category_mappings_source_category_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.category_mappings
    ADD CONSTRAINT category_mappings_source_category_id_key UNIQUE (source_category_id);


--
-- Name: destination_attributes destination_attributes_destination_id_attribute_d22ab1fe_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.destination_attributes
    ADD CONSTRAINT destination_attributes_destination_id_attribute_d22ab1fe_uniq UNIQUE (destination_id, attribute_type, workspace_id, display_name);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_q_ormq django_q_ormq_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_q_ormq
    ADD CONSTRAINT django_q_ormq_pkey PRIMARY KEY (id);


--
-- Name: django_q_schedule django_q_schedule_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_q_schedule
    ADD CONSTRAINT django_q_schedule_pkey PRIMARY KEY (id);


--
-- Name: django_q_task django_q_task_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_q_task
    ADD CONSTRAINT django_q_task_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: employee_mappings employee_mappings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_mappings
    ADD CONSTRAINT employee_mappings_pkey PRIMARY KEY (id);


--
-- Name: errors errors_expense_attribute_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.errors
    ADD CONSTRAINT errors_expense_attribute_id_key UNIQUE (expense_attribute_id);


--
-- Name: errors errors_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.errors
    ADD CONSTRAINT errors_pkey PRIMARY KEY (id);


--
-- Name: expense_attributes expense_attributes_value_attribute_type_wor_a06aa6b3_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_attributes
    ADD CONSTRAINT expense_attributes_value_attribute_type_wor_a06aa6b3_uniq UNIQUE (value, attribute_type, workspace_id);


--
-- Name: expense_fields expense_fields_attribute_type_workspace_id_22d6ab60_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_fields
    ADD CONSTRAINT expense_fields_attribute_type_workspace_id_22d6ab60_uniq UNIQUE (attribute_type, workspace_id);


--
-- Name: expense_fields expense_fields_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_fields
    ADD CONSTRAINT expense_fields_pkey PRIMARY KEY (id);


--
-- Name: expense_groups_expenses expense_groups_expenses_expensegroup_id_expense__6a42b67c_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_groups_expenses
    ADD CONSTRAINT expense_groups_expenses_expensegroup_id_expense__6a42b67c_uniq UNIQUE (expensegroup_id, expense_id);


--
-- Name: expense_groups_expenses expense_groups_expenses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_groups_expenses
    ADD CONSTRAINT expense_groups_expenses_pkey PRIMARY KEY (id);


--
-- Name: expense_groups expense_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_groups
    ADD CONSTRAINT expense_groups_pkey PRIMARY KEY (id);


--
-- Name: expenses expenses_expense_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_expense_id_key UNIQUE (expense_id);


--
-- Name: expenses expenses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_pkey PRIMARY KEY (id);


--
-- Name: destination_attributes fyle_accounting_mappings_destinationattribute_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.destination_attributes
    ADD CONSTRAINT fyle_accounting_mappings_destinationattribute_pkey PRIMARY KEY (id);


--
-- Name: expense_attributes fyle_accounting_mappings_expenseattribute_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_attributes
    ADD CONSTRAINT fyle_accounting_mappings_expenseattribute_pkey PRIMARY KEY (id);


--
-- Name: mappings fyle_accounting_mappings_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mappings
    ADD CONSTRAINT fyle_accounting_mappings_mapping_pkey PRIMARY KEY (id);


--
-- Name: mapping_settings fyle_accounting_mappings_mappingsetting_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mapping_settings
    ADD CONSTRAINT fyle_accounting_mappings_mappingsetting_pkey PRIMARY KEY (id);


--
-- Name: mappings fyle_accounting_mappings_source_type_source_id_de_e40411c3_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mappings
    ADD CONSTRAINT fyle_accounting_mappings_source_type_source_id_de_e40411c3_uniq UNIQUE (source_type, source_id, destination_type, workspace_id);


--
-- Name: fyle_credentials fyle_credentials_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fyle_credentials
    ADD CONSTRAINT fyle_credentials_pkey PRIMARY KEY (id);


--
-- Name: fyle_credentials fyle_credentials_workspace_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fyle_credentials
    ADD CONSTRAINT fyle_credentials_workspace_id_key UNIQUE (workspace_id);


--
-- Name: expense_group_settings fyle_expensegroupsettings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_group_settings
    ADD CONSTRAINT fyle_expensegroupsettings_pkey PRIMARY KEY (id);


--
-- Name: expense_group_settings fyle_expensegroupsettings_workspace_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_group_settings
    ADD CONSTRAINT fyle_expensegroupsettings_workspace_id_key UNIQUE (workspace_id);


--
-- Name: auth_tokens fyle_rest_auth_authtokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_tokens
    ADD CONSTRAINT fyle_rest_auth_authtokens_pkey PRIMARY KEY (id);


--
-- Name: auth_tokens fyle_rest_auth_authtokens_user_id_3b4bd82e_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_tokens
    ADD CONSTRAINT fyle_rest_auth_authtokens_user_id_3b4bd82e_uniq UNIQUE (user_id);


--
-- Name: general_mappings general_mappings_bank_account_name_workspace_id_cfa7c16d_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.general_mappings
    ADD CONSTRAINT general_mappings_bank_account_name_workspace_id_cfa7c16d_uniq UNIQUE (bank_account_name, workspace_id);


--
-- Name: general_mappings general_mappings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.general_mappings
    ADD CONSTRAINT general_mappings_pkey PRIMARY KEY (id);


--
-- Name: general_mappings general_mappings_workspace_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.general_mappings
    ADD CONSTRAINT general_mappings_workspace_id_key UNIQUE (workspace_id);


--
-- Name: last_export_details last_export_details_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.last_export_details
    ADD CONSTRAINT last_export_details_pkey PRIMARY KEY (id);


--
-- Name: last_export_details last_export_details_workspace_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.last_export_details
    ADD CONSTRAINT last_export_details_workspace_id_key UNIQUE (workspace_id);


--
-- Name: mapping_settings mapping_settings_source_field_destination_cdc65270_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mapping_settings
    ADD CONSTRAINT mapping_settings_source_field_destination_cdc65270_uniq UNIQUE (source_field, destination_field, workspace_id);


--
-- Name: payments payments_expense_group_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_expense_group_id_key UNIQUE (expense_group_id);


--
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- Name: reimbursements reimbursements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reimbursements
    ADD CONSTRAINT reimbursements_pkey PRIMARY KEY (id);


--
-- Name: task_logs task_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_logs
    ADD CONSTRAINT task_log_pkey PRIMARY KEY (id);


--
-- Name: tenant_mappings tenant_mappings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_mappings
    ADD CONSTRAINT tenant_mappings_pkey PRIMARY KEY (id);


--
-- Name: tenant_mappings tenant_mappings_tenant_name_workspace_id_e185ca31_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_mappings
    ADD CONSTRAINT tenant_mappings_tenant_name_workspace_id_e185ca31_uniq UNIQUE (tenant_name, workspace_id);


--
-- Name: tenant_mappings tenant_mappings_workspace_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_mappings
    ADD CONSTRAINT tenant_mappings_workspace_id_key UNIQUE (workspace_id);


--
-- Name: users users_user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_user_pkey PRIMARY KEY (id);


--
-- Name: users users_user_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_user_user_id_key UNIQUE (user_id);


--
-- Name: workspaces workspaces_fyle_org_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspaces
    ADD CONSTRAINT workspaces_fyle_org_id_key UNIQUE (fyle_org_id);


--
-- Name: workspaces workspaces_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspaces
    ADD CONSTRAINT workspaces_pkey PRIMARY KEY (id);


--
-- Name: workspaces_user workspaces_user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspaces_user
    ADD CONSTRAINT workspaces_user_pkey PRIMARY KEY (id);


--
-- Name: workspaces_user workspaces_user_workspace_id_user_id_aee37428_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspaces_user
    ADD CONSTRAINT workspaces_user_workspace_id_user_id_aee37428_uniq UNIQUE (workspace_id, user_id);


--
-- Name: workspace_general_settings workspaces_workspacegeneralsettings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspace_general_settings
    ADD CONSTRAINT workspaces_workspacegeneralsettings_pkey PRIMARY KEY (id);


--
-- Name: workspace_general_settings workspaces_workspacegeneralsettings_workspace_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspace_general_settings
    ADD CONSTRAINT workspaces_workspacegeneralsettings_workspace_id_key UNIQUE (workspace_id);


--
-- Name: workspace_schedules workspaces_workspaceschedule_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspace_schedules
    ADD CONSTRAINT workspaces_workspaceschedule_pkey PRIMARY KEY (id);


--
-- Name: workspace_schedules workspaces_workspaceschedule_schedule_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspace_schedules
    ADD CONSTRAINT workspaces_workspaceschedule_schedule_id_key UNIQUE (schedule_id);


--
-- Name: workspace_schedules workspaces_workspaceschedule_workspace_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspace_schedules
    ADD CONSTRAINT workspaces_workspaceschedule_workspace_id_key UNIQUE (workspace_id);


--
-- Name: xero_credentials xero_credentials_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.xero_credentials
    ADD CONSTRAINT xero_credentials_pkey PRIMARY KEY (id);


--
-- Name: xero_credentials xero_credentials_workspace_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.xero_credentials
    ADD CONSTRAINT xero_credentials_workspace_id_key UNIQUE (workspace_id);


--
-- Name: auth_cache_expires; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_cache_expires ON public.auth_cache USING btree (expires);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);


--
-- Name: bank_transaction_lineitems_bank_transaction_id_7e7debba; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX bank_transaction_lineitems_bank_transaction_id_7e7debba ON public.bank_transaction_lineitems USING btree (bank_transaction_id);


--
-- Name: bill_lineitems_bill_id_8d61e31f; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX bill_lineitems_bill_id_8d61e31f ON public.bill_lineitems USING btree (bill_id);


--
-- Name: category_mappings_destination_account_id_ebc44c1c; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX category_mappings_destination_account_id_ebc44c1c ON public.category_mappings USING btree (destination_account_id);


--
-- Name: category_mappings_destination_expense_head_id_0ed87fbd; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX category_mappings_destination_expense_head_id_0ed87fbd ON public.category_mappings USING btree (destination_expense_head_id);


--
-- Name: category_mappings_workspace_id_222ea301; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX category_mappings_workspace_id_222ea301 ON public.category_mappings USING btree (workspace_id);


--
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);


--
-- Name: django_q_task_id_32882367_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_q_task_id_32882367_like ON public.django_q_task USING btree (id varchar_pattern_ops);


--
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);


--
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: employee_mappings_destination_card_account_id_f030b899; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX employee_mappings_destination_card_account_id_f030b899 ON public.employee_mappings USING btree (destination_card_account_id);


--
-- Name: employee_mappings_destination_employee_id_b6764819; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX employee_mappings_destination_employee_id_b6764819 ON public.employee_mappings USING btree (destination_employee_id);


--
-- Name: employee_mappings_destination_vendor_id_c4bd73df; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX employee_mappings_destination_vendor_id_c4bd73df ON public.employee_mappings USING btree (destination_vendor_id);


--
-- Name: employee_mappings_source_employee_id_dd9948ba; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX employee_mappings_source_employee_id_dd9948ba ON public.employee_mappings USING btree (source_employee_id);


--
-- Name: employee_mappings_workspace_id_4a25f8c9; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX employee_mappings_workspace_id_4a25f8c9 ON public.employee_mappings USING btree (workspace_id);


--
-- Name: errors_expense_group_id_86fafc8b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX errors_expense_group_id_86fafc8b ON public.errors USING btree (expense_group_id);


--
-- Name: errors_workspace_id_a33dd61b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX errors_workspace_id_a33dd61b ON public.errors USING btree (workspace_id);


--
-- Name: expense_fields_workspace_id_b60af18c; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX expense_fields_workspace_id_b60af18c ON public.expense_fields USING btree (workspace_id);


--
-- Name: expense_groups_expenses_expense_id_af963907; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX expense_groups_expenses_expense_id_af963907 ON public.expense_groups_expenses USING btree (expense_id);


--
-- Name: expense_groups_expenses_expensegroup_id_c5b379a2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX expense_groups_expenses_expensegroup_id_c5b379a2 ON public.expense_groups_expenses USING btree (expensegroup_id);


--
-- Name: expense_groups_workspace_id_21fcb4ac; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX expense_groups_workspace_id_21fcb4ac ON public.expense_groups USING btree (workspace_id);


--
-- Name: expenses_expense_id_0e3511ea_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX expenses_expense_id_0e3511ea_like ON public.expenses USING btree (expense_id varchar_pattern_ops);


--
-- Name: fyle_accounting_mappings_d_workspace_id_a6a3ab6a; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fyle_accounting_mappings_d_workspace_id_a6a3ab6a ON public.destination_attributes USING btree (workspace_id);


--
-- Name: fyle_accounting_mappings_expenseattribute_workspace_id_4364b6d7; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fyle_accounting_mappings_expenseattribute_workspace_id_4364b6d7 ON public.expense_attributes USING btree (workspace_id);


--
-- Name: fyle_accounting_mappings_mapping_destination_id_79497f6e; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fyle_accounting_mappings_mapping_destination_id_79497f6e ON public.mappings USING btree (destination_id);


--
-- Name: fyle_accounting_mappings_mapping_source_id_7d692c36; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fyle_accounting_mappings_mapping_source_id_7d692c36 ON public.mappings USING btree (source_id);


--
-- Name: fyle_accounting_mappings_mapping_workspace_id_10d6edd3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fyle_accounting_mappings_mapping_workspace_id_10d6edd3 ON public.mappings USING btree (workspace_id);


--
-- Name: fyle_accounting_mappings_mappingsetting_workspace_id_c123c088; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fyle_accounting_mappings_mappingsetting_workspace_id_c123c088 ON public.mapping_settings USING btree (workspace_id);


--
-- Name: mapping_settings_expense_field_id_e9afc6c2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX mapping_settings_expense_field_id_e9afc6c2 ON public.mapping_settings USING btree (expense_field_id);


--
-- Name: payments_workspace_id_85c585c0; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX payments_workspace_id_85c585c0 ON public.payments USING btree (workspace_id);


--
-- Name: reimbursements_workspace_id_084805e4; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX reimbursements_workspace_id_084805e4 ON public.reimbursements USING btree (workspace_id);


--
-- Name: task_log_bank_transaction_id_eaafbba2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX task_log_bank_transaction_id_eaafbba2 ON public.task_logs USING btree (bank_transaction_id);


--
-- Name: task_log_bill_id_30283abe; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX task_log_bill_id_30283abe ON public.task_logs USING btree (bill_id);


--
-- Name: task_log_expense_group_id_241da11b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX task_log_expense_group_id_241da11b ON public.task_logs USING btree (expense_group_id);


--
-- Name: task_log_workspace_id_7ccc2065; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX task_log_workspace_id_7ccc2065 ON public.task_logs USING btree (workspace_id);


--
-- Name: task_logs_payment_id_7e677dd9; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX task_logs_payment_id_7e677dd9 ON public.task_logs USING btree (payment_id);


--
-- Name: users_user_user_id_4120b7b9_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX users_user_user_id_4120b7b9_like ON public.users USING btree (user_id varchar_pattern_ops);


--
-- Name: workspaces_fyle_org_id_a77e6782_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX workspaces_fyle_org_id_a77e6782_like ON public.workspaces USING btree (fyle_org_id varchar_pattern_ops);


--
-- Name: workspaces_user_user_id_4253baf7; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX workspaces_user_user_id_4253baf7 ON public.workspaces_user USING btree (user_id);


--
-- Name: workspaces_user_workspace_id_be6c5867; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX workspaces_user_workspace_id_be6c5867 ON public.workspaces_user USING btree (workspace_id);


--
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: bank_transaction_lineitems bank_transaction_lin_bank_transaction_id_7e7debba_fk_bank_tran; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_transaction_lineitems
    ADD CONSTRAINT bank_transaction_lin_bank_transaction_id_7e7debba_fk_bank_tran FOREIGN KEY (bank_transaction_id) REFERENCES public.bank_transactions(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: bank_transaction_lineitems bank_transaction_lineitems_expense_id_19112aa7_fk_expenses_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_transaction_lineitems
    ADD CONSTRAINT bank_transaction_lineitems_expense_id_19112aa7_fk_expenses_id FOREIGN KEY (expense_id) REFERENCES public.expenses(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: bank_transactions bank_transactions_expense_group_id_b8ed7247_fk_expense_g; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bank_transactions
    ADD CONSTRAINT bank_transactions_expense_group_id_b8ed7247_fk_expense_g FOREIGN KEY (expense_group_id) REFERENCES public.expense_groups(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: bill_lineitems bill_lineitems_bill_id_8d61e31f_fk_bills_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bill_lineitems
    ADD CONSTRAINT bill_lineitems_bill_id_8d61e31f_fk_bills_id FOREIGN KEY (bill_id) REFERENCES public.bills(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: bill_lineitems bill_lineitems_expense_id_fc7ff7c3_fk_expenses_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bill_lineitems
    ADD CONSTRAINT bill_lineitems_expense_id_fc7ff7c3_fk_expenses_id FOREIGN KEY (expense_id) REFERENCES public.expenses(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: bills bills_expense_group_id_245e4cc1_fk_expense_groups_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bills
    ADD CONSTRAINT bills_expense_group_id_245e4cc1_fk_expense_groups_id FOREIGN KEY (expense_group_id) REFERENCES public.expense_groups(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: category_mappings category_mappings_destination_account__ebc44c1c_fk_destinati; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.category_mappings
    ADD CONSTRAINT category_mappings_destination_account__ebc44c1c_fk_destinati FOREIGN KEY (destination_account_id) REFERENCES public.destination_attributes(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: category_mappings category_mappings_destination_expense__0ed87fbd_fk_destinati; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.category_mappings
    ADD CONSTRAINT category_mappings_destination_expense__0ed87fbd_fk_destinati FOREIGN KEY (destination_expense_head_id) REFERENCES public.destination_attributes(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: category_mappings category_mappings_source_category_id_46f19d95_fk_expense_a; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.category_mappings
    ADD CONSTRAINT category_mappings_source_category_id_46f19d95_fk_expense_a FOREIGN KEY (source_category_id) REFERENCES public.expense_attributes(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: category_mappings category_mappings_workspace_id_222ea301_fk_workspaces_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.category_mappings
    ADD CONSTRAINT category_mappings_workspace_id_222ea301_fk_workspaces_id FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_users_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: employee_mappings employee_mappings_destination_card_acc_f030b899_fk_destinati; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_mappings
    ADD CONSTRAINT employee_mappings_destination_card_acc_f030b899_fk_destinati FOREIGN KEY (destination_card_account_id) REFERENCES public.destination_attributes(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: employee_mappings employee_mappings_destination_employee_b6764819_fk_destinati; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_mappings
    ADD CONSTRAINT employee_mappings_destination_employee_b6764819_fk_destinati FOREIGN KEY (destination_employee_id) REFERENCES public.destination_attributes(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: employee_mappings employee_mappings_destination_vendor_i_c4bd73df_fk_destinati; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_mappings
    ADD CONSTRAINT employee_mappings_destination_vendor_i_c4bd73df_fk_destinati FOREIGN KEY (destination_vendor_id) REFERENCES public.destination_attributes(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: employee_mappings employee_mappings_source_employee_id_dd9948ba_fk_expense_a; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_mappings
    ADD CONSTRAINT employee_mappings_source_employee_id_dd9948ba_fk_expense_a FOREIGN KEY (source_employee_id) REFERENCES public.expense_attributes(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: employee_mappings employee_mappings_workspace_id_4a25f8c9_fk_workspaces_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_mappings
    ADD CONSTRAINT employee_mappings_workspace_id_4a25f8c9_fk_workspaces_id FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: errors errors_expense_attribute_id_23be4f13_fk_expense_attributes_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.errors
    ADD CONSTRAINT errors_expense_attribute_id_23be4f13_fk_expense_attributes_id FOREIGN KEY (expense_attribute_id) REFERENCES public.expense_attributes(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: errors errors_expense_group_id_86fafc8b_fk_expense_groups_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.errors
    ADD CONSTRAINT errors_expense_group_id_86fafc8b_fk_expense_groups_id FOREIGN KEY (expense_group_id) REFERENCES public.expense_groups(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: errors errors_workspace_id_a33dd61b_fk_workspaces_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.errors
    ADD CONSTRAINT errors_workspace_id_a33dd61b_fk_workspaces_id FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: expense_fields expense_fields_workspace_id_b60af18c_fk_workspaces_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_fields
    ADD CONSTRAINT expense_fields_workspace_id_b60af18c_fk_workspaces_id FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: expense_group_settings expense_group_settings_workspace_id_4c110bbe_fk_workspaces_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_group_settings
    ADD CONSTRAINT expense_group_settings_workspace_id_4c110bbe_fk_workspaces_id FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: expense_groups_expenses expense_groups_expen_expensegroup_id_c5b379a2_fk_expense_g; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_groups_expenses
    ADD CONSTRAINT expense_groups_expen_expensegroup_id_c5b379a2_fk_expense_g FOREIGN KEY (expensegroup_id) REFERENCES public.expense_groups(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: expense_groups_expenses expense_groups_expenses_expense_id_af963907_fk_expenses_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_groups_expenses
    ADD CONSTRAINT expense_groups_expenses_expense_id_af963907_fk_expenses_id FOREIGN KEY (expense_id) REFERENCES public.expenses(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: expense_groups expense_groups_workspace_id_21fcb4ac_fk_workspaces_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_groups
    ADD CONSTRAINT expense_groups_workspace_id_21fcb4ac_fk_workspaces_id FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: mappings fyle_accounting_mapp_destination_id_79497f6e_fk_fyle_acco; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mappings
    ADD CONSTRAINT fyle_accounting_mapp_destination_id_79497f6e_fk_fyle_acco FOREIGN KEY (destination_id) REFERENCES public.destination_attributes(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: mappings fyle_accounting_mapp_workspace_id_10d6edd3_fk_workspace; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mappings
    ADD CONSTRAINT fyle_accounting_mapp_workspace_id_10d6edd3_fk_workspace FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: expense_attributes fyle_accounting_mapp_workspace_id_4364b6d7_fk_workspace; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_attributes
    ADD CONSTRAINT fyle_accounting_mapp_workspace_id_4364b6d7_fk_workspace FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: destination_attributes fyle_accounting_mapp_workspace_id_a6a3ab6a_fk_workspace; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.destination_attributes
    ADD CONSTRAINT fyle_accounting_mapp_workspace_id_a6a3ab6a_fk_workspace FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: fyle_credentials fyle_credentials_workspace_id_52f7febf_fk_workspaces_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fyle_credentials
    ADD CONSTRAINT fyle_credentials_workspace_id_52f7febf_fk_workspaces_id FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_tokens fyle_rest_auth_authtokens_user_id_3b4bd82e_fk_users_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_tokens
    ADD CONSTRAINT fyle_rest_auth_authtokens_user_id_3b4bd82e_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: general_mappings general_mappings_workspace_id_19666c5c_fk_workspaces_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.general_mappings
    ADD CONSTRAINT general_mappings_workspace_id_19666c5c_fk_workspaces_id FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: last_export_details last_export_details_workspace_id_0af72f0e_fk_workspaces_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.last_export_details
    ADD CONSTRAINT last_export_details_workspace_id_0af72f0e_fk_workspaces_id FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: mapping_settings mapping_settings_expense_field_id_e9afc6c2_fk_expense_fields_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mapping_settings
    ADD CONSTRAINT mapping_settings_expense_field_id_e9afc6c2_fk_expense_fields_id FOREIGN KEY (expense_field_id) REFERENCES public.expense_fields(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: mapping_settings mapping_settings_workspace_id_590f14f3_fk_workspaces_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mapping_settings
    ADD CONSTRAINT mapping_settings_workspace_id_590f14f3_fk_workspaces_id FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: mappings mappings_source_id_fd4f378f_fk_expense_attributes_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mappings
    ADD CONSTRAINT mappings_source_id_fd4f378f_fk_expense_attributes_id FOREIGN KEY (source_id) REFERENCES public.expense_attributes(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: payments payments_expense_group_id_682a1bb5_fk_expense_groups_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_expense_group_id_682a1bb5_fk_expense_groups_id FOREIGN KEY (expense_group_id) REFERENCES public.expense_groups(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: payments payments_workspace_id_85c585c0_fk_workspaces_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_workspace_id_85c585c0_fk_workspaces_id FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reimbursements reimbursements_workspace_id_084805e4_fk_workspaces_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reimbursements
    ADD CONSTRAINT reimbursements_workspace_id_084805e4_fk_workspaces_id FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: task_logs task_log_bank_transaction_id_eaafbba2_fk_bank_transactions_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_logs
    ADD CONSTRAINT task_log_bank_transaction_id_eaafbba2_fk_bank_transactions_id FOREIGN KEY (bank_transaction_id) REFERENCES public.bank_transactions(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: task_logs task_log_bill_id_30283abe_fk_bills_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_logs
    ADD CONSTRAINT task_log_bill_id_30283abe_fk_bills_id FOREIGN KEY (bill_id) REFERENCES public.bills(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: task_logs task_log_expense_group_id_241da11b_fk_expense_groups_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_logs
    ADD CONSTRAINT task_log_expense_group_id_241da11b_fk_expense_groups_id FOREIGN KEY (expense_group_id) REFERENCES public.expense_groups(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: task_logs task_log_workspace_id_7ccc2065_fk_workspaces_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_logs
    ADD CONSTRAINT task_log_workspace_id_7ccc2065_fk_workspaces_id FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: task_logs task_logs_payment_id_7e677dd9_fk_payments_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_logs
    ADD CONSTRAINT task_logs_payment_id_7e677dd9_fk_payments_id FOREIGN KEY (payment_id) REFERENCES public.payments(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: tenant_mappings tenant_mappings_workspace_id_89603b44_fk_workspaces_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_mappings
    ADD CONSTRAINT tenant_mappings_workspace_id_89603b44_fk_workspaces_id FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: workspace_general_settings workspace_general_se_workspace_id_a218afd8_fk_workspace; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspace_general_settings
    ADD CONSTRAINT workspace_general_se_workspace_id_a218afd8_fk_workspace FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: workspace_schedules workspace_schedules_workspace_id_50ec990f_fk_workspaces_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspace_schedules
    ADD CONSTRAINT workspace_schedules_workspace_id_50ec990f_fk_workspaces_id FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: workspaces_user workspaces_user_user_id_4253baf7_fk_users_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspaces_user
    ADD CONSTRAINT workspaces_user_user_id_4253baf7_fk_users_user_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: workspaces_user workspaces_user_workspace_id_be6c5867_fk_workspaces_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspaces_user
    ADD CONSTRAINT workspaces_user_workspace_id_be6c5867_fk_workspaces_id FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: workspace_schedules workspaces_workspace_schedule_id_8274d659_fk_django_q_; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workspace_schedules
    ADD CONSTRAINT workspaces_workspace_schedule_id_8274d659_fk_django_q_ FOREIGN KEY (schedule_id) REFERENCES public.django_q_schedule(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: xero_credentials xero_credentials_workspace_id_84f484db_fk_workspaces_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.xero_credentials
    ADD CONSTRAINT xero_credentials_workspace_id_84f484db_fk_workspaces_id FOREIGN KEY (workspace_id) REFERENCES public.workspaces(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

