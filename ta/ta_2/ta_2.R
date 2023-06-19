# ================= Ayundatía 2 ================================#

rm(list=ls()) # Limpiar espacio de trabajo
options(scipen=9999) # desactivar notacion cientifica



if (!require("pacman")) install.packages("pacman") # Pacman para correr paquetes
pacman::p_load(car,
               dplyr,
               sjlabelled,
               tidyverse,
               ggplot2)


#Paquetes (En caso de no usar Pacman)
#library(dplyr)
#library(tidyverse) 
#library(car)
#library(ggplot2)

##  ===========Packages ===================== #
#p <- c("tidyverse","modelr")
#install.packages(p) # instala paquete



#Ruta dónde trabajaremos
setwd("C:/Users/froli/Dropbox/Observatorio/BASE DE DATOS OCS/BASE 2009-2019") 


#base de datos
#load("acciones_de_protesta_2009_2019_v.01.Rdata") # Base de datos descargada directamente desde internet
# Utilizamos repositorio de Dataverse Harvard
load(url("https://dataverse.harvard.edu/api/access/datafile/4880232"))



#cargar directo desde el computador con librería 
#install.packages("readxl") # para el caso de archivos "csv" utilizar librería "readr"
library (readxl)
data1 <- read_excel("base_OCS.xlsx")



# Estructura de la base de datos
str(acciones_de_protesta_2009_2019)



# Filtro de variables que vamos a utilizar
data <- acciones_de_protesta_2009_2019 %>% 
  select(pb,p5a, p5b, p5c, p6, p10, p11, p21, p25, p27, p29a, p29b, p29c, p29d, p29e, p29f)



## arrange: ordenación de datos
data %>% arrange(p5c) # se ordenan según la variable año para este caso



#Eliminamos la base original que ya no usamos
rm(acciones_de_protesta_2009_2019)



# pipes
data %>%
  select(p5c, p6, p21, p29a, p29b, p29c, p29d, p29e, p29f) %>% # selección de variables
  arrange(p5c) %>% #orden de variables    
  filter(p21== 1 &  p6== 9) # filtro o condición que estoy colocando

# esto también puede crear un subset de base de datos si así lo queremos.


# =========================================== Recodificación de variables =====================#


#visualizamos la variable 

table(data$p21)
table(data$p25)
table(data$p27)

data %>% select(p21,p25,p27) %>%
  mutate(p21_2 = if_else(p21==1,1,0), p25 = if_else(p25==1,1,0), p27_2= if_else(p27==1,1,0)) %>%  # creamos variable dicotómica "0" y "1"
  select(p21_2) %>% 
  with(table(p21_2))



#otra opción
data %>% select(p25) %>% 
  mutate(p25 = if_else(p25==1,p25,0)) %>% 
  select(p25) %>% 
  with(table(p25))

# Variables de texto
data$nacional <- ifelse(data$p10 == 'NACIONAL', 1, 0) #variable de texto

## mutate, case_when: creación de datos (empieza con todo NA y después substituye por pedazos)

#Protesta pacífica
data <- data %>%
  mutate( pacifica = case_when( 
    p29a >=1 & p29a <= 17 ~ "1",
    p29b >=1 & p29b <= 17  ~ "1", 
    p29c >=1 & p29c <= 17  ~ "1",
    p29d >=1 & p29d <= 17  ~ "1",
    p29e >=1 & p29e <= 17  ~ "1",
    p29f >=1 & p29f <=17 ~ "1",
    TRUE ~ "0"))

#etiqueta
data$pacifica <- factor(data$pacifica,labels = c('No', 'Sí'))
data$pacifica <- set_label(data$pacifica,label = "Táctica - Pacífica")

# macrozonas
data <- data %>% mutate( macrozona = case_when(p6 %in% c(15, 1:4) ~ "Norte",
                                               p6 %in% c(5:7, 16) ~ "Centro",
                                               p6 %in% c(13) ~ "RM",
                                               p6 %in% c(8:12, 14) ~ "Sur"))
data$macrozona <- set_label(data$macrozona,label = "Macrozonas")


### ====================== group_by: operaciones agrupadas. ==============================#

#Cantidad de protestas por año

data$ano <- factor(data$p5c,labels = c('2009', '2010', '2011','2012','2013','2014','2015','2016','2017','2018','2019'))
data$ano <- set_label(data$ano,label = "Años")

g1 <- data %>%
  group_by(ano) %>% # agrupamos por año
  summarise(freq = n()) # frecuencias de cada año


