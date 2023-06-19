library("tidyverse")
library("wesanderson")
library("cowplot")
library("lubridate")
library("viridis")

setwd(
  "~/Library/Mobile Documents/com~apple~CloudDocs/Teaching/ISUC/2020_2_data_analysis_r/repo/slides/class_12/")

# leer archivo csv
covid_data <- read_delim("covid_data.csv", delim=";")
covid_data <- covid_data %>% filter(date==as.Date("2020-11-17")) 
covid_data  %>% glimpse()



# Scatterplot

#jitter <- position_jitter(width = 10, height = 1)

covid_data %>% ggplot(aes(y=total_deaths_per_million, 
                          x=hospital_beds_per_thousand)) +
  geom_point(alpha=0.3) +
  scale_x_log10() + scale_y_log10() +
  geom_smooth(method = "lm", se=F)


# Scatterplot por grupos

covid_data %>% ggplot(aes(y=total_deaths_per_million, 
                          x=hospital_beds_per_thousand, 
                          group=continent,
                          colour=continent
                          )) +
  geom_point(alpha=0.3) +
  scale_x_log10() + scale_y_log10() +
  geom_smooth(method = "lm", se=F) +
  labs(x="Camas de hospital por mil hbs.", y="muertes totales por millón hbs.") +
  facet_wrap(continent ~ .) +
  theme_bw() +
  theme(legend.position = "bottom") 


# Density

p <- covid_data %>% ggplot(aes(y=total_deaths_per_million, x=gdp_per_capita)) +
  scale_x_log10() + scale_y_log10() +
  geom_density_2d_filled() +
  labs(title="Grafico de densidad",  x="GDP per cápita", y="muertes totales por millón hbs.") 
  
ggsave("miprimerggplot.pdf", p, width = 20, height = 20, units = "cm")
