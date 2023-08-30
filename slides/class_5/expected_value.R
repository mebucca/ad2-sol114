library(shiny)
library(ggplot2)

ui <- fluidPage(
  titlePanel(""),
  sidebarLayout(
    sidebarPanel(
      sliderInput("position", "Valor X:", min = -5, max = 5, value = 0, step = 0.01),
      verbatimTextOutput("cumulative_sum_text")  # Moved text here
    ),
    mainPanel(
      fluidRow(
        column(width = 6, plotOutput("pdf_plot")),
        column(width = 6, plotOutput("product_plot"))
      )
    )
  )
)

server <- function(input, output) {
  x_vals <- seq(-5, 5, length.out = 400)
  normal_dist <- dnorm(x_vals, mean = 0, sd = 1)
  
  cumulative_sum <- reactive({
    position <- input$position
    integration_x <- x_vals[x_vals <= position]
    integration_y <- integration_x * normal_dist[x_vals <= position]
    cum_sum <- sum(integration_y)
    cum_sum
  })
  
  output$pdf_plot <- renderPlot({
    shaded_area <- data.frame(
      x = c(-4, x_vals[x_vals <= input$position], input$position),
      y = c(0, normal_dist[x_vals <= input$position], 0)
    )
    
    ggplot() +
      geom_line(aes(x = x_vals, y = normal_dist), color = "#4953A6", size = 1) +
      geom_ribbon(data = shaded_area, aes(x = x, ymin = 0, ymax = y), fill = "#4953A6", alpha = 0.3) +
      scale_x_continuous(breaks = seq(-5, 5, by = 1)) +  # Set x-axis breaks
      labs(
        title = "f(x): densidad probabilística",
        x = "X",
        y = "f(x)"
      ) +
      theme_minimal()
  })
  
  output$product_plot <- renderPlot({
    product_vals <- x_vals * normal_dist
    
    current_cumulative_sum <- cumulative_sum()
    
    ggplot(data.frame(X = x_vals, Product = product_vals, CumulativeSum = cumsum(product_vals)),
           aes(x = X, y = Product)) +
      geom_line(color = "#4953A6", size = 1) +
      geom_point(aes(x = input$position, y = input$position * dnorm(input$position)),
                 color = "#DF484C", size = 3) +
      geom_line(data = data.frame(X = x_vals[x_vals <= input$position], Product = product_vals[x_vals <= input$position]),
                aes(x = X, y = Product), color = "#DF484C", size = 1) +
      geom_text(aes(x = input$position + 0.3, y = input$position * dnorm(input$position),
                    label = paste("Sum =", round(current_cumulative_sum, 2))),
                color = "#DF484C", hjust = 0) +
      scale_x_continuous(breaks = seq(-5, 5, by = 1)) +  # Set x-axis breaks
      labs(
        title = "x * f(x)",
        x = "X",
        y = "Value"
      ) +
      theme_minimal()
  })
  
  output$cumulative_sum_text <- renderText({
    paste("Integral x*f(x) hasta X=x:", round(cumulative_sum(), 2))
  })
}

shinyApp(ui = ui, server = server)
