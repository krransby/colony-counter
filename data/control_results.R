# Load data from .csv files
HQHand <- read.csv("data_HQ_hand.csv", header = T)
HQHough <- read.csv("data_HQ_hough.csv", header = T)
HQWater <- read.csv("data_HQ_water.csv", header = T)

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
houghMean <- c(convert_time(mean(HQHough$Time)), sprintf("%.2f", mean(HQHough$Colonies) / mean(HQHand$Colonies)), sprintf("%.2f", mean(HQHough$FalsePos)), sprintf("%.2f", mean(HQHough$FalseNeg)))
houghMin <- c(convert_time(min(HQHough$Time)), sprintf("%.2f", min(HQHough$Colonies / HQHand$Colonies)), min(HQHough$FalsePos), min(HQHough$FalseNeg))
houghMax <- c(convert_time(max(HQHough$Time)), sprintf("%.2f", max(HQHough$Colonies / HQHand$Colonies)), max(HQHough$FalsePos), max(HQHough$FalseNeg))
houghData <- matrix(c(houghMean, houghMin, houghMax), nrow = 3, byrow = TRUE, dimnames = list(c("Mean", "Min", "Max"), c("time", "Accuracy", "FPR", "FNR")))

# Get accuracy data for Watershed method
waterMean <- c(convert_time(mean(HQWater$Time)), sprintf("%.2f", mean(HQWater$Colonies) / mean(HQHand$Colonies)), sprintf("%.2f", mean(HQWater$FalsePos)), sprintf("%.2f", mean(HQWater$FalseNeg)))
waterMin <- c(convert_time(min(HQWater$Time)), sprintf("%.2f", min(HQWater$Colonies / HQHand$Colonies)), min(HQWater$FalsePos), min(HQWater$FalseNeg))
waterMax <- c(convert_time(max(HQWater$Time)), sprintf("%.2f", max(HQWater$Colonies / HQHand$Colonies)), max(HQWater$FalsePos), max(HQWater$FalseNeg))
waterData <- matrix(c(waterMean, waterMin, waterMax), nrow = 3, byrow = TRUE, dimnames = list(c("Mean", "Min", "Max"), c("time", "Accuracy", "FPR", "FNR")))

# Display output matrices
houghData
waterData


# Output image (simple): ====================================================================================================================================================================================

freedom <- 4

tempHand <- HQHand[order(HQHand$Colonies),]
tempHough <- HQHough[order(HQHough$Colonies),]
tempWater <- HQWater[order(HQWater$Colonies),]

trueSpline <- smooth.spline(tempHand$Colonies, tempHand$Colonies, keep.data = FALSE, df = freedom)
trueTimeSpline <- smooth.spline(tempHand$Colonies, tempHand$Time/60, keep.data = FALSE, df = freedom)

waterSpline <- smooth.spline(tempHand$Colonies, tempWater$Colonies, keep.data = FALSE, df = freedom)
waterSplineUpper <- smooth.spline(tempHand$Colonies, tempWater$Colonies+(tempWater$FalsePos+tempWater$FalseNeg), keep.data = FALSE, df = freedom)
waterSplineLower <- smooth.spline(tempHand$Colonies, tempWater$Colonies-(tempWater$FalsePos+tempWater$FalseNeg), keep.data = FALSE, df = freedom)

houghSpline <- smooth.spline(tempHand$Colonies, tempHough$Colonies, keep.data = FALSE, df = freedom)
houghSplineUpper <- smooth.spline(tempHand$Colonies, tempHough$Colonies+(tempHough$FalsePos+tempHough$FalseNeg), keep.data = FALSE, df = freedom)
houghSplineLower <- smooth.spline(tempHand$Colonies, tempHough$Colonies-(tempHough$FalsePos+tempHough$FalseNeg), keep.data = FALSE, df = freedom)

svg("images/control_data.svg", width = 10, height = 6)

layout(matrix(c(1,2), 1, 2, byrow = TRUE))

# make plot square
par(pty="s")

# ERROR RATES: =====================================================================
plot(tempHand$Colonies, tempHand$Colonies, type = "l", lty = 2, xlim = c(0, 1200), ylim = c(0, 1200), main = "Method error rates", xlab = "Number of colonies present", ylab = "Enumerated colonies")

# limit lines between 0 - 1200
clip(min(0), max(1200), min(0), max(1200))

# WATERSHED TRANSFORM: =================================================
# error rate:
polygon(c(0, waterSplineUpper$x, max(waterSplineUpper$x), rev(waterSplineLower$x)), c(min(waterSplineUpper$y), waterSplineUpper$y, max(waterSplineUpper$y), rev(waterSplineLower$y)), col = orange_soft, border = NA)
# colonies counted:
lines(waterSpline, lwd = 2, col = orange)

# HOUGH CIRCLE TRANSFORM: =================================================
# error rate:
polygon(c(0, houghSplineUpper$x, max(houghSplineUpper$x), rev(houghSplineLower$x)), c(min(houghSplineUpper$y), houghSplineUpper$y, max(houghSplineUpper$y), rev(houghSplineLower$y)), col = purple_soft, border = NA)
# colonies counted:
lines(houghSpline, lwd = 2, col = purple)

# "True" number of colonies
lines(trueSpline, lty = 2)

# Legend
legend("topleft", inset = 0.02, bty = "n", col = c(rgb(0, 0, 0, 1), purple, purple_soft, orange, orange_soft), lwd = c(1, 2, NA, 2, NA), lty = c(2, 1, NA, 1, NA), pch = c(NA, NA, 15, NA, 15), legend = c("True colonies", "Hough Circle colonies", "Hough Circle error rate", "Watershed colonies", "Watershed error rate"))


# TIME TAKEN: =====================================================================
plot(trueTimeSpline, type = "l", lty = 2, main = "Method processing time", xlab = "Number of colonies present", ylab = "Time (minutes)")

clip(min(0), max(1200), min(0), max(tempHand$Time)/60)

lines(smooth.spline(tempHand$Colonies, tempWater$Time/60, keep.data = FALSE, df = freedom), lwd = 2, col = orange)
lines(smooth.spline(tempHand$Colonies, tempHough$Time/60, keep.data = FALSE, df = freedom), lwd = 2, col = purple)

legend("topleft", inset = 0.02, bty = "n", col = c(rgb(0, 0, 0, 1), purple, orange), lwd = c(1, 2, 2), lty = c(2, 1, 1), legend = c("Hand counting", "Hough Circle Transform", "Watershed Transform"))

# 3. Close the file
dev.off()