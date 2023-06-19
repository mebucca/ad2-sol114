library("tidyverse")
library("lubridate")
library("knitr")

calendar <- tibble(fecha = c(seq(ymd('2021-08-16'),ymd('2021-12-06'), by = '1 week'), ymd('2021-12-19')) ) |>
            mutate(dia=day(fecha), mes=month(fecha))


# contenidos

calendar <- calendar |> mutate(contenido = 
                                 case_when(
                                   dia==16 & mes==8   ~ "Basics teoría de la Probabilidad",
                                   dia==23 & mes==8   ~ "Probabilidad Condicional",
                                   dia==30 & mes==8   ~ "Variables Aleatorias y Distribuciones Discretas",
                                   dia==6  & mes==9   ~ "E(X), Var(X) y MLE",
                                   dia==13 & mes==9   ~ "Tablas de contingencia: estructura probabilística",
                                   dia==20 & mes==9   ~ "Tablas de contingencia: medidas de independencia y asociación",
                                   dia==27 & mes==9   ~ "Modelo Lineal de Probabilidad (OLS)",
                                   dia==4  & mes==10  ~ "Clase práctica: parametrización de modelos de regresión",
                                   dia==11 & mes==10  ~ "Modelos Lineales Generalizados",
                                   dia==18 & mes==10  ~ "Regresión Logística: estructura teórica y estimación via MLE",
                                   dia==25 & mes==10  ~ "No hay clases",
                                   dia==1  & mes==11  ~ "Regresión Logística: interpretación de efectos",
                                   dia==8  & mes==11  ~ "Regresión Logística: inferencia",
                                   dia==15 & mes==11  ~ "Regresión Logística: ajuste y predicción",
                                   dia==22 & mes==11  ~ "Regresión Logística Multinomial",
                                   dia==29 & mes==11  ~ "Regresión Logística Ordenada",
                                   dia==6  & mes==12  ~ "Consideraciones finales",
                                   dia==19 & mes==12  ~ ""
                                 )
                               )


# Evaluaciones

calendar <- calendar |> mutate(entregas = 
                                 case_when(
                                   dia==16 & mes==8   ~ "",
                                   dia==23 & mes==8   ~ "Tarea corta 1",
                                   dia==30 & mes==8   ~ "Tarea corta 2",
                                   dia==6  & mes==9   ~ "",
                                   dia==13 & mes==9   ~ "Tarea corta 3",
                                   dia==20 & mes==9   ~ "",
                                   dia==27 & mes==9   ~ "Tarea corta 4",
                                   dia==4  & mes==10  ~ "",
                                   dia==11 & mes==10  ~ "",
                                   dia==18 & mes==10  ~ "",
                                   dia==25 & mes==10  ~ "",
                                   dia==1  & mes==11  ~ "",
                                   dia==8  & mes==11  ~ "Trabajo 1",
                                   dia==15 & mes==11  ~ "Tarea corta 5",
                                   dia==22 & mes==11  ~ "",
                                   dia==29 & mes==11  ~ "",
                                   dia==6  & mes==12  ~ "Trabajo 2",
                                   dia==19 & mes==12  ~ "Trabajo final"
                                 )
)

# Ayudantias
calendar <- calendar |> mutate(ayudantias = "")

kable(calendar |> select(-fecha))