-- =========================
-- REQUÊTE INITIALE
-- =========================

SELECT
  *
FROM
  `bigquery-public-data.stackoverflow.posts_questions` quest
JOIN
  `bigquery-public-data.stackoverflow.users` users
  ON quest.id = users.id
WHERE
  EXTRACT(YEAR FROM quest.creation_date) > 2018
LIMIT 100;


-- =========================
-- MESURES INITIALES
-- =========================

-- Version : Initiale
-- Colonnes : SELECT *
-- Période : depuis 2019
-- Octets traités :
-- Durée :
-- Slot ms :
-- Lignes : 100


-- =========================
-- REQUÊTE OPTIMISÉE
-- =========================



-- =========================
-- MESURES FINALES
-- =========================

-- Version : Optimisée
-- Colonnes :
-- Période :
-- Octets traités :
-- Durée :
-- Slot ms :
-- Lignes :


-- =========================
-- VUE MATÉRIALISÉE ET CONCLUSIONS
-- =========================