library(shiny)
library(ggplot2)

ui <- fluidPage(
  titlePanel("Ley de los Grandes Números"),
  
  sidebarLayout(
    sidebarPanel(
      numericInput("population_mean", "Media de la Población:", value = 0, min = -10, max = 10),
      numericInput("population_sd", "Desviación Estándar de la Población:", value = 1, min = 0.1, max = 10),
      sliderInput("max_sample_size", "Tamaño Máximo de la Muestra:", value = 10, min = 10, max = 1000),
      actionButton("refresh_simulation", "Limpiar")
    ),
    mainPanel(
      plotOutput("plot_lln")
    )
  )
)

server <- function(input, output, session) {
  
  plot_data <- reactive({
    set.seed(NULL)
    population <- rnorm(1e5, mean = input$population_mean, sd = input$population_sd)
    sample_means <- sapply(1:input$max_sample_size, function(n) {
      mean(sample(population, size = n))
    })
    
    data.frame(sample_size = 1:input$max_sample_size, sample_mean = sample_means)
  })
  
  observeEvent(input$refresh_simulation, {
    invalidateLater(1000, session) # invalidate after 1 second to reset the slider and refresh the plot.
  })
  
  output$plot_lln <- renderPlot({
    ggplot(plot_data(), aes(x = sample_size, y = sample_mean)) +
      geom_line(color = "#336699") +
      geom_hline(yintercept = input$population_mean, linetype = "dashed", color = "#B26666") +
      labs(title = "Ilustración de la Ley de los Grandes Números",
           x = "Tamaño de la Muestra",
           y = "Media de la Muestra") +
      theme_minimal() +
      theme(
        plot.title = element_text(face = "bold", size = 20),
        panel.border = element_rect(color = "black", fill = NA, linewidth = 1)
      )
  })
}

shinyApp(ui, server)

