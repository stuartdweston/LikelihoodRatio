create table first.first_01_pairs
as (select * from atlas_dr3.cdfs_radio_pairs);

truncate table first.first_01_pairs;

set global max_execution_time=0;
set global connect_timeout=86400;
set global wait_timeout=86400;
set global interactive_timeout=86400;


insert into first.first_01_pairs(cid1,cid2,ang_sep_arcsec)
         select t1.id, t2.id,
         format(sqrt(pow((t1.RA-t2.RA)*cos(radians(t1.Decl)),2)+pow(t1.Decl-t2.Decl,2))*3600,6)
         from first.first_01 as t1, first.first_01 as t2
         where pow((t1.RA-t2.RA)*cos(radians(t1.Decl)),2)+pow(t1.Decl-t2.Decl,2) <= pow(400/3600,2)
         and t1.id!=t2.id;
