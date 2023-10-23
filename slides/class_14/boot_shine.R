library(shiny)
library(ggplot2)

ui <- fluidPage(
  titlePanel("Bootstrap Demo con Función Personalizada"),
  
  sidebarLayout(
    sidebarPanel(
      helpText("Define tu muestra y elige cuántas re-muestras bootstrap deseas realizar."),
      
      numericInput("data_size", "Tamaño de la Muestra:", value = 30, min = 5, max = 500),
      numericInput("num_resamples", "Número de re-muestras Bootstrap:", value = 1000, min = 100, max = 10000),
      
      textInput("custom_function", "Escribe una función de R en la forma f(x):", value = "mean(x)"),
      helpText("Por ejemplo, puedes ingresar 'mean(x)', 'median(x)', 'sd(x)', o cualquier función que aplique a un vector 'x'."),
      
      actionButton("bootstrap_button", "Realizar Bootstrap")
    ),
    
    mainPanel(
      plotOutput("bootstrap_plot"),
      helpText("El gráfico muestra la distribución de la estadística elegida de las muestras bootstrapped. Permite comprender la variabilidad del estadístico.")
    )
  )
)

server <- function(input, output, session) {
  
  observeEvent(input$bootstrap_button, {
    # Generate a sample from a normal distribution
    original_sample <- rnorm(input$data_size)
    
    # Function to get a bootstrap resample
    bootstrap_resample <- function(data) {
      sample(data, length(data), replace = TRUE)
    }
    
    # Parse the user-defined function
    func <- tryCatch(eval(parse(text = paste("function(x)", input$custom_function))), error = function(e) return(NULL))
    
    if(is.null(func)) {
      showModal(modalDialog(
        title = "Error",
        "La función ingresada no es válida. Por favor, verifica e intenta de nuevo."
      ))
      return()
    }
    
    # Resample multiple times and apply the custom function for each resample
    bootstrap_values <- replicate(input$num_resamples, func(bootstrap_resample(original_sample)))
    
    output$bootstrap_plot <- renderPlot({
      ggplot(data.frame(bootstrap_values = bootstrap_values), aes(bootstrap_values)) +
        geom_histogram(fill = "#336699", color = "white", bins = 30) +
        geom_vline(aes(xintercept = func(original_sample)), linetype = "dashed", color = "#FF0000") +
        labs(title = paste("Distribución Bootstrap de", deparse(substitute(func))), 
             x = deparse(substitute(func)), 
             y = "Frecuencia") +
        theme_minimal()
    })
  })
}

shinyApp(ui, server)
