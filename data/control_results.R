# Load data from .csv files
hand <- read.csv("data_HQ_LQ_hand.csv", header = T)
HQHough <- read.csv("data_HQ_hough.csv", header = T)
HQwater <- read.csv("data_HQ_water.csv", header = T)

# X range to use for plotting
x <- seq(1:19)

# The mean overall accuracy of each method
mean(HQHough$Colonies) / mean(hand$Colonies)
mean(HQwater$Colonies) / mean(hand$Colonies)


# Plot the time taken (in minutes) by each method
# 1. Open png file
png("images/time_taken.png", width = 1000, height = 562.5)

# 2. Create the plot
plot(x, HQwater$Time/60, xaxt="n", type = "l", lwd = 2, col = rgb(0.5, 1, 0.5, 1), ylim = c(0,13), main = "Time taken by each method", xlab = "Test", ylab = "Time (minutes)")
axis(1, at = x)
lines(x, HQHough$Time/60, lwd = 2, col = rgb(1, 0.5, 1, 1))
lines(x, hand$Time/60, lwd = 1, lty = 2, col = rgb(0, 0, 0, 1))
legend(x = 11.5, y = 13, col = c(rgb(0, 0, 0, 1), rgb(0.5, 1, 0.5, 1), rgb(1, 0.5, 1, 1)), lwd = c(1, 2, 2), lty = c(2, 1, 1), legend = c("Hand counting", "Watershed Transform", "Hough Circle Transform"))

# 3. Close the file
dev.off()


# Plot the error ranges and total number of colonies found by each method
# 1. Open png file
png("images/error_rates.png", width = 1000, height = 562.5)

# 2. Create the plot
plot(x, HQwater$Colonies, xaxt="n", type = "l", lwd = 2, xlim = c(1,19), ylim = c(0, 1400), col = rgb(0.5, 1, 0.5, 1), main = "Number of colonies enumerated by each method", xlab = "Test", ylab = "Number of enumerated Colonies")
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

legend(x = 11.5, y = 1400, col = c(rgb(0, 0, 0, 1), rgb(0.5, 1, 0.5, 1), rgb(0.5, 1, 0.5, 0.25), rgb(1, 0.5, 1, 1), rgb(1, 0.5, 1, 0.25)), lwd = c(1, 2, NA, 2, NA), lty = c(2, 1, NA, 1, NA), pch = c(NA, NA, 15, NA, 15), legend = c("Actual number of colonies", "Watershed colonies", "Watershed error rate", "Hough Circle colonies", "Hough circle error rate"))

# 3. Close the file
dev.off()
