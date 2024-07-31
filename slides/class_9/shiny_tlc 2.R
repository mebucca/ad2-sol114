library(shiny)
library(ggplot2)

ui <- fluidPage(
  titlePanel("Visualización del Teorema del Límite Central"),
  
  sidebarLayout(
    sidebarPanel(
      sliderInput("sample_size", "Tamaño de la Muestra:", min = 1, max = 1000, value = 1)
    ),
    
    mainPanel(
      textOutput("description_text"),
      HTML("<br><br>"),  # Add vertical space
      plotOutput("clt_plot"),
      verbatimTextOutput("sample_statistics"),
      htmlOutput("explanation")
    )
  )
)

server <- function(input, output, session) {
  
  output$description_text <- renderText({
    return("La distribución subyacente es Uniforme(1, 100). Observa cómo la distribución de las medias muestrales se vuelve más en forma de campana (normal) a medida que aumenta el tamaño de la muestra, ilustrando el Teorema del Límite Central.")
  })
  
  output$clt_plot <- renderPlot({
    # Generar población usando distribución uniforme
    population <- runif(1e5, min = 1, max = 100)
    
    # Extraer múltiples muestras de la población y calcular sus medias
    sample_means <- replicate(1000, mean(sample(population, size = input$sample_size)))
    
    # Data frame para la gráfica
    data_to_plot <- data.frame(means = sample_means)
    
    # Generar gráfico
    ggplot(data_to_plot, aes(x = means)) +
      geom_histogram(fill = "#336699", color = "#225522", bins = 30, alpha = 0.7) +
      geom_vline(aes(xintercept = mean(population)), linetype = "dashed", color = "#B26666") +
      labs(title = "Distribución de Muestreo de las Medias Muestrales",
           subtitle = paste("Tamaño de Muestra:", input$sample_size),
           x = "Media Muestral",
           y = "Frecuencia") +
      theme_minimal() +
      theme(
        plot.title = element_text(face = "bold", size = 20),
        panel.border = element_rect(color = "black", fill = NA, linewidth = 1)
      )
  })
  
  output$sample_statistics <- renderText({
    # Utilizando las propiedades de la distribución uniforme para calcular la media y la varianza
    actual_mean <- (1 + 100) / 2
    actual_variance <- ((100 - 1)^2) / 12
    
    # Error Estándar
    standard_error <- sqrt(actual_variance / input$sample_size)
    
    paste("Media de las Medias Muestrales: ", round(actual_mean, 2),
          "\nError Estándar: ", round(standard_error, 2))
  })
  
  output$explanation <- renderUI({
    HTML("<strong>Explicación:</strong> 
         <p>El Teorema del Límite Central establece que la distribución de la suma (o promedio) de una gran cantidad de variables aleatorias independientes e idénticamente distribuidas se acercará a una distribución normal, independientemente de la forma de la distribución original.</p>")
  })
}

shinyApp(ui, server)
