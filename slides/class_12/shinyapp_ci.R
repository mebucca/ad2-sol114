library(shiny)
library(tidyverse)

ui <- fluidPage(
  titlePanel("Estimación de la Edad Promedio de Graduación en Chile (μ = 25 años)"),
  sidebarLayout(
    sidebarPanel(
      numericInput("num_samples",
                   "n:",
                   value = 100,
                   min = 10,
                   max = 500,
                   step = 10),
      numericInput("confidence_level",
                   "Nivel de Confianza:",
                   value = 0.95,
                   min = 0.50,
                   max = 0.99,
                   step = 0.01),
      actionButton("add_interval", "Generar Nueva Muestra"),
      actionButton("refresh_simulations", "Refrescar Simulaciones")  
    ),
    mainPanel(
      plotOutput("plot_intervals"),
      br(),
      tableOutput("interval_stats"),
      br(),
      tableOutput("interval_details")
    )
  )
)

server <- function(input, output, session) {
  
  rv <- reactiveValues(data = data.frame(start = numeric(0), end = numeric(0), 
                                         mean_estimate = numeric(0), color = character(0)),
                       contains_mean = 0,
                       does_not_contain_mean = 0)
  
  observeEvent(input$add_interval, {
    # Usamos una media verdadera de 25 (edad promedio de graduación en Chile)
    true_mean <- 25
    set.seed(NULL)
    samples <- rnorm(input$num_samples, mean = true_mean, sd = 5)  # Muestra aleatoria con desvío estándar de 5
    mean_samples <- mean(samples)
    se <- sd(samples) / sqrt(length(samples))
    z_value <- qnorm(1 - (1 - input$confidence_level) / 2)  # para dos colas
    CI_start <- mean_samples - z_value * se
    CI_end <- mean_samples + z_value * se
    
    # Determinar el color según si el IC contiene la media verdadera (μ = 25)
    interval_color <- ifelse(CI_start <= true_mean && CI_end >= true_mean, "#336699", "#B26666")
    
    rv$data <- rbind(rv$data, data.frame(start = CI_start, 
                                         end = CI_end, 
                                         mean_estimate = mean_samples, 
                                         color = interval_color))
    
    # Actualizar los contadores de si el IC contiene la media verdadera
    if(CI_start <= true_mean && CI_end >= true_mean) {
      rv$contains_mean <- rv$contains_mean + 1
    } else {
      rv$does_not_contain_mean <- rv$does_not_contain_mean + 1
    }
  })
  
  observeEvent(input$refresh_simulations, {
    rv$data <- data.frame(start = numeric(0), end = numeric(0), 
                          mean_estimate = numeric(0), color = character(0))
    rv$contains_mean <- 0
    rv$does_not_contain_mean <- 0
  })
  
  output$plot_intervals <- renderPlot({
    true_mean <- 25  # Media verdadera para la edad promedio de graduación
    ggplot(rv$data, aes(xmin = start, xmax = end, y = seq_along(start), fill = color)) +
      geom_rect(aes(ymin = seq_along(start) - 0.2, ymax = seq_along(start) + 0.2), alpha = 0.4) + 
      scale_fill_identity() +
      geom_vline(xintercept = true_mean, linetype = "dashed", color = "#225522", size = 1.2) +  # Línea para la media verdadera (μ = 25)
      geom_point(aes(x = mean_estimate, y = seq_along(mean_estimate)), color = "black", size = 3) +  # Punto para la media estimada (\hat{\mu})
      geom_errorbarh(aes(xmin = start, xmax = end, y = seq_along(start)), height = 0.2, color = "blue") +  # Líneas para el intervalo de confianza
      xlim(min(rv$data$start, na.rm = TRUE), max(rv$data$end, na.rm = TRUE)) +
      ylim(0, nrow(rv$data) + 1) +
      labs(title = "Intervalos de Confianza",
           subtitle = paste(input$confidence_level * 100, "% Nivel de Confianza"),
           x = "Valor",
           y = "Número de Intervalo") +
      theme_minimal() +
      theme(
        plot.title = element_text(face = "bold", size = 20),
        axis.text.y = element_blank(),  # Ocultar los números de los intervalos en el eje y
        axis.ticks.y = element_blank(),  
        panel.border = element_rect(color = "black", fill = NA, linewidth = 1)
      )
  })
  
  output$interval_stats <- renderTable({
    total_intervals <- rv$contains_mean + rv$does_not_contain_mean
    percentage_contains <- (rv$contains_mean / total_intervals) * 100
    data.frame(Categoría = c("Intervalos que contienen μ", 
                             "Intervalos que no contienen μ", 
                             "% que contienen μ"),
               Cantidad = c(rv$contains_mean, 
                            rv$does_not_contain_mean, 
                            percentage_contains))
  }, row.names = FALSE)
  
  output$interval_details <- renderTable({
    rv$data %>%
      dplyr::mutate(`Media Estimada` = round(mean_estimate, 3),
                    `Límite Inferior` = round(start, 3),
                    `Límite Superior` = round(end, 3)) %>%
      dplyr::select(HTML("&mu;&#770; (Media Estimada)"), `Límite Inferior`, `Límite Superior`)
  }, row.names = FALSE)
}

shinyApp(ui, server)
