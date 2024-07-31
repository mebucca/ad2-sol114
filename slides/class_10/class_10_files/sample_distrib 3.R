library(shiny)
library(ggplot2)

ui <- fluidPage(
  titlePanel("Distribución Muestral"),
  sidebarLayout(
    sidebarPanel(
      numericInput("true_mean",
                   "Media Verdadera:",
                   value = 0, min = -10, max = 10),
      numericInput("true_sd",
                   "Desviación Estándar Verdadera:",
                   value = 1, min = 1, max = 10),
      numericInput("sample_size",
                   "Tamaño de Muestra:",
                   value = 100, min = 10, max = 500),
      actionButton("generate_sample", "Generar Nueva Muestra"),
      actionButton("refresh_simulations", "Reiniciar Simulaciones")
    ),
    mainPanel(
      plotOutput("sample_distribution"),
      br(),
      tableOutput("sample_stats")
    )
  )
)

server <- function(input, output, session) {
  
  rv <- reactiveValues(samples = numeric(0))
  
  observeEvent(input$generate_sample, {
    new_sample <- rnorm(input$sample_size, mean = input$true_mean, sd = input$true_sd)
    rv$samples <- c(rv$samples, mean(new_sample))
  })
  
  observeEvent(input$refresh_simulations, {
    rv$samples <- numeric(0)  # Clear stored sample means
  })
  
  output$sample_distribution <- renderPlot({
    ggplot(data.frame(x = rv$samples), aes(x = x)) +
      geom_histogram(fill = "#336699", color = "#225522", bins = 30, alpha = 0.7) +
      geom_vline(aes(xintercept = input$true_mean), linetype = "dashed", color = "#B26666") +
      labs(title = "Distribución Muestral de la Media",
           x = "Media de la Muestra",
           y = "Frecuencia") +
      theme_minimal() +
      theme(
        plot.title = element_text(face = "bold", size = 20),
        panel.border = element_rect(color = "black", fill = NA, linewidth = 1)
      )
  })
  
  output$sample_stats <- renderTable({
    data.frame(
      `Media Verdadera` = input$true_mean,
      `Desviación Estándar Verdadera` = input$true_sd,
      `Media Muestral Promedio` = ifelse(length(rv$samples) > 0, mean(rv$samples), NA),
      `Error Estándar` = ifelse(length(rv$samples) > 0, sd(rv$samples), NA)
    )
  }, row.names = FALSE)
}

shinyApp(ui, server)

