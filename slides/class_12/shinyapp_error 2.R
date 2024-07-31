library(shiny)
library(ggplot2)
library(dplyr)

# Define colors
primary_color <- "#336699"
secondary_color <- "#B26666"

ui <- fluidPage(
  titlePanel("Error en Estimación"),
  
  sidebarLayout(
    sidebarPanel(
      wellPanel(
        numericInput("error_level", "Nivel de Error (e):", value = 0.5, min = 0.01, max = 3, step = 0.01),
        helpText("El nivel de error 'e' define la distancia máxima permitida entre el estimado y el parámetro poblacional.")
      ),
      wellPanel(
        numericInput("sample_size", "Tamaño de la Muestra (n):", value = 100, min = 1, max = 1000, step = 1),
        helpText("El tamaño de la muestra 'n' determina cuántos datos se están utilizando para el cálculo.")
      ),
      wellPanel(
        numericInput("population_sd", "Desviación Estándar Poblacional (σ):", value = 1, min = 0.1, max = 10, step = 0.1),
        helpText("La desviación estándar poblacional 'σ' nos da una idea de la dispersión de los datos en la población.")
      )
    ),
    
    mainPanel(
      plotOutput("error_plot", height = "400px"),
      verbatimTextOutput("probability_output"),
      helpText("El gráfico muestra la probabilidad de que el estimado esté dentro de una distancia 'e' del parámetro poblacional."),
      helpText("La región sombreada representa la probabilidad de que el error de estimación sea menor que 'e'.")
    )
  )
)

server <- function(input, output) {
  
  output$error_plot <- renderPlot({
    x_values <- seq(-3, 3, by = 0.01)
    y_values <- dnorm(x_values)
    normal_data <- data.frame(x = x_values, y = y_values)
    e_scaled <- input$error_level / (input$population_sd / sqrt(input$sample_size))
    
    ggplot(normal_data, aes(x = x, y = y)) +
      geom_line(color = secondary_color, size = 1) +
      geom_ribbon(data = normal_data %>% filter(x >= -e_scaled & x <= e_scaled),
                  aes(x = x, ymin = 0, ymax = y),
                  fill = secondary_color, alpha = 0.4) +
      labs(x = expression(Z[bar(X)]), y = "Densidad") +
      theme_minimal() +
      theme(
        plot.title = element_text(face = "bold", size = 20),
        axis.text = element_text(size = 12),
        axis.title = element_text(size = 14),
        panel.border = element_rect(color = "black", fill = NA, linewidth = 1)
      )
  })
  
  output$probability_output <- renderPrint({
    e_scaled <- input$error_level / (input$population_sd / sqrt(input$sample_size))
    probability <- pnorm(e_scaled) - pnorm(-e_scaled)
    cat("Probabilidad:", round(probability, 4))
  })
}

shinyApp(ui, server)
