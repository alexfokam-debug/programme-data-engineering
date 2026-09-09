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

select 
    *
from 
    unnest([
        struct(101 as order_id, 'Alice' as customer, 120.0 as order_total),
        struct(102 as orider_id, 'Bob' as customer, NULL as order_total),
        struct(103 as order_id, 'Charlie' as customer, 150.0 as order_total),
        struct(104 as order_id, 'David' as customer, 200.0 as order_total),
        struct(105 as order_id, 'Eve' as customer, 50.0 as order_total),
        struct(106 as order_id, 'Frank' as customer, 120.0 as order_total),
        struct(107 as order_id, 'Grace' as customer, NULL as order_total),
        struct(108 as order_id, 'Heidi' as customer, 250.0 as order_total),
        struct(109 as order_id, 'Ivan' as customer, NULL as order_total),
        struct(110 as order_id, 'Judy' as customer, 180.0 as order_total)
    ])

order by order_total asc