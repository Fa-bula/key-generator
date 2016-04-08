drop table given_keys;
create table given_keys(
  val text primary key not null check(length(val) = 4),
  is_repaid integer not null check(is_repaid in (0,1)) -- 0 - еще не погашен, 1 - погашен
);
