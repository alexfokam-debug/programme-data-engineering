/* @datacloud.settings
{
  "version": 1,
  "service": "BIG_QUERY",
  "connectionInfo": {
    "billingProjectId": "INHERIT",
    "location": "INHERIT"
  },
  "dialect": "GOOGLE_SQL"
}
*/

-- Recette 3.2  - Combining Related Rows
-- Objectif :
-- Combiner des clients et leurs commandes grâce à customer_id.

-- Cardinalité attendue :
-- - un client peut avoir plusieurs commandes
-- - une commande appartient à un seul client
-- - avec INNER JOIN, seuls les clients yant au moins une commande apparaissent.

with  customers as (
    select *
    from unnest([
        struct(1 as customer_id, 'Alice' as customer_name),
        struct(2 as customer_id, 'Bob' as customer_name),
        struct(3 as customer_id, 'Charlie' as customer_name),
        struct(4 as customer_id, 'David' as customer_name),
        struct(5 as customer_id, 'Eve' as customer_name)
    ])
),
orders as (
    select *
    from unnest([
        struct(101 as order_id, 1 as customer_id, 120.0 as order_total),
        struct(102 as order_id, 2 as customer_id, 150.0 as order_total),
        struct(103 as order_id, 1 as customer_id, 200.0 as order_total),
        struct(104 as order_id, 3 as customer_id, 50.0 as order_total),
        struct(105 as order_id, 4 as customer_id, 300.0 as order_total),
        struct(106 as order_id, 999 as customer_id, 75.0 as order_total)
    ])
)

select 
c.customer_id,
c.customer_name,
count (*) as nomber_of_orders,
from customers c
inner join orders o
on c.customer_id = o.customer_id
group by
c.customer_id,
c.customer_name
order by
c.customer_id asc;
/*
select count(*) as joined_row_count
from customers c
inner join orders o
on c.customer_id = o.customer_id*/

/*
select 
    c.customer_id,
    c.customer_name,
    o.order_id,
    o.order_total
from
    customers c
inner join
    orders o
on
    c.customer_id = o.customer_id
order by
    c.customer_id asc,
    o.order_id asc */