#Graficamos las frecuencias
ggplot(g1, aes(x = ano, y = freq)) + 
  geom_col(fill="darkgreen", alpha=0.5,width = 0.3) + # Gráfico de barra
  geom_text(aes(label = freq ), vjust = -0.3, size= 2.75) + # leyendas de cada gráfíco
  theme_bw() +  # Fondo blanco
  labs(x="Años", # eje X
       y="Frecuencia", # eje Y
       title = "Gráfico 1: Frecuencia por base años OCS")+
  coord_cartesian(ylim=c(0,5000)) # Rango del eje


# Porcentajes de la variable año
g2 <- g1 %>% arrange(desc(ano)) %>% # utilizamos los datos procesados en las frecuencias
  mutate(prop = round(freq/sum(freq),3)) # también puede ser mutate(prop = prop.table(prop))


#Gráficos los porcentajes
ggplot(g2, aes(x = ano, y = prop, label = scales::percent(prop, accuracy = .1))) + 
  geom_col(fill="darkgreen", alpha=0.5,width = 0.3) + 
  geom_text(position = position_dodge(width = .9),    
            vjust = -0.5,    
            size = 3) + 
  scale_y_continuous(labels = scales::percent) +  
  labs(x="Años", 
       y="Porcentaje",
       title = "Gráfico 2 : Porcentaje por años base OCS") +  
  theme_bw() + 
  coord_cartesian(ylim=c(0,0.3))


# Porcentajes de la variable region
data$region <- factor(data$p6,labels = c('Tarapacá', 'Antofagasta', 'Atacama','Coquimbo','Valparaíso','O´Higgins','Maule','Biobío','Araucanía','Los Lagos','Aysén','Magallanes','Metropolitana','Los Ríos','Arica y Parinacota','Ñuble'))
data$region <- set_label(data$region,label = "Regiones")


g3 <- data %>% group_by(macrozona) %>% # utilizando la misma fórmula de frecuencia y porcentaje a la vez
  summarise(freq = n()) %>% 
  arrange(desc(macrozona)) %>% 
  mutate(prop = round(freq/sum(freq),3)) 

# gráfico básico
ggplot(g3, aes(x = macrozona, y = prop, fill=macrozona, group=1, label = scales::percent(prop, accuracy = .1))) +    
  geom_col()+
  geom_text()+
  scale_y_continuous(labels = scales::percent)  +
  labs(x="Regiones", 
       y="Porcentaje",
       title = "Gráfico 2 : Porcentaje por regiones OCS",
       subtitle= "Acciones contenciosas por región (%)") +
  guides(fill = guide_legend(title = "Regiones")) + # nombres y colores de regiones en la leyenda 
  theme_bw()+
  coord_cartesian(ylim=c(0,0.5)) # escala de valores del eje "y"


# gráfico con algunas cosas más
ggplot(g3, aes(x = macrozona, y = prop, fill=macrozona, group=1, label = scales::percent(prop, accuracy = .1))) +    
  geom_col(aes(fill=macrozona),alpha=0.1,width = 0.2)+
  geom_text(position = position_dodge(width = .9),    
            vjust = -0.5,    
            size = 3) + 
  scale_y_continuous(labels = scales::percent)  +
  labs(x="Regiones", 
       y="Porcentaje",
       title = "Gráfico 2 : Porcentaje por regiones OCS",
       subtitle= "Acciones contenciosas por región (%)") +
  labs(fill = "Regiones") + # nombres y colores de regiones en la leyenda 
  theme_bw()+
  coord_cartesian(ylim=c(0,0.5)) # escala de valores del eje "y"





#=========================== Otras herramientas útiles ======================== #

#Cantidad de valores distintos
data %>% 
  summarise(distintos=n_distinct(p6)) # ver cantidad de casos distintos (parecido al comendo "unique")

sum(data$p5c, na.rm = TRUE)   # suma/ sacar NA para poder realizar las operaciones
class(data$p11) #tipo de variable
mean(data$p11, na.rm = TRUE)   # promedio
sd(data$p11, na.rm=TRUE)     # desviación estándar
max(data$p11,na.rm = TRUE)    # máximo
which.max(data$p11) # posición de valor máximo  / fila del valor máximo
min(data$p11)    # mínimo
which.min(data$p11) # posición de valor mínimo 
median(data$p11) # mediana
range(data$p11, na.rm = TRUE)  # rango
unique(data$p5c) # lista de elementos únicos para esta variable
