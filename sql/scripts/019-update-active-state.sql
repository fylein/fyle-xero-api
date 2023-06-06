rollback;

begin;

update destination_attributes set active = true where active is null;