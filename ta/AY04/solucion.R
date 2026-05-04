set.seed(42)

p     <- 0.3
mu    <- p
sigma <- sqrt(p * (1 - p))

cat("Parámetros teóricos de cada penal (distribución Bernoulli):\n")
cat("  Media:                 μ = p =", mu, "\n")
cat("  Desviación estándar:   σ =", round(sigma, 4), "\n\n")


tira_penales <- function(n) {
  resultados <- rbinom(n, size = 1, prob = p)
  cat("Se tiraron", n, "penal(es):", resultados, "\n")
  return(resultados)
}

tira_penales(1)

penales <- c()

for (x in 1:7){
  penales <- c(penales, mean(tira_penales(5)))
  
}

cat("Promedio de nuestros penales:", mean(penales), "y su desviación estándar", sd(penales))


#Segunda solución:
set.seed(42)
tira_penales(1) #Hay que volver a tirar el único penal para tener constancia en los resultados.

penales <- replicate(7, mean(tira_penales(5)))

cat("Promedio de nuestros penales:", mean(penales), "y su desviación estándar", sd(penales))
#Podemos observar que la media y la varianza que obtuvimos se desvia de la real
#debido a que la cantidad de muestras bajas que se realizaron. Si es que se aumentará
#el número de muestras, entonces convergeria más hacia sus valores reales.