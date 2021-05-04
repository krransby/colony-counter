# Load data from .csv files
hand <- read.csv("data_HQ_LQ_hand.csv", header = T)
HQHough <- read.csv("data_HQ_hough.csv", header = T)
HQwater <- read.csv("data_HQ_water.csv", header = T)

# X range to use for plotting
x <- seq(1:19)

# colours to use in plots
purple <- rgb(0.78, 0.2, 1, 1)
purple_soft <- rgb(0.78, 0.2, 1, 0.25)
orange <- rgb(1, 0.74, 0.1, 1)
orange_soft <- rgb(1, 0.74, 0.1, 0.25)

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
houghMin <- c(convert_time(min(HQHough$Time)), sprintf("%.2f", min(HQHough$Colonies / hand$Colonies)), min(HQHough$FalsePos), min(HQHough$FalseNeg))
houghMax <- c(convert_time(max(HQHough$Time)), sprintf("%.2f", max(HQHough$Colonies / hand$Colonies)), max(HQHough$FalsePos), max(HQHough$FalseNeg))
houghData <- matrix(c(houghMean, houghMin, houghMax), nrow = 3, byrow = TRUE, dimnames = list(c("Mean", "Min", "Max"), c("time", "Accuracy", "FPR", "FNR")))

# Get accuracy data for Watershed method
waterMean <- c(convert_time(mean(HQwater$Time)), sprintf("%.2f", mean(HQwater$Colonies) / mean(hand$Colonies)), sprintf("%.2f", mean(HQwater$FalsePos)), sprintf("%.2f", mean(HQwater$FalseNeg)))
waterMin <- c(convert_time(min(HQwater$Time)), sprintf("%.2f", min(HQwater$Colonies / hand$Colonies)), min(HQwater$FalsePos), min(HQwater$FalseNeg))
waterMax <- c(convert_time(max(HQwater$Time)), sprintf("%.2f", max(HQwater$Colonies / hand$Colonies)), max(HQwater$FalsePos), max(HQwater$FalseNeg))
waterData <- matrix(c(waterMean, waterMin, waterMax), nrow = 3, byrow = TRUE, dimnames = list(c("Mean", "Min", "Max"), c("time", "Accuracy", "FPR", "FNR")))

# Display output matrices
houghData
waterData


# Output image (complex): ====================================================================================================================================================================================

# 1. Open output file
#png("images/control_data.png", width = 1000, height = 1615)
svg("images/control_data.svg", width = 8, height = 8)

# set image layout
layout(matrix(c(1,1,2,2), 2, 2, byrow = TRUE))

# time ------------------------------------
plot(x, HQwater$Time/60, xaxt="n", type = "l", lwd = 2, col = purple, ylim = c(0,13), main = "Time taken by each method", xlab = "Test", ylab = "Time (minutes)")
axis(1, at = x)
lines(x, HQHough$Time/60, lwd = 2, col = orange)
lines(x, hand$Time/60, lwd = 1, lty = 2, col = rgb(0, 0, 0, 1))
legend("topleft", inset = 0.02, bty = "n", col = c(rgb(0, 0, 0, 1), purple, orange), lwd = c(1, 2, 2), lty = c(2, 1, 1), legend = c("Hand counting", "Watershed Transform", "Hough Circle Transform"))


# both accuracy ------------------------------------
plot(x, HQwater$Colonies, xaxt="n", type = "l", lwd = 2, xlim = c(1,19), ylim = c(0, 1400), col = orange, main = "Number of colonies enumerated by each method (with error rates)", xlab = "Test", ylab = "Number of enumerated Colonies")
axis(1, at = x)
# plot water error rate
upperBoundry = HQwater$Colonies + (abs(hand$Colonies - HQwater$Colonies) + HQwater$FalsePos)
lowerBoundry = HQwater$Colonies - (abs(hand$Colonies - HQwater$Colonies) - HQwater$FalseNeg)
polygon(c(x, rev(x)), c(upperBoundry, rev(lowerBoundry)), col = orange_soft, border = NA)
# plot hough error rate
upperBoundry = HQHough$Colonies + (abs(hand$Colonies - HQHough$Colonies) + HQHough$FalsePos)
lowerBoundry = HQHough$Colonies - (abs(hand$Colonies - HQHough$Colonies) - HQHough$FalseNeg)
polygon(c(x, rev(x)), c(upperBoundry, rev(lowerBoundry)), col = purple_soft, border = NA)
lines(x, HQHough$Colonies, lwd = 2, col = purple)
# hand count
lines(x, hand$Colonies, lwd = 1, lty = 2, col = rgb(0, 0, 0, 1))
# legend
legend("topleft", inset = 0.02, bty = "n", col = c(rgb(0, 0, 0, 1), orange, orange_soft, purple, purple_soft), lwd = c(1, 2, NA, 2, NA), lty = c(2, 1, NA, 1, NA), pch = c(NA, NA, 15, NA, 15), legend = c("True colonies", "Watershed colonies", "Watershed error rate", "Hough Circle colonies", "Hough Circle error rate"))

