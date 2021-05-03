# Load data from .csv files
hand <- read.csv("data_HQ_LQ_hand.csv", header = T)
HQHough <- read.csv("data_HQ_hough.csv", header = T)
HQwater <- read.csv("data_HQ_water.csv", header = T)

# X range to use for plotting
x <- seq(1:19)

# Convert from seconds to MM:SS.MS format
convert_time <- function(sec) {
  
  min <- 0
  
  while ((sec - 60) >= 0) {
    min = min + 1
    sec = sec - 60
  }
  if ((sec < 10) && (min < 10)) {
    output = sprintf("0%d:0%.2f", min, sec)
  } else if (min < 10) {
    output = sprintf("0%d:%.2f", min, sec)
  } else if (sec < 10) {
    output = sprintf("%d:0%.2f", min, sec)
  }
  
  return(output)
}

# Get accuracy data for Hough Circle method
houghMean <- c(convert_time(mean(HQHough$Time)), sprintf("%.2f", mean(HQHough$Colonies) / mean(hand$Colonies)), sprintf("%.2f", mean(HQHough$FalsePos)), sprintf("%.2f", mean(HQHough$FalseNeg)))
houghMin <- c(convert_time(min(HQHough$Time)), sprintf("%.2f", min(HQHough$Colonies) / min(hand$Colonies)), min(HQHough$FalsePos), min(HQHough$FalseNeg))
houghMax <- c(convert_time(max(HQHough$Time)), sprintf("%.2f", max(HQHough$Colonies) / max(hand$Colonies)), max(HQHough$FalsePos), max(HQHough$FalseNeg))
houghData <- matrix(c(houghMean, houghMin, houghMax), nrow = 3, byrow = TRUE, dimnames = list(c("Mean", "Min", "Max"), c("time", "Accuracy", "FPR", "FNR")))

# Get accuracy data for Watershed method
waterMean <- c(convert_time(mean(HQwater$Time)), sprintf("%.2f", mean(HQwater$Colonies) / mean(hand$Colonies)), sprintf("%.2f", mean(HQwater$FalsePos)), sprintf("%.2f", mean(HQwater$FalseNeg)))
waterMin <- c(convert_time(min(HQwater$Time)), sprintf("%.2f", min(HQwater$Colonies) / min(hand$Colonies)), min(HQwater$FalsePos), min(HQwater$FalseNeg))
waterMax <- c(convert_time(max(HQwater$Time)), sprintf("%.2f", max(HQwater$Colonies) / max(hand$Colonies)), max(HQwater$FalsePos), max(HQwater$FalseNeg))
waterData <- matrix(c(waterMean, waterMin, waterMax), nrow = 3, byrow = TRUE, dimnames = list(c("Mean", "Min", "Max"), c("time", "Accuracy", "FPR", "FNR")))

# Display outputs
houghData
waterData


# Plot the time taken (in minutes) by each method
# 1. Open png file
png("images/time_taken.png", width = 1000, height = 562.5)

# 2. Create the plot
plot(x, HQwater$Time/60, xaxt="n", type = "l", lwd = 2, col = rgb(0.5, 1, 0.5, 1), ylim = c(0,13), main = "Time taken by each method", xlab = "Test", ylab = "Time (minutes)")
axis(1, at = x)
lines(x, HQHough$Time/60, lwd = 2, col = rgb(1, 0.5, 1, 1))
lines(x, hand$Time/60, lwd = 1, lty = 2, col = rgb(0, 0, 0, 1))
legend("topright", inset = 0.01, col = c(rgb(0, 0, 0, 1), rgb(0.5, 1, 0.5, 1), rgb(1, 0.5, 1, 1)), lwd = c(1, 2, 2), lty = c(2, 1, 1), legend = c("Hand counting", "Watershed Transform", "Hough Circle Transform"))

# 3. Close the file
dev.off()


# Plot the error ranges and total number of colonies found by each method
# 1. Open png file
png("images/error_rates.png", width = 1000, height = 562.5)

# 2. Create the plot
plot(x, HQwater$Colonies, xaxt="n", type = "l", lwd = 2, xlim = c(1,19), ylim = c(0, 1400), col = rgb(0.5, 1, 0.5, 1), main = "Number of colonies enumerated by each method (with error rates)", xlab = "Test", ylab = "Number of enumerated Colonies")
axis(1, at = x)
# plot water error rate
upperBoundry = HQwater$Colonies + (abs(hand$Colonies - HQwater$Colonies) + HQwater$FalsePos)
lowerBoundry = HQwater$Colonies - (abs(hand$Colonies - HQwater$Colonies) - HQwater$FalseNeg)
polygon(c(x, x, min(x), min(x), max(x), max(x)), c(upperBoundry, lowerBoundry, upperBoundry[1], lowerBoundry[1], upperBoundry[19], lowerBoundry[19]), col = rgb(0.5, 1, 0.5, 0.25), border = NA)

# plot hough error rate
upperBoundry = HQHough$Colonies + (abs(hand$Colonies - HQHough$Colonies) + HQHough$FalsePos)
lowerBoundry = HQHough$Colonies - (abs(hand$Colonies - HQHough$Colonies) - HQHough$FalseNeg)
polygon(c(x, x, min(x), min(x), max(x), max(x)), c(upperBoundry, lowerBoundry, upperBoundry[1], lowerBoundry[1], upperBoundry[19], lowerBoundry[19]), col = rgb(1, 0.5, 1, 0.25), border = NA)
lines(x, HQHough$Colonies, lwd = 2, col = rgb(1, 0.5, 1, 1))

lines(x, hand$Colonies, lwd = 1, lty = 2, col = rgb(0, 0, 0, 1))

legend("topright", inset = 0.01, col = c(rgb(0, 0, 0, 1), rgb(0.5, 1, 0.5, 1), rgb(0.5, 1, 0.5, 0.25), rgb(1, 0.5, 1, 1), rgb(1, 0.5, 1, 0.25)), lwd = c(1, 2, NA, 2, NA), lty = c(2, 1, NA, 1, NA), pch = c(NA, NA, 15, NA, 15), legend = c("True colonies", "Watershed colonies", "Watershed error rate", "Hough Circle colonies", "Hough Circle error rate"))

# 3. Close the file
dev.off()
