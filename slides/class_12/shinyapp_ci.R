library(shiny)
library(ggplot2)

ui <- fluidPage(
  titlePanel(""),
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
      tableOutput("interval_stats")
    )
  )
)

server <- function(input, output, session) {
  
  rv <- reactiveValues(data = data.frame(start = numeric(0), end = numeric(0), color = character(0)),
                       contains_mean = 0,
                       does_not_contain_mean = 0)
  
  observeEvent(input$add_interval, {
    # Generate the new confidence interval
    set.seed(NULL)
    samples <- rnorm(input$num_samples)
    mean_samples <- mean(samples)
    se <- sd(samples) / sqrt(length(samples))
    z_value <- qnorm(1 - (1 - input$confidence_level) / 2)  # for two tails
    CI_start <- mean_samples - z_value * se
    CI_end <- mean_samples + z_value * se
    
    # Determine the color based on if the CI contains the true mean
    interval_color <- ifelse(CI_start <= 0 && CI_end >= 0, "#336699", "#B26666")
    
    rv$data <- rbind(rv$data, data.frame(start = CI_start, end = CI_end, color = interval_color))
    
    # Update counters based on if the CI contains the true mean (0 for standard normal)
    if(CI_start <= 0 && CI_end >= 0) {
      rv$contains_mean <- rv$contains_mean + 1
    } else {
      rv$does_not_contain_mean <- rv$does_not_contain_mean + 1
    }
  })
  
  observeEvent(input$refresh_simulations, {
    rv$data <- data.frame(start = numeric(0), end = numeric(0), color = character(0))
    rv$contains_mean <- 0
    rv$does_not_contain_mean <- 0
  })
  
  output$plot_intervals <- renderPlot({
    ggplot(rv$data, aes(xmin = start, xmax = end, y = seq_along(start), fill = color)) +
      geom_rect(aes(ymin = seq_along(start) - 0.2, ymax = seq_along(start) + 0.2), alpha = 1) + 
      scale_fill_identity() +
      geom_vline(xintercept = 0, linetype = "dashed", color = "#225522") +  # Green line for the true mean
      xlim(min(rv$data$start, na.rm = TRUE), max(rv$data$end, na.rm = TRUE)) +
      ylim(0, nrow(rv$data) + 1) +
      labs(title = "Intervalos de Confianza Generados",
           subtitle = paste(input$confidence_level * 100, "% Nivel de Confianza"),
           x = "Valor",
           y = "Número de Intervalo") +
      theme_minimal() +
      theme(
        plot.title = element_text(face = "bold", size = 20),
        axis.text = element_blank(),  
        axis.ticks = element_blank(),  
        panel.border = element_rect(color = "black", fill = NA, linewidth = 1)
      )
  })
  
  output$interval_stats <- renderTable({
    total_intervals <- rv$contains_mean + rv$does_not_contain_mean
    percentage_contains <- (rv$contains_mean / total_intervals) * 100
    data.frame(Categoría = c("Intervalos que contienen la media", "Intervalos que no contienen la media", "% que contienen la media"),
               Cantidad = c(rv$contains_mean, rv$does_not_contain_mean, percentage_contains))
  }, row.names = FALSE)
}

shinyApp(ui, server)