# 3. Close the file
dev.off()


# Output image (simple): ====================================================================================================================================================================================

tempHand <- hand[order(hand$Colonies),]
tempHough <- HQHough[order(HQHough$Colonies),]
tempWater <- HQwater[order(HQwater$Colonies),]

svg("images/control_data.svg", width = 10, height = 6)

layout(matrix(c(1,2), 1, 2, byrow = TRUE))

# make plot square
par(pty="s")

# ERROR RATES: =====================================================================
plot(tempHand$Colonies, tempHand$Colonies, type = "l", lty = 2, xlim = c(0, 1200), ylim = c(0, 1200), main = "Method error rates", xlab = "Number of colonies present", ylab = "Enumerated colonies")

# limit lines between 0 - 1200
clip(min(0), max(1200), min(0), max(1200))

# WATERSHED TRANSFORM: =================================================
polygon(c(0, 1200, 1200), c(0,#min(lm(HQwater$Colonies~hand$Colonies)$fitted.values),
                            max(lm(HQwater$Colonies+(HQwater$FalsePos+HQwater$FalseNeg)~hand$Colonies)$fitted.values),
                            max(lm(HQwater$Colonies-(HQwater$FalsePos+HQwater$FalseNeg)~hand$Colonies)$fitted.values)), col = orange_soft, border = NA)

# middle
#points(hand$Colonies, HQwater$Colonies, col = purple)
#abline(lm(HQwater$Colonies~hand$Colonies), col = purple)
lines(x = c(0, 1200), y = c(0, max(lm(HQwater$Colonies~hand$Colonies)$fitted.values)), lwd = 2, col = orange)


# HOUGH CIRCLE TRANSFORM: =================================================
polygon(c(0, 1200, 1200), c(min(lm(HQHough$Colonies~hand$Colonies)$fitted.values),
                            max(lm(HQHough$Colonies+(HQHough$FalsePos+HQHough$FalseNeg)~hand$Colonies)$fitted.values),
                            max(lm(HQHough$Colonies-(HQHough$FalsePos+HQHough$FalseNeg)~hand$Colonies)$fitted.values)), col = purple_soft, border = NA)
# middle
#points(hand$Colonies, HQHough$Colonies, col = orange)
abline(lm(HQHough$Colonies~hand$Colonies), lwd = 2, col = purple)

# actual number of colonies
lines(tempHand$Colonies, tempHand$Colonies, lty = 2)

# Legend
legend("topleft", inset = 0.02, bty = "n", col = c(rgb(0, 0, 0, 1), orange, orange_soft, purple, purple_soft), lwd = c(1, 2, NA, 2, NA), lty = c(2, 1, NA, 1, NA), pch = c(NA, NA, 15, NA, 15), legend = c("True colonies", "Watershed colonies", "Watershed error rate", "Hough Circle colonies", "Hough Circle error rate"))


# TIME TAKEN: =====================================================================
plot(tempHand$Colonies, lm(tempHand$Time/60~tempHand$Colonies)$fitted.values, type = "l", lty = 2, main = "Method processing time", xlab = "Number of colonies present", ylab = "Time (minutes)")

clip(min(0), max(1200), min(0), max(tempHand$Time)/60)

abline(lm(tempWater$Time/60~tempHand$Colonies), lwd = 2, col = orange)
abline(lm(tempHough$Time/60~tempHand$Colonies), lwd = 2, col = purple)

legend("topleft", inset = 0.02, bty = "n", col = c(rgb(0, 0, 0, 1), orange, purple), lwd = c(1, 2, 2), lty = c(2, 1, 1), legend = c("Hand counting", "Watershed Transform", "Hough Circle Transform"))

# 3. Close the file
dev.off()