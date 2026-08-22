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

WITH orders AS (

  SELECT STRUCT(
    '2341D' AS order_id,
    5 AS quantity,
    10.99 AS unit_price
  ) AS order_row

  UNION ALL

  SELECT STRUCT(
    '2341E' AS order_id,
    3 AS quantity,
    15.99 AS unit_price
  ) AS order_row

  UNION ALL

  SELECT STRUCT(
    '2341F' AS order_id,
    NULL AS quantity,
    20.99 AS unit_price
  ) AS order_row

),

projected_orders AS (
  SELECT
    o.order_row.order_id,
    o.order_row.quantity,
    o.order_row.unit_price,
    coalesce(o.order_row.quantity, 0)* o.order_row.unit_price AS total_price
  FROM orders AS o
)

SELECT
  *
FROM projected_orders AS o
where o.total_price >= 100

